from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import JsonResponse

from .models import OrdenTrabajo, LineaTrabajo, LineaRepuesto
from .forms import OrdenTrabajoForm, LineaTrabajoForm, LineaRepuestoForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE GESTIÓN DE ÓRDENES ====================

class ListarOrdenesView(UsuarioActivoMixin, ListView):
    """
    Vista para listar todas las órdenes de trabajo.
    Incluye filtros por estado, mecánico, cliente y búsqueda.
    """
    model = OrdenTrabajo
    template_name = 'ordenes/listar_ordenes.html'
    context_object_name = 'ordenes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('cliente', 'vehiculo', 'mecanico_asignado', 'cita')

        # Filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        mecanico = self.request.GET.get('mecanico')
        if mecanico:
            queryset = queryset.filter(mecanico_asignado_id=mecanico)

        prioridad = self.request.GET.get('prioridad')
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)

        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(numero_orden__icontains=busqueda) |
                Q(cliente__nombre__icontains=busqueda) |
                Q(cliente__apellidos__icontains=busqueda) |
                Q(vehiculo__matricula__icontains=busqueda)
            )

        # Ordenación
        orden = self.request.GET.get('orden', '-fecha_apertura')
        queryset = queryset.order_by(orden)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = OrdenTrabajo.EstadoOrden.choices
        context['prioridades'] = OrdenTrabajo.Prioridad.choices

        from apps.usuarios.models import Usuario
        context['mecanicos'] = Usuario.objects.filter(
            rol=Usuario.Rol.MECANICO, activo=True
        ).order_by('first_name', 'last_name')

        return context


class CrearOrdenView(AdminORecepcionistaMixin, CreateView):
    """Vista para crear una nueva orden de trabajo"""
    model = OrdenTrabajo
    form_class = OrdenTrabajoForm
    template_name = 'ordenes/crear_orden.html'

    def get_success_url(self):
        return reverse('ordenes:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.usuario_creacion = self.request.user
        orden = form.save()
        messages.success(self.request, f'Orden #{orden.numero_orden} creada exitosamente.')
        return super().form_valid(form)


class EditarOrdenView(AdminORecepcionistaMixin, UpdateView):
    """Vista para editar una orden de trabajo"""
    model = OrdenTrabajo
    form_class = OrdenTrabajoForm
    template_name = 'ordenes/editar_orden.html'

    def get_success_url(self):
        return reverse('ordenes:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        orden = form.save()
        messages.success(self.request, f'Orden #{orden.numero_orden} actualizada.')
        return super().form_valid(form)


class DetalleOrdenView(UsuarioActivoMixin, DetailView):
    """Vista para ver el detalle de una orden de trabajo"""
    model = OrdenTrabajo
    template_name = 'ordenes/detalle_orden.html'
    context_object_name = 'orden'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'cliente', 'vehiculo', 'mecanico_asignado', 'cita'
        ).prefetch_related('lineas_trabajo', 'lineas_repuesto')


class EliminarOrdenView(AdminORecepcionistaMixin, DeleteView):
    """Vista para eliminar una orden de trabajo"""
    model = OrdenTrabajo
    template_name = 'ordenes/eliminar_orden.html'
    success_url = reverse_lazy('ordenes:listar')

    def post(self, request, *args, **kwargs):
        orden = self.get_object()

        if orden.estado == OrdenTrabajo.EstadoOrden.COMPLETADA:
            messages.error(request, f'No se puede eliminar la orden #{orden.numero_orden} porque está completada.')
            return redirect('ordenes:detalle', pk=orden.pk)

        numero_orden = orden.numero_orden
        self.object = orden
        orden.delete()
        messages.success(request, f'Orden #{numero_orden} eliminada.')
        return redirect(self.success_url)


# ==================== VISTAS AJAX PARA LÍNEAS ====================

def agregar_linea_trabajo(request, pk):
    """Agregar línea de trabajo"""
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, pk=pk)
        if not orden.puede_editar:
            return JsonResponse({'success': False, 'error': 'Orden no editable'}, status=403)

        form = LineaTrabajoForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=False)
            linea.orden = orden
            linea.save()
            return JsonResponse({'success': True, 'linea_id': linea.id})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False}, status=405)


def eliminar_linea_trabajo(request, pk, linea_id):
    """Eliminar línea de trabajo"""
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, pk=pk)
        linea = get_object_or_404(LineaTrabajo, pk=linea_id, orden=orden)

        if not orden.puede_editar:
            return JsonResponse({'success': False, 'error': 'Orden no editable'}, status=403)

        linea.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)


def agregar_linea_repuesto(request, pk):
    """Agregar línea de repuesto"""
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, pk=pk)
        if not orden.puede_editar:
            return JsonResponse({'success': False, 'error': 'Orden no editable'}, status=403)

        form = LineaRepuestoForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=False)
            linea.orden = orden
            linea.save()
            return JsonResponse({'success': True, 'linea_id': linea.id})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False}, status=405)


def eliminar_linea_repuesto(request, pk, linea_id):
    """Eliminar línea de repuesto"""
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, pk=pk)
        linea = get_object_or_404(LineaRepuesto, pk=linea_id, orden=orden)

        if not orden.puede_editar:
            return JsonResponse({'success': False, 'error': 'Orden no editable'}, status=403)

        linea.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)
