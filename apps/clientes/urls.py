from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Gestión de clientes (Admin y Recepcionistas)
    path('', views.ListarClientesView.as_view(), name='listar'),
    path('crear/', views.CrearClienteView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.EditarClienteView.as_view(), name='editar'),
    path('<int:pk>/detalle/', views.DetalleClienteView.as_view(), name='detalle'),
    path('<int:pk>/eliminar/', views.EliminarClienteView.as_view(), name='eliminar'),
]
