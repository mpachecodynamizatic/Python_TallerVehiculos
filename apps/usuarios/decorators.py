from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.

    Args:
        *roles_permitidos: Roles que pueden acceder a la vista (ej: 'ADMIN', 'MECANICO')

    Uso:
        @rol_requerido('ADMIN', 'MECANICO')
        def mi_vista(request):
            pass

    Raises:
        PermissionDenied: Si el usuario no tiene el rol requerido
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Verificar si el usuario está activo
            if not request.user.activo:
                messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
                return redirect('login')

            # Superusuarios siempre tienen acceso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Verificar si el usuario tiene uno de los roles permitidos
            if request.user.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)

            # Si no tiene permiso, lanzar excepción
            raise PermissionDenied("No tienes permisos para acceder a esta página.")

        return wrapper
    return decorator


def solo_admin(view_func):
    """
    Decorador para vistas que solo pueden acceder administradores.

    Uso:
        @solo_admin
        def vista_solo_admin(request):
            pass
    """
    return rol_requerido('ADMIN')(view_func)


def solo_mecanico(view_func):
    """
    Decorador para vistas que solo pueden acceder mecánicos.

    Uso:
        @solo_mecanico
        def vista_solo_mecanico(request):
            pass
    """
    return rol_requerido('MECANICO')(view_func)


def solo_recepcionista(view_func):
    """
    Decorador para vistas que solo pueden acceder recepcionistas.

    Uso:
        @solo_recepcionista
        def vista_solo_recepcionista(request):
            pass
    """
    return rol_requerido('RECEPCIONISTA')(view_func)


def admin_o_recepcionista(view_func):
    """
    Decorador para vistas que pueden acceder administradores o recepcionistas.

    Uso:
        @admin_o_recepcionista
        def vista_admin_recepcion(request):
            pass
    """
    return rol_requerido('ADMIN', 'RECEPCIONISTA')(view_func)


def admin_o_mecanico(view_func):
    """
    Decorador para vistas que pueden acceder administradores o mecánicos.

    Uso:
        @admin_o_mecanico
        def vista_admin_mecanico(request):
            pass
    """
    return rol_requerido('ADMIN', 'MECANICO')(view_func)


def usuario_activo_requerido(view_func):
    """
    Decorador que solo verifica que el usuario esté activo (sin verificar rol).

    Uso:
        @usuario_activo_requerido
        def mi_vista(request):
            pass
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.activo:
            messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper
