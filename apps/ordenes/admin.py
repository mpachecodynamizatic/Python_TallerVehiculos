from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import OrdenTrabajo, LineaTrabajo, LineaRepuesto


class LineaTrabajoInline(admin.TabularInline):
    """Inline para líneas de trabajo"""
    model = LineaTrabajo
    extra = 1
    fields = ['descripcion', 'horas', 'precio_hora']


class LineaRepuestoInline(admin.TabularInline):
    """Inline para líneas de repuestos"""
    model = LineaRepuesto
    extra = 1
    fields = ['descripcion', 'cantidad', 'precio_unitario', 'descuento']


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    """Configuración del admin para Órdenes de Trabajo"""

    list_display = [
        'numero_orden',
        'cliente_link',
        'vehiculo_info',
        'mecanico_asignado',
        'estado_badge',
        'prioridad_badge',
        'fecha_apertura',
        'total_display',
    ]

    list_filter = [
        'estado',
        'prioridad',
        'mecanico_asignado',
        'fecha_apertura',
    ]

    search_fields = [
        'numero_orden',
        'cliente__nombre',
        'cliente__apellidos',
        'cliente__dni',
        'vehiculo__matricula',
        'vehiculo__marca',
        'vehiculo__modelo',
    ]

    readonly_fields = [
        'numero_orden',
        'fecha_creacion',
        'fecha_modificacion',
        'usuario_creacion',
        'total_display',
    ]

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'numero_orden',
                'cliente',
                'vehiculo',
                'cita',
                'estado',
                'prioridad',
            )
        }),
        ('Asignación', {
            'fields': (
                'mecanico_asignado',
                'kilometros_ingreso',
            )
        }),
        ('Descripción y Diagnóstico', {
            'fields': (
                'descripcion_problema',
                'diagnostico',
                'trabajos_realizados',
                'observaciones',
            )
        }),
        ('Tiempos', {
            'fields': (
                'tiempo_estimado',
                'tiempo_real',
                'fecha_apertura',
                'fecha_cierre',
            )
        }),
        ('Totales', {
            'fields': (
                'total_display',
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_modificacion',
                'usuario_creacion',
            ),
            'classes': ('collapse',),
        }),
    )

    inlines = [LineaTrabajoInline, LineaRepuestoInline]

    date_hierarchy = 'fecha_apertura'
    ordering = ['-fecha_apertura']
    list_per_page = 25

    @admin.display(description='Cliente')
    def cliente_link(self, obj):
        url = reverse('admin:clientes_cliente_change', args=[obj.cliente.pk])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.get_nombre_completo())

    @admin.display(description='Vehículo')
    def vehiculo_info(self, obj):
        url = reverse('admin:vehiculos_vehiculo_change', args=[obj.vehiculo.pk])
        return format_html(
            '<a href="{}">{} {} ({})</a>',
            url,
            obj.vehiculo.marca,
            obj.vehiculo.modelo,
            obj.vehiculo.matricula
        )

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        color_map = {
            OrdenTrabajo.EstadoOrden.ABIERTA: '#60A5FA',
            OrdenTrabajo.EstadoOrden.EN_PROCESO: '#A78BFA',
            OrdenTrabajo.EstadoOrden.PAUSADA: '#FCD34D',
            OrdenTrabajo.EstadoOrden.COMPLETADA: '#34D399',
            OrdenTrabajo.EstadoOrden.CANCELADA: '#F87171',
        }
        color = color_map.get(obj.estado, '#9CA3AF')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )

    @admin.display(description='Prioridad')
    def prioridad_badge(self, obj):
        color_map = {
            OrdenTrabajo.Prioridad.BAJA: '#9CA3AF',
            OrdenTrabajo.Prioridad.NORMAL: '#60A5FA',
            OrdenTrabajo.Prioridad.ALTA: '#F59E0B',
            OrdenTrabajo.Prioridad.URGENTE: '#F87171',
        }
        color = color_map.get(obj.prioridad, '#9CA3AF')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_prioridad_display()
        )

    @admin.display(description='Total')
    def total_display(self, obj):
        return f"€{obj.total:,.2f}"


@admin.register(LineaTrabajo)
class LineaTrabajoAdmin(admin.ModelAdmin):
    """Admin para líneas de trabajo"""
    list_display = ['orden', 'descripcion', 'horas', 'precio_hora', 'total_display']
    list_filter = ['orden__estado']
    search_fields = ['orden__numero_orden', 'descripcion']

    @admin.display(description='Total')
    def total_display(self, obj):
        return f"€{obj.total:,.2f}"


@admin.register(LineaRepuesto)
class LineaRepuestoAdmin(admin.ModelAdmin):
    """Admin para líneas de repuestos"""
    list_display = ['orden', 'descripcion', 'cantidad', 'precio_unitario', 'descuento', 'total_display']
    list_filter = ['orden__estado']
    search_fields = ['orden__numero_orden', 'descripcion']

    @admin.display(description='Total')
    def total_display(self, obj):
        return f"€{obj.total:,.2f}"
