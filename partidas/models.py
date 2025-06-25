from django.db import models
from django.contrib.auth.models import AbstractUser



capitulo = models.CharField(max_length=100, blank=True, null=True)


class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion_permisos = models.TextField()

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    estado_licencia = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

class LicenciaTemporal(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.BooleanField(default=True)

class PartidaArancelaria(models.Model):
    capitulo = models.CharField(max_length=10, default="Sin datos")
    partida = models.CharField(max_length=10, default="Sin datos")
    subpartida = models.CharField(max_length=10, default="Sin datos")
    codigo = models.CharField(max_length=50, default="Sin datos")
    descripcion = models.TextField(default="Sin datos")
    gravamen = models.CharField(max_length=50, default="Sin datos")
    ice_iehd = models.CharField(max_length=50, default="Sin datos")
    unidad_medida = models.CharField(max_length=50, default="Sin datos")
    despacho_frontera = models.CharField(max_length=50, default="Sin datos")
    tipo_documento = models.CharField(max_length=50, default="Sin datos")
    entidad_emite = models.CharField(max_length=100, default="Sin datos")
    disp_legal = models.TextField(default="Sin datos")
    can_ace36_ace47_ven = models.CharField(max_length=50, default="Sin datos")
    ace22_chi_prot = models.CharField(max_length=50, default="Sin datos")
    ace66_mexico = models.CharField(max_length=50, default="Sin datos")
    permisos = models.TextField(default="Sin datos")
    subpartidas = models.TextField(default="Sin datos")
    referencia_legal = models.TextField(default="Sin datos")

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Busqueda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termino_buscado = models.CharField(max_length=100)
    tipo_busqueda = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

class HistoriaActividad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

class Manual(models.Model):
    tipo = models.CharField(max_length=50)
    url_pdf = models.URLField()
    descripcion = models.TextField()

class InterfazSistema(models.Model):
    tema = models.CharField(max_length=20)
    tamaño_texto = models.CharField(max_length=10)
    modo_accesibilidad = models.BooleanField(default=False)
