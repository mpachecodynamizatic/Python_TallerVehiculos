from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from apps.clientes.models import Cliente


class Vehiculo(models.Model):
    """
    Modelo para gestionar vehículos del taller.
    Cada vehículo pertenece a un cliente.
    """

    # Validador para matrícula española (formato actual: 1234ABC o antiguo: M-1234-AB)
    matricula_regex = RegexValidator(
        regex=r'^[0-9]{4}[A-Z]{3}$|^[A-Z]-[0-9]{4}-[A-Z]{2}$|^[A-Z]{1,2}-[0-9]{4,5}$',
        message='Formato de matrícula inválido. Ej: 1234ABC o M-1234-AB'
    )

    # Choices para tipo de combustible
    class TipoCombustible(models.TextChoices):
        GASOLINA = 'GASOLINA', 'Gasolina'
        DIESEL = 'DIESEL', 'Diésel'
        ELECTRICO = 'ELECTRICO', 'Eléctrico'
        HIBRIDO = 'HIBRIDO', 'Híbrido'
        GLP = 'GLP', 'GLP (Gas Licuado del Petróleo)'
        GNC = 'GNC', 'GNC (Gas Natural Comprimido)'
        HIDROGENO = 'HIDROGENO', 'Hidrógeno'

    # Relación con Cliente
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='vehiculos',
        verbose_name='Cliente',
        help_text='Cliente propietario del vehículo'
    )

    # Información del Vehículo
    marca = models.CharField(
        max_length=50,
        verbose_name='Marca',
        help_text='Ej: Toyota, Ford, BMW'
    )

    modelo = models.CharField(
        max_length=100,
        verbose_name='Modelo',
        help_text='Ej: Corolla, Focus, Serie 3'
    )

    anio = models.PositiveIntegerField(
        verbose_name='Año',
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ],
        help_text='Año de fabricación del vehículo'
    )

    matricula = models.CharField(
        max_length=20,
        unique=True,
        validators=[matricula_regex],
        verbose_name='Matrícula',
        help_text='Formato: 1234ABC o M-1234-AB'
    )

    bastidor = models.CharField(
        max_length=17,
        unique=True,
        blank=True,
        verbose_name='Número de Bastidor (VIN)',
        help_text='17 caracteres - Vehicle Identification Number'
    )

    color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Color',
        help_text='Color principal del vehículo'
    )

    tipo_combustible = models.CharField(
        max_length=20,
        choices=TipoCombustible.choices,
        default=TipoCombustible.GASOLINA,
        verbose_name='Tipo de Combustible'
    )

    kilometraje = models.PositiveIntegerField(
        default=0,
        verbose_name='Kilometraje',
        help_text='Kilometraje actual del vehículo'
    )

    # Foto del vehículo
    foto_vehiculo = models.ImageField(
        upload_to='vehiculos/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto del Vehículo',
        help_text='Foto del vehículo (opcional)'
    )

    # Notas adicionales
    notas = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Información adicional sobre el vehículo'
    )

    # Campos de control
    activo = models.BooleanField(
        default=True,
        verbose_name='Vehículo activo',
        help_text='Los vehículos inactivos no aparecen en búsquedas'
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
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['matricula']),
            models.Index(fields=['cliente', '-fecha_registro']),
            models.Index(fields=['marca', 'modelo']),
        ]

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.matricula}"

    def get_absolute_url(self):
        return reverse('vehiculos:detalle', kwargs={'pk': self.pk})

    def get_nombre_completo(self):
        """Retorna el nombre completo del vehículo con matrícula"""
        return f"{self.marca} {self.modelo} ({self.matricula})"

    @property
    def total_ordenes(self):
        """Retorna el número de órdenes de trabajo asociadas"""
        try:
            return self.ordenes.count()
        except:
            # Temporal: hasta crear modelo OrdenTrabajo
            return 0

    @property
    def tiene_ordenes_pendientes(self):
        """Retorna True si el vehículo tiene órdenes pendientes"""
        try:
            return self.ordenes.filter(estado='PENDIENTE').exists()
        except:
            # Temporal: hasta crear modelo OrdenTrabajo
            return False

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para:
        - Convertir matrícula y bastidor a mayúsculas
        - Redimensionar foto si es necesario
        """
        # Convertir a mayúsculas
        if self.matricula:
            self.matricula = self.matricula.upper().strip()
        if self.bastidor:
            self.bastidor = self.bastidor.upper().strip()

        super().save(*args, **kwargs)

        # Redimensionar foto si existe
        if self.foto_vehiculo:
            try:
                from PIL import Image
                img = Image.open(self.foto_vehiculo.path)

                # Redimensionar si es muy grande
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.foto_vehiculo.path)
            except Exception:
                # Si falla la redimensión, continuar sin error
                pass
