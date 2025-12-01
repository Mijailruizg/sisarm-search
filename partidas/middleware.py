from django.shortcuts import redirect
from datetime import date

class VerificarLicenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Evitar bucle de redirecciones: permitir acceder a las rutas públicas
        # relacionadas con la renovación/soporte y la propia página de licencia
        # expirada sin forzar redirección.
        path = (request.path or '').lower()
        whitelist_prefixes = (
            '/licencia-expirada',
            '/solicitar-renovacion',
            '/soporte',
            '/accounts/logout',
            '/logout',
            '/static/',
            '/media/',
        )
        for p in whitelist_prefixes:
            if path.startswith(p):
                return self.get_response(request)

        if request.user.is_authenticated:
            # superusers siempre pasan
            if request.user.is_superuser:
                return self.get_response(request)

            licencia = request.user.licenciatemporal_set.order_by('-fecha_fin').first()
            if not licencia or licencia.fecha_fin < date.today() or not licencia.estado:
                return redirect('licencia_expirada')

        return self.get_response(request)
