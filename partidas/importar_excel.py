import openpyxl
import re
from .models import PartidaArancelaria

def importar_partidas_desde_excel(archivo):
    wb = openpyxl.load_workbook(archivo)
    hoja = wb.active

    # columnas esperadas en el Excel de entrada.
    # Nota: hemos eliminado 'subpartida' como columna obligatoria para permitir archivos sin ella.
    columnas_esperadas = [
        "capitulo", "partida", "codigo", "descripcion", "gravamen",
        "ice_iehd", "unidad_medida", "despacho_frontera", "tipo_documento",
        "entidad_emite", "disp_legal", "can_ace36_ace47_ven",
        # ace22 puede venir como columna combinada 'ace22_chi_prot' o en dos columnas separadas 'ace22_chi' y 'ace22_prot'
        "ace22_chi_prot", "ace22_chi", "ace22_prot", "ace66_mexico"
    ]

    # Leer fila de encabezados y normalizar nombres para hacer matching tolerante
    header_cells = next(hoja.iter_rows(min_row=1, max_row=1))
    encabezados_raw = [cell.value if cell.value is not None else "" for cell in header_cells]

    import unicodedata
    def normalize(s: str) -> str:
        s = (s or '')
        # quitar acentos
        s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        s = s.lower()
        # reemplazar caracteres no alfanuméricos por espacio
        s = re.sub(r'[^0-9a-z]+', ' ', s)
        s = ' '.join(s.split())
        return s

    encabezados = [normalize(h) for h in encabezados_raw]

    # Mapear nombres canónicos a posibles variantes en el Excel
    variantes = {
        'capitulo': ['capitulo', 'capítulo'],
        'partida': ['partida'],
        'subpartida': ['subpartida'],
        'codigo': ['codigo', 'código'],
        'descripcion': ['descripcion', 'descripcion de la mercancia', 'descripcion de la mercadería', 'descripcion de la mercancía', 'descripcion de la mercancia'],
        'gravamen': ['gravamen', 'impuesto'],
        'ice_iehd': ['ice iehd', 'ice', 'iehd', 'ice_iehd'],
        'unidad_medida': ['unidad de medida', 'unidad_medida', 'unidad'],
        'despacho_frontera': ['despacho en frontera', 'despacho frontera', 'despacho_frontera'],
        'tipo_documento': ['tipo de documento', 'tipo_documento'],
        'entidad_emite': ['entidad que emite', 'entidad_emite', 'entidad'],
        'disp_legal': ['disposicion legal', 'disposición legal', 'disp_legal', 'disposicion'],
        'can_ace36_ace47_ven': ['can ace36 ace47 ven', 'ace36 ace47', 'can_ace36_ace47_ven'],
        'ace22_chi_prot': ['ace22 chi prot', 'ace22_chi_prot', 'ace22', 'ace22 chi/prot', 'ace22 chi/prot'],
        'ace22_chi': ['ace22 chi', 'ace22_chi'],
        'ace22_prot': ['ace22 prot', 'ace22_prot'],
        'ace66_mexico': ['ace66 mexico', 'ace66_mexico', 'ace66']
    }

    # construir mapa de encabezado encontrado -> índice
    header_index = {h: idx for idx, h in enumerate(encabezados)}

    # función para buscar índice por variantes
    def find_index_for(variants):
        for v in variants:
            nv = normalize(v)
            if nv in header_index:
                return header_index[nv]
        # intentar matching por contains
        for v in variants:
            nv = normalize(v)
            for h, idx in header_index.items():
                if nv in h or h in nv:
                    return idx
        return None

    # campos mínimos requeridos
    required_min = ['capitulo', 'partida', 'codigo', 'descripcion']
    found = {}
    for campo in required_min:
        idx = find_index_for(variantes.get(campo, [campo]))
        if idx is None:
            raise Exception(f"El archivo no contiene la columna requerida: '{campo}'")
        found[campo] = idx

    # verificar que exista alguna forma de ace22: combinado o separados
    ace22_idx = find_index_for(variantes.get('ace22_chi_prot'))
    ace22_chi_idx = find_index_for(variantes.get('ace22_chi'))
    ace22_prot_idx = find_index_for(variantes.get('ace22_prot'))
    if ace22_idx is None and ace22_chi_idx is None and ace22_prot_idx is None:
        raise Exception("El archivo debe contener la columna 'ace22_chi_prot' o las columnas 'ace22_chi'/'ace22_prot'.")

    # Mapear índices adicionales opcionales para lectura posterior
    optional_fields = ['gravamen','ice_iehd','unidad_medida','despacho_frontera','tipo_documento','entidad_emite','disp_legal','can_ace36_ace47_ven','ace66_mexico','subpartida']
    for of in optional_fields:
        idx = find_index_for(variantes.get(of, [of]))
        if idx is not None:
            found[of] = idx
    # incluir ace22 indices
    if ace22_idx is not None:
        found['ace22_chi_prot'] = ace22_idx
    if ace22_chi_idx is not None:
        found['ace22_chi'] = ace22_chi_idx
    if ace22_prot_idx is not None:
        found['ace22_prot'] = ace22_prot_idx
    # ace66
    idx_a66 = find_index_for(variantes.get('ace66_mexico'))
    if idx_a66 is not None:
        found['ace66_mexico'] = idx_a66

    # Construir lista de encabezados 'canonicos' usados para zip (llenamos con '' cuando no exista)
    # Pero en lugar de usar zip con encabezados, construiremos los valores por índice en cada fila.

    for fila in hoja.iter_rows(min_row=2):
        row_vals = [cell.value for cell in fila]

        def get_by_key(key):
            idx = found.get(key)
            if idx is None or idx >= len(row_vals):
                return None
            return row_vals[idx]

        def limpiar(valor):
            return "" if valor in (None, "-", "–") else str(valor).strip()

        # construir un diccionario canónico con los campos que necesitamos
        datos_limpios = {
            'capitulo': limpiar(get_by_key('capitulo')),
            'partida': limpiar(get_by_key('partida')),
            'codigo': limpiar(get_by_key('codigo')),
            'descripcion': limpiar(get_by_key('descripcion')),
            'gravamen': limpiar(get_by_key('gravamen')),
            'ice_iehd': limpiar(get_by_key('ice_iehd')),
            'unidad_medida': limpiar(get_by_key('unidad_medida')),
            'despacho_frontera': limpiar(get_by_key('despacho_frontera')),
            'tipo_documento': limpiar(get_by_key('tipo_documento')),
            'entidad_emite': limpiar(get_by_key('entidad_emite')),
            'disp_legal': limpiar(get_by_key('disp_legal')),
            'can_ace36_ace47_ven': limpiar(get_by_key('can_ace36_ace47_ven')),
            'ace66_mexico': limpiar(get_by_key('ace66_mexico')),
            'subpartida': limpiar(get_by_key('subpartida'))
        }

        # obtener ace22 desde columna combinada o separadas
        ace22_val = ''
        combined = get_by_key('ace22_chi_prot')
        chi_val = get_by_key('ace22_chi')
        prot_val = get_by_key('ace22_prot')
        if combined:
            ace22_val = limpiar(combined)
        else:
            chi = limpiar(chi_val)
            prot = limpiar(prot_val)
            if chi and prot:
                ace22_val = f"{chi}; {prot}"
            elif chi:
                ace22_val = chi
            elif prot:
                ace22_val = prot

        if datos_limpios['codigo'] and not PartidaArancelaria.objects.filter(codigo=datos_limpios['codigo']).exists():
            PartidaArancelaria.objects.create(
                capitulo=datos_limpios['capitulo'],
                partida=datos_limpios['partida'],
                codigo=datos_limpios['codigo'],
                descripcion=datos_limpios['descripcion'],
                gravamen=datos_limpios.get('gravamen', ''),
                ice_iehd=datos_limpios.get('ice_iehd', ''),
                unidad_medida=datos_limpios.get('unidad_medida', ''),
                despacho_frontera=datos_limpios.get('despacho_frontera', ''),
                tipo_documento=datos_limpios.get('tipo_documento', ''),
                entidad_emite=datos_limpios.get('entidad_emite', ''),
                disp_legal=datos_limpios.get('disp_legal', ''),
                can_ace36_ace47_ven=datos_limpios.get('can_ace36_ace47_ven', ''),
                ace22_chi_prot=ace22_val,
                ace66_mexico=datos_limpios.get('ace66_mexico', '')
            )
