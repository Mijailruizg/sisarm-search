from django.core.exceptions import PermissionDenied

def rol_requerido(nombre_rol):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser: 
                return view_func(request, *args, **kwargs)
            if request.user.is_authenticated and request.user.rol and request.user.rol.nombre == nombre_rol:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
