from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView 

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('buscar/', views.buscar_partidas, name='buscar_partidas'),
    path('partida/<int:partida_id>/', views.detalle_partida, name='detalle_partida'),
    path('historial/', views.historial_buscador, name='historial_buscador'),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('admin/partidas/', views.panel_partidas, name='panel_partidas'),
    path('manuales/', views.ver_manuales, name='manuales'),
    path('ayuda/', views.chat_asistente, name='chat_asistente'),
    path('licencia-expirada/', views.licencia_expirada, name='licencia_expirada'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('soporte/', views.soporte, name='soporte'),
]
