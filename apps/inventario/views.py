from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, F

from .models import Repuesto, CategoriaRepuesto, MovimientoInventario
from .forms import RepuestoForm, CategoriaRepuestoForm, AjusteStockForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE REPUESTOS ====================

class ListarRepuestosView(UsuarioActivoMixin, ListView):
    """Vista para listar repuestos"""
    model = Repuesto
    template_name = 'inventario/listar_repuestos.html'
    context_object_name = 'repuestos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('categoria')

        # Filtros
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda) |
                Q(nombre__icontains=busqueda) |
                Q(marca__icontains=busqueda)
            )

        # Filtro de stock bajo
        if self.request.GET.get('stock_bajo'):
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))

        return queryset.order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaRepuesto.objects.filter(activo=True)
        return context


class CrearRepuestoView(AdminORecepcionistaMixin, CreateView):
    """Vista para crear repuesto"""
    model = Repuesto
    form_class = RepuestoForm
    template_name = 'inventario/crear_repuesto.html'
    success_url = reverse_lazy('inventario:listar')

    def form_valid(self, form):
        repuesto = form.save()
        messages.success(self.request, f'Repuesto "{repuesto.nombre}" creado exitosamente.')
        return super().form_valid(form)


class EditarRepuestoView(AdminORecepcionistaMixin, UpdateView):
    """Vista para editar repuesto"""
    model = Repuesto
    form_class = RepuestoForm
    template_name = 'inventario/editar_repuesto.html'
    success_url = reverse_lazy('inventario:listar')

    def form_valid(self, form):
        repuesto = form.save()
        messages.success(self.request, f'Repuesto "{repuesto.nombre}" actualizado.')
        return super().form_valid(form)


class DetalleRepuestoView(UsuarioActivoMixin, DetailView):
    """Vista para ver detalle de repuesto"""
    model = Repuesto
    template_name = 'inventario/detalle_repuesto.html'
    context_object_name = 'repuesto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all()[:20]
        return context


class EliminarRepuestoView(AdminORecepcionistaMixin, DeleteView):
    """Vista para eliminar repuesto"""
    model = Repuesto
    template_name = 'inventario/eliminar_repuesto.html'
    success_url = reverse_lazy('inventario:listar')

    def post(self, request, *args, **kwargs):
        repuesto = self.get_object()
        nombre = repuesto.nombre
        repuesto.delete()
        messages.success(request, f'Repuesto "{nombre}" eliminado.')
        return redirect(self.success_url)
