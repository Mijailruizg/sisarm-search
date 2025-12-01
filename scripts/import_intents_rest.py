#!/usr/bin/env python3
"""
Script para importar intents a Dialogflow usando REST API
"""
import csv
import json
import argparse
from google.auth import default
from google.auth.transport.requests import Request
import requests

def get_access_token():
    """Obtener token de acceso de Google"""
    from google.oauth2 import service_account
    import os
    
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    credentials.refresh(Request())
    return credentials.token

def create_intent_rest(project_id, language_code, display_name, training_phrases, responses):
    """Crear un intent usando REST API"""
    access_token = get_access_token()
    url = f"https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/intents"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Preparar training phrases
    training_phrases_data = []
    for phrase in training_phrases:
        training_phrases_data.append({
            "type": "EXAMPLE",
            "parts": [{"text": phrase}]
        })
    
    # Preparar mensajes de respuesta
    messages = []
    for response in responses:
        messages.append({
            "text": {
                "text": [response]
            }
        })
    
    payload = {
        "displayName": display_name,
        "languageCode": language_code,
        "priority": 500000,
        "isFallback": False,
        "trainingPhrases": training_phrases_data,
        "messages": messages if messages else [{
            "text": {
                "text": ["Entendido."]
            }
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            print(f"[OK] Intent creado: {display_name}")
            return True
        else:
            print(f"[ERROR] Error creando intent '{display_name}': {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Excepcion al crear intent '{display_name}': {e}")
        return False

def import_from_csv(project_id, csv_path, language_code="es"):
    """Importar intents desde CSV"""
    created = 0
    failed = 0
    
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get('intent_name') or row.get('display_name') or row.get('intent')
            if not name:
                print('[SKIP] Fila sin intent_name, saltando.')
                continue
            
            phrases = [s.strip() for s in row.get('training_phrases','').split('||') if s.strip()]
            responses = [s.strip() for s in row.get('responses','').split('||') if s.strip()]
            
            if not phrases:
                print(f'[SKIP] Intent {name} sin training phrases, saltando.')
                continue
            
            if create_intent_rest(project_id, language_code, name, phrases, responses):
                created += 1
            else:
                failed += 1
    
    print(f"\n[DONE] Importacion completada: {created} intents creados, {failed} errores")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Importar intents CSV a Dialogflow usando REST')
    parser.add_argument('--project', required=True, help='Dialogflow project id')
    parser.add_argument('--file', required=True, help='Path al CSV con intents')
    parser.add_argument('--language', default='es', help='Language code (default: es)')
    args = parser.parse_args()
    
    print(f"Importando intents desde {args.file} al proyecto {args.project}...")
    import_from_csv(args.project, args.file, args.language)
