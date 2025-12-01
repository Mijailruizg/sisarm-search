#!/usr/bin/env python3
"""
Genera un archivo HTML con instrucciones paso a paso para crear cada intent
manualmente en la consola de Dialogflow, con la información pre-llenada.
"""

import csv
import json
from pathlib import Path


def generate_html_guide(csv_file: str, output_file: str = 'dialogflow/intents_manual_guide.html'):
    """Genera un HTML interactivo con las instrucciones para crear intents."""
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise FileNotFoundError(f"No encontrado: {csv_file}")
    
    intents = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            intent_name = row.get('intent_name', '').strip()
            training_phrases_str = row.get('training_phrases', '')
            response_text = row.get('responses', '').strip()
            
            if not intent_name or not response_text:
                continue
            
            training_phrases = [p.strip() for p in training_phrases_str.split('||') if p.strip()]
            intents.append({
                'name': intent_name,
                'phrases': training_phrases,
                'response': response_text
            })
    
    # Generar HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guía: Crear Intents en Dialogflow</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        header p {{
            color: #666;
            margin-bottom: 15px;
        }}
        .steps {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .step {{
            background: #f0f0f0;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }}
        .step.active {{
            background: #667eea;
            color: white;
        }}
        .intent-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }}
        .intent-number {{
            display: inline-block;
            background: #667eea;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            text-align: center;
            line-height: 35px;
            font-weight: bold;
            margin-right: 10px;
        }}
        .intent-title {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .section-title {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .phrases {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        .phrase {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            font-size: 14px;
        }}
        .phrase:last-child {{
            border-bottom: none;
        }}
        .phrase-text {{
            background: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            display: inline-block;
            margin: 5px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .response {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4caf50;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }}
        .copy-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 10px;
        }}
        .copy-btn:hover {{
            background: #5568d3;
        }}
        .instructions {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #ffc107;
        }}
        .instructions h3 {{
            color: #856404;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .instructions ol {{
            margin-left: 20px;
            color: #856404;
            font-size: 13px;
        }}
        .instructions li {{
            margin-bottom: 8px;
        }}
        .code {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
            margin: 5px 0;
            border-left: 3px solid #667eea;
        }}
        footer {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 13px;
        }}
        .progress {{
            display: flex;
            gap: 5px;
            margin-top: 20px;
        }}
        .progress-item {{
            height: 4px;
            flex: 1;
            background: #e0e0e0;
            border-radius: 2px;
        }}
        .progress-item.done {{
            background: #4caf50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Crear Intents en Dialogflow ES</h1>
            <p>Guía paso a paso para crear {len(intents)} intents en tu agente SISARM</p>
            <div class="instructions">
                <h3>📍 Antes de comenzar:</h3>
                <ol>
                    <li>Abre Dialogflow: <strong><a href="https://dialogflow.cloud.google.com" target="_blank">https://dialogflow.cloud.google.com</a></strong></li>
                    <li>Selecciona tu proyecto: <strong>SISARM Assistant</strong></li>
                    <li>En el panel izquierdo, haz clic en <strong>Intents</strong></li>
                    <li>Haz clic en <strong>Create Intent</strong> para cada uno que se muestra abajo</li>
                </ol>
            </div>
            <div class="progress">
                {''.join([f'<div class="progress-item"></div>' for _ in range(len(intents))])}
            </div>
        </header>

        <div class="intents-container">
"""
    
    for idx, intent in enumerate(intents, 1):
        html_content += f"""
        <div class="intent-card">
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <div class="intent-number">{idx}</div>
                <div class="intent-title">{intent['name']}</div>
            </div>
            
            <div class="section">
                <div class="section-title">📝 Display Name</div>
                <div class="code">{intent['name']}</div>
                <button class="copy-btn" onclick="copyToClipboard(this)">Copiar</button>
            </div>
            
            <div class="section">
                <div class="section-title">🎯 Training Phrases ({len(intent['phrases'])} frases)</div>
                <div class="phrases">
                    {''.join([f'<div class="phrase"><div class="phrase-text">{phrase}</div></div>' for phrase in intent['phrases']])}
                </div>
                <button class="copy-btn" onclick="copyPhrasesToClipboard(this)">Copiar todas las frases</button>
            </div>
            
            <div class="section">
                <div class="section-title">💬 Response (Text Response)</div>
                <div class="response">{intent['response']}</div>
                <button class="copy-btn" onclick="copyToClipboard(this)">Copiar respuesta</button>
            </div>
        </div>
"""
    
    html_content += """
        </div>

        <footer>
            <p>✅ Una vez que hayas creado todos los intents, prueba el chat en tu aplicación SISARM</p>
            <p style="margin-top: 10px; font-size: 12px; color: #999;">Generated on November 28, 2025</p>
        </footer>
    </div>

    <script>
        function copyToClipboard(btn) {{
            const parent = btn.parentElement;
            const textToCopy = parent.querySelector('.code, .response')?.innerText || 
                             parent.querySelector('.intent-title')?.innerText;
            
            if (textToCopy) {{
                navigator.clipboard.writeText(textToCopy).then(() => {{
                    const originalText = btn.innerText;
                    btn.innerText = '✅ Copiado!';
                    setTimeout(() => {{
                        btn.innerText = originalText;
                    }}, 2000);
                }});
            }}
        }}

        function copyPhrasesToClipboard(btn) {{
            const parent = btn.parentElement;
            const phrases = Array.from(parent.querySelectorAll('.phrase-text'))
                .map(el => el.innerText)
                .join('\\n');
            
            if (phrases) {{
                navigator.clipboard.writeText(phrases).then(() => {{
                    const originalText = btn.innerText;
                    btn.innerText = '✅ Copiado!';
                    setTimeout(() => {{
                        btn.innerText = originalText;
                    }}, 2000);
                }});
            }}
        }}

        // Scroll to hash on load
        window.addEventListener('load', () => {{
            if (window.location.hash) {{
                document.querySelector(window.location.hash)?.scrollIntoView();
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Guardar HTML
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Guía HTML generada: {output_path}")
    print(f"\n📱 Abre en tu navegador para ver la guía completa:")
    print(f"   file:///{output_path.resolve()}")
    
    return output_path


if __name__ == '__main__':
    try:
        html_file = generate_html_guide('dialogflow/intents_sisarm_complete.csv')
        print(f"\n✨ Guía creada exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
