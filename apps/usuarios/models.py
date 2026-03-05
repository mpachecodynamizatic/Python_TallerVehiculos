from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
import os


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema de taller de vehículos.
    Extiende AbstractUser de Django para incluir campos adicionales y roles.
    """

    class Rol(models.TextChoices):
        """Roles disponibles en el sistema"""
        ADMIN = 'ADMIN', 'Administrador'
        MECANICO = 'MECANICO', 'Mecánico'
        RECEPCIONISTA = 'RECEPCIONISTA', 'Recepcionista'

    # Campo email obligatorio y único
    email = models.EmailField(
        'correo electrónico',
        unique=True,
        error_messages={
            'unique': 'Ya existe un usuario con este email.'
        }
    )

    # Rol del usuario en el sistema
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.RECEPCIONISTA,
        help_text='Rol del usuario en el sistema'
    )

    # Teléfono con validación de formato internacional
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='El formato de teléfono debe ser: "+999999999". Hasta 15 dígitos permitidos.'
    )
    telefono = models.CharField(
        'teléfono',
        max_length=15,
        blank=True,
        validators=[telefono_regex],
        help_text='Formato: +34600000000'
    )

    # Foto de perfil
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos_perfil/',
        blank=True,
        null=True,
        help_text='Imagen de perfil del usuario (se redimensionará a 300x300px)'
    )

    # Campo activo para deshabilitar usuarios sin eliminarlos
    activo = models.BooleanField(
        default=True,
        help_text='Indica si el usuario puede acceder al sistema'
    )

    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creación'
    )

    ultima_conexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='última conexión',
        help_text='Fecha y hora de la última vez que el usuario inició sesión'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
        permissions = [
            ('puede_gestionar_usuarios', 'Puede gestionar usuarios del sistema'),
            ('puede_ver_reportes', 'Puede ver reportes y estadísticas'),
        ]

    def __str__(self):
        """Representación en string del usuario"""
        nombre_completo = self.get_full_name()
        if nombre_completo:
            return f"{nombre_completo} ({self.get_rol_display()})"
        return f"{self.username} ({self.get_rol_display()})"

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para redimensionar la foto de perfil
        si excede las dimensiones máximas permitidas
        """
        super().save(*args, **kwargs)

        # Redimensionar foto de perfil si es necesario
        if self.foto_perfil:
            try:
                img = Image.open(self.foto_perfil.path)

                # Si la imagen es muy grande, redimensionarla
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(self.foto_perfil.path, quality=95, optimize=True)
            except Exception as e:
                # Log del error pero no detener la operación
                print(f"Error al redimensionar imagen: {e}")

    # Propiedades para verificar roles
    @property
    def es_admin(self):
        """Retorna True si el usuario es administrador"""
        return self.rol == self.Rol.ADMIN

    @property
    def es_mecanico(self):
        """Retorna True si el usuario es mecánico"""
        return self.rol == self.Rol.MECANICO

    @property
    def es_recepcionista(self):
        """Retorna True si el usuario es recepcionista"""
        return self.rol == self.Rol.RECEPCIONISTA

    def puede_gestionar_usuarios(self):
        """Verifica si el usuario tiene permiso para gestionar otros usuarios"""
        return self.es_admin or self.has_perm('usuarios.puede_gestionar_usuarios')

    def puede_ver_reportes(self):
        """Verifica si el usuario tiene permiso para ver reportes"""
        return self.es_admin or self.has_perm('usuarios.puede_ver_reportes')
