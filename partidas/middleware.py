from django.shortcuts import redirect
from datetime import date

class VerificarLicenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return self.get_response(request)

            licencia = request.user.licenciatemporal_set.order_by('-fecha_fin').first()
            if not licencia or licencia.fecha_fin < date.today() or not licencia.estado:
                return redirect('licencia_expirada')
        return self.get_response(request)
