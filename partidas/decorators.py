from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def rol_requerido(nombre_rol):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Si no está autenticado, redirigir a login
            if not request.user.is_authenticated:
                from django.urls import reverse
                return redirect(reverse('login'))
            # Si es superuser, permitir
            if request.user.is_superuser: 
                return view_func(request, *args, **kwargs)
            # Si tiene el rol requerido, permitir
            if request.user.rol and request.user.rol.nombre == nombre_rol:
                return view_func(request, *args, **kwargs)
            # Si no, denegar
            raise PermissionDenied
        return _wrapped_view
    return decorator
