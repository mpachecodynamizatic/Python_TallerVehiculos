from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone


@login_required
def dashboard(request):
    """Vista del dashboard principal"""
    from apps.clientes.models import Cliente
    from apps.citas.models import Cita
    from apps.ordenes.models import OrdenTrabajo
    from apps.facturacion.models import Factura
    from apps.vehiculos.models import Vehiculo
    from apps.inventario.models import Repuesto

    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)

    facturacion_mes = Factura.objects.filter(
        fecha_emision__gte=inicio_mes,
        estado__in=['PAGA', 'PARC'],
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')

    context = {
        # Tarjetas resumen
        'total_clientes': Cliente.objects.filter(activo=True).count(),
        'citas_hoy': Cita.objects.filter(fecha_hora__date=hoy).exclude(estado='CANC').count(),
        'ordenes_activas': OrdenTrabajo.objects.filter(estado__in=['ABIE', 'PROC']).count(),
        'facturacion_mes': facturacion_mes,
        # Subtítulos de tarjetas
        'total_vehiculos': Vehiculo.objects.count(),
        'ordenes_mes': OrdenTrabajo.objects.filter(fecha_apertura__date__gte=inicio_mes).count(),
        'facturas_vencidas': Factura.objects.filter(estado='VENC').count(),
        # Listas
        'proximas_citas': Cita.objects.filter(
            fecha_hora__date__gte=hoy,
            fecha_hora__date__lte=hoy + timezone.timedelta(days=7),
        ).exclude(estado__in=['CANC', 'COMP']).select_related(
            'cliente', 'vehiculo', 'mecanico_asignado'
        ).order_by('fecha_hora')[:8],
        'ordenes_recientes': OrdenTrabajo.objects.filter(
            estado__in=['ABIE', 'PROC', 'COMP']
        ).select_related(
            'cliente', 'vehiculo', 'mecanico_asignado'
        ).order_by('-fecha_apertura')[:6],
        'facturas_pendientes': Factura.objects.filter(
            estado__in=['PEND', 'PARC', 'VENC']
        ).select_related('cliente').order_by('fecha_vencimiento')[:6],
        'stock_bajo': Repuesto.objects.filter(
            activo=True,
            stock_actual__lte=F('stock_minimo'),
        ).order_by('stock_actual')[:5],
    }
    return render(request, 'dashboard.html', context)


def home(request):
    """Vista de la página de inicio"""
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, 'home.html')

