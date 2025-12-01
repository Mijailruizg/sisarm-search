#!/usr/bin/env python3
import os
import argparse
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

def create_kb_and_upload(project_id, kb_display_name, docs_dir):
    creds = _load_credentials()
    kb_client = dialogflow.KnowledgeBasesClient(credentials=creds)
    parent = f"projects/{project_id}"
    kb = dialogflow.types.KnowledgeBase(display_name=kb_display_name)
    kb_response = kb_client.create_knowledge_base(parent=parent, knowledge_base=kb)
    print("Created KB:", kb_response.name)
    kb_name = kb_response.name  # projects/{project_id}/knowledgeBases/{id}

    documents_client = dialogflow.DocumentsClient(credentials=creds)
    for filename in os.listdir(docs_dir):
        path = os.path.join(docs_dir, filename)
        if not os.path.isfile(path):
            continue
        mime_type = 'text/plain'
        if filename.lower().endswith('.html'):
            mime_type = 'text/html'
        doc = dialogflow.types.Document(display_name=filename, mime_type=mime_type, knowledge_types=[dialogflow.types.Document.KnowledgeType.FAQ])
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        # create_document accepts a document resource; here we pass content directly
        op = documents_client.create_document(parent=kb_name, document=doc, content=content)
        print(f'Uploading {filename} ... (operation started)')
        result = op.result(timeout=120)
        print(f'Uploaded {filename}: {result.name}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--kb', default='SISARM-KB')
    parser.add_argument('--docs', default='./dialogflow/kb_docs')
    parser.add_argument('--credentials', required=False, help='Path al JSON de credenciales (service account)')
    args = parser.parse_args()
    if args.credentials:
        _load_credentials(args.credentials)
    else:
        _load_credentials()

    if not os.path.isdir(args.docs):
        print('Docs directory not found:', args.docs)
        raise SystemExit(1)
    create_kb_and_upload(args.project, args.kb, args.docs)
