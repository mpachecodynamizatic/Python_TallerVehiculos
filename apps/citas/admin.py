from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Cita.
    """

    list_display = [
        'id',
        'fecha_hora_formateada',
        'cliente_link',
        'vehiculo_info',
        'tipo_servicio',
        'mecanico_asignado',
        'estado_badge',
        'duracion_formato_display',
        'fecha_creacion',
    ]

    list_filter = [
        'estado',
        'tipo_servicio',
        'mecanico_asignado',
        'fecha_hora',
        'recordatorio_enviado',
    ]

    search_fields = [
        'cliente__nombre',
        'cliente__apellidos',
        'cliente__dni',
        'vehiculo__matricula',
        'vehiculo__marca',
        'vehiculo__modelo',
        'descripcion',
    ]

    readonly_fields = [
        'id',
        'fecha_creacion',
        'fecha_modificacion',
        'usuario_creacion',
        'hora_fin',
        'duracion_formato_display',
    ]

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'id',
                'cliente',
                'vehiculo',
                'estado',
            )
        }),
        ('Programación', {
            'fields': (
                'fecha_hora',
                'duracion_estimada',
                'duracion_formato_display',
                'hora_fin',
                'tipo_servicio',
                'mecanico_asignado',
            )
        }),
        ('Detalles del Servicio', {
            'fields': (
                'descripcion',
                'notas',
            )
        }),
        ('Notificaciones', {
            'fields': (
                'recordatorio_enviado',
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

    date_hierarchy = 'fecha_hora'

    ordering = ['-fecha_hora']

    list_per_page = 25

    actions = ['marcar_confirmada', 'marcar_completada', 'marcar_cancelada']

    # ==================== MÉTODOS PERSONALIZADOS ====================

    @admin.display(description='Fecha y Hora', ordering='fecha_hora')
    def fecha_hora_formateada(self, obj):
        """Muestra la fecha y hora en formato legible"""
        return obj.fecha_hora.strftime('%d/%m/%Y %H:%M')

    @admin.display(description='Cliente')
    def cliente_link(self, obj):
        """Muestra el cliente como link al detalle"""
        url = reverse('admin:clientes_cliente_change', args=[obj.cliente.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.cliente.get_nombre_completo()
        )

    @admin.display(description='Vehículo')
    def vehiculo_info(self, obj):
        """Muestra información del vehículo"""
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
        """Muestra el estado con colores"""
        color_map = {
            Cita.EstadoCita.PENDIENTE: '#FCD34D',  # Amarillo
            Cita.EstadoCita.CONFIRMADA: '#60A5FA',  # Azul
            Cita.EstadoCita.EN_PROCESO: '#A78BFA',  # Púrpura
            Cita.EstadoCita.COMPLETADA: '#34D399',  # Verde
            Cita.EstadoCita.CANCELADA: '#F87171',   # Rojo
            Cita.EstadoCita.NO_ASISTIO: '#9CA3AF',  # Gris
        }
        color = color_map.get(obj.estado, '#9CA3AF')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )

    @admin.display(description='Duración')
    def duracion_formato_display(self, obj):
        """Muestra la duración en formato legible"""
        return obj.duracion_formato

    # ==================== ACCIONES PERSONALIZADAS ====================

    @admin.action(description='Marcar como Confirmada')
    def marcar_confirmada(self, request, queryset):
        """Marca las citas seleccionadas como confirmadas"""
        actualizadas = queryset.filter(estado=Cita.EstadoCita.PENDIENTE).update(
            estado=Cita.EstadoCita.CONFIRMADA
        )
        self.message_user(
            request,
            f'{actualizadas} cita(s) marcada(s) como confirmada(s).'
        )

    @admin.action(description='Marcar como Completada')
    def marcar_completada(self, request, queryset):
        """Marca las citas seleccionadas como completadas"""
        actualizadas = queryset.filter(estado=Cita.EstadoCita.EN_PROCESO).update(
            estado=Cita.EstadoCita.COMPLETADA
        )
        self.message_user(
            request,
            f'{actualizadas} cita(s) marcada(s) como completada(s).'
        )

    @admin.action(description='Marcar como Cancelada')
    def marcar_cancelada(self, request, queryset):
        """Marca las citas seleccionadas como canceladas"""
        actualizadas = queryset.filter(
            estado__in=[Cita.EstadoCita.PENDIENTE, Cita.EstadoCita.CONFIRMADA]
        ).update(estado=Cita.EstadoCita.CANCELADA)
        self.message_user(
            request,
            f'{actualizadas} cita(s) marcada(s) como cancelada(s).'
        )
