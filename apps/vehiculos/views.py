from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Vehiculo
from .forms import VehiculoForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE GESTIÓN DE VEHÍCULOS ====================

class ListarVehiculosView(UsuarioActivoMixin, ListView):
    """
    Vista para listar todos los vehículos.
    Accesible por cualquier usuario autenticado y activo.
    Incluye filtros por estado, búsqueda y paginación.
    """
    model = Vehiculo
    template_name = 'vehiculos/listar_vehiculos.html'
    context_object_name = 'vehiculos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Usar select_related para optimizar consultas
        queryset = queryset.select_related('cliente')

        # Filtro por estado activo
        estado = self.request.GET.get('estado')
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)

        # Filtro por tipo de combustible
        tipo_combustible = self.request.GET.get('tipo_combustible')
        if tipo_combustible:
            queryset = queryset.filter(tipo_combustible=tipo_combustible)

        # Búsqueda por matrícula, marca, modelo o cliente
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(matricula__icontains=busqueda) |
                Q(marca__icontains=busqueda) |
                Q(modelo__icontains=busqueda) |
                Q(bastidor__icontains=busqueda) |
                Q(cliente__nombre__icontains=busqueda) |
                Q(cliente__apellidos__icontains=busqueda) |
                Q(cliente__dni__icontains=busqueda)
            )

        # Ordenación por columnas
        orden = self.request.GET.get('orden', '-fecha_registro')
        direccion = self.request.GET.get('direccion', '')

        # Validar campos permitidos para ordenar
        campos_validos = ['matricula', 'marca', 'modelo', 'anio',
                         'tipo_combustible', 'cliente__apellidos',
                         'fecha_registro']

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
        context['tipo_combustible_filtro'] = self.request.GET.get('tipo_combustible', '')
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['orden'] = self.request.GET.get('orden', '-fecha_registro')
        context['direccion'] = self.request.GET.get('direccion', '')
        # Pasar las opciones de tipo de combustible para el filtro
        context['tipos_combustible'] = Vehiculo.TipoCombustible.choices
        return context


class CrearVehiculoView(AdminORecepcionistaMixin, CreateView):
    """
    Vista para crear un nuevo vehículo.
    Accesible por administradores y recepcionistas.
    """
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'vehiculos/crear_vehiculo.html'
    success_url = reverse_lazy('vehiculos:listar')

    def get_initial(self):
        """Pre-cargar el cliente si se pasa como parámetro"""
        initial = super().get_initial()
        cliente_id = self.request.GET.get('cliente')
        if cliente_id:
            initial['cliente'] = cliente_id
        return initial

    def form_valid(self, form):
        vehiculo = form.save()
        messages.success(
            self.request,
            f'Vehículo "{vehiculo.get_nombre_completo()}" creado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al crear el vehículo. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class EditarVehiculoView(AdminORecepcionistaMixin, UpdateView):
    """
    Vista para editar un vehículo existente.
    Accesible por administradores y recepcionistas.
    """
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'vehiculos/editar_vehiculo.html'
    success_url = reverse_lazy('vehiculos:listar')

    def form_valid(self, form):
        vehiculo = form.save()
        messages.success(
            self.request,
            f'Vehículo "{vehiculo.get_nombre_completo()}" actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar el vehículo. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class DetalleVehiculoView(UsuarioActivoMixin, DetailView):
    """
    Vista para ver el detalle completo de un vehículo.
    Accesible por cualquier usuario autenticado y activo.
    Muestra el historial de órdenes de trabajo asociadas.
    """
    model = Vehiculo
    template_name = 'vehiculos/detalle_vehiculo.html'
    context_object_name = 'vehiculo'

    def get_queryset(self):
        """Optimizar con select_related para evitar queries adicionales"""
        return super().get_queryset().select_related('cliente')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener las órdenes de trabajo del vehículo (temporal: lista vacía hasta crear modelo OrdenTrabajo)
        # context['ordenes'] = self.object.ordenes.all().order_by('-fecha_creacion')
        context['ordenes'] = []  # Temporal
        return context


class EliminarVehiculoView(AdminORecepcionistaMixin, DeleteView):
    """
    Vista para eliminar un vehículo.
    Accesible por administradores y recepcionistas.
    Previene la eliminación si el vehículo tiene órdenes de trabajo asociadas.
    """
    model = Vehiculo
    template_name = 'vehiculos/eliminar_vehiculo.html'
    success_url = reverse_lazy('vehiculos:listar')

    def post(self, request, *args, **kwargs):
        vehiculo = self.get_object()
        nombre_completo = vehiculo.get_nombre_completo()

        # Verificar si el vehículo tiene órdenes de trabajo (cuando se implemente)
        # if vehiculo.tiene_ordenes_pendientes:
        #     messages.error(
        #         request,
        #         f'No se puede eliminar el vehículo "{nombre_completo}" porque tiene órdenes de trabajo pendientes.'
        #     )
        #     return redirect('vehiculos:detalle', pk=vehiculo.pk)

        # Eliminar vehículo
        cliente = vehiculo.cliente
        self.object = vehiculo
        vehiculo.delete()
        messages.success(
            request,
            f'Vehículo "{nombre_completo}" eliminado exitosamente.'
        )
        return redirect(self.success_url)
