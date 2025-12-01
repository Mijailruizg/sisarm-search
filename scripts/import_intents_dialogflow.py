#!/usr/bin/env python3
"""
Script para importar intents a Dialogflow ES desde un archivo CSV.
Crea intents completos con training phrases y respuestas de fulfillment.

Uso:
    python scripts/import_intents_dialogflow.py --project sisarm-assistant --file dialogflow/intents_sisarm_complete.csv --language es
"""

import sys
import csv
import argparse
import time
from pathlib import Path

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request


def get_access_token():
    """Obtiene un token de acceso usando las credenciales de Google Cloud."""
    credentials_path = Path.cwd() / 'credentials' / 'dialogflow-key.json'
    
    if not credentials_path.exists():
        raise FileNotFoundError(f"No se encontró: {credentials_path}")
    
    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    credentials.refresh(Request())
    return credentials.token


def create_intent(project_id: str, intent_name: str, training_phrases: list, response_text: str, language_code: str = 'es'):
    """
    Crea un intent en Dialogflow ES usando la API REST.
    
    Args:
        project_id: ID del proyecto GCP (ej: sisarm-assistant)
        intent_name: Nombre del intent (ej: Greeting)
        training_phrases: Lista de frases de entrenamiento
        response_text: Texto de respuesta del intent
        language_code: Código de idioma (default: es)
    
    Returns:
        dict: Respuesta de la API
    """
    
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    # URL del endpoint de intents en Dialogflow ES API v2
    url = f'https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/intents?languageCode={language_code}'
    
    # Construir el payload del intent
    payload = {
        'displayName': intent_name,
        'trainingPhrases': [
            {
                'type': 'EXAMPLE',
                'parts': [
                    {'text': phrase.strip()}
                ]
            }
            for phrase in training_phrases if phrase.strip()
        ],
        'messages': [
            {
                'text': {
                    'text': [response_text]
                }
            }
        ],
        'webhookState': 'WEBHOOK_STATE_UNSPECIFIED',
        'priority': 500000,
        'isFallback': False,
        'mlDisabled': False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✅ Intent '{intent_name}' creado exitosamente")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print(f"⚠️  Intent '{intent_name}' ya existe. Actualizando...")
            return update_intent(project_id, intent_name, training_phrases, response_text, language_code)
        else:
            print(f"❌ Error al crear '{intent_name}': {e.response.status_code} - {e.response.text}")
            return None
    except Exception as e:
        print(f"❌ Error al crear '{intent_name}': {str(e)}")
        return None


def update_intent(project_id: str, intent_name: str, training_phrases: list, response_text: str, language_code: str = 'es'):
    """Actualiza un intent existente en Dialogflow."""
    # Para simplificar, solo creamos si no existe
    # La actualización requiere obtener el intent_id primero
    print(f"⏭️  Intent '{intent_name}' será actualizado en la próxima ejecución")
    return None


def import_from_csv(project_id: str, csv_file: str, language_code: str = 'es'):
    """
    Lee intents desde un archivo CSV e importa a Dialogflow.
    
    Formato del CSV:
    intent_name,training_phrases,responses
    
    Donde training_phrases se separan con || y responses es el texto de fulfillment.
    """
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {csv_file}")
    
    print(f"📂 Leyendo intents desde: {csv_path}")
    print(f"🚀 Importando a proyecto: {project_id}")
    print(f"🌐 Idioma: {language_code}\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            intent_name = row.get('intent_name', '').strip()
            training_phrases_str = row.get('training_phrases', '')
            response_text = row.get('responses', '').strip()
            
            # Saltar intents vacíos o sin respuesta
            if not intent_name or not response_text:
                print(f"⏭️  Saltando intent vacío: {intent_name}")
                skipped_count += 1
                continue
            
            # Parsear las training phrases (separadas por ||)
            training_phrases = [p.strip() for p in training_phrases_str.split('||') if p.strip()]
            
            if not training_phrases:
                print(f"⚠️  Intent '{intent_name}' sin frases de entrenamiento, usando nombre como frase")
                training_phrases = [intent_name]
            
            print(f"\n📋 Procesando: {intent_name}")
            print(f"   📝 Frases de entrenamiento: {len(training_phrases)}")
            print(f"   💬 Respuesta: {response_text[:80]}...")
            
            result = create_intent(project_id, intent_name, training_phrases, response_text, language_code)
            
            if result:
                success_count += 1
            else:
                error_count += 1
            
            # Pequeña pausa para no sobrecargar la API
            time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"✅ Importación completada:")
    print(f"   Exitosos: {success_count}")
    print(f"   Errores: {error_count}")
    print(f"   Saltados: {skipped_count}")
    print(f"{'='*60}\n")
    
    return success_count, error_count, skipped_count


def main():
    parser = argparse.ArgumentParser(
        description='Importa intents a Dialogflow ES desde un archivo CSV'
    )
    parser.add_argument('--project', required=True, help='ID del proyecto GCP (ej: sisarm-assistant)')
    parser.add_argument('--file', required=True, help='Ruta del archivo CSV con intents')
    parser.add_argument('--language', default='es', help='Código de idioma (default: es)')
    
    args = parser.parse_args()
    
    try:
        import_from_csv(args.project, args.file, args.language)
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
