
from django.contrib import admin
from .models import (
    Usuario, Rol, LicenciaTemporal, PartidaArancelaria,
    Busqueda, HistoriaActividad, Manual, InterfazSistema
)
from .models import PartidaReferencia
from .models import SearchStatisticTotal
from .models import SearchStatisticProductTotal
# SearchStatistic and SearchStatisticTotal are kept in models for analytics
# but not registered in the admin to avoid showing the ranking button.
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.shortcuts import render, redirect
from .models import NotificationLog

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'estado_licencia')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'is_active')
    actions = ['enviar_notificacion_por_correo']

    def enviar_notificacion_por_correo(self, request, queryset):
        """Acción de admin: mostrar formulario intermedio para asunto/mensaje y enviar email a los seleccionados."""
        # cuando el formulario se reenvía desde la plantilla intermedia, Django incluye
        # un hidden input 'post'='yes' para confirmar la acción; detectarlo y ejecutar.
        if request.POST.get('post') == 'yes':
            # ejecutar envío
            subject = request.POST.get('subject', '').strip()
            message_body = request.POST.get('message', '').strip()
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or ''
            sent = 0
            from django.urls import reverse
            # construir enlace absoluto a la página de ayuda/chat que activará la acción de abrir Soporte
            try:
                chat_url = request.build_absolute_uri(reverse('chat_asistente'))
            except Exception:
                chat_url = request.build_absolute_uri('/ayuda/')

            for user in queryset:
                if user.email:
                    try:
                        # permitir placeholders simples
                        body = message_body.replace('{username}', user.username)
                        # añadir enlace a soporte (plain y html)
                        # preparar parametros prefill: email y un mensaje sugerido
                        import urllib.parse as _up
                        prefill_params = {
                            'open_support': '1',
                            'email': user.email,
                            'prefill_subject': subject[:120],
                            'prefill_message': (body[:400] + '\n\n')
                        }
                        q = _up.urlencode(prefill_params)
                        support_link = f"{chat_url}?{q}"
                        plain_footer = f"\n\nPara contactar soporte usa el formulario en 'Soporte' o abre este enlace: {support_link}"
                        html_footer = f"<br><br>Para contactar soporte usa el formulario en 'Soporte' o pulsa <a href=\"{support_link}\">Toca aquí</a>."
                        body_plain = body + plain_footer
                        body_html = body.replace('\n', '<br>') + html_footer

                        err_msg = None
                        try:
                            # usar html_message para que el link sea clickable
                            sent_count = send_mail(subject, body_plain, from_email, [user.email], fail_silently=False, html_message=body_html)
                            success = bool(sent_count)
                        except Exception as e:
                            sent_count = 0
                            success = False
                            err_msg = str(e)
                        NotificationLog.objects.create(
                            destinatario=user,
                            destinatario_email=user.email,
                            asunto=subject,
                            cuerpo=body_plain,
                            enviado_por=request.user if request.user.is_authenticated else None,
                            success=success,
                            error_message=err_msg
                        )
                        if success:
                            sent += 1
                    except Exception:
                        # seguir con los demás
                        continue
            self.message_user(request, f"Notificación enviada a {sent} usuario(s).", level=messages.SUCCESS)
            return None

        # mostrar formulario intermedio
        context = {
            'users': queryset,
            'selected': [str(user.pk) for user in queryset],
            'default_subject': 'Notificación de SISARM',
            'default_message': 'Estimado usuario,\n\nEste es un mensaje del sistema SISARM.\n\nSaludos cordiales,\nEquipo SISARM'
        }
        return render(request, 'admin/send_notification.html', context)

    enviar_notificacion_por_correo.short_description = 'Enviar notificación por correo a los usuarios seleccionados'
    change_form_template = 'admin/partidas/usuario/change_form.html'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:usuario_id>/send_notification/', self.admin_site.admin_view(self.send_notification_view), name='partidas_usuario_send_notification'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra = extra_context or {}
        # URL para enviar notificación al usuario desde su change form
        from django.urls import reverse
        extra['send_notification_url'] = reverse('admin:partidas_usuario_send_notification', args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context=extra)

    def send_notification_view(self, request, usuario_id):
        # vista para componer y enviar un email a un único usuario desde el admin
        if not self.has_change_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        from .models import Usuario
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            self.message_user(request, 'Usuario no encontrado', level=messages.ERROR)
            return redirect('..')

        if request.method == 'POST':
            subject = request.POST.get('subject', '').strip()
            message_body = request.POST.get('message', '').strip()
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or ''
            if usuario.email:
                try:
                    # permitir placeholders simples
                    body = message_body.replace('{username}', usuario.username)
                    # construir enlace absoluto a la página de ayuda/chat que activará la acción de abrir Soporte
                    from django.urls import reverse
                    try:
                        chat_url = request.build_absolute_uri(reverse('chat_asistente'))
                    except Exception:
                        chat_url = request.build_absolute_uri('/ayuda/')
                    support_link = f"{chat_url}?open_support=1"
                    plain_footer = f"\n\nPara contactar soporte usa el formulario en 'Soporte' o abre este enlace: {support_link}"
                    html_footer = f"<br><br>Para contactar soporte usa el formulario en 'Soporte' o pulsa <a href=\"{support_link}\">Toca aquí</a>."
                    body_plain = body + plain_footer
                    body_html = body.replace('\n', '<br>') + html_footer
                    err_msg = None
                    try:
                        sent_count = send_mail(subject, body_plain, from_email, [usuario.email], fail_silently=False, html_message=body_html)
                        success = bool(sent_count)
                    except Exception as e:
                        success = False
                        err_msg = str(e)
                    NotificationLog.objects.create(
                        destinatario=usuario,
                        destinatario_email=usuario.email,
                        asunto=subject,
                        cuerpo=body_plain,
                        enviado_por=request.user if request.user.is_authenticated else None,
                        success=success,
                        error_message=err_msg
                    )
                    if success:
                        self.message_user(request, f'Correo enviado a {usuario.email}', level=messages.SUCCESS)
                    else:
                        self.message_user(request, f'Error al enviar correo a {usuario.email}', level=messages.ERROR)
                except Exception:
                    self.message_user(request, f'Error al enviar correo a {usuario.email}', level=messages.ERROR)
            else:
                self.message_user(request, 'El usuario no tiene email registrado.', level=messages.WARNING)
            # redirigir de vuelta al change form
            from django.urls import reverse
            return redirect(reverse('admin:partidas_usuario_change', args=[usuario_id]))

        # GET: mostrar formulario simple
        context = {'usuario': usuario}
        return render(request, 'admin/partidas/usuario/send_single_notification.html', context)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion_permisos')

@admin.register(LicenciaTemporal)
class LicenciaTemporalAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('usuario__username',)

@admin.register(PartidaArancelaria)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'capitulo', 'partida', 'subpartida', 'gravamen')
    search_fields = ('codigo', 'descripcion', 'capitulo', 'partida', 'subpartida')
    list_filter = ('capitulo', 'gravamen')

@admin.register(Busqueda)
class BusquedaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'termino_buscado', 'tipo_busqueda', 'fecha')
    list_filter = ('tipo_busqueda', 'fecha')
    search_fields = ('usuario__username', 'termino_buscado')
    actions = ['generar_ranking_ultimo_mes']

    def generar_ranking_ultimo_mes(self, request, queryset):
        """Genera estadísticas agregadas para el último mes y las guarda en SearchStatistic."""
        fin = timezone.now().date()
        inicio = fin - timedelta(days=30)
        # Usar contadores diarios para rendimiento: sumar SearchStatisticDaily por capítulo en el rango
        from .models import SearchStatisticDaily
        daily_qs = SearchStatisticDaily.objects.filter(fecha__range=(inicio, fin))
        cap_counts = {}
        for d in daily_qs:
            cap = d.capitulo or 'Sin capítulo'
            cap_counts[cap] = cap_counts.get(cap, 0) + d.count

        # Notificar al admin con el total de capítulos calculados
        messages.success(request, f"Ranking calculado para {inicio} — {fin}. {len(cap_counts)} capítulos encontrados.")
    generar_ranking_ultimo_mes.short_description = 'Generar ranking (último mes)'


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'version', 'url_pdf', 'updated_at')
    search_fields = ('tipo', 'descripcion', 'version')
    list_filter = ('tipo',)


@admin.register(PartidaReferencia)
class PartidaReferenciaAdmin(admin.ModelAdmin):
    list_display = ('partida', 'titulo', 'numero_resolucion', 'fecha_norma', 'archivo', 'creado_en')
    search_fields = ('partida__codigo', 'titulo', 'numero_resolucion')
    list_filter = ('creado_en',)

@admin.register(SearchStatisticTotal)
class SearchStatisticTotalAdmin(admin.ModelAdmin):
    """Mostrar ranking acumulado de búsquedas en el admin."""
    list_display = ('capitulo', 'total', 'actualizado_en')
    search_fields = ('capitulo',)
    ordering = ('-total',)
    readonly_fields = ('capitulo', 'total', 'actualizado_en')

# Note: SearchStatistic (periodic aggregated snapshots) remains unregistered
# to avoid duplicate UI; only the accumulated ranking is exposed as requested.


@admin.register(SearchStatisticProductTotal)
class SearchStatisticProductTotalAdmin(admin.ModelAdmin):
    """Mostrar ranking de productos buscados con su capítulo."""
    list_display = ('codigo', 'capitulo', 'total', 'actualizado_en')
    search_fields = ('codigo', 'descripcion', 'capitulo')
    ordering = ('-total',)
    readonly_fields = ('codigo', 'descripcion', 'capitulo', 'total', 'actualizado_en')
    # Usar plantilla personalizada para mostrar tarjetas (layout 'bonito')
    change_list_template = 'admin/partidas/searchstatisticproducttotal/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """Proveer top_products y top_chapters al template personalizado del changelist."""
        qs = SearchStatisticProductTotal.objects.order_by('-total')[:50]
        top = []
        for idx, p in enumerate(qs, start=1):
            top.append({
                'rank': idx,
                'codigo': p.codigo,
                'descripcion': p.descripcion or '',
                'capitulo': p.capitulo or '',
                'total': f"{p.total:,}"
            })

        from django.db.models import Sum
        chap_qs = (
            SearchStatisticProductTotal.objects.values('capitulo')
            .annotate(total_sum=Sum('total'))
            .order_by('-total_sum')[:50]
        )
        top_chapters = []
        for idx, c in enumerate(chap_qs, start=1):
            top_chapters.append({
                'rank': idx,
                'capitulo': c['capitulo'] or 'Sin capítulo',
                'total': f"{c['total_sum']:,}"
            })

        extra = {'top_products': top, 'top_chapters': top_chapters, 'title': 'Ranking de productos buscados'}
        # Además: calcular estadísticas de gravamen por capítulo (promedio, min, max, count)
        # Permitir filtros simples vía GET: entidad_emite, capitulos (coma-separados)
        entidad = request.GET.get('entidad_emite', '').strip()
        capitulos_param = request.GET.get('capitulos', '').strip()
        try:
            from decimal import Decimal, InvalidOperation
            import re as _re
            from .models import PartidaArancelaria

            def _parse_gravamen(val):
                if not val:
                    return None
                s = str(val).strip()
                m = _re.search(r"[-+]?\d+[\.,]?\d*", s)
                if not m:
                    return None
                num = m.group(0).replace(',', '.')
                try:
                    return Decimal(num)
                except InvalidOperation:
                    return None

            part_qs = PartidaArancelaria.objects.all()
            if entidad:
                part_qs = part_qs.filter(entidad_emite__icontains=entidad)
            if capitulos_param:
                caps = [c.strip() for c in capitulos_param.split(',') if c.strip()]
                part_qs = part_qs.filter(capitulo__in=caps)

            # Agrupar por capítulo en Python (por robustez con texto en gravamen)
            chap_map = {}
            for p in part_qs:
                cap = p.capitulo or 'Sin capítulo'
                g = _parse_gravamen(p.gravamen)
                if g is None:
                    continue
                data = chap_map.setdefault(cap, {'values': [], 'count': 0})
                data['values'].append(g)
                data['count'] += 1

            chapter_stats = []
            for cap, data in chap_map.items():
                vals = data['values']
                if not vals:
                    continue
                mn = min(vals)
                mx = max(vals)
                tot = sum(vals)
                avg = (tot / len(vals)) if len(vals) > 0 else None
                chapter_stats.append({
                    'capitulo': cap,
                    'promedio': float(round(avg, 2)) if avg is not None else None,
                    'min': float(round(mn, 2)) if mn is not None else None,
                    'max': float(round(mx, 2)) if mx is not None else None,
                    'count': data['count']
                })
            # ordenar por capítulo
            chapter_stats = sorted(chapter_stats, key=lambda x: (x['capitulo'] or ''))
            extra['chapter_stats'] = chapter_stats
            extra['stats_filters'] = {'entidad_emite': entidad, 'capitulos': capitulos_param}
        except Exception:
            # No bloquear el admin si ocurre un error; mostrar nada
            extra['chapter_stats'] = []
            extra['stats_filters'] = {'entidad_emite': '', 'capitulos': ''}
        if extra_context:
            extra.update(extra_context)
        return super().changelist_view(request, extra_context=extra)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'destinatario_email', 'destinatario', 'asunto', 'success')
    list_filter = ('success', 'fecha_hora', 'enviado_por')
    search_fields = ('destinatario_email', 'asunto', 'cuerpo')
    readonly_fields = ('destinatario', 'destinatario_email', 'asunto', 'cuerpo', 'enviado_por', 'success', 'fecha_hora')
    ordering = ('-fecha_hora',)
    actions = ['reintentar_envio']

    def reintentar_envio(self, request, queryset):
        """Reintenta enviar los registros seleccionados. Actualiza success y fecha_hora."""
        from django.utils import timezone
        from django.core.mail import send_mail
        from django.conf import settings as djsettings
        attempted = 0
        succeeded = 0
        for log in queryset:
            # intentar reenviar al email registrado
            to_addr = log.destinatario_email
            asunto = log.asunto or ''
            cuerpo = log.cuerpo or ''
            from_email = getattr(djsettings, 'DEFAULT_FROM_EMAIL', '') or ''
            err_msg = None
            try:
                sent_count = send_mail(asunto, cuerpo, from_email, [to_addr], fail_silently=False)
                success = bool(sent_count)
            except Exception as e:
                success = False
                err_msg = str(e)
            # actualizar el registro existente
            log.success = success
            log.enviado_por = request.user if request.user.is_authenticated else None
            log.fecha_hora = timezone.now()
            log.error_message = err_msg
            log.save()
            attempted += 1
            if success:
                succeeded += 1

        self.message_user(request, f"Reintento: {attempted} registros procesados; {succeeded} re-envíos exitosos.", level=messages.INFO)
    reintentar_envio.short_description = 'Reintentar envío de notificaciones seleccionadas'


# Crear un registro por defecto del Manual de Administrador si no existe (útil para entornos de desarrollo)
try:
    from django.contrib.sites.models import Site
    # Evitar ejecutar durante migraciones iniciales (cuando la DB no está lista)
    from django.db import connection
    if connection.introspection.table_names():
        Manual.objects.get_or_create(
            tipo='Manual Administrador',
            defaults={
                'url_pdf': '/static/manuals/manual_administrador.pdf',
                'descripcion': 'Manual para administradores: instalación, importación y gestión de partidas.'
            }
        )
        # Añadir guía del buscador y manual de usuario si no existen
        Manual.objects.get_or_create(
            tipo='Guía del Buscador',
            defaults={
                'url_pdf': '/static/manuals/guia_buscador.pdf',
                'descripcion': 'Guía rápida para usar la función de búsqueda: código, descripción y filtros.',
                'version': 'v1.0'
            }
        )
        Manual.objects.get_or_create(
            tipo='Manual de Usuario',
            defaults={
                'url_pdf': '/static/manuals/manual_usuario_completo.pdf',
                'descripcion': 'Manual completo de usuario: descripción de todas las funciones del sistema.',
                'version': 'v1.0'
            }
        )
except Exception:
    # No interrumpir el arranque si la DB no está lista o en migraciones
    pass


