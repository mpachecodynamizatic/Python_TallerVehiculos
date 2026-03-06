from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Cliente.
    """
    model = Cliente

    # Campos mostrados en la lista
    list_display = [
        'dni',
        'apellidos',
        'nombre',
        'email',
        'telefono',
        'ciudad',
        'activo',
        'numero_vehiculos',
        'fecha_registro'
    ]

    # Filtros en la barra lateral
    list_filter = [
        'activo',
        'ciudad',
        'fecha_registro',
        'fecha_actualizacion'
    ]

    # Campos de búsqueda
    search_fields = [
        'nombre',
        'apellidos',
        'dni',
        'email',
        'telefono',
        'ciudad'
    ]

    # Ordenamiento por defecto
    ordering = ['-fecha_registro']

    # Campos readonly
    readonly_fields = [
        'fecha_registro',
        'fecha_actualizacion'
    ]

    # Personalizar fieldsets para la vista de detalle/edición
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'nombre',
                'apellidos',
                'dni'
            )
        }),
        ('Información de Contacto', {
            'fields': (
                'email',
                'telefono',
                'telefono_alternativo'
            )
        }),
        ('Dirección', {
            'fields': (
                'direccion',
                'ciudad',
                'codigo_postal'
            )
        }),
        ('Información Adicional', {
            'fields': (
                'notas',
                'activo'
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_registro',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )

    # Acciones personalizadas
    actions = ['activar_clientes', 'desactivar_clientes']

    def numero_vehiculos(self, obj):
        """Muestra el número de vehículos del cliente"""
        return obj.total_vehiculos
    numero_vehiculos.short_description = 'Vehículos'
    numero_vehiculos.admin_order_field = 'vehiculos'

    def activar_clientes(self, request, queryset):
        """Acción para activar clientes seleccionados"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'{count} cliente(s) activado(s) exitosamente.'
        )
    activar_clientes.short_description = 'Activar clientes seleccionados'

    def desactivar_clientes(self, request, queryset):
        """Acción para desactivar clientes seleccionados"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'{count} cliente(s) desactivado(s) exitosamente.'
        )
    desactivar_clientes.short_description = 'Desactivar clientes seleccionados'
