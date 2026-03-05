from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q

from .models import Usuario
from .forms import UsuarioCreationForm, UsuarioUpdateForm, PerfilUsuarioForm, CambiarPasswordForm
from .mixins import SoloAdminMixin, UsuarioActivoMixin
from .decorators import solo_admin


# ==================== VISTAS DE GESTIÓN DE USUARIOS (SOLO ADMIN) ====================

class ListarUsuariosView(SoloAdminMixin, ListView):
    """
    Vista para listar todos los usuarios del sistema.
    Solo accesible por administradores.
    """
    model = Usuario
    template_name = 'usuarios/listar_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por rol
        rol = self.request.GET.get('rol')
        if rol and rol in ['ADMIN', 'MECANICO', 'RECEPCIONISTA']:
            queryset = queryset.filter(rol=rol)

        # Filtro por estado activo
        estado = self.request.GET.get('estado')
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)

        # Búsqueda por nombre, email o username
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(username__icontains=busqueda) |
                Q(first_name__icontains=busqueda) |
                Q(last_name__icontains=busqueda) |
                Q(email__icontains=busqueda)
            )

        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rol_filtro'] = self.request.GET.get('rol', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['busqueda'] = self.request.GET.get('busqueda', '')
        return context


class CrearUsuarioView(SoloAdminMixin, CreateView):
    """
    Vista para crear un nuevo usuario.
    Solo accesible por administradores.
    """
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/crear_usuario.html'
    success_url = reverse_lazy('usuarios:listar')

    def form_valid(self, form):
        usuario = form.save(commit=False)
        usuario.activo = True
        usuario.save()
        messages.success(
            self.request,
            f'Usuario "{usuario.username}" creado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al crear el usuario. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class EditarUsuarioView(SoloAdminMixin, UpdateView):
    """
    Vista para editar un usuario existente.
    Solo accesible por administradores.
    """
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/editar_usuario.html'
    success_url = reverse_lazy('usuarios:listar')

    def form_valid(self, form):
        usuario = form.save()
        messages.success(
            self.request,
            f'Usuario "{usuario.username}" actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar el usuario. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class EliminarUsuarioView(SoloAdminMixin, DeleteView):
    """
    Vista para eliminar un usuario.
    Solo accesible por administradores.
    """
    model = Usuario
    template_name = 'usuarios/eliminar_usuario.html'
    success_url = reverse_lazy('usuarios:listar')

    def post(self, request, *args, **kwargs):
        usuario = self.get_object()
        username = usuario.username

        # Prevenir que un admin se elimine a sí mismo
        if usuario == request.user:
            messages.error(
                request,
                'No puedes eliminar tu propia cuenta.'
            )
            return redirect('usuarios:listar')

        # Eliminar usuario
        self.object = usuario
        usuario.delete()
        messages.success(
            request,
            f'Usuario "{username}" eliminado exitosamente.'
        )
        return redirect(self.success_url)


@solo_admin
def activar_desactivar_usuario(request, pk):
    """
    Vista AJAX para activar/desactivar un usuario.
    Solo accesible por administradores.
    """
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)

        # Prevenir que un admin se desactive a sí mismo
        if usuario == request.user:
            return JsonResponse({
                'success': False,
                'error': 'No puedes desactivar tu propia cuenta.'
            }, status=400)

        # Toggle del estado activo
        usuario.activo = not usuario.activo
        usuario.save(update_fields=['activo'])

        estado_texto = 'activado' if usuario.activo else 'desactivado'
        messages.success(
            request,
            f'Usuario "{usuario.username}" {estado_texto} exitosamente.'
        )

        return JsonResponse({
            'success': True,
            'activo': usuario.activo,
            'message': f'Usuario {estado_texto}'
        })

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


# ==================== VISTAS DE PERFIL DE USUARIO ====================

class PerfilUsuarioView(UsuarioActivoMixin, DetailView):
    """
    Vista para que un usuario vea su propio perfil.
    Accesible por cualquier usuario autenticado y activo.
    """
    model = Usuario
    template_name = 'usuarios/perfil.html'
    context_object_name = 'usuario'

    def get_object(self):
        """Retorna el usuario actual (no permite ver perfiles de otros)"""
        return self.request.user


class EditarPerfilView(UsuarioActivoMixin, UpdateView):
    """
    Vista para que un usuario edite su propio perfil.
    Accesible por cualquier usuario autenticado y activo.
    """
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/editar_perfil.html'
    success_url = reverse_lazy('usuarios:perfil')

    def get_object(self):
        """Retorna el usuario actual (no permite editar perfiles de otros)"""
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request,
            'Tu perfil ha sido actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al actualizar tu perfil. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


class CambiarPasswordView(UsuarioActivoMixin, PasswordChangeView):
    """
    Vista para que un usuario cambie su contraseña.
    Accesible por cualquier usuario autenticado y activo.
    """
    form_class = CambiarPasswordForm
    template_name = 'usuarios/cambiar_password.html'
    success_url = reverse_lazy('usuarios:perfil')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Tu contraseña ha sido cambiada exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Error al cambiar la contraseña. Por favor, verifica los datos ingresados.'
        )
        return super().form_invalid(form)


# ==================== VISTA DE DETALLE DE USUARIO (ADMIN) ====================

class DetalleUsuarioView(SoloAdminMixin, DetailView):
    """
    Vista para ver el detalle completo de un usuario.
    Solo accesible por administradores.
    """
    model = Usuario
    template_name = 'usuarios/detalle_usuario.html'
    context_object_name = 'usuario_detalle'
