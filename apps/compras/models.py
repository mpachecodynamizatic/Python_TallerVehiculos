from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from apps.usuarios.models import Usuario
from apps.inventario.models import Repuesto


class Proveedor(models.Model):
    """
    Modelo para gestionar proveedores de repuestos.
    """
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre o razón social del proveedor'
    )

    cif = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='CIF/NIF',
        help_text='Código de identificación fiscal'
    )

    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name='Email'
    )

    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono'
    )

    direccion = models.CharField(
        max_length=200,
        verbose_name='Dirección'
    )

    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )

    codigo_postal = models.CharField(
        max_length=10,
        verbose_name='Código Postal'
    )

    pais = models.CharField(
        max_length=100,
        default='España',
        verbose_name='País'
    )

    contacto_principal = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Contacto Principal',
        help_text='Nombre de la persona de contacto'
    )

    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
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
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['cif']),
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return self.nombre

    @property
    def total_ordenes(self):
        """Retorna el total de órdenes de compra"""
        return self.ordenes_compra.count()

    @property
    def total_comprado(self):
        """Retorna el monto total comprado a este proveedor"""
        return self.ordenes_compra.filter(
            estado__in=['RECV', 'RECP']
        ).aggregate(models.Sum('total'))['total__sum'] or Decimal('0.00')


class OrdenCompra(models.Model):
    """
    Modelo para gestionar órdenes de compra a proveedores.
    """

    class EstadoOrden(models.TextChoices):
        """Estados de la orden de compra"""
        BORRADOR = 'BORR', 'Borrador'
        ENVIADA = 'ENVI', 'Enviada'
        RECIBIDA_PARCIAL = 'RECP', 'Recibida Parcial'
        RECIBIDA_COMPLETA = 'RECV', 'Recibida Completa'
        CANCELADA = 'CANC', 'Cancelada'

    numero_orden = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='Número de Orden'
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='ordenes_compra',
        verbose_name='Proveedor'
    )

    fecha_orden = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de Orden'
    )

    fecha_entrega_esperada = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Entrega Esperada'
    )

    estado = models.CharField(
        max_length=4,
        choices=EstadoOrden.choices,
        default=EstadoOrden.BORRADOR,
        verbose_name='Estado'
    )

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

    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes_compra_creadas',
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
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-fecha_orden', '-numero_orden']
        indexes = [
            models.Index(fields=['numero_orden']),
            models.Index(fields=['proveedor', '-fecha_orden']),
            models.Index(fields=['estado', '-fecha_orden']),
        ]

    def __str__(self):
        return f"{self.numero_orden} - {self.proveedor.nombre}"

    def save(self, *args, **kwargs):
        """Generar número de orden automáticamente"""
        if not self.numero_orden:
            hoy = timezone.now()
            prefijo = f"OC-{hoy.strftime('%Y%m%d')}"

            # Buscar el último número del día
            ultima_orden = OrdenCompra.objects.filter(
                numero_orden__startswith=prefijo
            ).order_by('numero_orden').last()

            if ultima_orden:
                ultimo_num = int(ultima_orden.numero_orden.split('-')[-1])
                nuevo_num = ultimo_num + 1
            else:
                nuevo_num = 1

            self.numero_orden = f"{prefijo}-{nuevo_num:04d}"

        super().save(*args, **kwargs)

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        if self.fecha_entrega_esperada and self.fecha_orden:
            if self.fecha_entrega_esperada < self.fecha_orden:
                raise ValidationError({
                    'fecha_entrega_esperada': 'La fecha de entrega no puede ser anterior a la fecha de orden.'
                })

    def calcular_totales(self):
        """Calcula los totales de la orden"""
        lineas = self.lineas.all()

        self.subtotal = sum(linea.subtotal for linea in lineas)
        self.iva_monto = sum(linea.iva_monto for linea in lineas)
        self.total = self.subtotal + self.iva_monto

        self.save()

    def actualizar_estado(self):
        """Actualiza el estado según las líneas recibidas"""
        lineas = self.lineas.all()

        if not lineas.exists():
            return

        total_lineas = lineas.count()
        lineas_completas = lineas.filter(
            cantidad_recibida__gte=models.F('cantidad_solicitada')
        ).count()
        lineas_parciales = lineas.filter(
            cantidad_recibida__gt=0,
            cantidad_recibida__lt=models.F('cantidad_solicitada')
        ).count()

        if lineas_completas == total_lineas:
            self.estado = self.EstadoOrden.RECIBIDA_COMPLETA
        elif lineas_parciales > 0 or lineas_completas > 0:
            self.estado = self.EstadoOrden.RECIBIDA_PARCIAL

        self.save()

    # ==================== PROPERTIES ====================

    @property
    def puede_editar(self):
        """Verifica si la orden puede ser editada"""
        return self.estado in [self.EstadoOrden.BORRADOR, self.EstadoOrden.ENVIADA]

    @property
    def esta_completa(self):
        """Verifica si la orden está completamente recibida"""
        return self.estado == self.EstadoOrden.RECIBIDA_COMPLETA

    @property
    def porcentaje_recibido(self):
        """Calcula el porcentaje de mercancía recibida"""
        lineas = self.lineas.all()
        if not lineas.exists():
            return 0

        total_solicitado = sum(linea.cantidad_solicitada for linea in lineas)
        total_recibido = sum(linea.cantidad_recibida for linea in lineas)

        if total_solicitado > 0:
            return (total_recibido / total_solicitado) * 100
        return 0

    def get_estado_badge_class(self):
        """Devuelve las clases CSS para el badge del estado"""
        clases = {
            self.EstadoOrden.BORRADOR: 'bg-gray-100 text-gray-800',
            self.EstadoOrden.ENVIADA: 'bg-blue-100 text-blue-800',
            self.EstadoOrden.RECIBIDA_PARCIAL: 'bg-yellow-100 text-yellow-800',
            self.EstadoOrden.RECIBIDA_COMPLETA: 'bg-green-100 text-green-800',
            self.EstadoOrden.CANCELADA: 'bg-red-100 text-red-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')


class LineaCompra(models.Model):
    """
    Modelo para las líneas de una orden de compra.
    """
    orden_compra = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name='lineas',
        verbose_name='Orden de Compra'
    )

    repuesto = models.ForeignKey(
        Repuesto,
        on_delete=models.PROTECT,
        related_name='lineas_compra',
        verbose_name='Repuesto'
    )

    cantidad_solicitada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad Solicitada'
    )

    cantidad_recibida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Cantidad Recibida'
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

    class Meta:
        verbose_name = 'Línea de Compra'
        verbose_name_plural = 'Líneas de Compra'
        ordering = ['id']

    def __str__(self):
        return f"{self.orden_compra.numero_orden} - {self.repuesto.nombre}"

    @property
    def subtotal(self):
        """Calcula el subtotal de la línea sin IVA"""
        subtotal_base = self.cantidad_solicitada * self.precio_unitario
        descuento_monto = subtotal_base * (self.descuento / 100)
        return subtotal_base - descuento_monto

    @property
    def iva_monto(self):
        """Calcula el monto del IVA"""
        return self.subtotal * (self.repuesto.iva / 100)

    @property
    def total(self):
        """Calcula el total con IVA"""
        return self.subtotal + self.iva_monto

    @property
    def cantidad_pendiente(self):
        """Calcula la cantidad pendiente de recibir"""
        return self.cantidad_solicitada - self.cantidad_recibida

    @property
    def esta_completa(self):
        """Verifica si la línea está completamente recibida"""
        return self.cantidad_recibida >= self.cantidad_solicitada

    def recibir_mercancia(self, cantidad, usuario):
        """
        Recibe mercancía y actualiza el stock del repuesto.
        """
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')

        if self.cantidad_recibida + cantidad > self.cantidad_solicitada:
            raise ValidationError(
                f'No se puede recibir más de lo solicitado. '
                f'Pendiente: {self.cantidad_pendiente}'
            )

        # Actualizar cantidad recibida
        self.cantidad_recibida += cantidad
        self.save()

        # Actualizar stock del repuesto
        from apps.inventario.models import MovimientoInventario
        self.repuesto.ajustar_stock(
            cantidad=cantidad,
            tipo_movimiento=MovimientoInventario.TipoMovimiento.ENTRADA,
            usuario=usuario,
            notas=f'Recepción de orden de compra {self.orden_compra.numero_orden}'
        )

        # Actualizar estado de la orden
        self.orden_compra.actualizar_estado()
