from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone

from .models import Factura, LineaFactura
from .forms import FacturaForm, LineaFacturaFormSet, RegistrarPagoForm
from apps.ordenes.models import OrdenTrabajo
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE FACTURAS ====================

class ListarFacturasView(UsuarioActivoMixin, ListView):
    """Vista para listar facturas"""
    model = Factura
    template_name = 'facturacion/listar_facturas.html'
    context_object_name = 'facturas'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'orden_trabajo', 'usuario_creador')

        # Filtros
        cliente = self.request.GET.get('cliente')
        if cliente:
            queryset = queryset.filter(cliente_id=cliente)

        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(numero_factura__icontains=busqueda) |
                Q(cliente__nombre__icontains=busqueda) |
                Q(cliente__apellidos__icontains=busqueda)
            )

        # Filtro de vencidas
        if self.request.GET.get('vencidas'):
            queryset = queryset.filter(
                fecha_vencimiento__lt=timezone.now().date(),
                estado__in=[Factura.EstadoFactura.PENDIENTE, Factura.EstadoFactura.PAGADA_PARCIAL]
            )

        return queryset.order_by('-fecha_emision', '-numero_factura')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.clientes.models import Cliente
        context['clientes'] = Cliente.objects.filter(activo=True)
        context['estados'] = Factura.EstadoFactura.choices
        return context


class CrearFacturaView(AdminORecepcionistaMixin, CreateView):
    """Vista para crear factura"""
    model = Factura
    form_class = FacturaForm
    template_name = 'facturacion/crear_factura.html'
    success_url = reverse_lazy('facturacion:listar')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LineaFacturaFormSet(self.request.POST)
        else:
            context['formset'] = LineaFacturaFormSet()
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            factura = form.save(commit=False)
            factura.usuario_creador = self.request.user
            factura.save()

            formset.instance = factura
            formset.save()

            # Calcular totales
            factura.calcular_totales()

            messages.success(
                self.request,
                f'Factura "{factura.numero_factura}" creada exitosamente.'
            )
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class EditarFacturaView(AdminORecepcionistaMixin, UpdateView):
    """Vista para editar factura"""
    model = Factura
    form_class = FacturaForm
    template_name = 'facturacion/editar_factura.html'

    def get_success_url(self):
        return reverse_lazy('facturacion:detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LineaFacturaFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = LineaFacturaFormSet(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            factura = form.save()
            formset.save()

            # Recalcular totales
            factura.calcular_totales()

            messages.success(self.request, f'Factura "{factura.numero_factura}" actualizada.')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DetalleFacturaView(UsuarioActivoMixin, DetailView):
    """Vista para ver detalle de factura"""
    model = Factura
    template_name = 'facturacion/detalle_factura.html'
    context_object_name = 'factura'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lineas'] = self.object.lineas.all()
        return context


class EliminarFacturaView(AdminORecepcionistaMixin, DeleteView):
    """Vista para eliminar factura"""
    model = Factura
    template_name = 'facturacion/eliminar_factura.html'
    success_url = reverse_lazy('facturacion:listar')

    def post(self, request, *args, **kwargs):
        factura = self.get_object()

        if factura.esta_pagada:
            messages.error(request, 'No se pueden eliminar facturas pagadas.')
            return redirect('facturacion:detalle', pk=factura.pk)

        numero = factura.numero_factura
        factura.delete()
        messages.success(request, f'Factura "{numero}" eliminada.')
        return redirect(self.success_url)


# ==================== VISTA PARA GENERAR DESDE ORDEN ====================

@transaction.atomic
def generar_desde_orden_view(request, orden_pk):
    """Vista para generar factura desde una orden de trabajo"""
    orden = get_object_or_404(OrdenTrabajo, pk=orden_pk)

    # Verificar que la orden no tenga ya una factura
    if orden.facturas.exists():
        messages.warning(request, 'Esta orden ya tiene facturas asociadas.')
        return redirect('ordenes:detalle', pk=orden.pk)

    # Crear factura
    factura = Factura.objects.create(
        cliente=orden.cliente,
        orden_trabajo=orden,
        fecha_emision=timezone.now().date(),
        usuario_creador=request.user
    )

    # Crear líneas desde la orden (mano de obra)
    for linea_trabajo in orden.lineas_trabajo.all():
        LineaFactura.objects.create(
            factura=factura,
            descripcion=linea_trabajo.descripcion,
            cantidad=linea_trabajo.horas,
            precio_unitario=linea_trabajo.precio_hora,
            descuento=Decimal('0.00'),
            iva=Decimal('21.00')
        )

    # Crear líneas desde la orden (repuestos)
    for linea_repuesto in orden.lineas_repuesto.all():
        LineaFactura.objects.create(
            factura=factura,
            descripcion=linea_repuesto.descripcion,
            cantidad=linea_repuesto.cantidad,
            precio_unitario=linea_repuesto.precio_unitario,
            descuento=linea_repuesto.descuento,
            iva=Decimal('21.00')
        )

    # Calcular totales
    factura.calcular_totales()

    messages.success(
        request,
        f'Factura "{factura.numero_factura}" generada desde orden "{orden.numero_orden}".'
    )
    return redirect('facturacion:detalle', pk=factura.pk)


# ==================== VISTA PARA REGISTRAR PAGO ====================

@transaction.atomic
def registrar_pago_view(request, pk):
    """Vista para registrar un pago en una factura"""
    factura = get_object_or_404(Factura, pk=pk)

    if factura.esta_pagada:
        messages.warning(request, 'Esta factura ya está completamente pagada.')
        return redirect('facturacion:detalle', pk=factura.pk)

    if request.method == 'POST':
        form = RegistrarPagoForm(request.POST, factura=factura)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            metodo = form.cleaned_data['metodo_pago']
            fecha = form.cleaned_data['fecha_pago']

            try:
                factura.registrar_pago(monto, metodo, fecha)
                messages.success(
                    request,
                    f'Pago de €{monto} registrado correctamente. '
                    f'Saldo pendiente: €{factura.saldo_pendiente}'
                )
                return redirect('facturacion:detalle', pk=factura.pk)
            except Exception as e:
                messages.error(request, f'Error al registrar pago: {str(e)}')
    else:
        form = RegistrarPagoForm(factura=factura)

    context = {
        'form': form,
        'factura': factura,
    }
    return render(request, 'facturacion/registrar_pago.html', context)
