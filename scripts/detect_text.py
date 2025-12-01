#!/usr/bin/env python3
import argparse
import os
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account

_CREDENTIALS = None

def _load_credentials(path=None):
    global _CREDENTIALS
    if _CREDENTIALS:
        return _CREDENTIALS
    path = path or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not path:
        raise SystemExit('GOOGLE_APPLICATION_CREDENTIALS no definido; pasa --credentials o exporta la variable de entorno.')
    if not os.path.isfile(path):
        raise SystemExit(f'Archivo de credenciales no encontrado: {path}')
    creds = service_account.Credentials.from_service_account_file(path)
    _CREDENTIALS = creds
    return creds

def detect_text(project_id, session_id, text, language='es'):
    creds = _load_credentials()
    session_client = dialogflow.SessionsClient(credentials=creds)
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Response:", response.query_result.fulfillment_text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--session', default='test-session')
    parser.add_argument('--text', required=True)
    parser.add_argument('--credentials', required=False, help='Path al JSON de credenciales (service account)')
    args = parser.parse_args()
    if args.credentials:
        _load_credentials(args.credentials)
    else:
        _load_credentials()
    detect_text(args.project, args.session, args.text)
