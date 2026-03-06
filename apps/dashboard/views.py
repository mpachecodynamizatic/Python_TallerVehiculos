# Dashboard view implemented in apps/core/views.py



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)

        # -- Importaciones locales para evitar dependencias circulares --
        from apps.clientes.models import Cliente
        from apps.citas.models import Cita
        from apps.ordenes.models import OrdenTrabajo
        from apps.facturacion.models import Factura
        from apps.vehiculos.models import Vehiculo
        from apps.inventario.models import Repuesto

        # === TARJETAS RESUMEN ===
        context['total_clientes'] = Cliente.objects.filter(activo=True).count()
        context['citas_hoy'] = Cita.objects.filter(
            fecha_hora__date=hoy
        ).exclude(estado='CANC').count()
        context['ordenes_activas'] = OrdenTrabajo.objects.filter(
            estado__in=['ABIE', 'PROC']
        ).count()
        facturacion_mes = Factura.objects.filter(
            fecha_emision__gte=inicio_mes,
            estado__in=['PAGA', 'PARC'],
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        context['facturacion_mes'] = facturacion_mes

        # === CITAS PRÓXIMAS (hoy + 7 días) ===
        context['proximas_citas'] = Cita.objects.filter(
            fecha_hora__date__gte=hoy,
            fecha_hora__date__lte=hoy + timezone.timedelta(days=7),
        ).exclude(estado__in=['CANC', 'COMP']).select_related(
            'cliente', 'vehiculo', 'mecanico_asignado'
        ).order_by('fecha_hora')[:8]

        # === ÓRDENES RECIENTES ===
        context['ordenes_recientes'] = OrdenTrabajo.objects.filter(
            estado__in=['ABIE', 'PROC', 'COMP']
        ).select_related('cliente', 'vehiculo', 'mecanico_asignado'
        ).order_by('-fecha_apertura')[:6]

        # === FACTURAS PENDIENTES ===
        context['facturas_pendientes'] = Factura.objects.filter(
            estado__in=['PEND', 'PARC', 'VENC']
        ).select_related('cliente').order_by('fecha_vencimiento')[:6]

        # === STOCK BAJO ===
        context['stock_bajo'] = Repuesto.objects.filter(
            activo=True,
            stock_actual__lte=models_stock_minimo()
        )[:5]

        # === ESTADÍSTICAS ADICIONALES ===
        context['total_vehiculos'] = Vehiculo.objects.count()
        context['ordenes_mes'] = OrdenTrabajo.objects.filter(
            fecha_apertura__date__gte=inicio_mes
        ).count()
        context['facturas_vencidas'] = Factura.objects.filter(
            estado='VENC'
        ).count()

        return context


def models_stock_minimo():
    """Helper para filtrar repuestos con stock bajo el mínimo."""
    from django.db.models import F
    # Retorna una expresión — se usa como valor de referencia en la view
    return F('stock_minimo')

