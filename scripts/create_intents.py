#!/usr/bin/env python3
"""
Script para crear intents en Dialogflow ES usando la API REST v2 beta.
Usa credenciales de cuenta de servicio para autenticación.

Este script intenta crear intents y maneja los errores de permisos gracefully.
"""

import json
import csv
import time
import requests
from pathlib import Path
from google.oauth2 import service_account
from google.auth.transport.requests import Request


def get_access_token():
    """Obtiene token de acceso de Google Cloud."""
    creds_path = Path('credentials/dialogflow-key.json')
    if not creds_path.exists():
        raise FileNotFoundError(f"No encontrado: {creds_path}")
    
    credentials = service_account.Credentials.from_service_account_file(
        str(creds_path),
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    credentials.refresh(Request())
    return credentials.token


def import_intents_from_csv(project_id: str, csv_file: str, language_code: str = 'es'):
    """Importa intents desde CSV a Dialogflow ES."""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No encontrado: {csv_file}")
    
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    print(f"📂 Leyendo intents de: {csv_path}")
    print(f"🚀 Importando a: {project_id}")
    print(f"🌐 Idioma: {language_code}\n")
    
    success = 0
    errors = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        intents_data = list(reader)
    
    # Primero, obtener la lista de intents existentes
    get_url = f'https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/intents?languageCode={language_code}'
    
    try:
        resp = requests.get(get_url, headers=headers, timeout=30)
        existing_intents = {}
        if resp.status_code == 200:
            data = resp.json()
            for intent in data.get('intents', []):
                existing_intents[intent['displayName']] = intent['name']
            print(f"✅ {len(existing_intents)} intents existentes encontrados\n")
    except Exception as e:
        print(f"⚠️  No se pudo verificar intents existentes: {e}\n")
        existing_intents = {}
    
    # Crear intents
    for idx, row in enumerate(intents_data, 1):
        intent_name = row.get('intent_name', '').strip()
        training_phrases_str = row.get('training_phrases', '')
        response_text = row.get('responses', '').strip()
        
        if not intent_name or not response_text:
            continue
        
        training_phrases = [p.strip() for p in training_phrases_str.split('||') if p.strip()]
        
        if not training_phrases:
            training_phrases = [intent_name]
        
        print(f"[{idx}] {intent_name}")
        print(f"    📝 {len(training_phrases)} frases")
        
        # Si el intent ya existe, saltarlo
        if intent_name in existing_intents:
            print(f"    ✓ Ya existe\n")
            success += 1
            continue
        
        # Construir payload
        payload = {
            'displayName': intent_name,
            'trainingPhrases': [
                {
                    'type': 'EXAMPLE',
                    'parts': [{'text': phrase}]
                }
                for phrase in training_phrases
            ],
            'messages': [
                {
                    'text': {
                        'text': [response_text]
                    }
                }
            ],
            'priority': 500000,
            'isFallback': False,
            'mlDisabled': False
        }
        
        # Crear intent
        url = f'https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/intents?languageCode={language_code}'
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"    ✅ Creado\n")
                success += 1
            elif response.status_code == 409:
                print(f"    ✓ Ya existe (409)\n")
                success += 1
            else:
                error_msg = response.json().get('error', {}).get('message', response.text)
                print(f"    ❌ Error {response.status_code}: {error_msg}\n")
                errors += 1
                
                # Mostrar detalles de permiso denegado
                if response.status_code == 403:
                    print("    💡 Necesitas permisos 'dialogflow.intents.create'")
                    print("    📝 Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts")
                    print("    📝 Selecciona: dialogflow-agent")
                    print("    📝 Agrega rol: 'Dialogflow API Editor'\n")
        
        except Exception as e:
            print(f"    ❌ Excepción: {str(e)}\n")
            errors += 1
        
        # Pausa entre requests
        time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"✅ Exitosos: {success}")
    print(f"❌ Errores: {errors}")
    print(f"{'='*60}\n")
    
    if errors > 0:
        print("💡 PRÓXIMOS PASOS:")
        print("1. Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("2. Selecciona proyecto: SISARM Assistant")
        print("3. Abre cuenta: dialogflow-agent")
        print("4. Pestaña ROLES → Asignar roles")
        print("5. Busca y selecciona: 'Dialogflow API Editor'")
        print("6. Haz clic: GUARDAR")
        print("7. Espera 30-60 segundos")
        print("8. Ejecuta este script nuevamente\n")
    
    return success, errors


if __name__ == '__main__':
    try:
        success, errors = import_intents_from_csv(
            'sisarm-assistant',
            'dialogflow/intents_sisarm_complete.csv',
            'es'
        )
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import sys
        sys.exit(1)
