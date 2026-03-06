from django.contrib import admin
from .models import Proveedor, OrdenCompra, LineaCompra


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cif', 'email', 'telefono', 'ciudad', 'activo']
    list_filter = ['activo', 'pais', 'ciudad']
    search_fields = ['nombre', 'cif', 'email', 'telefono', 'contacto_principal']
    list_editable = ['activo']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    ordering = ['nombre']

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'cif', 'email', 'telefono', 'contacto_principal')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'codigo_postal', 'pais')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


class LineaCompraInline(admin.TabularInline):
    model = LineaCompra
    extra = 1
    fields = ['repuesto', 'cantidad_solicitada', 'cantidad_recibida', 'precio_unitario', 'descuento']
    readonly_fields = []


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ['numero_orden', 'proveedor', 'fecha_orden', 'estado', 'total', 'usuario_creador']
    list_filter = ['estado', 'fecha_orden', 'proveedor']
    search_fields = ['numero_orden', 'proveedor__nombre']
    readonly_fields = ['numero_orden', 'fecha_creacion', 'fecha_modificacion', 'subtotal', 'iva_monto', 'total']
    ordering = ['-fecha_orden', '-numero_orden']
    inlines = [LineaCompraInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_orden', 'proveedor', 'fecha_orden', 'fecha_entrega_esperada', 'estado')
        }),
        ('Totales', {
            'fields': ('subtotal', 'iva_monto', 'total')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('usuario_creador', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LineaCompra)
class LineaCompraAdmin(admin.ModelAdmin):
    list_display = ['orden_compra', 'repuesto', 'cantidad_solicitada', 'cantidad_recibida', 'precio_unitario', 'descuento']
    list_filter = ['orden_compra__estado', 'orden_compra__fecha_orden']
    search_fields = ['orden_compra__numero_orden', 'repuesto__nombre', 'repuesto__codigo']
    ordering = ['-orden_compra__fecha_orden']
