#!/usr/bin/env python3
"""Pruebas del endpoint /api/chat-help/"""

import requests
import json
import time

# Esperar a que el servidor esté listo
time.sleep(2)

url = 'http://127.0.0.1:8000/api/chat-help/'

test_cases = [
    ('Hola', 'Saludo'),
    ('Para qué sirve el sistema', 'Sistema'),
    ('Cómo busco una partida', 'Búsqueda'),
    ('Cómo uso los filtros', 'Filtros'),
    ('Renovar licencia', 'Licencia'),
    ('Ver soporte', 'Soporte'),
]

print('=' * 80)
print('🧪 PRUEBAS DEL ENDPOINT /api/chat-help/')
print('=' * 80)

for message, tipo in test_cases:
    try:
        response = requests.post(
            url,
            data={
                'message': message,
                'session_id': 'test-session',
                'public': '1'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            ok = data.get('ok')
            reply = data.get('reply', '')
            preview = reply[:100].replace('\n', ' ')
            if len(reply) > 100:
                preview += '...'
            
            print(f'\n✅ {tipo}')
            print(f'   Tú: "{message}"')
            print(f'   Status: {response.status_code}')
            print(f'   Respuesta: {preview}')
        else:
            print(f'\n❌ {tipo}')
            print(f'   Status: {response.status_code}')
            print(f'   Error: {response.text[:100]}')
    
    except Exception as e:
        print(f'\n❌ {tipo}')
        print(f'   Error: {str(e)}')

print('\n' + '=' * 80)
print('✨ Pruebas completadas')
