from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.clientes.models import Cliente
from apps.ordenes.models import OrdenTrabajo
from apps.usuarios.models import Usuario


class Factura(models.Model):
    """
    Modelo para gestionar facturas.
    """

    class EstadoFactura(models.TextChoices):
        """Estados de la factura"""
        PENDIENTE = 'PEND', 'Pendiente'
        PAGADA = 'PAGA', 'Pagada'
        PAGADA_PARCIAL = 'PARC', 'Pagada Parcial'
        VENCIDA = 'VENC', 'Vencida'
        CANCELADA = 'CANC', 'Cancelada'

    class MetodoPago(models.TextChoices):
        """Métodos de pago"""
        EFECTIVO = 'EFEC', 'Efectivo'
        TARJETA = 'TARJ', 'Tarjeta'
        TRANSFERENCIA = 'TRAN', 'Transferencia'
        BIZUM = 'BIZU', 'Bizum'
        OTRO = 'OTRO', 'Otro'

    numero_factura = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='Número de Factura'
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='facturas',
        verbose_name='Cliente'
    )

    orden_trabajo = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas',
        verbose_name='Orden de Trabajo'
    )

    fecha_emision = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Emisión'
    )

    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de Vencimiento'
    )

    estado = models.CharField(
        max_length=4,
        choices=EstadoFactura.choices,
        default=EstadoFactura.PENDIENTE,
        verbose_name='Estado'
    )

    # Totales
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )

    iva_monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='IVA'
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Total'
    )

    # Pagos
    monto_pagado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Monto Pagado'
    )

    metodo_pago = models.CharField(
        max_length=4,
        choices=MetodoPago.choices,
        blank=True,
        verbose_name='Método de Pago'
    )

    fecha_pago = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Pago'
    )

    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facturas_creadas',
        verbose_name='Creado por'
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision', '-numero_factura']
        indexes = [
            models.Index(fields=['numero_factura']),
            models.Index(fields=['cliente', '-fecha_emision']),
            models.Index(fields=['estado', '-fecha_emision']),
        ]

    def __str__(self):
        return f"{self.numero_factura} - {self.cliente.get_nombre_completo()}"

    def save(self, *args, **kwargs):
        """Generar número de factura automáticamente"""
        if not self.numero_factura:
            hoy = timezone.now()
            prefijo = f"F-{hoy.strftime('%Y%m%d')}"

            # Buscar el último número del día
            ultima_factura = Factura.objects.filter(
                numero_factura__startswith=prefijo
            ).order_by('numero_factura').last()

            if ultima_factura:
                ultimo_num = int(ultima_factura.numero_factura.split('-')[-1])
                nuevo_num = ultimo_num + 1
            else:
                nuevo_num = 1

            self.numero_factura = f"{prefijo}-{nuevo_num:04d}"

        # Establecer fecha de vencimiento si no está definida (30 días por defecto)
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.fecha_emision + timedelta(days=30)

        super().save(*args, **kwargs)

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        if self.fecha_vencimiento and self.fecha_emision:
            if self.fecha_vencimiento < self.fecha_emision:
                raise ValidationError({
                    'fecha_vencimiento': 'La fecha de vencimiento no puede ser anterior a la fecha de emisión.'
                })

    def calcular_totales(self):
        """Calcula los totales de la factura"""
        lineas = self.lineas.all()

        self.subtotal = sum(linea.subtotal for linea in lineas)
        self.iva_monto = sum(linea.iva_monto for linea in lineas)
        self.total = self.subtotal + self.iva_monto

        # Actualizar estado según pagos
        self.actualizar_estado_pago()

        self.save()

    def actualizar_estado_pago(self):
        """Actualiza el estado según el monto pagado"""
        if self.monto_pagado >= self.total:
            self.estado = self.EstadoFactura.PAGADA
        elif self.monto_pagado > 0:
            self.estado = self.EstadoFactura.PAGADA_PARCIAL
        elif self.fecha_vencimiento < timezone.now().date() and self.estado == self.EstadoFactura.PENDIENTE:
            self.estado = self.EstadoFactura.VENCIDA

    def registrar_pago(self, monto, metodo_pago, fecha_pago=None):
        """Registra un pago en la factura"""
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a cero.')

        if self.monto_pagado + monto > self.total:
            raise ValidationError(
                f'El pago excede el total de la factura. '
                f'Pendiente: €{self.saldo_pendiente}'
            )

        self.monto_pagado += monto
        self.metodo_pago = metodo_pago
        self.fecha_pago = fecha_pago or timezone.now().date()

        self.actualizar_estado_pago()
        self.save()

    # ==================== PROPERTIES ====================

    @property
    def esta_pagada(self):
        """Verifica si la factura está completamente pagada"""
        return self.estado == self.EstadoFactura.PAGADA

    @property
    def esta_vencida(self):
        """Verifica si la factura está vencida"""
        return (
            self.fecha_vencimiento < timezone.now().date() and
            not self.esta_pagada
        )

    @property
    def saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        return self.total - self.monto_pagado

    @property
    def porcentaje_pagado(self):
        """Calcula el porcentaje pagado"""
        if self.total > 0:
            return (self.monto_pagado / self.total) * 100
        return 0

    @property
    def dias_para_vencimiento(self):
        """Calcula los días restantes para el vencimiento"""
        if self.esta_pagada:
            return 0
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days

    def get_estado_badge_class(self):
        """Devuelve las clases CSS para el badge del estado"""
        clases = {
            self.EstadoFactura.PENDIENTE: 'bg-yellow-100 text-yellow-800',
            self.EstadoFactura.PAGADA: 'bg-green-100 text-green-800',
            self.EstadoFactura.PAGADA_PARCIAL: 'bg-blue-100 text-blue-800',
            self.EstadoFactura.VENCIDA: 'bg-red-100 text-red-800',
            self.EstadoFactura.CANCELADA: 'bg-gray-100 text-gray-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')


class LineaFactura(models.Model):
    """
    Modelo para las líneas de una factura.
    """
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='lineas',
        verbose_name='Factura'
    )

    descripcion = models.CharField(
        max_length=500,
        verbose_name='Descripción'
    )

    cantidad = models.DecimalField(
        max_digits=10,
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
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Descuento (%)'
    )

    iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('21.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='IVA (%)'
    )

    class Meta:
        verbose_name = 'Línea de Factura'
        verbose_name_plural = 'Líneas de Factura'
        ordering = ['id']

    def __str__(self):
        return f"{self.factura.numero_factura} - {self.descripcion}"

    @property
    def subtotal(self):
        """Calcula el subtotal de la línea sin IVA"""
        subtotal_base = self.cantidad * self.precio_unitario
        descuento_monto = subtotal_base * (self.descuento / 100)
        return subtotal_base - descuento_monto

    @property
    def iva_monto(self):
        """Calcula el monto del IVA"""
        return self.subtotal * (self.iva / 100)

    @property
    def total(self):
        """Calcula el total con IVA"""
        return self.subtotal + self.iva_monto
