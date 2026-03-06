from django.contrib import admin
from .models import Factura, LineaFactura


class LineaFacturaInline(admin.TabularInline):
    model = LineaFactura
    extra = 1
    fields = ['descripcion', 'cantidad', 'precio_unitario', 'descuento', 'iva']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero_factura', 'cliente', 'fecha_emision', 'fecha_vencimiento', 'estado', 'total', 'saldo_pendiente']
    list_filter = ['estado', 'fecha_emision', 'metodo_pago']
    search_fields = ['numero_factura', 'cliente__nombre', 'cliente__apellidos']
    readonly_fields = ['numero_factura', 'fecha_creacion', 'fecha_modificacion', 'subtotal', 'iva_monto', 'total', 'monto_pagado']
    ordering = ['-fecha_emision', '-numero_factura']
    inlines = [LineaFacturaInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_factura', 'cliente', 'orden_trabajo', 'fecha_emision', 'fecha_vencimiento', 'estado')
        }),
        ('Totales', {
            'fields': ('subtotal', 'iva_monto', 'total')
        }),
        ('Pago', {
            'fields': ('monto_pagado', 'metodo_pago', 'fecha_pago')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('usuario_creador', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LineaFactura)
class LineaFacturaAdmin(admin.ModelAdmin):
    list_display = ['factura', 'descripcion', 'cantidad', 'precio_unitario', 'descuento', 'iva', 'total']
    list_filter = ['factura__estado', 'factura__fecha_emision']
    search_fields = ['factura__numero_factura', 'descripcion']
    ordering = ['-factura__fecha_emision']
