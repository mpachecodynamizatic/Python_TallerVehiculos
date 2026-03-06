from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse


class Cliente(models.Model):
    """
    Modelo para gestionar clientes del taller.
    Un cliente puede tener múltiples vehículos asociados.
    """

    # Validador para DNI/NIF español
    dni_regex = RegexValidator(
        regex=r'^[0-9]{8}[A-Z]$|^[XYZ][0-9]{7}[A-Z]$',
        message='Formato de DNI/NIE inválido. Debe ser 12345678A o X1234567A'
    )

    # Validador para teléfono
    telefono_regex = RegexValidator(
        regex=r'^\+?[0-9]{9,15}$',
        message='Formato de teléfono inválido. Ej: +34600000000 o 600000000'
    )

    # Validador para código postal español
    codigo_postal_regex = RegexValidator(
        regex=r'^[0-9]{5}$',
        message='El código postal debe tener 5 dígitos'
    )

    # Información Personal
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )

    apellidos = models.CharField(
        max_length=150,
        verbose_name='Apellidos'
    )

    dni = models.CharField(
        max_length=10,
        unique=True,
        validators=[dni_regex],
        verbose_name='DNI/NIE',
        help_text='Formato: 12345678A o X1234567A'
    )

    # Información de Contacto
    email = models.EmailField(
        verbose_name='Correo electrónico',
        blank=True
    )

    telefono = models.CharField(
        max_length=15,
        validators=[telefono_regex],
        verbose_name='Teléfono',
        help_text='Formato: +34600000000'
    )

    telefono_alternativo = models.CharField(
        max_length=15,
        blank=True,
        validators=[telefono_regex],
        verbose_name='Teléfono alternativo',
        help_text='Opcional'
    )

    # Dirección
    direccion = models.CharField(
        max_length=255,
        verbose_name='Dirección',
        blank=True
    )

    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad',
        blank=True
    )

    codigo_postal = models.CharField(
        max_length=5,
        blank=True,
        validators=[codigo_postal_regex],
        verbose_name='Código postal'
    )

    # Notas adicionales
    notas = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Información adicional sobre el cliente'
    )

    # Campos de control
    activo = models.BooleanField(
        default=True,
        verbose_name='Cliente activo',
        help_text='Los clientes inactivos no aparecen en búsquedas'
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['apellidos', 'nombre']),
            models.Index(fields=['-fecha_registro']),
        ]
        permissions = [
            ('ver_clientes_inactivos', 'Puede ver clientes inactivos'),
        ]

    def __str__(self):
        return f"{self.apellidos}, {self.nombre} - {self.dni}"

    def get_absolute_url(self):
        return reverse('clientes:detalle', kwargs={'pk': self.pk})

    def get_nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellidos}"

    @property
    def total_vehiculos(self):
        """Retorna el número de vehículos asociados"""
        return self.vehiculos.count()

    @property
    def tiene_vehiculos(self):
        """Retorna True si el cliente tiene vehículos registrados"""
        return self.vehiculos.exists()
