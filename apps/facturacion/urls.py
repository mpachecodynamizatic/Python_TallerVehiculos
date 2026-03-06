from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    # Facturas
    path('', views.ListarFacturasView.as_view(), name='listar'),
    path('crear/', views.CrearFacturaView.as_view(), name='crear'),
    path('<int:pk>/', views.DetalleFacturaView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarFacturaView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarFacturaView.as_view(), name='eliminar'),

    # Generar desde orden
    path('generar-desde-orden/<int:orden_pk>/', views.generar_desde_orden_view, name='generar_desde_orden'),

    # Registrar pago
    path('<int:pk>/registrar-pago/', views.registrar_pago_view, name='registrar_pago'),
]
