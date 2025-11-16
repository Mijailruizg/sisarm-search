import os

try:
    from google.cloud import dialogflow_v2 as dialogflow
except Exception:
    dialogflow = None

PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
LANG = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'es')


def _ensure_available():
    if dialogflow is None:
        raise RuntimeError('google-cloud-dialogflow no está instalado. Instala con pip install google-cloud-dialogflow')
    if not PROJECT_ID:
        raise RuntimeError('DIALOGFLOW_PROJECT_ID no configurado en variables de entorno.')


def get_chat_response(text: str, session_id: str = None, language_code: str = None) -> str:
    """Envía `text` a Dialogflow (detect_intent) y devuelve el texto de fulfillment.

    Nota: requiere credenciales de Google Cloud (GOOGLE_APPLICATION_CREDENTIALS) y
    DIALOGFLOW_PROJECT_ID configurado en las variables de entorno.
    """
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
    return fulfillment.strip()


def stream_chat_response(text: str, session_id: str = None, language_code: str = None):
    """Dialogflow no ofrece streaming token a token; devolvemos la respuesta completa en un solo yield.
    Esto mantiene la misma firma que el cliente anterior para compatibilidad.
    """
    resp = get_chat_response(text, session_id=session_id, language_code=language_code)
    yield resp
