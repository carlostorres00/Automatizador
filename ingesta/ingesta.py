"""
Orquestador mínimo de la Ingesta.

Recorre una carpeta de documentos de entrada y devuelve una lista de
`DocumentoExtraido`, uno por archivo, con su contenido crudo ya extraído.

Esto NO es todavía el Expediente Estructurado -- es el paso previo. Mapear
este contenido crudo a los campos del expediente (objetivos, actividades,
estado del arte...) es trabajo del Agente técnico, que sí usará un LLM.
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from extractores.pdf_extractor import extraer_texto_pdf
from extractores.docx_extractor import extraer_texto_docx
from extractores.xlsx_extractor import extraer_tablas_xlsx
from extractores.imagen_extractor import describir_imagen, DescripcionImagen

EXTENSIONES_PDF = {".pdf"}
EXTENSIONES_DOCX = {".docx"}
EXTENSIONES_XLSX = {".xlsx", ".xlsm"}
EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg"}


class DocumentoExtraido(BaseModel):
    nombre_archivo: str
    ruta: str
    tipo: str  # "pdf" | "xlsx" | "imagen" | "no_soportado"
    contenido_texto: Optional[str] = None
    contenido_tabular: Optional[dict[str, list[list]]] = None
    descripcion_imagen: Optional[DescripcionImagen] = None


def ingestar_carpeta(ruta_carpeta: str) -> list[DocumentoExtraido]:
    documentos: list[DocumentoExtraido] = []
    carpeta = Path(ruta_carpeta)

    for archivo in sorted(carpeta.iterdir()):
        if not archivo.is_file():
            continue

        extension = archivo.suffix.lower()

        if extension in EXTENSIONES_PDF:
            documentos.append(DocumentoExtraido(
                nombre_archivo=archivo.name,
                ruta=str(archivo),
                tipo="pdf",
                contenido_texto=extraer_texto_pdf(str(archivo)),
            ))

        elif extension in EXTENSIONES_DOCX:
            documentos.append(DocumentoExtraido(
                nombre_archivo=archivo.name,
                ruta=str(archivo),
                tipo="docx",
                contenido_texto=extraer_texto_docx(str(archivo)),
            ))

        elif extension in EXTENSIONES_XLSX:
            documentos.append(DocumentoExtraido(
                nombre_archivo=archivo.name,
                ruta=str(archivo),
                tipo="xlsx",
                contenido_tabular=extraer_tablas_xlsx(str(archivo)),
            ))

        elif extension in EXTENSIONES_IMAGEN:
            documentos.append(DocumentoExtraido(
                nombre_archivo=archivo.name,
                ruta=str(archivo),
                tipo="imagen",
                descripcion_imagen=describir_imagen(str(archivo)),
            ))

        else:
            documentos.append(DocumentoExtraido(
                nombre_archivo=archivo.name,
                ruta=str(archivo),
                tipo="no_soportado",
            ))

    return documentos