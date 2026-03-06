from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Vistas principales
    path('', views.ListarCitasView.as_view(), name='listar'),
    path('crear/', views.CrearCitaView.as_view(), name='crear'),
    path('<int:pk>/', views.DetalleCitaView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarCitaView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarCitaView.as_view(), name='eliminar'),

    # Vista de calendario
    path('calendario/', views.CalendarioCitasView.as_view(), name='calendario'),

    # Vistas AJAX
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_cita, name='cambiar_estado'),
    path('api/citas-json/', views.obtener_citas_json, name='citas_json'),
]
