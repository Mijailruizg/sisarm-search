from django.shortcuts import render, get_object_or_404, redirect
from .models import PartidaArancelaria, Busqueda, Manual, LicenciaTemporal, Rol
from .forms import CargarExcelForm, PartidaForm, RegistroUsuarioForm
from .importar_excel import importar_partidas_desde_excel
from .decorators import rol_requerido
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth import login
from django.db.models import Q
from datetime import timedelta
from django.utils.safestring import mark_safe
import re

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                try:
                    rol_usuario = Rol.objects.get(nombre__iexact='usuario')
                    usuario.rol = rol_usuario
                except Rol.DoesNotExist:
                    messages.error(request, "El rol 'usuario' no existe. Contacta al administrador.")
                    return redirect('registro')

                usuario.save()

                if not LicenciaTemporal.objects.filter(usuario=usuario).exists():
                    fecha_inicio = now()
                    fecha_fin = fecha_inicio + timedelta(days=7)
                    LicenciaTemporal.objects.create(
                        usuario=usuario,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        estado=True
                    )

                login(request, usuario)
                return redirect('inicio')
            except Exception as e:
                messages.error(request, f"Ocurrió un error al registrar: {e}")
                return redirect('registro')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registration/registro.html', {'form': form})


@login_required
def inicio(request):
    return render(request, 'partidas/inicio.html')

@login_required
def buscar_partidas(request):
    partidas = PartidaArancelaria.objects.all()
    termino = request.GET.get('termino', '').strip()
    capitulo = request.GET.get('capitulo', '').strip()
    gravamen = request.GET.get('gravamen', '').strip()
    tipo_documento = request.GET.get('tipo_documento', '').strip()
    entidad_emite = request.GET.get('entidad_emite', '').strip()

    if termino:
        partidas = partidas.filter(Q(codigo__icontains=termino) | Q(descripcion__icontains=termino))

    if capitulo:
        partidas = partidas.filter(capitulo__icontains=capitulo)
    if gravamen:
        partidas = partidas.filter(gravamen__icontains=gravamen)
    if tipo_documento:
        partidas = partidas.filter(tipo_documento__icontains=tipo_documento)
    if entidad_emite:
        partidas = partidas.filter(entidad_emite__icontains=entidad_emite)

    if request.user.is_authenticated and termino:
        Busqueda.objects.create(
            usuario=request.user,
            termino_buscado=termino,
            tipo_busqueda="Texto o Código",
            fecha=now()
        )

    capitulo_relacionado = partidas.first().capitulo if partidas.exists() else None
    relacionadas = PartidaArancelaria.objects.filter(
        capitulo=capitulo_relacionado
    ).exclude(id__in=partidas)[:15] if capitulo_relacionado else []

    similares = []
    if termino:
        similares = PartidaArancelaria.objects.filter(
            descripcion__icontains=termino
        ).exclude(id__in=partidas.values_list('id', flat=True))[:15]

    if termino:
        patron = re.compile(re.escape(termino), re.IGNORECASE)
        for p in partidas:
            p.descripcion_resaltada = mark_safe(
                patron.sub(
                    lambda m: f'<mark style="background-color:#00ff55; color:#000; padding:0.2em 0.3em; border-radius:5px;">{m.group(0)}</mark>',
                    p.descripcion
                )
            )
        for s in similares:
            s.descripcion_resaltada = mark_safe(
                patron.sub(
                    lambda m: f'<mark style="background-color:#00ff55; color:#000; padding:0.2em 0.3em; border-radius:5px;">{m.group(0)}</mark>',
                    s.descripcion
                )
            )
    else:
        for p in partidas:
            p.descripcion_resaltada = p.descripcion
        for s in similares:
            s.descripcion_resaltada = s.descripcion

    capitulos_disponibles = PartidaArancelaria.objects.values_list('capitulo', flat=True).distinct()
    gravamenes_disponibles = PartidaArancelaria.objects.values_list('gravamen', flat=True).distinct()
    tipos_disponibles = PartidaArancelaria.objects.values_list('tipo_documento', flat=True).distinct()
    entidades_disponibles = PartidaArancelaria.objects.values_list('entidad_emite', flat=True).distinct()

    return render(request, 'partidas/buscar.html', {
        'resultados': partidas,
        'termino': termino,
        'relacionadas': relacionadas,
        'similares': similares,
        'capitulo': capitulo_relacionado,
        'filtros': {
            'capitulo': capitulo,
            'gravamen': gravamen,
            'tipo_documento': tipo_documento,
            'entidad_emite': entidad_emite
        },
        'capitulos': capitulos_disponibles,
        'gravamenes': gravamenes_disponibles,
        'tipos_doc': tipos_disponibles,
        'entidades': entidades_disponibles
    })

@login_required
def detalle_partida(request, partida_id):
    partida = get_object_or_404(PartidaArancelaria, id=partida_id)
    return render(request, 'partidas/detalle_partida.html', {'partida': partida})

@login_required
def historial_buscador(request):
    historial = Busqueda.objects.filter(usuario=request.user).order_by('-fecha')[:20]
    return render(request, 'partidas/historial.html', {'historial': historial})

@login_required
@rol_requerido('Administrador')
def importar_excel(request):
    if request.method == 'POST':
        form = CargarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            importar_partidas_desde_excel(archivo)
            messages.success(request, "Partidas importadas correctamente.")
    else:
        form = CargarExcelForm()
    return render(request, 'partidas/importar_excel.html', {'form': form})

@login_required
@rol_requerido('Administrador')
def panel_partidas(request):
    partidas = PartidaArancelaria.objects.all()
    return render(request, 'partidas/panel_partidas.html', {'partidas': partidas})

@login_required
def ver_manuales(request):
    manuales = Manual.objects.all()
    return render(request, 'partidas/manuales.html', {'manuales': manuales})

def chat_asistente(request):
    mensaje = request.GET.get('mensaje', '').lower().strip()
    respuesta = ""
    sugerencias = []

    if not mensaje:
        respuesta = "¡Hola! ¿En qué puedo ayudarte?"
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]

    elif mensaje in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
        respuesta = "¡Hola! ¿Cómo puedo ayudarte hoy?"
        sugerencias = ["¿Cómo buscar partidas?", "¿Dónde están los manuales?", "¿Qué es la licencia?"]

    elif mensaje in ["gracias", "muchas gracias", "ok", "entiendo"]:
        respuesta = "¡De nada! Estoy aquí para ayudarte si necesitas algo más."
        sugerencias = ["Buscar partida", "Mi licencia", "Soporte"]

    elif mensaje in ["adiós", "chau", "hasta luego"]:
        respuesta = "¡Hasta pronto! Si necesitas más ayuda, aquí estaré."
        sugerencias = []

    elif "qué es una subpartida" in mensaje or mensaje == "subpartida":
        respuesta = (
            "Una subpartida es una subdivisión dentro de una partida arancelaria que permite clasificar el producto con mayor detalle."
        )
        sugerencias = ["¿Qué significa ICE/IEHD?", "¿Dónde veo los documentos requeridos?"]

    elif "dónde veo los documentos" in mensaje or "ver documentos requeridos" in mensaje:
        respuesta = (
            "Puedes ver los requisitos y documentos exigidos haciendo clic en una partida desde el buscador.<br>"
            "Ahí verás el tipo de documento, entidad emisora y disposición legal correspondiente."
        )
        sugerencias = ["Buscar partida", "¿Qué entidad emite el permiso?"]

    elif "qué entidad emite el permiso" in mensaje:
        respuesta = (
            "La entidad que emite el permiso está especificada dentro del detalle de cada partida arancelaria.<br>"
            "Puedes consultarla al hacer clic sobre una partida en los resultados de búsqueda."
        )
        sugerencias = ["Buscar partida", "¿Dónde veo los documentos requeridos?"]

    elif "tienen soporte" in mensaje or "hay soporte" in mensaje or "disponen de soporte" in mensaje:
        respuesta = (
            "¡Sí! Contamos con soporte técnico para ayudarte.<br>"
            "Haz clic en el botón <strong>Soporte</strong> del menú o directamente desde <a href='/soporte' class='btn btn-sm btn-success'>aquí</a>."
        )
        sugerencias = ["¿Atienden por WhatsApp?", "¿Cuánto tardan en responder?"]

    elif "cuánto tardan en responder" in mensaje:
        respuesta = (
            "El tiempo de respuesta del soporte puede variar, pero normalmente respondemos en menos de 24 horas hábiles.<br>"
            "También puedes escribir directamente a soporte@sisarm.com."
        )
        sugerencias = ["¿Puedo escribir por WhatsApp?", "Contactar soporte"]

    elif "ice" in mensaje or "iehd" in mensaje:
        respuesta = (
            "ICE es el Impuesto al Consumo Específico y IEHD es el Impuesto Especial a los Hidrocarburos y Derivados.<br>"
            "Se aplican a productos como bebidas, tabacos y combustibles según la normativa."
        )
        sugerencias = ["¿Dónde se ve ese impuesto?", "¿A qué partidas aplica?"]

    elif "requisitos de una partida" in mensaje or "documentos de una partida" in mensaje:
        respuesta = (
            "Puedes ver los requisitos y documentos exigidos haciendo clic en una partida desde el buscador.<br>"
            "Ahí verás el tipo de documento, entidad emisora y disposición legal correspondiente."
        )
        sugerencias = ["Buscar partida", "¿Qué entidad emite el permiso?"]

    elif "capítulo arancelario" in mensaje or "qué es un capítulo" in mensaje:
        respuesta = (
            "Un capítulo arancelario agrupa productos similares bajo un mismo código base.<br>"
            "Por ejemplo, el Capítulo 01 incluye animales vivos, el 02 carnes, etc."
        )
        sugerencias = ["Buscar partida", "Filtrar por capítulo"]

    elif "qué es una partida" in mensaje or "partida arancelaria" in mensaje:
        respuesta = (
            "Una partida arancelaria es un código que clasifica un tipo de producto en el comercio internacional.<br>"
            "Define impuestos, permisos y requisitos para su importación o exportación."
        )
        sugerencias = ["¿Qué es una subpartida?", "¿Cómo buscar una partida?"]

    elif "buscar" in mensaje or mensaje == "buscar partida":
        respuesta = (
            "Para buscar una partida arancelaria:<br>"
            "• Haz clic en <strong>Buscar Partidas</strong> desde el menú principal.<br>"
            "• Escribe el código o la descripción.<br>"
            "• Usa filtros como capítulo, gravamen o entidad emisora."
        )
        sugerencias = ["¿Qué es una partida?", "¿Cómo usar filtros avanzados?"]

    elif "filtro" in mensaje:
        respuesta = (
            "En el buscador puedes usar filtros como:<br>"
            "• <strong>Capítulo</strong><br>"
            "• <strong>Gravamen</strong><br>"
            "• <strong>Entidad que emite</strong><br>"
            "• <strong>Tipo de documento</strong>"
        )
        sugerencias = ["¿Qué filtro me conviene usar?", "¿Qué es un capítulo arancelario?"]

    elif "licencia" in mensaje or "caduca" in mensaje or mensaje == "mi licencia":
        respuesta = (
            "Tu licencia temporal dura 7 días desde el registro.<br>"
            "Te da acceso completo al sistema. Si expira, debes contactar al administrador para renovarla."
        )
        sugerencias = ["¿Qué es la licencia?", "¿Cómo renovarla?"]

    elif "qué es la licencia" in mensaje:
        respuesta = (
            "Es un permiso de uso que habilita tu acceso al sistema durante un periodo de tiempo determinado (7 días en cuentas nuevas)."
        )
        sugerencias = ["¿Está activa mi licencia?", "¿Qué pasa si caduca?"]

    elif "manual buscador" in mensaje or "manual del buscador" in mensaje:
        respuesta = (
            "Puedes revisar el manual llamado <strong>Guía del Buscador</strong> en la sección de manuales.<br>"
            "Ahí se explica cómo hacer búsquedas por texto, código y filtros."
        )
        sugerencias = ["Ver manuales", "Buscar partida"]

    elif "manual administrador" in mensaje or "manual para admin" in mensaje:
        respuesta = (
            "Sí, hay manuales específicos para administradores. Explican cómo importar archivos Excel, gestionar partidas y usuarios."
        )
        sugerencias = ["Ver manuales", "¿Cómo importar partidas?"]

    elif "manual" in mensaje or mensaje == "ver manuales":
        respuesta = (
            "Los manuales están en la sección <strong>Manuales</strong> del menú principal.<br>"
        )
        sugerencias = ["¿Qué manual explica el buscador?", "¿Hay manuales para administradores?"]

    elif "registro" in mensaje or "crear cuenta" in mensaje:
        respuesta = (
            "Puedes crear una cuenta desde la pantalla principal en <strong>Crear cuenta</strong>.<br>"
            "Necesitarás un nombre de usuario, correo electrónico."
        )
        sugerencias = ["¿Qué datos necesito?", "¿Puedo registrarme sin correo?"]

    elif "qué datos necesito" in mensaje or "datos para registrarme" in mensaje:
        respuesta = (
            "Se solicita nombre, apellido, correo electrónico, nombre de usuario y contraseña."
        )
        sugerencias = ["Crear cuenta", "¿Puedo registrarme sin correo?"]

    elif "registrarme sin correo" in mensaje:
        respuesta = (
            "No. Actualmente necesitas un correo válido para crear una cuenta y recibir notificaciones importantes."
        )
        sugerencias = ["Crear cuenta", "¿Qué datos necesito?"]

    elif "error" in mensaje or "problema" in mensaje or "no puedo" in mensaje:
        respuesta = (
            "¿Tienes un problema? Aquí algunas recomendaciones:<br>"
            "• Verifica usuario y contraseña.<br>"
            "• Asegúrate de que tu licencia esté activa.<br>"
            "• Recarga la página o prueba en otro navegador."
        )
        sugerencias = ["Mi licencia está vencida", "No encuentro partidas", "No puedo iniciar sesión"]

    elif "soporte" in mensaje or "contactar" in mensaje or "ayuda" in mensaje or mensaje == "contactar soporte":
        respuesta = (
            "Puedes contactar soporte:<br>"
            "• Botón <strong>Soporte</strong> en el menú principal<br>"
            "<a href='/soporte' class='btn btn-sm btn-success'>Ir a soporte</a>"
        )
        sugerencias = ["¿Atienden por WhatsApp?", "¿Cuánto tardan en responder?"]

    else:
        respuesta = (
            "No entendí tu consulta, pero puedo ayudarte con lo siguiente:"
        )
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]

    context = {
        "mensaje": mensaje,
        "respuesta": respuesta,
        "sugerencias": sugerencias
    }
    return render(request, 'partidas/chat.html', context)

def licencia_expirada(request):
    return render(request, 'partidas/licencia_expirada.html')

from django.shortcuts import render

@login_required
def soporte(request):
    return render(request, 'partidas/soporte.html')
