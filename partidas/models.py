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
    # indica si ya se envió la notificación previa al vencimiento para evitar emails repetidos
    notified_pre_expiry = models.BooleanField(default=False)

class PartidaArancelaria(models.Model):
    capitulo = models.CharField(max_length=200, default="Sin datos")
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
    # fecha de última actualización para habilitar filtros por rango de fechas
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Busqueda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termino_buscado = models.CharField(max_length=100)
    tipo_busqueda = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    # resumen de resultados: cadena legible que puede incluir número de hits y ejemplos de códigos
    resultados = models.TextField(blank=True, default='')

class HistoriaActividad(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

class SolicitudSoporte(models.Model):
    """Registro de solicitudes enviadas por usuarios al equipo de soporte."""
    ESTADO_CHOICES = (
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('error', 'Error'),
    )
    # nombre del remitente (puede ser proporcionado por anónimos o rellenado desde el usuario autenticado)
    nombre = models.CharField(max_length=150, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    correo = models.CharField(max_length=254)
    asunto = models.CharField(max_length=255, blank=True, null=True)
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        return f"{self.creado_en} | {user} | {self.asunto or 'Sin asunto'}"
class Manual(models.Model):
    tipo = models.CharField(max_length=50)
    url_pdf = models.URLField()
    descripcion = models.TextField()
    # versión del documento (p. ej. 'v1.2') para control de cambios
    version = models.CharField(max_length=30, blank=True, null=True)
    # fecha de última actualización del documento (se actualiza al guardar)
    updated_at = models.DateTimeField(auto_now=True)

class InterfazSistema(models.Model):
    tema = models.CharField(max_length=20)
    tamaño_texto = models.CharField(max_length=10)
    modo_accesibilidad = models.BooleanField(default=False)


class SearchStatistic(models.Model):
    """Estadísticas agregadas por capítulo para un periodo dado."""
    capitulo = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)
    periodo_inicio = models.DateField(null=True, blank=True)
    periodo_fin = models.DateField(null=True, blank=True)
    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ranking de productos buscados'
        verbose_name_plural = 'Ranking de productos buscados'

    def __str__(self):
        return f"{self.capitulo} — {self.count}"


class SearchStatisticDaily(models.Model):
    """Contador diario por capítulo para registrar búsquedas en tiempo real."""
    capitulo = models.CharField(max_length=100)
    fecha = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('capitulo', 'fecha')
        verbose_name = 'Cuenta diaria de búsquedas'
        verbose_name_plural = 'Cuentas diarias de búsquedas'

    def __str__(self):
        return f"{self.fecha} | {self.capitulo} — {self.count}"


class SearchStatisticTotal(models.Model):
    """Contador acumulado por capítulo, se incrementa en tiempo real por cada búsqueda relevante."""
    capitulo = models.CharField(max_length=100, unique=True)
    total = models.BigIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ranking de capítulos buscados'
        verbose_name_plural = 'Ranking de capítulos buscados'

    def __str__(self):
        return f"{self.capitulo} — {self.total}"


class SearchStatisticProductTotal(models.Model):
    """Contador acumulado por producto (partida) con su capítulo correspondiente."""
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    capitulo = models.CharField(max_length=100, blank=True, null=True)
    total = models.BigIntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ranking de productos buscados'
        verbose_name_plural = 'Ranking de productos buscados'

    def __str__(self):
        return f"{self.codigo} ({self.capitulo}) — {self.total}"


class ExportLog(models.Model):
    """Registro simple de exportaciones realizadas por administradores."""
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    filtros = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        return f"{self.fecha_hora} | {user} | {self.accion}"


class ClickLog(models.Model):
    """Registro de clicks importantes hechos por usuarios (historial -> detalle, etc.)."""
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    partida = models.ForeignKey(PartidaArancelaria, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=100, default='click')
    extra = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        part = self.partida.codigo if self.partida else 'N/A'
        return f"{self.fecha_hora} | {user} | {self.accion} | {part}"


class PartidaReferencia(models.Model):
    """Referencia legal o documento asociado a una partida."""
    partida = models.ForeignKey(PartidaArancelaria, on_delete=models.CASCADE, related_name='referencias')
    titulo = models.CharField(max_length=200, blank=True, null=True)
    texto = models.TextField(blank=True, null=True)
    fecha_norma = models.DateField(blank=True, null=True)
    numero_resolucion = models.CharField(max_length=100, blank=True, null=True)
    nota = models.CharField(max_length=250, blank=True, null=True)
    archivo = models.FileField(upload_to='referencias/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        titulo = self.titulo or (self.numero_resolucion or 'Referencia')
        return f"{self.partida.codigo} — {titulo}"


class ChatMessage(models.Model):
    """Registro de mensajes enviados al asistente y su respuesta."""
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje = models.TextField()
    respuesta = models.TextField(blank=True, null=True)
    publico = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        return f"{self.created_at} | {user}: {self.mensaje[:40]}"


class NotificationLog(models.Model):
    """Registro de envíos de notificaciones/correos desde el admin."""
    destinatario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    destinatario_email = models.CharField(max_length=254, blank=True, null=True)
    asunto = models.CharField(max_length=255, blank=True, null=True)
    cuerpo = models.TextField(blank=True, null=True)
    enviado_por = models.ForeignKey(Usuario, related_name='notificaciones_enviadas', on_delete=models.SET_NULL, null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        to_addr = self.destinatario_email or (self.destinatario.username if self.destinatario else 'N/A')
        status = 'OK' if self.success else 'FAIL'
        return f"{self.fecha_hora} | {to_addr} | {status}"
