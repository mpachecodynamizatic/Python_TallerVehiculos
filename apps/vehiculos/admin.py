from django.contrib import admin
from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Vehiculo.
    """
    model = Vehiculo

    # Campos mostrados en la lista
    list_display = [
        'matricula',
        'marca_modelo',
        'anio',
        'get_cliente_nombre',
        'tipo_combustible',
        'kilometraje',
        'activo',
        'fecha_registro'
    ]

    # Filtros en la barra lateral
    list_filter = [
        'activo',
        'tipo_combustible',
        'marca',
        'anio',
        'fecha_registro'
    ]

    # Campos de búsqueda
    search_fields = [
        'matricula',
        'bastidor',
        'marca',
        'modelo',
        'cliente__nombre',
        'cliente__apellidos',
        'cliente__dni'
    ]

    # Ordenamiento por defecto
    ordering = ['-fecha_registro']

    # Campos readonly
    readonly_fields = [
        'fecha_registro',
        'fecha_actualizacion'
    ]

    # Autocompletar para cliente
    autocomplete_fields = ['cliente']

    # Personalizar fieldsets para la vista de detalle/edición
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Información del Vehículo', {
            'fields': (
                'marca',
                'modelo',
                'anio',
                'color'
            )
        }),
        ('Identificación', {
            'fields': (
                'matricula',
                'bastidor'
            )
        }),
        ('Características Técnicas', {
            'fields': (
                'tipo_combustible',
                'kilometraje'
            )
        }),
        ('Multimedia', {
            'fields': ('foto_vehiculo',)
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
    actions = ['activar_vehiculos', 'desactivar_vehiculos']

    def marca_modelo(self, obj):
        """Muestra marca y modelo juntos"""
        return f"{obj.marca} {obj.modelo}"
    marca_modelo.short_description = 'Vehículo'
    marca_modelo.admin_order_field = 'marca'

    def get_cliente_nombre(self, obj):
        """Muestra el nombre del cliente"""
        return obj.cliente.get_nombre_completo()
    get_cliente_nombre.short_description = 'Cliente'
    get_cliente_nombre.admin_order_field = 'cliente__apellidos'

    def activar_vehiculos(self, request, queryset):
        """Acción para activar vehículos seleccionados"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'{count} vehículo(s) activado(s) exitosamente.'
        )
    activar_vehiculos.short_description = 'Activar vehículos seleccionados'

    def desactivar_vehiculos(self, request, queryset):
        """Acción para desactivar vehículos seleccionados"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'{count} vehículo(s) desactivado(s) exitosamente.'
        )
    desactivar_vehiculos.short_description = 'Desactivar vehículos seleccionados'
