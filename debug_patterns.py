#!/usr/bin/env python3
"""Debug de los patterns de keywords."""

import re

text_lower = "como uso los filtros"
text_normalized = re.sub(r'[áéíóú]', lambda m: {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
}[m.group()], text_lower)

print(f"Texto: {text_lower}")
print(f"Normalizado: {text_normalized}")
print()

patterns = [
    (r'\bfiltro\b|\bcapítulo\b|\bgravamen\b', 'Filtros'),
    (r'\bmanual\b|\bguia\b|\btutorial\b|\bguia\b', 'Manuales'),
    (r'\bdocumento\b|\brequisito\b|\bcertificado\b|\bdocumentacio', 'Documentos'),
]

for pattern, name in patterns:
    match = re.search(pattern, text_normalized)
    print(f"{name}: {match is not None}")
    if match:
        print(f"  Matched: {match.group()}")
