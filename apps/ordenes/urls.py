from django.urls import path
from . import views

app_name = 'ordenes'

urlpatterns = [
    # Vistas principales
    path('', views.ListarOrdenesView.as_view(), name='listar'),
    path('crear/', views.CrearOrdenView.as_view(), name='crear'),
    path('<int:pk>/', views.DetalleOrdenView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarOrdenView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarOrdenView.as_view(), name='eliminar'),

    # Vistas AJAX para líneas de trabajo
    path('<int:pk>/trabajo/agregar/', views.agregar_linea_trabajo, name='agregar_trabajo'),
    path('<int:pk>/trabajo/<int:linea_id>/eliminar/', views.eliminar_linea_trabajo, name='eliminar_trabajo'),

    # Vistas AJAX para líneas de repuestos
    path('<int:pk>/repuesto/agregar/', views.agregar_linea_repuesto, name='agregar_repuesto'),
    path('<int:pk>/repuesto/<int:linea_id>/eliminar/', views.eliminar_linea_repuesto, name='eliminar_repuesto'),
]
