from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Cita
from .forms import CitaForm, CambiarEstadoCitaForm
from apps.usuarios.mixins import AdminORecepcionistaMixin, UsuarioActivoMixin


# ==================== VISTAS DE GESTIÓN DE CITAS ====================

class ListarCitasView(UsuarioActivoMixin, ListView):
    """
    Vista para listar todas las citas.
    Accesible por cualquier usuario autenticado y activo.
    Incluye filtros por estado, mecánico, fecha y búsqueda.
    """
    model = Cita
    template_name = 'citas/listar_citas.html'
    context_object_name = 'citas'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Usar select_related para optimizar consultas
        queryset = queryset.select_related('cliente', 'vehiculo', 'mecanico_asignado')

        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtro por mecánico
        mecanico = self.request.GET.get('mecanico')
        if mecanico:
            queryset = queryset.filter(mecanico_asignado_id=mecanico)

        # Filtro por fecha (hoy, semana, mes)
        periodo = self.request.GET.get('periodo')
        if periodo:
            hoy = timezone.now().date()
            if periodo == 'hoy':
                queryset = queryset.filter(fecha_hora__date=hoy)
            elif periodo == 'semana':
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                fin_semana = inicio_semana + timedelta(days=6)
                queryset = queryset.filter(fecha_hora__date__range=[inicio_semana, fin_semana])
            elif periodo == 'mes':
                queryset = queryset.filter(
                    fecha_hora__year=hoy.year,
                    fecha_hora__month=hoy.month
                )

        # Filtro por rango de fechas personalizado
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_desde and fecha_hasta:
            queryset = queryset.filter(fecha_hora__date__range=[fecha_desde, fecha_hasta])

        # Búsqueda por cliente, vehículo o descripción
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=busqueda) |
                Q(cliente__apellidos__icontains=busqueda) |
                Q(cliente__dni__icontains=busqueda) |
                Q(vehiculo__matricula__icontains=busqueda) |
                Q(vehiculo__marca__icontains=busqueda) |
                Q(vehiculo__modelo__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )

        # Ordenación por columnas
        orden = self.request.GET.get('orden', '-fecha_hora')
        direccion = self.request.GET.get('direccion', '')

        # Validar campos permitidos para ordenar
        campos_validos = ['fecha_hora', 'cliente__apellidos', 'vehiculo__matricula',
                         'mecanico_asignado__last_name', 'tipo_servicio', 'estado',
                         'fecha_creacion']

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
            queryset = queryset.order_by('-fecha_hora')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['mecanico_filtro'] = self.request.GET.get('mecanico', '')
        context['periodo_filtro'] = self.request.GET.get('periodo', '')
        context['fecha_desde'] = self.request.GET.get('fecha_desde', '')
        context['fecha_hasta'] = self.request.GET.get('fecha_hasta', '')
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['orden'] = self.request.GET.get('orden', '-fecha_hora')
        context['direccion'] = self.request.GET.get('direccion', '')

        # Opciones para filtros
        context['estados'] = Cita.EstadoCita.choices

        # Obtener mecánicos activos para el filtro
        from apps.usuarios.models import Usuario
        context['mecanicos'] = Usuario.objects.filter(
            rol=Usuario.Rol.MECANICO,
            activo=True
        ).order_by('first_name', 'last_name')

        return context


class CrearCitaView(AdminORecepcionistaMixin, CreateView):
    """
    Vista para crear una nueva cita.
    Accesible por administradores y recepcionistas.
    """
    model = Cita
    form_class = CitaForm
    template_name = 'citas/crear_cita.html'
    success_url = reverse_lazy('citas:listar')

    def get_initial(self):
        """Pre-cargar cliente o vehículo si se pasan como parámetros"""
        initial = super().get_initial()
        cliente_id = self.request.GET.get('cliente')
        vehiculo_id = self.request.GET.get('vehiculo')

        if cliente_id:
            initial['cliente'] = cliente_id
        if vehiculo_id:
            initial['vehiculo'] = vehiculo_id
            # Si hay vehículo, cargar su cliente automáticamente
            from apps.vehiculos.models import Vehiculo
            vehiculo = Vehiculo.objects.filter(pk=vehiculo_id).first()
            if vehiculo:
                initial['cliente'] = vehiculo.cliente_id

        return initial

    def get_form_kwargs(self):
        """Pasar el usuario actual al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Asignar el usuario que crea la cita
        form.instance.usuario_creacion = self.request.user
        cita = form.save()
        messages.success(
            self.request,
            f'Cita #{cita.pk} creada exitosamente para {cita.cliente.get_nombre_completo()} '
            f'el {cita.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al crear la cita. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class EditarCitaView(AdminORecepcionistaMixin, UpdateView):
    """
    Vista para editar una cita existente.
    Accesible por administradores y recepcionistas.
    """
    model = Cita
    form_class = CitaForm
    template_name = 'citas/editar_cita.html'
    success_url = reverse_lazy('citas:listar')

    def get_form_kwargs(self):
        """Pasar el usuario actual al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        cita = form.save()
        messages.success(
            self.request,
            f'Cita #{cita.pk} actualizada exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar la cita. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class DetalleCitaView(UsuarioActivoMixin, DetailView):
    """
    Vista para ver el detalle completo de una cita.
    Accesible por cualquier usuario autenticado y activo.
    """
    model = Cita
    template_name = 'citas/detalle_cita.html'
    context_object_name = 'cita'

    def get_queryset(self):
        """Optimizar con select_related"""
        return super().get_queryset().select_related(
            'cliente',
            'vehiculo',
            'vehiculo__cliente',
            'mecanico_asignado',
            'usuario_creacion'
        )


class EliminarCitaView(AdminORecepcionistaMixin, DeleteView):
    """
    Vista para eliminar una cita.
    Accesible por administradores y recepcionistas.
    """
    model = Cita
    template_name = 'citas/eliminar_cita.html'
    success_url = reverse_lazy('citas:listar')

    def post(self, request, *args, **kwargs):
        cita = self.get_object()
        cita_info = f"Cita #{cita.pk} - {cita.cliente.get_nombre_completo()} ({cita.fecha_hora.strftime('%d/%m/%Y %H:%M')})"

        # Verificar si la cita puede ser eliminada
        if cita.estado in [Cita.EstadoCita.EN_PROCESO, Cita.EstadoCita.COMPLETADA]:
            messages.error(
                request,
                f'No se puede eliminar la cita porque ya está {cita.get_estado_display().lower()}. '
                f'Considere cancelarla en su lugar.'
            )
            return redirect('citas:detalle', pk=cita.pk)

        # Eliminar cita
        self.object = cita
        cita.delete()
        messages.success(
            request,
            f'Cita eliminada exitosamente: {cita_info}.'
        )
        return redirect(self.success_url)


class CalendarioCitasView(UsuarioActivoMixin, TemplateView):
    """
    Vista para mostrar el calendario de citas.
    Muestra las citas en formato de calendario mensual/semanal/diario.
    """
    template_name = 'citas/calendario_citas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el mes y año actual o desde parámetros
        hoy = timezone.now().date()
        mes = int(self.request.GET.get('mes', hoy.month))
        anio = int(self.request.GET.get('anio', hoy.year))

        # Calcular primer y último día del mes
        primer_dia = datetime(anio, mes, 1).date()
        if mes == 12:
            ultimo_dia = datetime(anio + 1, 1, 1).date() - timedelta(days=1)
        else:
            ultimo_dia = datetime(anio, mes + 1, 1).date() - timedelta(days=1)

        # Obtener todas las citas del mes
        citas = Cita.objects.filter(
            fecha_hora__date__gte=primer_dia,
            fecha_hora__date__lte=ultimo_dia
        ).select_related('cliente', 'vehiculo', 'mecanico_asignado').order_by('fecha_hora')

        # Filtrar por mecánico si se especifica
        mecanico_id = self.request.GET.get('mecanico')
        if mecanico_id:
            citas = citas.filter(mecanico_asignado_id=mecanico_id)

        # Calcular mes anterior y siguiente para navegación
        if mes == 1:
            mes_anterior = 12
            anio_anterior = anio - 1
        else:
            mes_anterior = mes - 1
            anio_anterior = anio

        if mes == 12:
            mes_siguiente = 1
            anio_siguiente = anio + 1
        else:
            mes_siguiente = mes + 1
            anio_siguiente = anio

        context['citas'] = citas
        context['mes'] = mes
        context['anio'] = anio
        context['hoy'] = hoy
        context['primer_dia'] = primer_dia
        context['ultimo_dia'] = ultimo_dia
        context['mes_anterior'] = mes_anterior
        context['anio_anterior'] = anio_anterior
        context['mes_siguiente'] = mes_siguiente
        context['anio_siguiente'] = anio_siguiente

        # Obtener mecánicos para filtro
        from apps.usuarios.models import Usuario
        context['mecanicos'] = Usuario.objects.filter(
            rol=Usuario.Rol.MECANICO,
            activo=True
        ).order_by('first_name', 'last_name')
        context['mecanico_filtro'] = mecanico_id

        return context


# ==================== VISTAS AJAX ====================

def cambiar_estado_cita(request, pk):
    """
    Vista para cambiar el estado de una cita vía AJAX.
    Accesible por usuarios con permisos (admin, recepcionista).
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)

    if not (request.user.es_admin or request.user.es_recepcionista):
        return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)

    if request.method == 'POST':
        cita = get_object_or_404(Cita, pk=pk)
        nuevo_estado = request.POST.get('estado')

        # Validar que el estado sea válido
        estados_validos = [choice[0] for choice in Cita.EstadoCita.choices]
        if nuevo_estado not in estados_validos:
            return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)

        # Actualizar estado
        estado_anterior = cita.get_estado_display()
        cita.estado = nuevo_estado
        cita.save()

        messages.success(
            request,
            f'Estado de cita #{cita.pk} actualizado de "{estado_anterior}" a "{cita.get_estado_display()}".'
        )

        return JsonResponse({
            'success': True,
            'nuevo_estado': cita.get_estado_display(),
            'badge_class': cita.get_estado_badge_class()
        })

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


def obtener_citas_json(request):
    """
    Vista para obtener citas en formato JSON (para el calendario).
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    # Obtener parámetros de fecha
    fecha_desde = request.GET.get('start')
    fecha_hasta = request.GET.get('end')

    if not fecha_desde or not fecha_hasta:
        return JsonResponse({'error': 'Parámetros de fecha requeridos'}, status=400)

    # Convertir a datetime
    try:
        fecha_desde = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
        fecha_hasta = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

    # Obtener citas en el rango de fechas
    citas = Cita.objects.filter(
        fecha_hora__range=[fecha_desde, fecha_hasta]
    ).select_related('cliente', 'vehiculo', 'mecanico_asignado')

    # Filtrar por mecánico si se especifica
    mecanico_id = request.GET.get('mecanico')
    if mecanico_id:
        citas = citas.filter(mecanico_asignado_id=mecanico_id)

    # Convertir a formato JSON para FullCalendar
    eventos = []
    for cita in citas:
        eventos.append({
            'id': cita.pk,
            'title': f"{cita.cliente.get_nombre_completo()} - {cita.get_tipo_servicio_display()}",
            'start': cita.fecha_hora.isoformat(),
            'end': cita.hora_fin.isoformat(),
            'color': cita.get_estado_color(),
            'url': f"/citas/{cita.pk}/",
            'extendedProps': {
                'cliente': cita.cliente.get_nombre_completo(),
                'vehiculo': f"{cita.vehiculo.marca} {cita.vehiculo.modelo} ({cita.vehiculo.matricula})",
                'mecanico': cita.mecanico_asignado.get_full_name() if cita.mecanico_asignado else 'Sin asignar',
                'estado': cita.get_estado_display(),
                'descripcion': cita.descripcion[:100]
            }
        })

    return JsonResponse(eventos, safe=False)
