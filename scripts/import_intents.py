# scripts/import_intents.py
import csv
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

def create_intent(project_id, display_name, phrases, responses):
    creds = _load_credentials()
    client = dialogflow.IntentsClient(credentials=creds)
    parent = f"projects/{project_id}/agent"
    training_phrases = []
    for p in phrases:
        training_phrases.append(dialogflow.types.Intent.TrainingPhrase(parts=[dialogflow.types.Intent.TrainingPhrase.Part(text=p)]))
    messages = []
    for r in responses:
        messages.append(dialogflow.types.Intent.Message(text=dialogflow.types.Intent.Message.Text(text=[r])))
    intent = dialogflow.types.Intent(display_name=display_name, training_phrases=training_phrases, messages=messages)
    resp = client.create_intent(parent=parent, intent=intent)
    print(f'Created intent: {resp.display_name}')

def import_from_csv(project_id, csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get('intent_name') or row.get('display_name') or row.get('intent')
            if not name:
                print('Fila sin intent_name, saltando.')
                continue
            phrases = [s.strip() for s in row.get('training_phrases','').split('||') if s.strip()]
            responses = [s.strip() for s in row.get('responses','').split('||') if s.strip()]
            if not phrases:
                print(f'Intent {name} sin training phrases, saltando.')
                continue
            create_intent(project_id, name, phrases, responses)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importar intents CSV a Dialogflow ES')
    parser.add_argument('--project', required=True, help='Dialogflow project id')
    parser.add_argument('--file', required=True, help='Path al CSV con intents')
    parser.add_argument('--credentials', required=False, help='Path al JSON de credenciales (service account)')
    args = parser.parse_args()
    if args.credentials:
        _load_credentials(args.credentials)
    else:
        _load_credentials()
    import_from_csv(args.project, args.file)
