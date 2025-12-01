import os
import re

PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
LANG = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'es')

KNOWLEDGE_BASE = {
    'hola|buenos|saludos|hay.*alguien|como.*estas|como estas|como\\s+esta':
        """¡Hola! Soy el Asistente de SISARM. Soy tu ayudante para buscar partidas arancelarias, entender cómo funciona el sistema y resolver tus dudas. ¿En qué puedo ayudarte hoy?""",
    'ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones':
        """Soy tu asistente personal. Puedo ayudarte con:

1️⃣ Buscar Partidas
2️⃣ Ver Manuales
3️⃣ Mi Licencia
4️⃣ Contactar Soporte

Escribe el número (por ejemplo, `1`) o la opción que prefieras.""",
    'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system|función|qué.*hace|para.*qué.*sirve':
        """SISARM es un buscador inteligente de partidas arancelarias. Te ayuda a buscar códigos por descripción o código, filtrar por capítulos y ver documentación requerida para cada partida.""",
    'buscar|search|cómo.*busco|como.*busco|busca.*partida|partida':
        """Puedes buscar por código (ej: 010121) o por descripción (ej: 'carne de res'). Usa los filtros para refinar resultados.""",
    '010121|carne|bovino|ejemplo.*búsqueda':
        """Ejemplo: busca '010121' o 'carne de res' para ver la partida correspondiente y documentos requeridos.""",
    'filtro|filtros|capítulo|capitulo|gravamen|filtrar':
        """Usa los filtros en la interfaz para limitar por capítulo, gravamen y requisitos.""",
    'documento|documentos|requisito|requisitos|certificado|documentación':
        """En la vista de detalle de cada partida verás la lista de documentos requeridos: certificados, permisos, etc.""",
    'licencia|vence|estado.*licencia|renovar|reactivar':
        """Para renovar la licencia, abre Soporte y envía tus datos; el equipo responde en menos de 24 horas hábiles.""",
    'soporte|contacto|ayuda.*humana|equipo|problema':
        """Completa el formulario de Soporte con tu nombre, correo y descripción del problema y el equipo te responderá.""",
    'manual|guia|guías|guia|tutorial|documentación|como.*usar':
        """En la sección Manuales encontrarás guías prácticas, FAQ y ejemplos de búsqueda.""",
    'exportar|excel|descargar|csv|pdf':
        """Usa el botón Descargar/Exportar en resultados para obtener Excel, CSV o PDF con los campos principales.""",
}

DEFAULT_RESPONSE = """Entiendo que quieres más información. Puedo ayudarte con:

- ¿Qué es SISARM?
- Cómo buscar
- Cómo filtrar
- Licencia
- Documentos
- Soporte

Escribe la opción o tu pregunta."""


def _normalize(s: str) -> str:
    if not s:
        return ''
    s_low = s.lower()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
        'ñ': 'n', 'Ñ': 'n'
    }
    for k, v in replacements.items():
        s_low = s_low.replace(k, v)
    return s_low


def _get_response_from_keywords(text: str) -> str:
    text_n = _normalize(text or '')

    # número simple -> menú
    m = re.fullmatch(r"\s*(\d+)\s*", text_n)
    if m:
        n = int(m.group(1))
        menu_map = {
            1: 'que\\s+es',
            2: 'manual|guia|guías|guia',
            3: 'licencia',
            4: 'soporte|contacto'
        }
        pat = menu_map.get(n)
        if pat:
            for k, v in KNOWLEDGE_BASE.items():
                if pat in k:
                    return v

    best = None
    best_score = 0
    for keys, resp in KNOWLEDGE_BASE.items():
        for key in keys.split('|'):
            key = key.strip()
            if not key:
                continue
            try:
                if re.search(key, text_n):
                    score = len(key)
                    if score > best_score:
                        best_score = score
                        best = resp
            except re.error:
                if key in text_n:
                    score = len(key)
                    if score > best_score:
                        best_score = score
                        best = resp

    return best or DEFAULT_RESPONSE


# API público simple
def get_chat_response(text: str, session_id: str = None, language_code: str = None) -> str:
    return _get_response_from_keywords(text)


def stream_chat_response(text: str, session_id: str = None, language_code: str = None):
    yield get_chat_response(text, session_id=session_id, language_code=language_code)
import os
import re

PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
LANG = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'es')

KNOWLEDGE_BASE = {
    'hola|buenos|saludos|¿hay.*alguien|como.*estas|como estas|como\\s+esta': """¡Hola! Soy el Asistente de SISARM. Soy tu ayudante para buscar partidas arancelarias, entender cómo funciona el sistema y resolver tus dudas. ¿En qué puedo ayudarte hoy?""",
    'ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones': """Soy tu asistente personal. Puedo ayudarte con:\n\n1️⃣ Buscar Partidas\n2️⃣ Ver Manuales\n3️⃣ Mi Licencia\n4️⃣ Contactar Soporte\n\nEscribe el número (por ejemplo, `1`) o la opción que prefieras.""",
    'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system|función|qué.*hace|para.*qué.*sirve': """SISARM es un buscador inteligente de partidas arancelarias. Te ayuda a buscar códigos por descripción o código, filtrar por capítulos y ver documentación requerida para cada partida.""",
    'buscar|search|cómo.*busco|como.*busco|busca.*partida|partida': """Puedes buscar por código (ej: 010121) o por descripción (ej: 'carne de res'). Usa los filtros para refinar resultados.""",
    '010121|carne|bovino|ejemplo.*búsqueda': """Ejemplo: busca '010121' o 'carne de res' para ver la partida correspondiente y documentos requeridos.""",
    'filtro|filtros|capítulo|capitulo|gravamen|filtrar': """Usa los filtros en la interfaz para limitar por capítulo, gravamen y requisitos.""",
    'documento|documentos|requisito|requisitos|certificado|documentación': """En la vista de detalle de cada partida verás la lista de documentos requeridos: certificados, permisos, etc.""",
    'licencia|vence|estado.*licencia|renovar|reactivar': """Para renovar la licencia, abre Soporte y envía tus datos; el equipo responde en menos de 24 horas hábiles.""",
    'soporte|contacto|ayuda.*humana|equipo|problema': """Completa el formulario de Soporte con tu nombre, correo y descripción del problema y el equipo te responderá.""",
    'manual|guia|guías|guia|tutorial|documentación|como.*usar': """En la sección Manuales encontrarás guías prácticas, FAQ y ejemplos de búsqueda.""",
    'exportar|excel|descargar|csv|pdf': """Usa el botón Descargar/Exportar en resultados para obtener Excel, CSV o PDF con los campos principales.""",
}

DEFAULT_RESPONSE = """Entiendo que quieres más información. Puedo ayudarte con:\n\n- ¿Qué es SISARM?\n- Cómo buscar\n- Cómo filtrar\n- Licencia\n- Documentos\n- Soporte\n\nEscribe la opción o tu pregunta."""


def _normalize(s: str) -> str:
    return re.sub(r'[áéíóúÁÉÍÓÚ]', lambda m: {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u'
    }[m.group()], s.lower())


def _get_response_from_keywords(text: str) -> str:
    text_n = _normalize(text)

    # número simple -> menú
    m = re.fullmatch(r"\s*(\d+)\s*", text_n)
    if m:
        n = int(m.group(1))
        menu_map = {
            1: 'que\\s+es',
            2: 'manual|guia|guías|guia',
            3: 'licencia',
            4: 'soporte|contacto'
        }
        pat = menu_map.get(n)
        if pat:
            for k, v in KNOWLEDGE_BASE.items():
                if pat in k:
                    return v

    best = None
    best_score = 0
    for keys, resp in KNOWLEDGE_BASE.items():
        for key in keys.split('|'):
            key = key.strip()
            if not key:
                continue
            try:
                if re.search(key, text_n):
                    score = len(key)
                    if score > best_score:
                        best_score = score
                        best = resp
            except re.error:
                if key in text_n:
                    score = len(key)
                    if score > best_score:
                        best_score = score
                        best = resp

    return best or DEFAULT_RESPONSE


# API público simple
def get_chat_response(text: str, session_id: str = None, language_code: str = None) -> str:
    return _get_response_from_keywords(text)


def stream_chat_response(text: str, session_id: str = None, language_code: str = None):
    yield get_chat_response(text, session_id=session_id, language_code=language_code)
