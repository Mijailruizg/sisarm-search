#!/usr/bin/env python3
"""
Script para generar un JSON estructurado que contiene todos los intents
y que puede ser importado manualmente a Dialogflow.

Este archivo JSON contiene toda la información necesaria para crear
intents en Dialogflow manualmente o a través de la consola.
"""

import json
import csv
from pathlib import Path


def csv_to_intents_json(csv_file: str, output_file: str = None):
    """
    Convierte un CSV de intents a un formato JSON para Dialogflow.
    
    Args:
        csv_file: Ruta del archivo CSV
        output_file: Ruta del archivo JSON a generar (default: dialogflow/intents.json)
    """
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró: {csv_file}")
    
    if output_file is None:
        output_file = csv_path.parent / 'intents_structured.json'
    
    intents = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            intent_name = row.get('intent_name', '').strip()
            training_phrases_str = row.get('training_phrases', '')
            response_text = row.get('responses', '').strip()
            
            if not intent_name or not response_text:
                continue
            
            # Parsear las training phrases
            training_phrases = [
                p.strip() for p in training_phrases_str.split('||') 
                if p.strip()
            ]
            
            intent_obj = {
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
            
            intents.append(intent_obj)
    
    # Guardar como JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'intents': intents}, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(intents)} intents guardados en: {output_file}")
    print("\nIntents generados:")
    for intent in intents:
        print(f"  - {intent['displayName']} ({len(intent['trainingPhrases'])} frases)")
    
    return output_file


def print_intents_summary(csv_file: str):
    """Imprime un resumen de los intents para crear manualmente en la consola."""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró: {csv_file}")
    
    print("=" * 80)
    print("INTENTS PARA CREAR EN DIALOGFLOW")
    print("=" * 80)
    print("\nSi no puedes usar la API, crea estos intents manualmente:\n")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            intent_name = row.get('intent_name', '').strip()
            training_phrases_str = row.get('training_phrases', '')
            response_text = row.get('responses', '').strip()
            
            if not intent_name or not response_text:
                continue
            
            training_phrases = [
                p.strip() for p in training_phrases_str.split('||') 
                if p.strip()
            ]
            
            print(f"\n{idx}. {intent_name}")
            print("-" * 80)
            print("Frases de entrenamiento:")
            for phrase in training_phrases:
                print(f"  • {phrase}")
            print(f"\nRespuesta:")
            print(f"  {response_text}")
            print()


if __name__ == '__main__':
    import sys
    
    csv_file = 'dialogflow/intents_sisarm_complete.csv'
    
    # Generar JSON
    try:
        json_file = csv_to_intents_json(csv_file)
        print(f"\n✨ Archivo JSON generado: {json_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Mostrar resumen
    print("\n" + "=" * 80)
    print_intents_summary(csv_file)
