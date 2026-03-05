from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del admin para el modelo Usuario personalizado.
    """
    model = Usuario

    # Campos mostrados en la lista
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'rol',
        'activo',
        'is_staff',
        'fecha_creacion',
        'ultima_conexion'
    ]

    # Filtros en la barra lateral
    list_filter = [
        'rol',
        'activo',
        'is_staff',
        'is_superuser',
        'fecha_creacion',
        'ultima_conexion'
    ]

    # Campos de búsqueda
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'telefono'
    ]

    # Ordenamiento por defecto
    ordering = ['-fecha_creacion']

    # Campos readonly
    readonly_fields = [
        'fecha_creacion',
        'ultima_conexion',
        'date_joined',
        'last_login'
    ]

    # Personalizar fieldsets para la vista de detalle/edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': (
                'rol',
                'telefono',
                'foto_perfil',
                'activo'
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'ultima_conexion'
            )
        }),
    )

    # Personalizar fieldsets para agregar nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'rol',
                'telefono',
                'foto_perfil'
            )
        }),
    )

    # Acciones personalizadas
    actions = ['activar_usuarios', 'desactivar_usuarios']

    def activar_usuarios(self, request, queryset):
        """Acción para activar usuarios seleccionados"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'{count} usuario(s) activado(s) exitosamente.'
        )
    activar_usuarios.short_description = 'Activar usuarios seleccionados'

    def desactivar_usuarios(self, request, queryset):
        """Acción para desactivar usuarios seleccionados"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'{count} usuario(s) desactivado(s) exitosamente.'
        )
    desactivar_usuarios.short_description = 'Desactivar usuarios seleccionados'
