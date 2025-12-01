import os
import re

try:
    from google.cloud import dialogflow_v2 as dialogflow
except Exception:
    dialogflow = None

import os
import re

try:
    from google.cloud import dialogflow_v2 as dialogflow
except Exception:
    dialogflow = None

PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
LANG = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'es')


# Base de conocimiento de palabras clave y respuestas
KNOWLEDGE_BASE = {
    # saludos y ayudas rápidas
    'hola|buenos|saludos|¿hay.*alguien|como.*estas|como estas|como\\s+esta': """¡Hola! Soy el Asistente de SISARM. Soy tu ayudante para buscar partidas arancelarias, entender cómo funciona el sistema y resolver tus dudas. ¿En qué puedo ayudarte hoy?""",

    # oferta de opciones (menu)
    'ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones': """Soy tu asistente personal. Puedo ayudarte con:

1️⃣ **Buscar Partidas** - Te guío en búsquedas por código o descripción
2️⃣ **Ver Manuales** - Acceso a guías y tutoriales del sistema
3️⃣ **Mi Licencia** - Verificar estado y renovación
4️⃣ **Contactar Soporte** - Conectarte con el equipo técnico

Escribe el número (por ejemplo, `1`) o la opción que prefieras.
""",

    # qué es / objetivo
    'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system|función|qué.*hace|para.*qué.*sirve': """SISARM es un buscador inteligente de partidas arancelarias. Te ayuda a:
- Buscar códigos de partidas arancelarias por descripción o código
- Filtrar por capítulo, sección o requisitos aduanales
- Ver documentos requeridos para cada partida
- Gestionar tu licencia de usuario

Es una herramienta esencial para despachantes aduanales, operadores de comercio exterior y profesionales del sector logístico.
""",

    # búsqueda
    'buscar|search|cómo.*busco|como.*busco|busca.*partida|partida': """Para buscar una partida arancelaria:
1. Ve a **Buscar Partidas** en el menú principal
2. Puedes buscar de dos formas:
   - **Por Código**: Ingresa el código de partida (ej: 010121)
   - **Por Descripción**: Escribe qué es (ej: 'leche en polvo', 'carne de res')
3. Presiona Buscar o Enter
"""Módulo cliente de fallback para Dialogflow: intenta usar Dialogflow y,
si falla, responde con una base de conocimiento local definida por
palabras clave.

Este archivo contiene solo texto en UTF-8 y patrones simples en español.
"""

import os
import re

try:
    from google.cloud import dialogflow_v2 as dialogflow
except Exception:
    dialogflow = None

PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
LANG = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'es')


# Base de conocimiento de palabras clave y respuestas
KNOWLEDGE_BASE = {
    'hola|buenos|saludos|¿hay.*alguien|como.*estas|como estas|como\\s+esta': """¡Hola! Soy el Asistente de SISARM. Soy tu ayudante para buscar partidas arancelarias, entender cómo funciona el sistema y resolver tus dudas. ¿En qué puedo ayudarte hoy?""",
    'ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones': """Soy tu asistente personal. Puedo ayudarte con:

1️⃣ Buscar Partidas
2️⃣ Ver Manuales
3️⃣ Mi Licencia
4️⃣ Contactar Soporte

Escribe el número (por ejemplo, `1`) o la opción que prefieras.
""",
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


DEFAULT_RESPONSE = """Entiendo que quieres más información. Puedo ayudarte con:

- ¿Qué es SISARM?
- Cómo buscar
- Cómo filtrar
- Licencia
- Documentos
- Soporte

Escribe la opción o tu pregunta."""


def _ensure_available():
    if dialogflow is None:
        raise RuntimeError('google-cloud-dialogflow no está instalado. Instala con pip install google-cloud-dialogflow')
    if not PROJECT_ID:
        raise RuntimeError('DIALOGFLOW_PROJECT_ID no configurado en variables de entorno.')


def _get_response_from_keywords(text: str) -> str:
        'hola|buenos|saludos|¿hay.*alguien|como.*estas|como estas|como\\s+esta': """¡Hola! Soy el Asistente de SISARM. Soy tu ayudante para buscar partidas arancelarias, entender cómo funciona el sistema y resolver tus dudas. ¿En qué puedo ayudarte hoy?""",
        'ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones': """Soy tu asistente personal. Puedo ayudarte con:

    1️⃣ Buscar Partidas
    2️⃣ Ver Manuales
    3️⃣ Mi Licencia
    4️⃣ Contactar Soporte

    Escribe el número (por ejemplo, `1`) o la opción que prefieras.
    """,
        'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system|función|qué.*hace|para.*qué.*sirve': """SISARM es un buscador inteligente de partidas arancelarias. Te ayuda a buscar códigos por descripción o código, filtrar por capítulos y ver documentación requerida para cada partida.""",
        'buscar|search|cómo.*busco|como.*busco|busca.*partida|partida': """Puedes buscar por código (ej: 010121) o por descripción (ej: 'carne de res'). Usa los filtros para refinar resultados.""",
        '010121|carne|bovino|ejemplo.*búsqueda': """Ejemplo: busca '010121' o 'carne de res' para ver la partida correspondiente y documentos requeridos.""",
        'filtro|filtros|capítulo|capitulo|gravamen|filtrar': """Usa los filtros en la interfaz para limitar por capítulo, gravamen y requisitos.""",
        'documento|documentos|requisito|requisitos|certificado|documentación': """En la vista de detalle de cada partida verás la lista de documentos requeridos: certificados, permisos, etc.""",
        'licencia|vence|estado.*licencia|renovar|reactivar': """Para renovar la licencia, abre Soporte y envía tus datos; el equipo responde en menos de 24 horas hábiles.""",
        'soporte|contacto|ayuda.*humana|equipo|problema': """Completa el formulario de Soporte con tu nombre, correo y descripción del problema y el equipo te responderá.""",
        'manual|guia|guías|guia|tutorial|documentación|como.*usar': """En la sección Manuales encontrarás guías prácticas, FAQ y ejemplos de búsqueda.""",
        'exportar|excel|descargar|csv|pdf': """Usa el botón Descargar/Exportar en resultados para obtener Excel, CSV o PDF con los campos principales.""",
    text_lower = text.lower()

    # Normalizar el texto (eliminar acentos)
    def normalize(s):
        return re.sub(r'[áéíóúÁÉÍÓÚ]', lambda m: {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u'
        }[m.group()], s)

    text_normalized = normalize(text_lower)

    # Si el usuario envía sólo un número, mapear a menú
    digits = re.fullmatch(r"\s*(\d+)\s*", text_normalized)
    if digits:
        n = int(digits.group(1))
        menu_map = {
            1: 'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system',
            2: 'manual|guia|guías|guia|tutorial|documentación|como.*usar',
            3: 'licencia|vence|estado.*licencia|renovar|reactivar',
            4: 'soporte|contacto|ayuda.*humana|equipo|problema'
        }
        pattern_key = menu_map.get(n)
        if pattern_key:
            for k, resp in KNOWLEDGE_BASE.items():
                if pattern_key in k:
                    return resp

    # Buscar coincidencias simples en KNOWLEDGE_BASE
    best_match = None
    best_score = 0
    for keywords, response in KNOWLEDGE_BASE.items():
        for keyword in keywords.split('|'):
            keyword = keyword.strip()
            if not keyword:
                continue
            try:
                if re.search(keyword, text_normalized):
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = response
            except re.error:
                if keyword in text_normalized:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = response

    return best_match or DEFAULT_RESPONSE


def get_chat_response(text: str, session_id: str = None, language_code: str = None) -> str:
    """Intenta obtener respuesta de Dialogflow; si falla, usa fallback local."""
    try:
        _ensure_available()
        if not session_id:
            session_id = os.getenv('DIALOGFLOW_SESSION_ID', 'default-session')
        language = language_code or LANG

        client = dialogflow.SessionsClient()
        session = client.session_path(PROJECT_ID, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=language)
        query_input = dialogflow.QueryInput(text=text_input)
        response = client.detect_intent(request={"session": session, "query_input": query_input})

        fulfillment = response.query_result.fulfillment_text or ''
        if fulfillment.strip():
            return fulfillment.strip()
        return _get_response_from_keywords(text)
    except Exception as e:
        print(f"⚠️  Dialogflow no disponible: {e}")
        return _get_response_from_keywords(text)


def stream_chat_response(text: str, session_id: str = None, language_code: str = None):
    resp = get_chat_response(text, session_id=session_id, language_code=language_code)
    yield resp

    'exportar|excel|descargar|csv|pdf': """Para **exportar a Excel**:

1. Realiza una búsqueda en Buscar Partidas
2. Haz clic en el botón **Descargar/Exportar** (generalmente en la esquina superior)
3. Selecciona el formato: Excel, PDF o CSV
4. Se descargará un archivo con los resultados filtrados

El archivo incluye:
- Código de partida
- Descripción
- Aranceles
- Requisitos
- Documentación necesaria

¿Necesitas exportar búsquedas específicas?""",
}
    
    if re.search(r'\bsoporte|\bcontacto|\bequipo|\bproblema', text_normalized):
        return KNOWLEDGE_BASE['soporte|contacto|ayuda.*humana|equipo|problema']
    
    if re.search(r'\bbuscar|\bcómo|\bsearch|\bpartida', text_normalized):
        return KNOWLEDGE_BASE['buscar|search|cómo.*busco|busca.*partida']
    
    if re.search(r'\bsirve|\bfuncion|\bqué.*hace|\bpara', text_normalized):
        return KNOWLEDGE_BASE['system|función|qué.*hace|para.*qué.*sirve']
    
    if re.search(r'\bayuda|\bqué.*puedes|\bfunciones|\bopciones', text_normalized):
        return KNOWLEDGE_BASE['ayuda|qué.*puedes.*hacer|opciones|me.*puedes.*ayudar|funciones']
    
        # 1) Si el usuario envía solo un número (ej. '1'), mapearlo a las opciones del menú
        digits = re.fullmatch(r"\s*(\d+)\s*", text_normalized)
        if digits:
            n = int(digits.group(1))
            menu_map = {
                1: 'que\\s+es|qué\\s+es|que\\s+es\\s+sisarm|qué\\s+es\\s+sisarm|system',
                2: 'manual|guia|guías|guia|tutorial|documentación|como.*usar',
                3: 'licencia|vence|estado.*licencia|renovar|reactivar',
                4: 'soporte|contacto|ayuda.*humana|equipo|problema'
            }
            pattern_key = menu_map.get(n)
            if pattern_key:
                # buscar la respuesta asociada en KNOWLEDGE_BASE
                for k, resp in KNOWLEDGE_BASE.items():
                    if k == pattern_key or pattern_key in k:
                        return resp

        # 2) Buscar coincidencias de palabras clave por prioridad
        best_match = None
        best_score = 0
        for keywords, response in KNOWLEDGE_BASE.items():
            # probar cada alternativa dentro de la clave separada por |
            for keyword in keywords.split('|'):
                keyword = keyword.strip()
                if not keyword:
                    continue
                try:
                    if re.search(keyword, text_normalized):
                        # score por longitud de patrón (más específico = mayor puntuación)
                        score = len(keyword)
                        if score > best_score:
                            best_score = score
                            best_match = response
                except re.error:
                    # si el patrón no es un regex válido, hacer búsqueda literal
                    if keyword in text_normalized:
                        score = len(keyword)
                        if score > best_score:
                            best_score = score
                            best_match = response

        return best_match or DEFAULT_RESPONSE


def get_chat_response(text: str, session_id: str = None, language_code: str = None) -> str:
    """Envía `text` a Dialogflow (detect_intent) y devuelve el texto de fulfillment.
    
    Si Dialogflow no está disponible o no encuentra un intent, usa búsqueda por palabras clave.
    
    Nota: requiere credenciales de Google Cloud (GOOGLE_APPLICATION_CREDENTIALS) y
    DIALOGFLOW_PROJECT_ID configurado en las variables de entorno.
    """
    
    # Intentar obtener respuesta de Dialogflow
    try:
        _ensure_available()
        if not session_id:
            session_id = os.getenv('DIALOGFLOW_SESSION_ID', 'default-session')
        language = language_code or LANG
        
        client = dialogflow.SessionsClient()
        session = client.session_path(PROJECT_ID, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=language)
        query_input = dialogflow.QueryInput(text=text_input)
        response = client.detect_intent(request={"session": session, "query_input": query_input})
        
        fulfillment = response.query_result.fulfillment_text or ''
        
        # Si Dialogflow devuelve respuesta, usarla
        if fulfillment.strip():
            return fulfillment.strip()
        
        # Si no hay respuesta de Dialogflow, usar palabras clave
        return _get_response_from_keywords(text)
    
    except Exception as e:
        # Si hay error (conexión, permisos, etc.), usar palabras clave
        print(f"⚠️  Dialogflow no disponible: {str(e)}")
        return _get_response_from_keywords(text)


def stream_chat_response(text: str, session_id: str = None, language_code: str = None):
    """Dialogflow no ofrece streaming token a token; devolvemos la respuesta completa en un solo yield.
    Esto mantiene la misma firma que el cliente anterior para compatibilidad.
    """
    resp = get_chat_response(text, session_id=session_id, language_code=language_code)
    yield resp
