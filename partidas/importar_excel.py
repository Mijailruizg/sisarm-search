import openpyxl
from .models import PartidaArancelaria

def importar_partidas_desde_excel(archivo):
    wb = openpyxl.load_workbook(archivo)
    hoja = wb.active

    columnas_esperadas = [
        "capitulo", "partida", "subpartida", "codigo", "descripcion", "gravamen",
        "ice_iehd", "unidad_medida", "despacho_frontera", "tipo_documento",
        "entidad_emite", "disp_legal", "can_ace36_ace47_ven",
        "ace22_chi_prot", "ace66_mexico"
    ]

    encabezados = [cell.value.strip().lower() if cell.value else "" for cell in next(hoja.iter_rows(min_row=1, max_row=1))]

    for campo in columnas_esperadas:
        if campo not in encabezados:
            raise Exception(f"El archivo no contiene la columna requerida: '{campo}'")

    for fila in hoja.iter_rows(min_row=2):
        datos = dict(zip(encabezados, [cell.value for cell in fila]))

        def limpiar(valor):
            return "" if valor in (None, "-", "–") else str(valor).strip()

        datos_limpios = {k: limpiar(v) for k, v in datos.items()}

        if datos_limpios["codigo"] and not PartidaArancelaria.objects.filter(codigo=datos_limpios["codigo"]).exists():
            PartidaArancelaria.objects.create(
                capitulo=datos_limpios["capitulo"],
                partida=datos_limpios["partida"],
                subpartida=datos_limpios["subpartida"],
                codigo=datos_limpios["codigo"],
                descripcion=datos_limpios["descripcion"],
                gravamen=datos_limpios["gravamen"],
                ice_iehd=datos_limpios["ice_iehd"],
                unidad_medida=datos_limpios["unidad_medida"],
                despacho_frontera=datos_limpios["despacho_frontera"],
                tipo_documento=datos_limpios["tipo_documento"],
                entidad_emite=datos_limpios["entidad_emite"],
                disp_legal=datos_limpios["disp_legal"],
                can_ace36_ace47_ven=datos_limpios["can_ace36_ace47_ven"],
                ace22_chi_prot=datos_limpios["ace22_chi_prot"],
                ace66_mexico=datos_limpios["ace66_mexico"]
            )
