from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

from apps.usuarios.models import Usuario


class CategoriaRepuesto(models.Model):
    """
    Modelo para categorías de repuestos.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre'
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código único de la categoría'
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        verbose_name = 'Categoría de Repuesto'
        verbose_name_plural = 'Categorías de Repuestos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Repuesto(models.Model):
    """
    Modelo para gestionar repuestos e inventario.
    """
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único del repuesto'
    )

    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    categoria = models.ForeignKey(
        CategoriaRepuesto,
        on_delete=models.PROTECT,
        related_name='repuestos',
        verbose_name='Categoría'
    )

    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Marca'
    )

    ubicacion_almacen = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Ubicación en Almacén',
        help_text='Ejemplo: Estante A3, Pasillo 2, etc.'
    )

    # Stock
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Stock Actual'
    )

    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Stock Mínimo',
        help_text='Nivel mínimo para generar alerta'
    )

    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Stock Máximo'
    )

    # Precios
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio de Compra (€)'
    )

    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio de Venta (€)'
    )

    iva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('21.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='IVA (%)',
        help_text='Porcentaje de IVA aplicable'
    )

    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    # Imagen
    foto = models.ImageField(
        upload_to='inventario/repuestos/',
        null=True,
        blank=True,
        verbose_name='Foto'
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

    class Meta:
        verbose_name = 'Repuesto'
        verbose_name_plural = 'Repuestos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria', 'nombre']),
            models.Index(fields=['stock_actual']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar que precio de venta sea mayor que precio de compra
        if self.precio_venta and self.precio_compra:
            if self.precio_venta <= self.precio_compra:
                raise ValidationError({
                    'precio_venta': 'El precio de venta debe ser mayor que el precio de compra.'
                })

        # Validar que stock máximo sea mayor que stock mínimo
        if self.stock_maximo and self.stock_minimo:
            if self.stock_maximo <= self.stock_minimo:
                raise ValidationError({
                    'stock_maximo': 'El stock máximo debe ser mayor que el stock mínimo.'
                })

    # ==================== PROPERTIES ====================

    @property
    def esta_bajo_stock(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo

    @property
    def esta_sin_stock(self):
        """Verifica si no hay stock"""
        return self.stock_actual <= 0

    @property
    def porcentaje_stock(self):
        """Calcula el porcentaje de stock actual vs máximo"""
        if self.stock_maximo and self.stock_maximo > 0:
            return (self.stock_actual / self.stock_maximo) * 100
        return 0

    @property
    def margen_beneficio(self):
        """Calcula el margen de beneficio en porcentaje"""
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0

    @property
    def precio_venta_con_iva(self):
        """Calcula el precio de venta con IVA incluido"""
        return self.precio_venta * (1 + self.iva / 100)

    @property
    def valor_stock(self):
        """Calcula el valor total del stock actual a precio de compra"""
        return self.stock_actual * self.precio_compra

    def get_nivel_stock_class(self):
        """Devuelve la clase CSS según el nivel de stock"""
        if self.esta_sin_stock:
            return 'bg-red-100 text-red-800'
        elif self.esta_bajo_stock:
            return 'bg-yellow-100 text-yellow-800'
        else:
            return 'bg-green-100 text-green-800'

    # ==================== MÉTODOS ====================

    def ajustar_stock(self, cantidad, tipo_movimiento, usuario, orden_trabajo=None, notas=''):
        """
        Ajusta el stock del repuesto y crea un movimiento.
        Cantidad positiva = entrada, negativa = salida
        """
        self.stock_actual += Decimal(str(cantidad))
        if self.stock_actual < 0:
            raise ValidationError('El stock no puede ser negativo.')
        self.save()

        # Crear movimiento
        MovimientoInventario.objects.create(
            repuesto=self,
            tipo=tipo_movimiento,
            cantidad=abs(Decimal(str(cantidad))),
            stock_anterior=self.stock_actual - Decimal(str(cantidad)),
            stock_posterior=self.stock_actual,
            usuario=usuario,
            orden_trabajo=orden_trabajo,
            notas=notas
        )


class MovimientoInventario(models.Model):
    """
    Modelo para registrar movimientos de inventario.
    """

    class TipoMovimiento(models.TextChoices):
        """Tipos de movimiento de inventario"""
        ENTRADA = 'ENTR', 'Entrada'
        SALIDA = 'SALI', 'Salida'
        AJUSTE = 'AJUS', 'Ajuste'
        DEVOLUCION = 'DEVO', 'Devolución'

    repuesto = models.ForeignKey(
        Repuesto,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name='Repuesto'
    )

    tipo = models.CharField(
        max_length=4,
        choices=TipoMovimiento.choices,
        verbose_name='Tipo de Movimiento'
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad'
    )

    stock_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Anterior'
    )

    stock_posterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Posterior'
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Movimiento'
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movimientos_inventario',
        verbose_name='Usuario'
    )

    orden_trabajo = models.ForeignKey(
        'ordenes.OrdenTrabajo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventario',
        verbose_name='Orden de Trabajo'
    )

    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['repuesto', '-fecha']),
            models.Index(fields=['tipo', '-fecha']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.repuesto.codigo} - {self.cantidad}"

    def get_tipo_badge_class(self):
        """Devuelve las clases CSS para el badge del tipo"""
        clases = {
            self.TipoMovimiento.ENTRADA: 'bg-green-100 text-green-800',
            self.TipoMovimiento.SALIDA: 'bg-red-100 text-red-800',
            self.TipoMovimiento.AJUSTE: 'bg-blue-100 text-blue-800',
            self.TipoMovimiento.DEVOLUCION: 'bg-purple-100 text-purple-800',
        }
        return clases.get(self.tipo, 'bg-gray-100 text-gray-800')
