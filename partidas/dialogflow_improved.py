
import unicodedata
import difflib
import re
from django.conf import settings


def _normalize(text: str) -> str:
    """Normaliza texto: convierte a minúsculas y elimina acentos."""
    if not text:
        return ''
    try:
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    except Exception:
        pass
    return text.lower()


def _normalize_and_clean(text: str) -> str:
    """Normaliza y limpia espacios múltiples."""
    m = _normalize(text or '')
    m = ' '.join(m.split()) 
    return m


def _correct_typos(text: str) -> str:
    """Corrige typos comunes."""
    corrections = {
        'ola': 'hola',
        'ta bien': 'esta bien',
        'esta bien': 'esta bien',
        'gracais': 'gracias',
        'jeje': 'riendo',
        'nose': 'no se',
        'xd': 'riendo',
        'lol': 'riendo',
    }
    return corrections.get(text, text)


def contains_any(text: str, keywords: list) -> bool:
    """Verifica si el texto contiene alguna palabra clave."""
    return any(keyword in text for keyword in keywords)


def contains_word_similar(text: str, target_word: str, threshold: float = 0.7) -> bool:
    """Busca si una palabra similar a target_word está en text."""
    words = text.split()
    for word in words:
        similarity = difflib.SequenceMatcher(None, word, target_word).ratio()
        if similarity >= threshold:
            return True
    return False


def generate_chat_response(mensaje: str, request=None) -> tuple:
    """
    Genera una respuesta inteligente basada en el mensaje del usuario.
    Retorna tupla: (respuesta_html, sugerencias_list, action_dict_o_none)
    """
    respuesta = ""
    sugerencias = []
    action = None

    if not mensaje:
        respuesta = "¡Hola! Soy el Asistente de SISARM. ¿En qué puedo ayudarte hoy?"
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]
        return respuesta, sugerencias, None


    m = _normalize_and_clean(mensaje)
    m = _correct_typos(m)
    

    if re.fullmatch(r'\d+', m.strip()):
        num = int(m.strip())
        menu_options = {
            1: (
                "<strong>🔍 Buscar Partidas</strong><br><br>"
                "¿Qué quieres buscar?<br><br>"
                "Puedes usar:<br>"
                "• <strong>Código:</strong> 010121 (6 dígitos)<br>"
                "• <strong>Descripción:</strong> carne, computadora, tela<br>"
                "• <strong>Capítulo:</strong> 01, 02, 04 (agricultura, carnes, lácteos)<br><br>"
                "Escribe lo que buscas y te daré los resultados."
            ),
            2: (
                "<strong>📚 Ver Manuales</strong><br><br>"
                "Documentación disponible:<br><br>"
                "📖 <strong>Guía del Buscador</strong> - Cómo buscar paso a paso<br>"
                "📖 <strong>Manual Administrador</strong> - Para gestionar el sistema<br>"
                "📖 <strong>FAQ</strong> - Preguntas frecuentes<br><br>"
                "¿Cuál necesitas?"
            ),
            3: (
                "<strong>🎫 Mi Licencia</strong><br><br>"
                "Iniciá sesión para ver el estado de tu licencia.<br><br>"
                "Podrás ver:<br>"
                "✔️ Fecha de vencimiento<br>"
                "✔️ Días restantes<br>"
                "✔️ Opción de renovar<br><br>"
                "¿Ya tiene cuenta?"
            ),
            4: (
                "<strong>💬 Contactar Soporte</strong><br><br>"
                "Canales disponibles:<br><br>"
                "📧 <strong>Email:</strong> soporte@sisarm.com<br>"
                "📋 <strong>Formulario:</strong> Desde el menú 'Soporte'<br>"
                "💬 <strong>WhatsApp:</strong> +591 7 7682918<br><br>"
                "Respuesta en menos de 24h hábiles."
            )
        }
        
        if num in menu_options:
            respuesta = menu_options[num]
            sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]
            return respuesta, sugerencias, None
        else:
            respuesta = (
                "Opción no válida. Elige una:<br><br>"
                "1️⃣ Buscar partidas<br>"
                "2️⃣ Ver manuales<br>"
                "3️⃣ Mi licencia<br>"
                "4️⃣ Contactar soporte"
            )
            sugerencias = ["1", "2", "3", "4"]
            return respuesta, sugerencias, None


    if contains_any(m, ['me ayudas', 'me ayuda', 'puedes ayudar', 'puedes ayuda', 'necesito ayuda', 
                        'necesito ayuda', 'ayudame', 'ayúdame', 'dame una mano', 'me das una mano',
                        'dame ayuda', 'requiero ayuda', 'precisá ayuda', 'precisa ayuda',
                        'necesito soporte', 'requiero soporte', 'dame soporte', 'me das soporte']):
        respuesta = (
            "¡Claro que sí! Estoy aquí para ayudarte 😊<br><br>"
            "Puedo asistirte con:<br><br>"
            "1️⃣ <strong>Buscar partidas</strong> - Por código o descripción<br>"
            "2️⃣ <strong>Ver manuales</strong> - Guías de uso<br>"
            "3️⃣ <strong>Mi licencia</strong> - Estado de tu acceso<br>"
            "4️⃣ <strong>Contactar soporte</strong> - Hablar con el equipo<br><br>"
            "¿Cuál necesitas? Escribe el número (1-4) o cuéntame qué busca."
        )
        sugerencias = ["Buscar partida", "Ver manuales", "Contactar soporte"]
        return respuesta, sugerencias, None


    if m in {'si', 'sí', 's', 'ok', 'vale', 'dale', 'claro', 'bueno', 'esta bien', 'listo'}:
        if request:
            try:
                last_action = request.session.pop('chat_last_action', None)
                if last_action:
                    respuesta = 'Abriendo la página solicitada...'
                    return respuesta, [], last_action
            except Exception:
                pass
        respuesta = '¡Perfecto! ¿En qué más puedo ayudarte?'
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]
        return respuesta, sugerencias, None


    if m in ['riendo', 'jaja', 'jajaja', 'haha']:
        respuesta = "😄 ¡Me encanta tu sentido del humor! Pero en serio, ¿qué necesitas? Puedo ayudarte con búsquedas, manuales o tu licencia."
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia"]
        return respuesta, sugerencias, None


    if m in ['no se', 'sin idea', 'no idea']:
        respuesta = (
            "¡Sin problema! Aquí te muestro lo que puedo hacer:<br><br>"
            "🔍 <strong>Buscar partidas</strong> por código o descripción<br>"
            "📚 <strong>Ver manuales</strong> para aprender a usar el sistema<br>"
            "🎫 <strong>Mi licencia</strong> para revisar tu estado de acceso<br>"
            "💬 <strong>Contactar soporte</strong> si tienes dudas específicas"
        )
        sugerencias = ["Buscar partida", "Ver manuales"]
        return respuesta, sugerencias, None


    if contains_any(m, ['hola', 'buenos', 'buenas', 'saludos', 'como estas', 'cómo estás']):
        respuesta = (
            "¡Hola! Soy el Asistente Virtual de SISARM Search. Estoy aquí para ayudarte a buscar partidas arancelarias, "
            "revisar documentación y resolver dudas. ¿Qué necesitas?"
        )
        sugerencias = ["Buscar partida", "Ver manuales", "Mi licencia", "Contactar soporte"]
        return respuesta, sugerencias, None


    if m in ['gracias', 'muchas gracias', 'entiendo', 'merci']:
        respuesta = "Con gusto. Si necesitas algo más, aquí estoy para ayudarte 😊"
        sugerencias = ["Buscar partida", "Mi licencia", "Contactar soporte"]
        return respuesta, sugerencias, None

    if m in ['adiós', 'adios', 'chau', 'hasta luego', 'bye']:
        respuesta = "¡Hasta luego! Vuelve cuando necesites, estaré aquí para ayudarte."
        return respuesta, [], None

    if 'buscar' in m or m == 'buscar partida' or 'busco' in m or 'buscá' in m:
        respuesta = (
            "<strong>Cómo buscar una partida:</strong><br><br>"
            "1️⃣ Ve a <strong>'Buscar Partidas'</strong> en el menú<br>"
            "2️⃣ Escribe el código (ej: 010121) o descripción (ej: 'carne')<br>"
            "3️⃣ Presiona Enter<br>"
            "4️⃣ Usa los filtros para refinar<br><br>"
            "Ejemplos:<br>"
            "• <strong>Código:</strong> 010121 (carnes)<br>"
            "• <strong>Descripción:</strong> carne, tomate, zapatos<br>"
            "• <strong>Capítulo:</strong> 01 (animales), 02 (carnes)"
        )
        sugerencias = ["Buscar partida", "¿Cómo uso los filtros?", "Qué es una partida"]
        return respuesta, sugerencias, None

    if contains_any(m, ['donde veo', 'dónde veo', 'donde estan', 'dónde están', 'donde aparece', 
                        'donde busco', 'dónde busco', 'donde encuentro']):
        if 'resultado' in m or 'resultado' in mensaje:
            respuesta = (
                "Los <strong>resultados</strong> aparecen cuando usas el buscador:<br><br>"
                "1️⃣ Haz clic en el buscador (lupa 🔍)<br>"
                "2️⃣ Escribe lo que buscas<br>"
                "3️⃣ Se mostrará una lista con partidas<br>"
                "4️⃣ Haz clic en una para ver detalles"
            )
            sugerencias = ["Buscar partida", "Filtros disponibles"]
        elif 'documento' in m or 'certificado' in m or 'requisito' in m:
            respuesta = (
                "<strong>Documentos y requisitos:</strong><br><br>"
                "Están en el <strong>detalle de cada partida</strong>:<br><br>"
                "1️⃣ Busca la partida<br>"
                "2️⃣ Haz clic en el resultado<br>"
                "3️⃣ Abajo ves 'Documentos Requeridos'<br>"
                "4️⃣ Aparece quién emite, tipo de doc, etc."
            )
            sugerencias = ["Buscar partida", "Qué documentos necesito"]
        elif 'filtro' in m:
            respuesta = (
                "Los <strong>filtros</strong> aparecen en la barra de búsqueda:<br><br>"
                "📌 <strong>Capítulo:</strong> por categoría<br>"
                "📌 <strong>Gravamen:</strong> por arancel<br>"
                "📌 <strong>Entidad:</strong> por quien emite<br>"
                "📌 <strong>Requisitos:</strong> por exigencias<br><br>"
                "Selecciona lo que quieras filtrar y presiona buscar."
            )
            sugerencias = ["Filtrar por capítulo", "Buscar partida"]
        else:
            respuesta = (
                "Puedo ayudarte a encontrar en SISARM:<br><br>"
                "🔍 <strong>Partidas</strong> - Busca por código o descripción<br>"
                "📊 <strong>Filtros</strong> - Refina por capítulo, gravamen, etc<br>"
                "📄 <strong>Documentos</strong> - Requisitos de cada partida<br><br>"
                "¿Qué necesitás buscar?"
            )
            sugerencias = ["Buscar partida", "Ver documentos"]
        return respuesta, sugerencias, None

    if 'qué es una partida' in m or 'partida arancelaria' in m:
        respuesta = (
            "Una <strong>partida arancelaria</strong> es un código de 6 dígitos que identifica un producto "
            "en comercio internacional. Cada partida tiene: descripción, gravamen, documentos requeridos y más."
        )
        sugerencias = ["Buscar partida", "¿Qué es una subpartida?"]
        return respuesta, sugerencias, None

    if 'subpartida' in m:
        respuesta = (
            "Una <strong>subpartida</strong> es una subdivisión de una partida que permite "
            "clasificación más precisa y requisitos específicos."
        )
        sugerencias = ["Buscar partida", "¿Dónde veo los documentos?"]
        return respuesta, sugerencias, None

    if 'capítulo' in m and ('qué' in m or 'que' in m or 'es' in m):
        respuesta = (
            "Un <strong>capítulo arancelario</strong> agrupa partidas por familia de productos. "
            "Hay 21 capítulos: Capítulo 01 (animales), 02 (carnes), 04 (lácteos), etc."
        )
        sugerencias = ["Buscar partida", "Filtrar por capítulo"]
        return respuesta, sugerencias, None


    if 'filtro' in m or 'filtrar' in m:
        respuesta = (
            "<strong>Filtros disponibles:</strong><br><br>"
            "🏷️ <strong>Capítulo:</strong> agrupa por familia<br>"
            "💰 <strong>Gravamen:</strong> filtra por impuestos<br>"
            "🏛️ <strong>Entidad:</strong> quién emite el documento<br>"
            "📋 <strong>Requisitos:</strong> qué se exige<br><br>"
            "Aplica uno o varios al mismo tiempo."
        )
        sugerencias = ["Buscar partida", "Filtrar por capítulo"]
        return respuesta, sugerencias, None

    if 'gravamen' in m or 'impuesto' in m or 'ice' in m or 'iehd' in m:
        respuesta = (
            "En el detalle de cada partida encontrás:<br><br>"
            "💰 <strong>Gravamen:</strong> porcentaje o valor del arancel<br>"
            "🔶 <strong>ICE/IEHD:</strong> impuestos especiales (combustibles, bebidas, etc.)<br><br>"
            "Para verlo: busca la partida y haz clic en el resultado."
        )
        sugerencias = ["Buscar partida", "Ver detalle de partida"]
        return respuesta, sugerencias, None

    if 'documento' in m or 'requisito' in m or 'certificado' in m:
        respuesta = (
            "<strong>Documentos requeridos:</strong><br><br>"
            "En el detalle de cada partida verás:<br>"
            "📄 Tipos de documento necesarios<br>"
            "🏛️ Entidad que emite<br>"
            "⚖️ Disposición legal<br><br>"
            "Busca la partida y haz clic para ver todos."
        )
        sugerencias = ["Buscar partida", "Contactar soporte"]
        return respuesta, sugerencias, None

    if 'entidad' in m:
        respuesta = (
            "La <strong>entidad emisora</strong> es el organismo responsable de emitir documentos. "
            "Ejemplos: Ministerio de Agricultura, Autoridad Sanitaria, Aduana.<br><br>"
            "Verla: busca la partida y en el detalle aparecerá."
        )
        sugerencias = ["Buscar partida", "Ver detalle de partida"]
        return respuesta, sugerencias, None


    if ('manual' in m or m == 'ver manuales' or 'guia' in m or 'guía' in m or 
        'documentacion' in m or 'documentación' in m or 'aprende' in m or 'aprender' in m):
        if 'buscador' in m or 'buscar' in m:
            respuesta = (
                "La <strong>Guía del Buscador</strong> te enseña:<br><br>"
                "✔️ Cómo buscar por código o descripción<br>"
                "✔️ Cómo usar filtros<br>"
                "✔️ Ejemplos prácticos<br>"
                "✔️ Cómo leer los resultados<br>"
                "✔️ Qué significan los campos<br><br>"
                "La encuentras en 'Manuales' del menú."
            )
        elif 'admin' in m or 'administrador' in m:
            respuesta = (
                "El <strong>Manual Administrador</strong> explica:<br><br>"
                "✔️ Importar partidas desde Excel<br>"
                "✔️ Gestionar usuarios<br>"
                "✔️ Crear o editar partidas<br>"
                "✔️ Configuración del sistema<br>"
                "✔️ Hacer backups<br><br>"
                "Solo para administradores. Disponible en 'Manuales'."
            )
        elif 'faq' in m or 'preguntas' in m or 'frecuentes' in m:
            respuesta = (
                "<strong>FAQ - Preguntas Frecuentes</strong><br><br>"
                "Responde las dudas más comunes:<br><br>"
                "❓ ¿Cómo busco una partida?<br>"
                "❓ ¿Qué es un capítulo arancelario?<br>"
                "❓ ¿Qué documentos necesito?<br>"
                "❓ ¿Cómo se usa el filtro de gravamen?<br>"
                "❓ ¿Cuál es mi licencia?<br><br>"
                "Disponible en 'Manuales'."
            )
        else:
            respuesta = (
                "En <strong>'Manuales'</strong> encontrás:<br><br>"
                "📖 <strong>Guía del Buscador</strong> - Para buscar partidas<br>"
                "📖 <strong>Manual Administrador</strong> - Gestión del sistema<br>"
                "📖 <strong>FAQ</strong> - Preguntas frecuentes<br>"
                "📖 <strong>Ejemplos prácticos</strong> - Casos de uso<br><br>"
                "Todo con instrucciones detalladas."
            )
        sugerencias = ["Ver manuales", "Buscar partida", "FAQ"]
        return respuesta, sugerencias, None


    if 'registro' in m or 'crear cuenta' in m:
        respuesta = (
            "<strong>Para crear una cuenta:</strong><br><br>"
            "1️⃣ Haz clic en 'Crear cuenta'<br>"
            "2️⃣ Completa los datos<br>"
            "3️⃣ Confirma tu correo<br>"
            "4️⃣ ¡Listo! 7 días de prueba<br><br>"
            "Necesitás: nombre, apellido, correo, usuario, contraseña."
        )
        sugerencias = ["¿Qué datos necesito?", "Crear cuenta"]
        return respuesta, sugerencias, None

    if contains_any(m, ['qué datos', 'que datos', 'datos para registrarme']):
        respuesta = (
            "<strong>Datos requeridos:</strong><br><br>"
            "👤 Nombre completo<br>"
            "👤 Apellido<br>"
            "📧 Correo electrónico<br>"
            "👨‍💻 Nombre de usuario<br>"
            "🔒 Contraseña (8+ caracteres)<br><br>"
            "El correo debe ser válido."
        )
        sugerencias = ["Crear cuenta", "¿Puedo registrarme sin correo?"]
        return respuesta, sugerencias, None

    if 'sin correo' in m:
        respuesta = (
            "No, el correo es obligatorio porque:<br><br>"
            "✔️ Confirmar tu identidad<br>"
            "✔️ Recibir notificaciones<br>"
            "✔️ Recuperar tu cuenta<br><br>"
            "Si tienes problemas, contacta soporte."
        )
        sugerencias = ["Crear cuenta", "Contactar soporte"]
        return respuesta, sugerencias, None


    if m == 'mi licencia' or 'licencia' in m or 'caduca' in m:
        if not request or not (hasattr(request, 'user') and request.user.is_authenticated):
            respuesta = "Para ver el estado de tu licencia debes iniciar sesión primero. Luego preguntame 'Mi licencia'."
            sugerencias = ["Iniciar sesión", "Crear cuenta"]
        else:
            try:
                from datetime import date
                from .models import LicenciaTemporal
                licencia = LicenciaTemporal.objects.filter(usuario=request.user, estado=True).order_by('-fecha_fin').first()
                if licencia:
                    hoy = date.today()
                    dias_restantes = (licencia.fecha_fin - hoy).days
                    if dias_restantes > 0:
                        respuesta = (
                            f"✅ <strong>Tu licencia está activa</strong><br><br>"
                            f"Vence el: <strong>{licencia.fecha_fin}</strong><br>"
                            f"Te quedan: <strong>{dias_restantes} días</strong>"
                        )
                    else:
                        respuesta = (
                            f"❌ <strong>Tu licencia expiró</strong><br><br>"
                            f"Fecha: {licencia.fecha_fin}<br><br>"
                            f"Para renovarla usa Soporte."
                        )
                else:
                    respuesta = "⚠️ No se encontró licencia activa. Contacta al administrador."
            except Exception:
                respuesta = "No se pudo obtener información. Intenta más tarde o contacta soporte."
            sugerencias = ["Renovar licencia", "Contactar soporte"]
        return respuesta, sugerencias, None

    if 'qué es la licencia' in m or 'que es la licencia' in m:
        respuesta = (
            "<strong>¿Qué es una licencia?</strong><br><br>"
            "Tu permiso de acceso a SISARM durante un período.<br><br>"
            "📅 <strong>Prueba:</strong> 7 días (nuevos usuarios)<br>"
            "📅 <strong>Pago:</strong> 1, 3 ó 12 meses"
        )
        sugerencias = ["¿Está activa mi licencia?", "Cómo renovarla"]
        return respuesta, sugerencias, None

    if 'renovar' in m or 'como renovarla' in m or 'cómo renovarla' in m:
        respuesta = (
            "<strong>Para renovar:</strong><br><br>"
            "1️⃣ Ve a '<strong>Soporte</strong>'<br>"
            "2️⃣ Indica que necesitas renovación<br>"
            "3️⃣ Responderemos en <24h"
        )
        sugerencias = ["Contactar soporte", "¿Cuánto tardan?"]
        return respuesta, sugerencias, None


    if ('soporte' in m or 'contactar' in m or 'ayuda' in m or m == 'contactar soporte' or
        'problema' in m or 'error' in m or 'falla' in m or 'no funciona' in m or
        'broca' in m or 'reportar' in m or 'reporte' in m or 'bug' in m or 'issue' in m):
        
        if 'whatsapp' in m or 'whats' in m or contains_word_similar(m, 'whatsapp'):
            try:
                wa_number = getattr(settings, 'SUPPORT_WHATSAPP_NUMBER', '59177682918')
                wa_text = getattr(settings, 'SUPPORT_WHATSAPP_TEXT', 'Hola, necesito ayuda con SISARM Search.')
            except Exception:
                wa_number = '59177682918'
                wa_text = 'Hola, necesito ayuda con SISARM Search.'
            try:
                from urllib.parse import quote
                wa_link = f'https://wa.me/{wa_number}?text={quote(wa_text)}'
            except Exception:
                wa_link = f'https://wa.me/{wa_number}'
            respuesta = (
                "El soporte principal es vía formulario (<strong>Soporte</strong>) y correo <strong>soporte@sisarm.com</strong>. "
                "Si prefieres WhatsApp, aquí está nuestro número."
                f" <br><br><a href=\"{wa_link}\" target=\"_blank\" class=\"btn btn-success\">Abrir WhatsApp</a>"
            )
            sugerencias = ["Contactar soporte", "Ver manuales"]
            action = {'open_whatsapp': wa_link, 'action_text': 'Abrir WhatsApp'}
            return respuesta, sugerencias, action
        elif 'tiempo' in m or 'tardan' in m or 'demora' in m or 'cuanto' in m or 'cuánto' in m:
            respuesta = (
                "⏱️ <strong>Tiempo de respuesta:</strong><br><br>"
                "Normalmente: <strong>menos de 24 horas hábiles</strong><br><br>"
                "Si es urgente, indícalo en tu consulta. Priorizamos casos críticos."
            )
            sugerencias = ["Contactar soporte", "¿Atienden por WhatsApp?"]
            return respuesta, sugerencias, None
        else:
            respuesta = (
                "<strong>Formas de contactar:</strong><br><br>"
                "1️⃣ <strong>Formulario:</strong> 'Contactar Soporte' en el menú<br>"
                "2️⃣ <strong>Correo:</strong> soporte@sisarm.com<br>"
                "3️⃣ <strong>WhatsApp:</strong> +591 7 7682918<br><br>"
                "Respuesta en <24h hábiles."
            )
            sugerencias = ["Ir a soporte", "¿Atienden por WhatsApp?"]

            if any(kw in m for kw in ["abre", "abrir", "abrí", "abre la pagina", "abre la página", "abrir soporte"]) or m.strip() in ('contactar soporte', 'contactar'):
                action = {'open_support': '/soporte/', 'action_text': 'Abrir la página de Soporte.'}
                respuesta = "Abriendo Soporte..."
                return respuesta, sugerencias, action

            try:
                if request:
                    request.session['chat_last_action'] = {'open_support': '/soporte/', 'action_text': 'Abrir la página de Soporte.'}
            except Exception:
                pass
            return respuesta, sugerencias, None


    respuesta = (
        "No entendí exactamente tu consulta 😕<br><br>"
        "Puedo ayudarte con:<br><br>"
        "1️⃣ <strong>Buscar partidas</strong> - Por código o descripción<br>"
        "2️⃣ <strong>Ver manuales</strong> - Guías y documentación<br>"
        "3️⃣ <strong>Mi licencia</strong> - Revisar estado de acceso<br>"
        "4️⃣ <strong>Contactar soporte</strong> - Hablar con el equipo<br><br>"
        "Escribe el número (1-4) o cuéntame qué necesitás."
    )
    sugerencias = ["1", "2", "3", "4"]

    return respuesta, sugerencias, None
