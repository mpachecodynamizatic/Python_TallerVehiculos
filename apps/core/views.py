from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """Vista del dashboard principal"""
    context = {
        'total_clientes': 0,
        'citas_hoy': 0,
        'ordenes_activas': 0,
        'facturacion_mes': 0,
    }
    return render(request, 'dashboard.html', context)


def home(request):
    """Vista de la página de inicio"""
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, 'home.html')
