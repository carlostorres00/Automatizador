"""
Prueba manual de la Ingesta sobre el caso sintético 01.

Ejecutar con:
    python prueba_ingesta.py

Requiere que exista, relativo a este archivo, la carpeta:
    ../casos_prueba/caso_sintetico_01/entrada/
Ajusta RUTA_CASO si tu estructura de carpetas es distinta.
"""

from ingesta import ingestar_carpeta

RUTA_CASO = "../casos_prueba/caso_sintetico_01/entrada"

documentos = ingestar_carpeta(RUTA_CASO)

print(f"Documentos ingeridos: {len(documentos)}\n")

for doc in documentos:
    print(f"=== {doc.nombre_archivo} ({doc.tipo}) ===")

    if doc.tipo == "pdf":
        print(doc.contenido_texto[:400])
        print("... (truncado)\n")

    elif doc.tipo == "xlsx":
        for hoja, filas in doc.contenido_tabular.items():
            print(f"  Hoja '{hoja}':")
            for fila in filas:
                print(f"    {fila}")
        print()

    elif doc.tipo == "imagen":
        print(f"  {doc.descripcion_imagen.descripcion}")
        print(f"  (placeholder: {doc.descripcion_imagen.es_placeholder})\n")

    else:
        print("  Tipo no soportado por la ingesta actual.\n")
