from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Count

from .models import Cliente
from .forms import ClienteForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE GESTIÓN DE CLIENTES ====================

class ListarClientesView(AdminORecepcionistaMixin, ListView):
    """
    Vista para listar todos los clientes.
    Accesible por administradores y recepcionistas.
    Incluye filtros por estado, búsqueda y paginación.
    """
    model = Cliente
    template_name = 'clientes/listar_clientes.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Anotar con el número de vehículos
        queryset = queryset.annotate(num_vehiculos=Count('vehiculos'))

        # Filtro por estado activo
        estado = self.request.GET.get('estado')
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)

        # Búsqueda por nombre, apellidos, DNI, email o teléfono
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(apellidos__icontains=busqueda) |
                Q(dni__icontains=busqueda) |
                Q(email__icontains=busqueda) |
                Q(telefono__icontains=busqueda)
            )

        # Ordenación por columnas
        orden = self.request.GET.get('orden', '-fecha_registro')
        direccion = self.request.GET.get('direccion', '')

        # Validar campos permitidos para ordenar
        campos_validos = ['dni', 'nombre', 'apellidos', 'email', 'ciudad',
                         'fecha_registro', 'num_vehiculos']

        # Limpiar el prefijo - si existe
        campo_orden = orden.lstrip('-')

        if campo_orden in campos_validos:
            # Si la dirección es 'desc' y el campo no tiene -, agregarlo
            if direccion == 'desc' and not orden.startswith('-'):
                orden = f'-{orden}'
            # Si la dirección es 'asc' y el campo tiene -, quitarlo
            elif direccion == 'asc' and orden.startswith('-'):
                orden = orden.lstrip('-')
            queryset = queryset.order_by(orden)
        else:
            queryset = queryset.order_by('-fecha_registro')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['orden'] = self.request.GET.get('orden', '-fecha_registro')
        context['direccion'] = self.request.GET.get('direccion', '')
        return context


class CrearClienteView(AdminORecepcionistaMixin, CreateView):
    """
    Vista para crear un nuevo cliente.
    Accesible por administradores y recepcionistas.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/crear_cliente.html'
    success_url = reverse_lazy('clientes:listar')

    def form_valid(self, form):
        cliente = form.save()
        messages.success(
            self.request,
            f'Cliente "{cliente.get_nombre_completo()}" creado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al crear el cliente. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class EditarClienteView(AdminORecepcionistaMixin, UpdateView):
    """
    Vista para editar un cliente existente.
    Accesible por administradores y recepcionistas.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/editar_cliente.html'
    success_url = reverse_lazy('clientes:listar')

    def form_valid(self, form):
        cliente = form.save()
        messages.success(
            self.request,
            f'Cliente "{cliente.get_nombre_completo()}" actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar el cliente. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class DetalleClienteView(UsuarioActivoMixin, DetailView):
    """
    Vista para ver el detalle completo de un cliente.
    Accesible por cualquier usuario autenticado y activo.
    Muestra todos los vehículos asociados al cliente.
    """
    model = Cliente
    template_name = 'clientes/detalle_cliente.html'
    context_object_name = 'cliente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los vehículos del cliente
        context['vehiculos'] = self.object.vehiculos.all().order_by('-fecha_registro')
        return context


class EliminarClienteView(AdminORecepcionistaMixin, DeleteView):
    """
    Vista para eliminar un cliente.
    Accesible por administradores y recepcionistas.
    Previene la eliminación si el cliente tiene vehículos asociados.
    """
    model = Cliente
    template_name = 'clientes/eliminar_cliente.html'
    success_url = reverse_lazy('clientes:listar')

    def post(self, request, *args, **kwargs):
        cliente = self.get_object()
        nombre_completo = cliente.get_nombre_completo()

        # Verificar si el cliente tiene vehículos
        if cliente.tiene_vehiculos:
            messages.error(
                request,
                f'No se puede eliminar el cliente "{nombre_completo}" porque tiene {cliente.total_vehiculos} vehículo(s) asociado(s). '
                f'Primero debe eliminar o reasignar los vehículos.'
            )
            return redirect('clientes:detalle', pk=cliente.pk)

        # Eliminar cliente
        self.object = cliente
        cliente.delete()
        messages.success(
            request,
            f'Cliente "{nombre_completo}" eliminado exitosamente.'
        )
        return redirect(self.success_url)
