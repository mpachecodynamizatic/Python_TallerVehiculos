from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Gestión de usuarios (Solo Admin)
    path('', views.ListarUsuariosView.as_view(), name='listar'),
    path('crear/', views.CrearUsuarioView.as_view(), name='crear'),
    path('<int:pk>/editar/', views.EditarUsuarioView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarUsuarioView.as_view(), name='eliminar'),
    path('<int:pk>/detalle/', views.DetalleUsuarioView.as_view(), name='detalle'),
    path('<int:pk>/activar/', views.activar_desactivar_usuario, name='activar_desactivar'),

    # Perfil de usuario (Cualquier usuario autenticado)
    path('perfil/', views.PerfilUsuarioView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    path('perfil/cambiar-password/', views.CambiarPasswordView.as_view(), name='cambiar_password'),
]
