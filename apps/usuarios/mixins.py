from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


class RolRequeridoMixin(LoginRequiredMixin):
    """
    Mixin que verifica el rol del usuario para vistas basadas en clases (CBVs).

    Atributos:
        roles_permitidos: Lista de roles que pueden acceder a la vista

    Uso:
        class MiVista(RolRequeridoMixin, ListView):
            roles_permitidos = ['ADMIN', 'MECANICO']
            model = MiModelo
    """
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        # Verificar autenticación primero (heredado de LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Verificar si el usuario está activo
        if not request.user.activo:
            messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
            return redirect('login')

        # Superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Verificar rol del usuario
        if request.user.rol not in self.roles_permitidos:
            raise PermissionDenied("No tienes permisos para acceder a esta página.")

        return super().dispatch(request, *args, **kwargs)


class SoloAdminMixin(RolRequeridoMixin):
    """
    Mixin para vistas que solo pueden acceder administradores.

    Uso:
        class MiVista(SoloAdminMixin, ListView):
            model = MiModelo
    """
    roles_permitidos = ['ADMIN']


class SoloMecanicoMixin(RolRequeridoMixin):
    """
    Mixin para vistas que solo pueden acceder mecánicos.

    Uso:
        class MiVista(SoloMecanicoMixin, ListView):
            model = MiModelo
    """
    roles_permitidos = ['MECANICO']


class SoloRecepcionistaMixin(RolRequeridoMixin):
    """
    Mixin para vistas que solo pueden acceder recepcionistas.

    Uso:
        class MiVista(SoloRecepcionistaMixin, ListView):
            model = MiModelo
    """
    roles_permitidos = ['RECEPCIONISTA']


class AdminORecepcionistaMixin(RolRequeridoMixin):
    """
    Mixin para vistas que pueden acceder administradores o recepcionistas.

    Uso:
        class MiVista(AdminORecepcionistaMixin, ListView):
            model = MiModelo
    """
    roles_permitidos = ['ADMIN', 'RECEPCIONISTA']


class AdminOMecanicoMixin(RolRequeridoMixin):
    """
    Mixin para vistas que pueden acceder administradores o mecánicos.

    Uso:
        class MiVista(AdminOMecanicoMixin, ListView):
            model = MiModelo
    """
    roles_permitidos = ['ADMIN', 'MECANICO']


class UsuarioActivoMixin(LoginRequiredMixin):
    """
    Mixin que solo verifica que el usuario esté activo (sin verificar rol).

    Uso:
        class MiVista(UsuarioActivoMixin, DetailView):
            model = MiModelo
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.activo:
            messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)
