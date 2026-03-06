from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.db import transaction

from .models import Proveedor, OrdenCompra, LineaCompra
from .forms import ProveedorForm, OrdenCompraForm, LineaCompraFormSet, RecibirMercanciaForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE PROVEEDORES ====================

class ListarProveedoresView(UsuarioActivoMixin, ListView):
    """Vista para listar proveedores"""
    model = Proveedor
    template_name = 'compras/listar_proveedores.html'
    context_object_name = 'proveedores'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Búsqueda
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(cif__icontains=busqueda) |
                Q(email__icontains=busqueda) |
                Q(telefono__icontains=busqueda)
            )

        # Filtro de activos
        if self.request.GET.get('activo'):
            queryset = queryset.filter(activo=True)

        return queryset.order_by('nombre')


class CrearProveedorView(AdminORecepcionistaMixin, CreateView):
    """Vista para crear proveedor"""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'compras/crear_proveedor.html'
    success_url = reverse_lazy('compras:listar_proveedores')

    def form_valid(self, form):
        proveedor = form.save()
        messages.success(self.request, f'Proveedor "{proveedor.nombre}" creado exitosamente.')
        return super().form_valid(form)


class EditarProveedorView(AdminORecepcionistaMixin, UpdateView):
    """Vista para editar proveedor"""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'compras/editar_proveedor.html'
    success_url = reverse_lazy('compras:listar_proveedores')

    def form_valid(self, form):
        proveedor = form.save()
        messages.success(self.request, f'Proveedor "{proveedor.nombre}" actualizado.')
        return super().form_valid(form)


class DetalleProveedorView(UsuarioActivoMixin, DetailView):
    """Vista para ver detalle de proveedor"""
    model = Proveedor
    template_name = 'compras/detalle_proveedor.html'
    context_object_name = 'proveedor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordenes_recientes'] = self.object.ordenes_compra.all()[:10]
        return context


class EliminarProveedorView(AdminORecepcionistaMixin, DeleteView):
    """Vista para eliminar proveedor"""
    model = Proveedor
    template_name = 'compras/eliminar_proveedor.html'
    success_url = reverse_lazy('compras:listar_proveedores')

    def post(self, request, *args, **kwargs):
        proveedor = self.get_object()
        nombre = proveedor.nombre
        proveedor.delete()
        messages.success(request, f'Proveedor "{nombre}" eliminado.')
        return redirect(self.success_url)


# ==================== VISTAS DE ÓRDENES DE COMPRA ====================

class ListarOrdenesCompraView(UsuarioActivoMixin, ListView):
    """Vista para listar órdenes de compra"""
    model = OrdenCompra
    template_name = 'compras/listar_ordenes.html'
    context_object_name = 'ordenes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('proveedor', 'usuario_creador')

        # Filtros
        proveedor = self.request.GET.get('proveedor')
        if proveedor:
            queryset = queryset.filter(proveedor_id=proveedor)

        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(numero_orden__icontains=busqueda) |
                Q(proveedor__nombre__icontains=busqueda)
            )

        return queryset.order_by('-fecha_orden', '-numero_orden')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.filter(activo=True)
        context['estados'] = OrdenCompra.EstadoOrden.choices
        return context


class CrearOrdenCompraView(AdminORecepcionistaMixin, CreateView):
    """Vista para crear orden de compra"""
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'compras/crear_orden.html'
    success_url = reverse_lazy('compras:listar_ordenes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LineaCompraFormSet(self.request.POST)
        else:
            context['formset'] = LineaCompraFormSet()
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            orden = form.save(commit=False)
            orden.usuario_creador = self.request.user
            orden.save()

            formset.instance = orden
            formset.save()

            # Calcular totales
            orden.calcular_totales()

            messages.success(
                self.request,
                f'Orden de compra "{orden.numero_orden}" creada exitosamente.'
            )
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class EditarOrdenCompraView(AdminORecepcionistaMixin, UpdateView):
    """Vista para editar orden de compra"""
    model = OrdenCompra
    form_class = OrdenCompraForm
    template_name = 'compras/editar_orden.html'

    def get_success_url(self):
        return reverse_lazy('compras:detalle_orden', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LineaCompraFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = LineaCompraFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if not self.object.puede_editar:
            messages.error(self.request, 'Esta orden no puede ser editada.')
            return redirect(self.get_success_url())

        if formset.is_valid():
            orden = form.save()
            formset.save()

            # Recalcular totales
            orden.calcular_totales()

            messages.success(self.request, f'Orden "{orden.numero_orden}" actualizada.')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DetalleOrdenCompraView(UsuarioActivoMixin, DetailView):
    """Vista para ver detalle de orden de compra"""
    model = OrdenCompra
    template_name = 'compras/detalle_orden.html'
    context_object_name = 'orden'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lineas'] = self.object.lineas.select_related('repuesto')
        return context


class EliminarOrdenCompraView(AdminORecepcionistaMixin, DeleteView):
    """Vista para eliminar orden de compra"""
    model = OrdenCompra
    template_name = 'compras/eliminar_orden.html'
    success_url = reverse_lazy('compras:listar_ordenes')

    def post(self, request, *args, **kwargs):
        orden = self.get_object()

        if orden.estado != OrdenCompra.EstadoOrden.BORRADOR:
            messages.error(request, 'Solo se pueden eliminar órdenes en estado Borrador.')
            return redirect('compras:detalle_orden', pk=orden.pk)

        numero = orden.numero_orden
        orden.delete()
        messages.success(request, f'Orden "{numero}" eliminada.')
        return redirect(self.success_url)


# ==================== VISTA PARA RECIBIR MERCANCÍA ====================

@transaction.atomic
def recibir_mercancia_view(request, pk):
    """Vista para recibir mercancía de una línea de compra"""
    linea = get_object_or_404(LineaCompra, pk=pk)

    if linea.esta_completa:
        messages.warning(request, 'Esta línea ya está completamente recibida.')
        return redirect('compras:detalle_orden', pk=linea.orden_compra.pk)

    if request.method == 'POST':
        form = RecibirMercanciaForm(request.POST, linea_compra=linea)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']

            try:
                linea.recibir_mercancia(cantidad, request.user)
                messages.success(
                    request,
                    f'Recibidas {cantidad} unidades de {linea.repuesto.nombre}. '
                    f'Stock actualizado correctamente.'
                )
                return redirect('compras:detalle_orden', pk=linea.orden_compra.pk)
            except Exception as e:
                messages.error(request, f'Error al recibir mercancía: {str(e)}')
    else:
        form = RecibirMercanciaForm(linea_compra=linea)

    context = {
        'form': form,
        'linea': linea,
        'orden': linea.orden_compra,
    }
    return render(request, 'compras/recibir_mercancia.html', context)
