from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.usuarios.models import Usuario
from apps.citas.models import Cita


class OrdenTrabajo(models.Model):
    """
    Modelo para gestionar las órdenes de trabajo del taller.
    Una orden de trabajo registra todos los servicios realizados en un vehículo.
    """

    class EstadoOrden(models.TextChoices):
        """Estados posibles de una orden de trabajo"""
        ABIERTA = 'ABIE', 'Abierta'
        EN_PROCESO = 'PROC', 'En Proceso'
        PAUSADA = 'PAUS', 'Pausada'
        COMPLETADA = 'COMP', 'Completada'
        CANCELADA = 'CANC', 'Cancelada'

    class Prioridad(models.TextChoices):
        """Niveles de prioridad"""
        BAJA = 'BAJA', 'Baja'
        NORMAL = 'NORM', 'Normal'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGE', 'Urgente'

    # Número de orden (autoincremental)
    numero_orden = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Número de Orden',
        help_text='Número único de la orden de trabajo'
    )

    # Relaciones
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes',
        verbose_name='Cita Asociada',
        help_text='Cita que originó esta orden (opcional)'
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ordenes',
        verbose_name='Cliente'
    )

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name='ordenes',
        verbose_name='Vehículo'
    )

    mecanico_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_asignadas',
        limit_choices_to={'rol': Usuario.Rol.MECANICO, 'activo': True},
        verbose_name='Mecánico Asignado'
    )

    # Información de la orden
    fecha_apertura = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Apertura'
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Cierre'
    )

    estado = models.CharField(
        max_length=4,
        choices=EstadoOrden.choices,
        default=EstadoOrden.ABIERTA,
        verbose_name='Estado'
    )

    prioridad = models.CharField(
        max_length=4,
        choices=Prioridad.choices,
        default=Prioridad.NORMAL,
        verbose_name='Prioridad'
    )

    # Información del vehículo
    kilometros_ingreso = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
        verbose_name='Kilómetros al Ingreso',
        help_text='Kilometraje del vehículo al ingresar al taller'
    )

    # Descripciones y diagnóstico
    descripcion_problema = models.TextField(
        verbose_name='Descripción del Problema',
        help_text='Descripción del problema reportado por el cliente'
    )

    diagnostico = models.TextField(
        blank=True,
        verbose_name='Diagnóstico',
        help_text='Diagnóstico técnico realizado por el mecánico'
    )

    trabajos_realizados = models.TextField(
        blank=True,
        verbose_name='Trabajos Realizados',
        help_text='Descripción detallada de los trabajos realizados'
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
        help_text='Observaciones adicionales sobre la orden'
    )

    # Tiempo
    tiempo_estimado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Tiempo Estimado (horas)',
        help_text='Tiempo estimado de trabajo en horas'
    )

    tiempo_real = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Tiempo Real (horas)',
        help_text='Tiempo real de trabajo en horas'
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
        related_name='ordenes_creadas',
        verbose_name='Creado Por'
    )

    class Meta:
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Órdenes de Trabajo'
        ordering = ['-fecha_apertura']
        indexes = [
            models.Index(fields=['numero_orden']),
            models.Index(fields=['estado', 'fecha_apertura']),
            models.Index(fields=['mecanico_asignado', 'estado']),
            models.Index(fields=['cliente']),
            models.Index(fields=['vehiculo']),
        ]

    def __str__(self):
        return f"Orden #{self.numero_orden} - {self.cliente.get_nombre_completo()}"

    def save(self, *args, **kwargs):
        """Override del save para generar número de orden automático"""
        if not self.numero_orden:
            # Generar número de orden en formato: OT-YYYYMMDD-XXXX
            hoy = timezone.now()
            prefijo = f"OT-{hoy.strftime('%Y%m%d')}"

            # Obtener el último número del día
            ultima_orden = OrdenTrabajo.objects.filter(
                numero_orden__startswith=prefijo
            ).order_by('-numero_orden').first()

            if ultima_orden:
                # Extraer el número secuencial y sumar 1
                ultimo_num = int(ultima_orden.numero_orden.split('-')[-1])
                nuevo_num = ultimo_num + 1
            else:
                nuevo_num = 1

            self.numero_orden = f"{prefijo}-{nuevo_num:04d}"

        super().save(*args, **kwargs)

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar que el vehículo pertenece al cliente
        if self.vehiculo and self.cliente:
            if self.vehiculo.cliente != self.cliente:
                raise ValidationError({
                    'vehiculo': 'El vehículo seleccionado no pertenece al cliente.'
                })

        # Validar que la fecha de cierre sea posterior a la de apertura
        if self.fecha_cierre and self.fecha_apertura:
            if self.fecha_cierre < self.fecha_apertura:
                raise ValidationError({
                    'fecha_cierre': 'La fecha de cierre no puede ser anterior a la fecha de apertura.'
                })

    # ==================== PROPERTIES ====================

    @property
    def esta_abierta(self):
        """Verifica si la orden está abierta"""
        return self.estado == self.EstadoOrden.ABIERTA

    @property
    def esta_en_proceso(self):
        """Verifica si la orden está en proceso"""
        return self.estado == self.EstadoOrden.EN_PROCESO

    @property
    def esta_pausada(self):
        """Verifica si la orden está pausada"""
        return self.estado == self.EstadoOrden.PAUSADA

    @property
    def esta_completada(self):
        """Verifica si la orden está completada"""
        return self.estado == self.EstadoOrden.COMPLETADA

    @property
    def esta_cancelada(self):
        """Verifica si la orden está cancelada"""
        return self.estado == self.EstadoOrden.CANCELADA

    @property
    def puede_editar(self):
        """Verifica si la orden puede ser editada"""
        return self.estado not in [self.EstadoOrden.COMPLETADA, self.EstadoOrden.CANCELADA]

    @property
    def puede_completar(self):
        """Verifica si la orden puede ser completada"""
        return self.estado in [self.EstadoOrden.EN_PROCESO, self.EstadoOrden.PAUSADA]

    @property
    def dias_abierta(self):
        """Calcula los días que lleva abierta la orden"""
        if self.fecha_cierre:
            delta = self.fecha_cierre - self.fecha_apertura
        else:
            delta = timezone.now() - self.fecha_apertura
        return delta.days

    @property
    def total_mano_obra(self):
        """Calcula el total de mano de obra"""
        return sum(linea.total for linea in self.lineas_trabajo.all())

    @property
    def total_repuestos(self):
        """Calcula el total de repuestos"""
        return sum(linea.total for linea in self.lineas_repuesto.all())

    @property
    def subtotal(self):
        """Calcula el subtotal (sin IVA)"""
        return self.total_mano_obra + self.total_repuestos

    @property
    def iva_monto(self):
        """Calcula el monto del IVA (21%)"""
        return self.subtotal * Decimal('0.21')

    @property
    def total(self):
        """Calcula el total final (con IVA)"""
        return self.subtotal + self.iva_monto

    def get_estado_color(self):
        """Devuelve el color CSS según el estado"""
        colores = {
            self.EstadoOrden.ABIERTA: 'blue',
            self.EstadoOrden.EN_PROCESO: 'purple',
            self.EstadoOrden.PAUSADA: 'yellow',
            self.EstadoOrden.COMPLETADA: 'green',
            self.EstadoOrden.CANCELADA: 'red',
        }
        return colores.get(self.estado, 'gray')

    def get_estado_badge_class(self):
        """Devuelve las clases CSS para el badge del estado"""
        clases = {
            self.EstadoOrden.ABIERTA: 'bg-blue-100 text-blue-800',
            self.EstadoOrden.EN_PROCESO: 'bg-purple-100 text-purple-800',
            self.EstadoOrden.PAUSADA: 'bg-yellow-100 text-yellow-800',
            self.EstadoOrden.COMPLETADA: 'bg-green-100 text-green-800',
            self.EstadoOrden.CANCELADA: 'bg-red-100 text-red-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')

    def get_prioridad_badge_class(self):
        """Devuelve las clases CSS para el badge de prioridad"""
        clases = {
            self.Prioridad.BAJA: 'bg-gray-100 text-gray-800',
            self.Prioridad.NORMAL: 'bg-blue-100 text-blue-800',
            self.Prioridad.ALTA: 'bg-orange-100 text-orange-800',
            self.Prioridad.URGENTE: 'bg-red-100 text-red-800',
        }
        return clases.get(self.prioridad, 'bg-gray-100 text-gray-800')

    # ==================== MÉTODOS ====================

    def iniciar_trabajo(self):
        """Inicia el trabajo en la orden"""
        if self.estado == self.EstadoOrden.ABIERTA:
            self.estado = self.EstadoOrden.EN_PROCESO
            self.save()
            return True
        return False

    def pausar(self):
        """Pausa la orden"""
        if self.estado == self.EstadoOrden.EN_PROCESO:
            self.estado = self.EstadoOrden.PAUSADA
            self.save()
            return True
        return False

    def reanudar(self):
        """Reanuda una orden pausada"""
        if self.estado == self.EstadoOrden.PAUSADA:
            self.estado = self.EstadoOrden.EN_PROCESO
            self.save()
            return True
        return False

    def completar(self):
        """Completa la orden"""
        if self.puede_completar:
            self.estado = self.EstadoOrden.COMPLETADA
            self.fecha_cierre = timezone.now()
            self.save()
            return True
        return False

    def cancelar(self, motivo=''):
        """Cancela la orden"""
        if self.puede_editar:
            self.estado = self.EstadoOrden.CANCELADA
            self.fecha_cierre = timezone.now()
            if motivo:
                self.observaciones = f"{self.observaciones}\n\nMotivo de cancelación: {motivo}".strip()
            self.save()
            return True
        return False


class LineaTrabajo(models.Model):
    """
    Modelo para las líneas de mano de obra en una orden de trabajo.
    """
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='lineas_trabajo',
        verbose_name='Orden de Trabajo'
    )

    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción del Trabajo'
    )

    horas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Horas'
    )

    precio_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio por Hora (€)'
    )

    class Meta:
        verbose_name = 'Línea de Trabajo'
        verbose_name_plural = 'Líneas de Trabajo'
        ordering = ['id']

    def __str__(self):
        return f"{self.descripcion} - {self.horas}h x €{self.precio_hora}"

    @property
    def total(self):
        """Calcula el total de la línea"""
        return self.horas * self.precio_hora


class LineaRepuesto(models.Model):
    """
    Modelo para las líneas de repuestos en una orden de trabajo.
    """
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='lineas_repuesto',
        verbose_name='Orden de Trabajo'
    )

    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción del Repuesto'
    )

    cantidad = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad'
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio Unitario (€)'
    )

    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name='Descuento (%)',
        help_text='Descuento en porcentaje (0-100)'
    )

    class Meta:
        verbose_name = 'Línea de Repuesto'
        verbose_name_plural = 'Líneas de Repuesto'
        ordering = ['id']

    def __str__(self):
        return f"{self.descripcion} - {self.cantidad} x €{self.precio_unitario}"

    @property
    def subtotal(self):
        """Calcula el subtotal sin descuento"""
        return self.cantidad * self.precio_unitario

    @property
    def monto_descuento(self):
        """Calcula el monto del descuento"""
        return self.subtotal * (self.descuento / Decimal('100'))

    @property
    def total(self):
        """Calcula el total con descuento aplicado"""
        return self.subtotal - self.monto_descuento
