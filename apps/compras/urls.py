from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    # Proveedores
    path('proveedores/', views.ListarProveedoresView.as_view(), name='listar_proveedores'),
    path('proveedores/crear/', views.CrearProveedorView.as_view(), name='crear_proveedor'),
    path('proveedores/<int:pk>/', views.DetalleProveedorView.as_view(), name='detalle_proveedor'),
    path('proveedores/<int:pk>/editar/', views.EditarProveedorView.as_view(), name='editar_proveedor'),
    path('proveedores/<int:pk>/eliminar/', views.EliminarProveedorView.as_view(), name='eliminar_proveedor'),

    # Órdenes de Compra
    path('ordenes/', views.ListarOrdenesCompraView.as_view(), name='listar_ordenes'),
    path('ordenes/crear/', views.CrearOrdenCompraView.as_view(), name='crear_orden'),
    path('ordenes/<int:pk>/', views.DetalleOrdenCompraView.as_view(), name='detalle_orden'),
    path('ordenes/<int:pk>/editar/', views.EditarOrdenCompraView.as_view(), name='editar_orden'),
    path('ordenes/<int:pk>/eliminar/', views.EliminarOrdenCompraView.as_view(), name='eliminar_orden'),

    # Recepción de mercancía
    path('lineas/<int:pk>/recibir/', views.recibir_mercancia_view, name='recibir_mercancia'),
]
