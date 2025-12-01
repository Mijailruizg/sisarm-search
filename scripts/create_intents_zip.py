#!/usr/bin/env python3
"""
Genera un archivo Zip con todos los intents en el formato que Dialogflow espera.
Este archivo puede ser importado directamente en Dialogflow usando la consola.
"""

import csv
import json
import zipfile
from pathlib import Path
from io import StringIO


def create_intents_zip(csv_file: str, output_zip: str = 'dialogflow/intents_sisarm.zip'):
    """Crea un archivo ZIP con los intents en formato Dialogflow."""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No encontrado: {csv_file}")
    
    zip_path = Path(output_zip)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Leer intents del CSV
    intents_list = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            intent_name = row.get('intent_name', '').strip()
            training_phrases_str = row.get('training_phrases', '')
            response_text = row.get('responses', '').strip()
            
            if not intent_name or not response_text:
                continue
            
            training_phrases = [p.strip() for p in training_phrases_str.split('||') if p.strip()]
            intents_list.append({
                'displayName': intent_name,
                'trainingPhrases': training_phrases,
                'responses': [response_text]
            })
    
    # Crear archivo ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, intent in enumerate(intents_list, 1):
            # Crear directorio para cada intent
            intent_dir = f"agent/{intent['displayName']}"
            
            # Archivo usersays_es.json (training phrases)
            usersays_data = []
            for phrase in intent['trainingPhrases']:
                usersays_data.append({
                    'id': f'{idx}-{len(usersays_data)}',
                    'data': [
                        {
                            'text': phrase,
                            'userDefined': False
                        }
                    ],
                    'isTemplate': False,
                    'count': 0,
                    'lastModified': 0
                })
            
            zf.writestr(
                f"{intent_dir}/usersays_es.json",
                json.dumps(usersays_data, indent=2, ensure_ascii=False)
            )
            
            # Archivo intent.json (metadata y respuestas)
            intent_data = {
                'id': f'{idx}',
                'name': intent['displayName'],
                'auto': True,
                'contexts': [],
                'responses': [
                    {
                        'resetContexts': False,
                        'affectedContexts': [],
                        'parameters': [],
                        'messages': [
                            {
                                'type': 0,
                                'speech': intent['responses']
                            }
                        ],
                        'defaultResponsePlatforms': {},
                        'source': 'agent'
                    }
                ],
                'priority': 500000,
                'systemIntentId': '',
                'fallbackIntent': False,
                'webhookUsed': False,
                'webhookForSlotFilling': False,
                'conditionalResponses': [],
                'condition': '',
                'conditionalFollowupEvents': [],
                'diagnostic': {
                    'userSays': [
                        {
                            'count': 0,
                            'estimate_small': False
                        }
                    ]
                }
            }
            
            zf.writestr(
                f"{intent_dir}/intent.json",
                json.dumps(intent_data, indent=2, ensure_ascii=False)
            )
    
    print(f"✅ Archivo ZIP creado: {zip_path}")
    print(f"\n📦 El ZIP contiene {len(intents_list)} intents")
    print(f"\n📋 Para importar en Dialogflow:")
    print(f"   1. Ve a: https://dialogflow.cloud.google.com")
    print(f"   2. Selecciona tu agente: SISARM Assistant")
    print(f"   3. Haz clic en el icono ⚙️ (Settings)")
    print(f"   4. Pestaña: Export and Import")
    print(f"   5. Haz clic: Restore from ZIP")
    print(f"   6. Selecciona: {zip_path.name}")
    
    return zip_path


if __name__ == '__main__':
    try:
        zip_file = create_intents_zip('dialogflow/intents_sisarm_complete.csv')
        print(f"\n✨ ZIP generado exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
