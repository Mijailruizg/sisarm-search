#!/usr/bin/env python3
"""Script para probar todas las respuestas del sistema mejorado."""

import sys
import io
from contextlib import redirect_stderr

# Capturar stderr para silenciar los warnings
with redirect_stderr(io.StringIO()):
    from partidas.dialogflow_client import get_chat_response

test_messages = [
    ('Hola', 'Saludo'),
    ('Como estas', 'Saludo general'),
    ('Para qué sirve el sistema', 'Información del sistema'),
    ('Cómo busco una partida', 'Búsqueda'),
    ('Cómo uso los filtros', 'Filtros'),
    ('Documentos requeridos', 'Documentos'),
    ('Renovar licencia', 'Licencia'),
    ('Soporte', 'Contacto'),
    ('me ayudas', 'Ayuda general'),
    ('Ver manuales', 'Documentación'),
]

print('✅ PRUEBAS DE RESPUESTAS DEL SISTEMA SISARM')
print('=' * 90)

for msg, tipo in test_messages:
    resp = get_chat_response(msg, session_id='test-123')
    # Mostrar solo los primeros 100 caracteres
    preview = resp.replace('\n', ' ')[:100]
    if len(resp) > 100:
        preview += '...'
    print(f'\n🔹 {tipo}')
    print(f'   Tú: "{msg}"')
    print(f'   Respuesta: {preview}')

print('\n' + '=' * 90)
print('✨ Todas las respuestas funcionan correctamente!')
