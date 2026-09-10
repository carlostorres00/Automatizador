"""
Extracción de texto de PDFs: texto digital + OCR sobre imágenes incrustadas.

A diferencia de la primera versión (que solo leía texto digital con pypdf),
esta también ejecuta OCR (Tesseract) sobre las imágenes que haya dentro del
PDF -- necesario para documentos que mezclan texto digital con capturas de
pantalla, diagramas escaneados, sellos, etc.

Requiere tener instalado el BINARIO de Tesseract en el sistema (no basta con
`pip install pytesseract`, que solo es el envoltorio de Python que llama a
ese binario) y el paquete de idioma español:
    Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-spa
    Windows: instalador de https://github.com/UB-Mannheim/tesseract/wiki
             (marcar "Spanish" en el instalador)
"""

import io
import logging

import pymupdf
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Umbrales para decidir si un resultado de OCR es lo bastante fiable como
# para incorporarse al texto final, en vez de aceptar cualquier resultado.
OCR_MIN_CONFIDENCE = 40.0  # confianza media de Tesseract (0-100)
OCR_MIN_CHARS = 3          # longitud mínima del texto reconocido
OCR_MIN_PIXELS = 30        # ancho/alto mínimo en píxeles (descarta iconos/adornos)


def _hacer_ocr(imagen: Image.Image) -> tuple[str, float]:
    """Ejecuta OCR sobre una imagen y devuelve (texto, confianza_media)."""
    if imagen.mode not in ("RGB", "L"):
        imagen = imagen.convert("RGB")

    datos = pytesseract.image_to_data(imagen, lang="spa", output_type=pytesseract.Output.DICT)

    lineas: dict[tuple[int, int, int], list[str]] = {}
    confianzas = []
    for i, palabra in enumerate(datos["text"]):
        conf = float(datos["conf"][i])
        if conf >= 0:
            confianzas.append(conf)
        palabra = palabra.strip()
        if not palabra:
            continue
        clave = (datos["block_num"][i], datos["par_num"][i], datos["line_num"][i])
        lineas.setdefault(clave, []).append(palabra)

    texto = "\n".join(" ".join(p) for p in lineas.values()).strip()
    confianza_media = sum(confianzas) / len(confianzas) if confianzas else 0.0
    return texto, confianza_media


def _ocr_merece_incorporarse(texto: str, confianza: float, imagen: Image.Image) -> bool:
    """Filtra resultados de OCR poco fiables (iconos, ruido, texto ilegible)."""
    if imagen.width < OCR_MIN_PIXELS or imagen.height < OCR_MIN_PIXELS:
        return False
    if len(texto) < OCR_MIN_CHARS:
        return False
    if confianza < OCR_MIN_CONFIDENCE:
        return False
    return True


def extraer_texto_pdf(ruta_archivo: str) -> str:
    """
    Devuelve el texto completo del PDF, página por página (con marcador de
    página para trazabilidad), combinando el texto digital con el resultado
    de OCR sobre las imágenes incrustadas que superen el umbral de confianza.

    El texto que proviene de OCR se marca con el prefijo "[OCR]" para que
    cualquier agente o revisor posterior pueda tratarlo con más cautela que
    al texto digital nativo -- el OCR puede equivocarse, el texto digital no.
    """
    try:
        pdf = pymupdf.open(ruta_archivo)
    except Exception as e:
        logger.error(f"No se pudo abrir el PDF '{ruta_archivo}': {e}")
        return ""

    partes_por_pagina = []

    try:
        for pagina in pdf:
            texto_pagina = ""
            try:
                contenido = pagina.get_text("dict", sort=True)
            except Exception as e:
                logger.error(f"Error extrayendo contenido de la página {pagina.number + 1}: {e}")
                partes_por_pagina.append(f"--- página {pagina.number + 1} ---\n")
                continue

            for bloque in contenido.get("blocks", []):
                tipo = bloque.get("type")

                if tipo == 0:  # bloque de texto digital
                    lineas = []
                    for linea in bloque.get("lines", []):
                        texto_linea = "".join(span["text"] for span in linea.get("spans", []))
                        if texto_linea:
                            lineas.append(texto_linea)
                    texto_bloque = " ".join(lineas)
                    if texto_bloque.strip():
                        texto_pagina += texto_bloque + "\n"

                elif tipo == 1:  # bloque de imagen -> intentar OCR
                    try:
                        imagen = Image.open(io.BytesIO(bloque["image"]))
                    except Exception as e:
                        logger.warning(f"No se pudo decodificar una imagen: {e}")
                        continue
                    try:
                        texto_ocr, confianza = _hacer_ocr(imagen)
                    except Exception as e:
                        logger.warning(f"Falló el OCR sobre una imagen: {e}")
                        continue
                    if _ocr_merece_incorporarse(texto_ocr, confianza, imagen):
                        texto_pagina += f"[OCR] {texto_ocr}\n"

            partes_por_pagina.append(f"--- página {pagina.number + 1} ---\n{texto_pagina.strip()}")
    finally:
        pdf.close()

    return "\n\n".join(partes_por_pagina)