from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Repuestos
    path('', views.ListarRepuestosView.as_view(), name='listar'),
    path('crear/', views.CrearRepuestoView.as_view(), name='crear'),
    path('<int:pk>/', views.DetalleRepuestoView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarRepuestoView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarRepuestoView.as_view(), name='eliminar'),
]
