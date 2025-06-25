from django.shortcuts import redirect

def rol_requerido(rol):
    def decorador(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.is_authenticated and request.user.rol and request.user.rol.nombre == rol:
                return view_func(request, *args, **kwargs)
            return redirect('licencia_expirada')  
        return wrapper
    return decorador
