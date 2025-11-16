from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView 
from django.views.generic.base import RedirectView

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('estadisticas-aranceles/', views.estadisticas_aranceles, name='estadisticas_aranceles'),
    path('log/click/', views.log_click, name='log_click'),
    path('registro/', views.registro, name='registro'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('buscar/', views.buscar_partidas, name='buscar_partidas'),
    path('aranceles/', views.lista_aranceles, name='lista_aranceles'),
    path('aranceles/<str:capitulo>/', views.aranceles_por_capitulo, name='aranceles_por_capitulo'),
    path('detalle-partida/<int:partida_id>/', views.detalle_partida, name='detalle_partida'),
    # mantener redirección desde la ruta antigua /partida/<id>/ a la nueva /detalle-partida/<id>/ (compatibilidad)
    path('partida/<int:partida_id>/', RedirectView.as_view(pattern_name='detalle_partida', permanent=True)),
    path('historial/', views.historial_buscador, name='historial_buscador'),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('admin/partidas/', views.panel_partidas, name='panel_partidas'),
    path('exportar-excel/', views.exportar_partidas_excel, name='exportar_partidas_excel'),
    # usar ruta distinta a /admin/ para evitar colisión con el admin de Django
    path('admin-busquedas/', views.admin_busquedas, name='admin_busquedas'),
    path('referencia/solicitar-ayuda/<int:referencia_id>/', views.solicitar_ayuda_documento, name='solicitar_ayuda_documento'),
    path('manuales/', views.ver_manuales, name='manuales'),
    path('manuales/guia-buscador/', views.guia_buscador_html, name='guia_buscador_html'),
    path('manuales/descargar/', views.descargar_manual_usuario, name='descargar_manual_usuario'),
    path('ayuda/', views.chat_asistente, name='chat_asistente'),
    path('api/chat-help/', views.api_chat_help, name='api_chat_help'),
    path('api/autocomplete/', views.api_autocomplete, name='api_autocomplete'),
    path('api/stats-by-chapter/', views.api_stats_by_chapter, name='api_stats_by_chapter'),
    path('api/autocomplete-entidades/', views.api_autocomplete_entidades, name='api_autocomplete_entidades'),
    path('api/autocomplete-capitulos/', views.api_autocomplete_capitulos, name='api_autocomplete_capitulos'),
    path('licencia-expirada/', views.licencia_expirada, name='licencia_expirada'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('soporte/', views.soporte, name='soporte'),
    path('soporte/submit/', views.soporte_submit, name='soporte_submit'),
]
