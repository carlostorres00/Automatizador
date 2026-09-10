"""
Descripción de evidencias visuales (imágenes sin texto relevante que leer).

TODO (fase LLM): sustituir el cuerpo de `describir_imagen` por una llamada real
a un modelo con visión (barato/intermedio, según la tabla del prompt maestro),
que reciba la imagen y devuelva una descripción estructurada + a qué fase del
proyecto corresponde. La firma de la función (qué recibe, qué devuelve) ya está
pensada para que ese cambio no afecte a nada más del sistema: quien llame a
`describir_imagen` seguirá recibiendo un `DescripcionImagen` igual que ahora.

Por ahora, sin API configurada, se deja constancia explícita de que esto es un
placeholder -- nunca se debe confundir esta descripción con una real.
"""

from pydantic import BaseModel


class DescripcionImagen(BaseModel):
    descripcion: str
    fase_asociada: str | None = None
    es_placeholder: bool = True  # True mientras no haya una llamada real a visión


def describir_imagen(ruta_archivo: str) -> DescripcionImagen:
    """
    Placeholder. Cuando se active la fase LLM, esta función deberá:
      1. Cargar la imagen y enviarla a un modelo con visión.
      2. Pedir una descripción estructurada del contenido técnico.
      3. Pedir a qué fase/actividad del proyecto corresponde (si es inferible).
    De momento devuelve un aviso explícito de pendiente, para que no se
    confunda con una descripción real en ningún informe.
    """
    return DescripcionImagen(
        descripcion=f"[PENDIENTE: describir con visión] Archivo: {ruta_archivo}",
        fase_asociada=None,
        es_placeholder=True,
    )
