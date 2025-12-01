"""
RUTAS DEL SISTEMA SISARM SEARCH
================================
Módulo: partidas/urls.py

Principales rutas:
  - /inicio/: Página de inicio (menú principal)
  - /buscar/: Búsqueda de partidas arancelarias
  - /detalle-partida/<id>/: Detalle completo de una partida
  - /importar-excel/: Cargar datos desde Excel
  - /exportar-excel/: Descargar resultados como Excel
  - /ayuda/: Chat asistido con Dialogflow
  - /manuales/: Documentación y guías de usuario
  - /estadisticas-aranceles/: Reportes y estadísticas
  - /api/: Endpoints para operaciones dinámicas (autocompletado, chat, webhooks)
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView 
from django.views.generic.base import RedirectView

urlpatterns = [
    # === VISTAS PRINCIPALES ===
    path('inicio/', views.inicio, name='inicio'),  # Página de bienvenida
    path('estadisticas-aranceles/', views.estadisticas_aranceles, name='estadisticas_aranceles'),  # Reportes
    
    # === AUTENTICACIÓN ===
    path('registro/', views.registro, name='registro'),  # Registrar nuevo usuario
    path('accounts/login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),  # Login
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Cierre de sesión
    
    # === BÚSQUEDA Y DETALLE DE PARTIDAS ===
    path('buscar/', views.buscar_partidas, name='buscar_partidas'),  # Búsqueda principal
    path('aranceles/', views.lista_aranceles, name='lista_aranceles'),  # Listado completo
    path('aranceles/<str:capitulo>/', views.aranceles_por_capitulo, name='aranceles_por_capitulo'),  # Por capítulo
    path('detalle-partida/<int:partida_id>/', views.detalle_partida, name='detalle_partida'),  # Detalle de partida
    path('partida/<int:partida_id>/', RedirectView.as_view(pattern_name='detalle_partida', permanent=True)),  # Compatibilidad
    
    # === HISTORIAL Y LOGS ===
    path('historial/', views.historial_buscador, name='historial_buscador'),  # Historial de búsquedas del usuario
    path('log/click/', views.log_click, name='log_click'),  # Log de clics (analítica)
    
    # === IMPORTACIÓN Y EXPORTACIÓN ===
    path('importar-excel/', views.importar_excel, name='importar_excel'),  # Cargar datos desde Excel
    path('exportar-excel/', views.exportar_partidas_excel, name='exportar_partidas_excel'),  # Descargar como Excel
    
    # === ADMINISTRACIÓN ===
    path('admin/partidas/', views.panel_partidas, name='panel_partidas'),  # Panel admin de partidas
    path('admin-busquedas/', views.admin_busquedas, name='admin_busquedas'),  # Admin de búsquedas (evita colisión con /admin/)
    
    # === DOCUMENTACIÓN Y MANUALES ===
    path('manuales/', views.ver_manuales, name='manuales'),  # Centro de manuales
    path('manuales/guia-buscador/', views.guia_buscador_html, name='guia_buscador_html'),  # Guía interactiva
    path('manuales/descargar/', views.descargar_manual_usuario, name='descargar_manual_usuario'),  # Descargar PDF
    
    # === CHAT Y SOPORTE ===
    path('ayuda/', views.chat_asistente, name='chat_asistente'),  # Chat de ayuda con Dialogflow
    path('soporte/', views.soporte, name='soporte'),  # Formulario de soporte
    path('soporte/submit/', views.soporte_submit, name='soporte_submit'),  # Envío de soporte
    path('referencia/solicitar-ayuda/<int:referencia_id>/', views.solicitar_ayuda_documento, name='solicitar_ayuda_documento'),  # Ayuda por referencia
    
    # === LICENCIA ===
    path('licencia-expirada/', views.licencia_expirada, name='licencia_expirada'),  # Página licencia vencida
    path('solicitar-renovacion/', views.solicitar_renovacion, name='solicitar_renovacion'),  # Solicitar renovación
    
    # === APIs INTERNAS (AJAX/REST) ===
    path('api/chat-help/', views.api_chat_help, name='api_chat_help'),  # Chat AJAX
    path('api/dialogflow-webhook/', views.dialogflow_webhook, name='dialogflow_webhook'),  # Webhook Dialogflow
    path('api/autocomplete/', views.api_autocomplete, name='api_autocomplete'),  # Autocompletado de códigos
    path('api/stats-by-chapter/', views.api_stats_by_chapter, name='api_stats_by_chapter'),  # Estadísticas por capítulo
    path('api/autocomplete-entidades/', views.api_autocomplete_entidades, name='api_autocomplete_entidades'),  # Autocomplete entidades
    path('api/autocomplete-capitulos/', views.api_autocomplete_capitulos, name='api_autocomplete_capitulos'),  # Autocomplete capítulos
]
