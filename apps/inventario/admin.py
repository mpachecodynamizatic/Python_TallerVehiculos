from django.contrib import admin
from .models import CategoriaRepuesto, Repuesto, MovimientoInventario


@admin.register(CategoriaRepuesto)
class CategoriaRepuestoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'marca', 'stock_actual', 'stock_minimo', 'precio_venta', 'activo']
    list_filter = ['categoria', 'activo', 'marca']
    search_fields = ['codigo', 'nombre', 'descripcion', 'marca']
    list_editable = ['activo']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    ordering = ['nombre']

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'marca', 'ubicacion_almacen', 'foto')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo', 'stock_maximo')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_venta', 'iva')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['repuesto', 'tipo', 'cantidad', 'stock_anterior', 'stock_posterior', 'fecha', 'usuario', 'orden_trabajo']
    list_filter = ['tipo', 'fecha']
    search_fields = ['repuesto__codigo', 'repuesto__nombre', 'notas']
    readonly_fields = ['fecha']
    ordering = ['-fecha']

    def has_add_permission(self, request):
        # Los movimientos solo deben crearse a través de las vistas o métodos del modelo
        return False

    def has_change_permission(self, request, obj=None):
        # Los movimientos no deben editarse una vez creados (auditoría)
        return False
