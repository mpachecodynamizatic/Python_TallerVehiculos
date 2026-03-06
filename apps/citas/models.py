from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.usuarios.models import Usuario


class Cita(models.Model):
    """
    Modelo para gestionar las citas del taller.
    Una cita representa un agendamiento de servicio para un vehículo específico.
    """

    class TipoServicio(models.TextChoices):
        """Tipos de servicio disponibles"""
        MANTENIMIENTO = 'MANT', 'Mantenimiento General'
        CAMBIO_ACEITE = 'ACEI', 'Cambio de Aceite'
        REVISION = 'REVI', 'Revisión'
        REPARACION = 'REPA', 'Reparación'
        ITV = 'ITV', 'Inspección Técnica (ITV)'
        NEUMATICOS = 'NEUM', 'Neumáticos'
        FRENOS = 'FREN', 'Frenos'
        SUSPENSION = 'SUSP', 'Suspensión'
        ELECTRICIDAD = 'ELEC', 'Sistema Eléctrico'
        MOTOR = 'MOTO', 'Motor'
        DIAGNOSTICO = 'DIAG', 'Diagnóstico'
        OTRO = 'OTRO', 'Otro'

    class EstadoCita(models.TextChoices):
        """Estados posibles de una cita"""
        PENDIENTE = 'PEND', 'Pendiente'
        CONFIRMADA = 'CONF', 'Confirmada'
        EN_PROCESO = 'PROC', 'En Proceso'
        COMPLETADA = 'COMP', 'Completada'
        CANCELADA = 'CANC', 'Cancelada'
        NO_ASISTIO = 'NOASIS', 'No Asistió'

    # Relaciones
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Cliente',
        help_text='Cliente que solicita el servicio'
    )

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name='Vehículo',
        help_text='Vehículo a atender'
    )

    mecanico_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_asignadas',
        limit_choices_to={'rol': Usuario.Rol.MECANICO, 'activo': True},
        verbose_name='Mecánico Asignado',
        help_text='Mecánico responsable del servicio'
    )

    # Información de la cita
    fecha_hora = models.DateTimeField(
        verbose_name='Fecha y Hora',
        help_text='Fecha y hora programada para la cita'
    )

    duracion_estimada = models.PositiveIntegerField(
        verbose_name='Duración Estimada (minutos)',
        default=60,
        help_text='Duración estimada del servicio en minutos'
    )

    tipo_servicio = models.CharField(
        max_length=4,
        choices=TipoServicio.choices,
        verbose_name='Tipo de Servicio'
    )

    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción del servicio solicitado'
    )

    # Estado y seguimiento
    estado = models.CharField(
        max_length=6,
        choices=EstadoCita.choices,
        default=EstadoCita.PENDIENTE,
        verbose_name='Estado'
    )

    notas = models.TextField(
        blank=True,
        verbose_name='Notas Internas',
        help_text='Notas adicionales para el taller'
    )

    recordatorio_enviado = models.BooleanField(
        default=False,
        verbose_name='Recordatorio Enviado',
        help_text='Indica si se envió recordatorio al cliente'
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )

    usuario_creacion = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='citas_creadas',
        verbose_name='Creado Por'
    )

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora', 'estado']),
            models.Index(fields=['mecanico_asignado', 'fecha_hora']),
            models.Index(fields=['cliente']),
            models.Index(fields=['vehiculo']),
        ]

    def __str__(self):
        return f"Cita {self.pk} - {self.cliente.get_nombre_completo()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar que la fecha/hora sea futura (solo para citas nuevas o modificadas)
        if self.fecha_hora and self.fecha_hora < timezone.now():
            if not self.pk or self.estado == self.EstadoCita.PENDIENTE:
                raise ValidationError({
                    'fecha_hora': 'La fecha y hora debe ser futura.'
                })

        # Validar que el vehículo pertenece al cliente
        if self.vehiculo and self.cliente:
            if self.vehiculo.cliente != self.cliente:
                raise ValidationError({
                    'vehiculo': 'El vehículo seleccionado no pertenece al cliente.'
                })

        # Validar conflictos de horario con otras citas del mismo mecánico
        if self.mecanico_asignado and self.fecha_hora:
            self._validar_conflicto_horarios()

    def _validar_conflicto_horarios(self):
        """Valida que no haya conflictos de horario con otras citas del mecánico"""
        hora_inicio = self.fecha_hora
        hora_fin = hora_inicio + timedelta(minutes=self.duracion_estimada)

        # Buscar citas del mismo mecánico que se superpongan
        citas_conflictivas = Cita.objects.filter(
            mecanico_asignado=self.mecanico_asignado,
            fecha_hora__lt=hora_fin,
            fecha_hora__gte=hora_inicio - timedelta(minutes=120)  # Ventana de 2 horas
        ).exclude(
            estado__in=[self.EstadoCita.CANCELADA, self.EstadoCita.COMPLETADA]
        )

        # Excluir la cita actual si ya existe
        if self.pk:
            citas_conflictivas = citas_conflictivas.exclude(pk=self.pk)

        for cita in citas_conflictivas:
            cita_fin = cita.fecha_hora + timedelta(minutes=cita.duracion_estimada)
            # Verificar si hay superposición
            if hora_inicio < cita_fin and hora_fin > cita.fecha_hora:
                raise ValidationError({
                    'mecanico_asignado': f'El mecánico ya tiene una cita programada '
                                       f'el {cita.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}.'
                })

    def save(self, *args, **kwargs):
        """Override del save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)

    # ==================== PROPERTIES ====================

    @property
    def hora_fin(self):
        """Calcula la hora de finalización estimada"""
        return self.fecha_hora + timedelta(minutes=self.duracion_estimada)

    @property
    def duracion_formato(self):
        """Devuelve la duración en formato legible"""
        horas = self.duracion_estimada // 60
        minutos = self.duracion_estimada % 60
        if horas > 0:
            return f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"
        return f"{minutos}min"

    @property
    def esta_pendiente(self):
        """Verifica si la cita está pendiente"""
        return self.estado == self.EstadoCita.PENDIENTE

    @property
    def esta_confirmada(self):
        """Verifica si la cita está confirmada"""
        return self.estado == self.EstadoCita.CONFIRMADA

    @property
    def esta_en_proceso(self):
        """Verifica si la cita está en proceso"""
        return self.estado == self.EstadoCita.EN_PROCESO

    @property
    def esta_completada(self):
        """Verifica si la cita está completada"""
        return self.estado == self.EstadoCita.COMPLETADA

    @property
    def esta_cancelada(self):
        """Verifica si la cita está cancelada"""
        return self.estado == self.EstadoCita.CANCELADA

    @property
    def puede_cancelar(self):
        """Verifica si la cita puede ser cancelada"""
        return self.estado in [self.EstadoCita.PENDIENTE, self.EstadoCita.CONFIRMADA]

    @property
    def puede_confirmar(self):
        """Verifica si la cita puede ser confirmada"""
        return self.estado == self.EstadoCita.PENDIENTE

    @property
    def puede_iniciar(self):
        """Verifica si la cita puede iniciarse"""
        return self.estado == self.EstadoCita.CONFIRMADA and self.fecha_hora <= timezone.now()

    @property
    def esta_atrasada(self):
        """Verifica si la cita está atrasada"""
        return (
            self.estado in [self.EstadoCita.PENDIENTE, self.EstadoCita.CONFIRMADA] and
            self.fecha_hora < timezone.now()
        )

    @property
    def es_hoy(self):
        """Verifica si la cita es hoy"""
        return self.fecha_hora.date() == timezone.now().date()

    @property
    def dias_hasta_cita(self):
        """Calcula días hasta la cita"""
        if self.fecha_hora > timezone.now():
            delta = self.fecha_hora - timezone.now()
            return delta.days
        return 0

    def get_estado_color(self):
        """Devuelve el color CSS según el estado"""
        colores = {
            self.EstadoCita.PENDIENTE: 'yellow',
            self.EstadoCita.CONFIRMADA: 'blue',
            self.EstadoCita.EN_PROCESO: 'purple',
            self.EstadoCita.COMPLETADA: 'green',
            self.EstadoCita.CANCELADA: 'red',
            self.EstadoCita.NO_ASISTIO: 'gray',
        }
        return colores.get(self.estado, 'gray')

    def get_estado_badge_class(self):
        """Devuelve las clases CSS para el badge del estado"""
        clases = {
            self.EstadoCita.PENDIENTE: 'bg-yellow-100 text-yellow-800',
            self.EstadoCita.CONFIRMADA: 'bg-blue-100 text-blue-800',
            self.EstadoCita.EN_PROCESO: 'bg-purple-100 text-purple-800',
            self.EstadoCita.COMPLETADA: 'bg-green-100 text-green-800',
            self.EstadoCita.CANCELADA: 'bg-red-100 text-red-800',
            self.EstadoCita.NO_ASISTIO: 'bg-gray-100 text-gray-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')

    # ==================== MÉTODOS ====================

    def confirmar(self):
        """Confirma la cita"""
        if self.puede_confirmar:
            self.estado = self.EstadoCita.CONFIRMADA
            self.save()
            return True
        return False

    def iniciar(self):
        """Inicia el servicio de la cita"""
        if self.puede_iniciar:
            self.estado = self.EstadoCita.EN_PROCESO
            self.save()
            return True
        return False

    def completar(self):
        """Completa la cita"""
        if self.esta_en_proceso:
            self.estado = self.EstadoCita.COMPLETADA
            self.save()
            return True
        return False

    def cancelar(self, motivo=''):
        """Cancela la cita"""
        if self.puede_cancelar:
            self.estado = self.EstadoCita.CANCELADA
            if motivo:
                self.notas = f"{self.notas}\n\nMotivo de cancelación: {motivo}".strip()
            self.save()
            return True
        return False

    def marcar_no_asistio(self):
        """Marca la cita como no asistida"""
        if self.estado in [self.EstadoCita.PENDIENTE, self.EstadoCita.CONFIRMADA]:
            self.estado = self.EstadoCita.NO_ASISTIO
            self.save()
            return True
        return False
