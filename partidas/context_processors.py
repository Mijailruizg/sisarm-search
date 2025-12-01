from datetime import date

def license_info(request):
    """Context processor que añade información de licencia al contexto de todas las plantillas.
    Retorna claves:
      - licencia_dias_restantes: int | None (conteo inclusivo)
      - licencia_estado: 'ok' | 'expiring' | 'expired' | None
      - licencia_fecha_fin: ISO date string | None
    """
    ctx = {
        'licencia_dias_restantes': None,
        'licencia_estado': None,
        'licencia_fecha_fin': None,
    }
    try:
        if request.user.is_authenticated:
            from .models import LicenciaTemporal
            licencia = LicenciaTemporal.objects.filter(usuario=request.user, estado=True).order_by('-fecha_fin').first()
            if licencia:
                hoy = date.today()
                # raw_days puede ser negativo si la fecha de fin ya pasó
                raw_days = (licencia.fecha_fin - hoy).days
                # Conteo inclusivo: por convención del sistema mostramos raw_days + 1
                dias_inclusivos = raw_days + 1
                # conservar signo para indicar expiradas con valores negativos
                ctx['licencia_dias_restantes'] = dias_inclusivos
                ctx['licencia_fecha_fin'] = licencia.fecha_fin.isoformat()

                # Mapeo de colores/estados según criterio:
                # - más de 5 días: estado 'ok' (blanco)
                # - entre 1 y 5 días (incl.): 'expiring' (amarillo)
                # - 0 o menos: 'expired' (rojo)

                # valor absoluto para mostrar cuando esté expirado
                try:
                    ctx['licencia_dias_abs'] = abs(int(dias_inclusivos))
                except Exception:
                    ctx['licencia_dias_abs'] = None

                # Determinar estado según umbrales
                if dias_inclusivos is None:
                    ctx['licencia_estado'] = None
                elif dias_inclusivos > 5:
                    ctx['licencia_estado'] = 'ok'
                elif dias_inclusivos >= 1:
                    ctx['licencia_estado'] = 'expiring'
                else:
                    ctx['licencia_estado'] = 'expired'
    except Exception:
        # no bloquear render si hay un error; dejar valores None
        pass
    return ctx
