from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import OrdenTrabajo, LineaTrabajo, LineaRepuesto
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.usuarios.models import Usuario
from apps.citas.models import Cita


class OrdenTrabajoForm(forms.ModelForm):
    """
    Formulario para crear y editar órdenes de trabajo.
    """

    class Meta:
        model = OrdenTrabajo
        fields = [
            'cita',
            'cliente',
            'vehiculo',
            'kilometros_ingreso',
            'mecanico_asignado',
            'prioridad',
            'descripcion_problema',
            'diagnostico',
            'trabajos_realizados',
            'observaciones',
            'tiempo_estimado',
            'tiempo_real',
            'estado',
        ]
        widgets = {
            'cita': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'cliente': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'x-model': 'clienteId',
                '@change': 'cargarVehiculos()'
            }),
            'vehiculo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'x-bind:disabled': '!clienteId'
            }),
            'kilometros_ingreso': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '0',
                'max': '999999',
                'placeholder': '0'
            }),
            'mecanico_asignado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'descripcion_problema': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Describa el problema reportado por el cliente...'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Diagnóstico técnico realizado...'
            }),
            'trabajos_realizados': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Descripción detallada de los trabajos realizados...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'tiempo_estimado': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.25',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'tiempo_real': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.25',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario con filtros personalizados"""
        super().__init__(*args, **kwargs)

        # Filtrar citas disponibles (confirmadas o en proceso, sin orden asociada)
        citas_disponibles = Cita.objects.filter(
            estado__in=[Cita.EstadoCita.CONFIRMADA, Cita.EstadoCita.EN_PROCESO]
        ).exclude(
            ordenes__isnull=False
        ).select_related('cliente', 'vehiculo').order_by('-fecha_hora')

        # Si es edición y ya tiene cita, incluirla en las opciones
        if self.instance.pk and self.instance.cita:
            citas_disponibles = Cita.objects.filter(
                pk=self.instance.cita.pk
            ) | citas_disponibles

        self.fields['cita'].queryset = citas_disponibles
        self.fields['cita'].required = False

        # Filtrar solo clientes activos
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('apellidos', 'nombre')

        # Si hay una instancia (edición), filtrar vehículos del cliente
        if self.instance and self.instance.cliente_id:
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(
                cliente=self.instance.cliente,
                activo=True
            ).order_by('marca', 'modelo')
        else:
            # En creación, mostrar todos los vehículos activos
            self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True).order_by('marca', 'modelo')

        # Filtrar solo mecánicos activos
        self.fields['mecanico_asignado'].queryset = Usuario.objects.filter(
            rol=Usuario.Rol.MECANICO,
            activo=True
        ).order_by('first_name', 'last_name')
        self.fields['mecanico_asignado'].required = False

        # Campos opcionales
        self.fields['diagnostico'].required = False
        self.fields['trabajos_realizados'].required = False
        self.fields['observaciones'].required = False
        self.fields['tiempo_estimado'].required = False
        self.fields['tiempo_real'].required = False

        # Labels personalizados
        self.fields['cita'].label = 'Cita Asociada (opcional)'
        self.fields['cliente'].label = 'Cliente'
        self.fields['vehiculo'].label = 'Vehículo'
        self.fields['kilometros_ingreso'].label = 'Kilómetros al Ingreso'
        self.fields['mecanico_asignado'].label = 'Mecánico Asignado'
        self.fields['prioridad'].label = 'Prioridad'
        self.fields['descripcion_problema'].label = 'Descripción del Problema'
        self.fields['diagnostico'].label = 'Diagnóstico Técnico'
        self.fields['trabajos_realizados'].label = 'Trabajos Realizados'
        self.fields['observaciones'].label = 'Observaciones'
        self.fields['tiempo_estimado'].label = 'Tiempo Estimado (horas)'
        self.fields['tiempo_real'].label = 'Tiempo Real (horas)'

        # Si es una orden nueva, ocultar el campo estado
        if not self.instance.pk:
            self.fields.pop('estado', None)
        else:
            self.fields['estado'].label = 'Estado de la Orden'

    def clean_vehiculo(self):
        """Validar que el vehículo pertenece al cliente seleccionado"""
        vehiculo = self.cleaned_data.get('vehiculo')
        cliente = self.cleaned_data.get('cliente')

        if vehiculo and cliente:
            if vehiculo.cliente != cliente:
                raise ValidationError('El vehículo seleccionado no pertenece al cliente.')
            if not vehiculo.activo:
                raise ValidationError('No se pueden crear órdenes para vehículos inactivos.')

        return vehiculo

    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()

        # Si hay cita, validar que cliente y vehículo coincidan
        cita = cleaned_data.get('cita')
        cliente = cleaned_data.get('cliente')
        vehiculo = cleaned_data.get('vehiculo')

        if cita:
            if cliente and cita.cliente != cliente:
                raise ValidationError({
                    'cliente': 'El cliente debe coincidir con el cliente de la cita.'
                })
            if vehiculo and cita.vehiculo != vehiculo:
                raise ValidationError({
                    'vehiculo': 'El vehículo debe coincidir con el vehículo de la cita.'
                })

        return cleaned_data


class LineaTrabajoForm(forms.ModelForm):
    """
    Formulario para agregar líneas de mano de obra a una orden.
    """

    class Meta:
        model = LineaTrabajo
        fields = ['descripcion', 'horas', 'precio_hora']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Descripción del trabajo...'
            }),
            'horas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.25',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'precio_hora': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].label = 'Descripción del Trabajo'
        self.fields['horas'].label = 'Horas'
        self.fields['precio_hora'].label = 'Precio por Hora (€)'

        # Establecer precio por defecto si está vacío
        if not self.instance.pk:
            self.fields['precio_hora'].initial = Decimal('50.00')  # Precio por defecto


class LineaRepuestoForm(forms.ModelForm):
    """
    Formulario para agregar líneas de repuestos a una orden.
    """

    class Meta:
        model = LineaRepuesto
        fields = ['descripcion', 'cantidad', 'precio_unitario', 'descuento']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Descripción del repuesto...'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '1.00'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.00',
                'max': '100.00',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].label = 'Descripción del Repuesto'
        self.fields['cantidad'].label = 'Cantidad'
        self.fields['precio_unitario'].label = 'Precio Unitario (€)'
        self.fields['descuento'].label = 'Descuento (%)'

        # Establecer valores por defecto
        if not self.instance.pk:
            self.fields['cantidad'].initial = Decimal('1.00')
            self.fields['descuento'].initial = Decimal('0.00')
