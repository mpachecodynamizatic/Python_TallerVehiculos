from django.urls import path
from . import views

app_name = 'vehiculos'

urlpatterns = [
    # Gestión de vehículos
    path('', views.ListarVehiculosView.as_view(), name='listar'),
    path('crear/', views.CrearVehiculoView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.EditarVehiculoView.as_view(), name='editar'),
    path('<int:pk>/detalle/', views.DetalleVehiculoView.as_view(), name='detalle'),
    path('<int:pk>/eliminar/', views.EliminarVehiculoView.as_view(), name='eliminar'),
]
