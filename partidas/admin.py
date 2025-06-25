
from django.contrib import admin
from .models import (
    Usuario, Rol, LicenciaTemporal, PartidaArancelaria,
    Busqueda, HistoriaActividad, Manual, InterfazSistema
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'estado_licencia')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'is_active')

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


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'url_pdf')


