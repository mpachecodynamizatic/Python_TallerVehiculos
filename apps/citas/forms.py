from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Cita
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.usuarios.models import Usuario


class CitaForm(forms.ModelForm):
    """
    Formulario para crear y editar citas.
    Incluye validaciones personalizadas y widgets con estilos Tailwind CSS.
    """

    class Meta:
        model = Cita
        fields = [
            'cliente',
            'vehiculo',
            'fecha_hora',
            'duracion_estimada',
            'tipo_servicio',
            'mecanico_asignado',
            'descripcion',
            'notas',
            'estado',
        ]
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'x-model': 'clienteId',
                '@change': 'cargarVehiculos()'
            }),
            'vehiculo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'x-bind:disabled': '!clienteId'
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            }),
            'duracion_estimada': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '15',
                'step': '15',
                'placeholder': '60'
            }),
            'tipo_servicio': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'mecanico_asignado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describa el servicio solicitado por el cliente...'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notas internas del taller (opcional)...'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }
        help_texts = {
            'duracion_estimada': 'Duración estimada en minutos (mínimo 15, múltiplos de 15)',
            'mecanico_asignado': 'Opcional: Asignar un mecánico específico',
            'notas': 'Notas internas, no visibles para el cliente',
        }

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario con filtros personalizados"""
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('apellidos', 'nombre')

        # Si hay una instancia (edición), filtrar vehículos del cliente
        if self.instance and self.instance.cliente_id:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
                cliente=self.instance.cliente,
                activo=True
            ).order_by('marca', 'modelo')
        else:
            # En creación, mostrar todos los vehículos activos (se filtrará con Alpine.js)
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True).order_by('marca', 'modelo')

        # Filtrar solo mecánicos activos
        self.fields['mecanico_asignado'].queryset = Usuario.objects.filter(
            rol=Usuario.Rol.MECANICO,
            activo=True
        ).order_by('first_name', 'last_name')
        self.fields['mecanico_asignado'].required = False

        # Hacer notas opcionales
        self.fields['notas'].required = False

        # Labels personalizados
        self.fields['cliente'].label = 'Cliente'
        self.fields['vehiculo'].label = 'Vehículo'
        self.fields['fecha_hora'].label = 'Fecha y Hora'
        self.fields['duracion_estimada'].label = 'Duración (minutos)'
        self.fields['tipo_servicio'].label = 'Tipo de Servicio'
        self.fields['mecanico_asignado'].label = 'Mecánico Asignado'
        self.fields['descripcion'].label = 'Descripción del Servicio'
        self.fields['notas'].label = 'Notas Internas'

        # Si es una cita nueva, ocultar el campo estado
        if not self.instance.pk:
            self.fields.pop('estado', None)
        else:
            self.fields['estado'].label = 'Estado de la Cita'

    def clean_fecha_hora(self):
        """Validar que la fecha/hora sea futura"""
        fecha_hora = self.cleaned_data.get('fecha_hora')

        if fecha_hora:
            # Solo validar para citas nuevas o si se cambió la fecha
            if not self.instance.pk or self.instance.fecha_hora != fecha_hora:
                # Permitir un margen de 5 minutos para evitar problemas de sincronización
                if fecha_hora < timezone.now() - timedelta(minutes=5):
                    raise ValidationError('La fecha y hora debe ser futura.')

                # Validar horario laboral (8:00 - 20:00)
                hora = fecha_hora.hour
                if hora < 8 or hora >= 20:
                    raise ValidationError('Las citas deben agendarse entre las 8:00 y las 20:00 horas.')

                # Validar que no sea domingo
                if fecha_hora.weekday() == 6:  # 6 = Domingo
                    raise ValidationError('No se pueden agendar citas los domingos.')

        return fecha_hora

    def clean_duracion_estimada(self):
        """Validar duración estimada"""
        duracion = self.cleaned_data.get('duracion_estimada')

        if duracion:
            if duracion < 15:
                raise ValidationError('La duración mínima es de 15 minutos.')
            if duracion > 480:  # 8 horas
                raise ValidationError('La duración máxima es de 8 horas (480 minutos).')
            if duracion % 15 != 0:
                raise ValidationError('La duración debe ser múltiplo de 15 minutos.')

        return duracion

    def clean_vehiculo(self):
        """Validar que el vehículo pertenece al cliente seleccionado"""
        vehiculo = self.cleaned_data.get('vehiculo')
        cliente = self.cleaned_data.get('cliente')

        if vehiculo and cliente:
            if vehiculo.cliente != cliente:
                raise ValidationError('El vehículo seleccionado no pertenece al cliente.')
            if not vehiculo.activo:
                raise ValidationError('No se pueden agendar citas para vehículos inactivos.')

        return vehiculo

    def clean(self):
        """Validaciones adicionales del formulario completo"""
        cleaned_data = super().clean()

        mecanico = cleaned_data.get('mecanico_asignado')
        fecha_hora = cleaned_data.get('fecha_hora')
        duracion = cleaned_data.get('duracion_estimada')

        # Validar conflictos de horario si hay mecánico asignado
        if mecanico and fecha_hora and duracion:
            self._validar_conflicto_mecanico(mecanico, fecha_hora, duracion)

        return cleaned_data

    def _validar_conflicto_mecanico(self, mecanico, fecha_hora, duracion):
        """Valida que el mecánico no tenga otra cita en el mismo horario"""
        hora_inicio = fecha_hora
        hora_fin = hora_inicio + timedelta(minutes=duracion)

        # Buscar citas del mismo mecánico que se superpongan
        citas_conflictivas = Cita.objects.filter(
            mecanico_asignado=mecanico,
            fecha_hora__lt=hora_fin,
            fecha_hora__gte=hora_inicio - timedelta(hours=2)
        ).exclude(
            estado__in=[Cita.EstadoCita.CANCELADA, Cita.EstadoCita.COMPLETADA]
        )

        # Excluir la cita actual si es edición
        if self.instance.pk:
            citas_conflictivas = citas_conflictivas.exclude(pk=self.instance.pk)

        for cita in citas_conflictivas:
            cita_fin = cita.fecha_hora + timedelta(minutes=cita.duracion_estimada)
            # Verificar superposición
            if hora_inicio < cita_fin and hora_fin > cita.fecha_hora:
                raise ValidationError({
                    'mecanico_asignado': f'El mecánico {mecanico.get_full_name()} ya tiene una cita '
                                       f'programada el {cita.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. '
                                       f'Por favor, elija otro horario u otro mecánico.'
                })


class CambiarEstadoCitaForm(forms.Form):
    """
    Formulario simple para cambiar el estado de una cita.
    """
    estado = forms.ChoiceField(
        choices=Cita.EstadoCita.choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label='Nuevo Estado'
    )

    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'rows': 3,
            'placeholder': 'Motivo del cambio (opcional)...'
        }),
        label='Motivo'
    )
