"""
Schema del Expediente Estructurado.

Este módulo define la estructura de datos central del sistema. Ningún agente
debería releer los documentos originales una vez construido el expediente:
todo lo que necesitan analistas, consultor, redactores y revisores vive aquí,
con trazabilidad explícita hasta su origen documental.

Principio de diseño: cada pieza de información relevante (actividad, objetivo,
afirmación del estado del arte, etc.) referencia los `evidencia_ids` que la
respaldan. Una `Evidencia` a su vez guarda el documento y la ubicación exacta
de origen. Esto hace que la cadena "afirmación -> evidencia -> documento ->
página" sea un dato consultable por código, no una convención de redacción.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Vocabularios controlados (Enums)
# ---------------------------------------------------------------------------

class TipoEvidencia(str, Enum):
    TEXTO_IMPRESO = "texto_impreso"          # OCR clásico
    TEXTO_MANUSCRITO = "texto_manuscrito"    # OCR + fallback multimodal
    IMAGEN_SIN_TEXTO = "imagen_sin_texto"    # descripción por visión
    DOCUMENTO_TEXTUAL = "documento_textual"  # PDF/DOCX/XLSX con texto extraíble


class TipoActividadIDi(str, Enum):
    INVESTIGACION = "investigacion"
    DESARROLLO = "desarrollo"
    INNOVACION_TECNOLOGICA = "innovacion_tecnologica"
    NO_DEDUCIBLE = "no_deducible"
    PENDIENTE_CLASIFICAR = "pendiente_clasificar"


class TipoIncidencia(str, Enum):
    INFO_FALTANTE = "info_faltante"
    CONTRADICCION = "contradiccion"
    EVIDENCIA_FALTANTE = "evidencia_faltante"
    DATO_A_CONFIRMAR = "dato_a_confirmar"
    POSIBLE_PROBLEMA_IDI = "posible_problema_idi"
    REVISION_HUMANA = "revision_humana"


class PrioridadIncidencia(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoIncidencia(str, Enum):
    ABIERTA = "abierta"
    RESUELTA = "resuelta"


class TipoObjetivo(str, Enum):
    TECNOLOGICO = "tecnologico"
    EMPRESARIAL = "empresarial"


# ---------------------------------------------------------------------------
# Evidencias y trazabilidad
# ---------------------------------------------------------------------------

class Evidencia(BaseModel):
    """
    Unidad mínima de respaldo documental. Toda afirmación relevante en la
    memoria debe poder señalar a una o más evidencias como las que aquí se
    definen.
    """
    id: str  # p.ej. "EVIDENCIA_023"
    numero: int  # número visible en la memoria ("Figura 3")
    descripcion: str
    tipo: TipoEvidencia
    fase_asociada: Optional[str] = None
    documento_origen: str  # nombre/ruta del documento original en el ZIP
    pagina_o_ubicacion: Optional[str] = None  # p.ej. "página 17" o "diapositiva 4"
    ruta_archivo_conservado: str  # ruta al archivo real, para la Integración
    empresa_cooperante: Optional[str] = None  # si el expediente es multiempresa


# ---------------------------------------------------------------------------
# Datos generales
# ---------------------------------------------------------------------------

class EmpresaCooperante(BaseModel):
    nombre: str
    cif: str
    orden: int
    numero_informe_motivado: Optional[str] = None  # "N/A" si no aplica


class DatosGenerales(BaseModel):
    titulo_proyecto: str
    acronimo: str  # 10 caracteres alfanuméricos, salvo sufijo 01/02/03 en cooperación
    empresa_principal: str
    cif_empresa_principal: str
    en_cooperacion: bool = False
    empresas_cooperantes: list[EmpresaCooperante] = Field(default_factory=list)
    fecha_inicio_proyecto: date
    fecha_fin_proyecto: Optional[date] = None
    ejercicio_fiscal_inicio: date
    ejercicio_fiscal_fin: date
    codigo_unesco: str
    tipologia_certificacion: Optional[str] = None  # p.ej. "contenido y primera ejecución"


# ---------------------------------------------------------------------------
# Bloques narrativos (con trazabilidad a evidencias)
# ---------------------------------------------------------------------------

class Objetivo(BaseModel):
    id: str
    tipo: TipoObjetivo
    descripcion: str
    evidencia_ids: list[str] = Field(default_factory=list)


class EstadoDelArte(BaseModel):
    descripcion: str
    referencias: list[str] = Field(default_factory=list)
    limitaciones_identificadas: list[str] = Field(default_factory=list)
    evidencia_ids: list[str] = Field(default_factory=list)


class NovedadTecnologica(BaseModel):
    id: str
    descripcion: str
    es_objetiva_mercado: Optional[bool] = None  # objetiva (mercado) vs subjetiva (empresa)
    evidencia_ids: list[str] = Field(default_factory=list)


class Actividad(BaseModel):
    """
    Una actividad dentro de una fase del proyecto. El redactor de 1.2 genera,
    por fase, un bloque narrativo que integra estas actividades junto con sus
    resultados y evidencias -- no se redactan como piezas sueltas.
    """
    id: str
    fase: str  # p.ej. "Fase 1: Análisis y Diseño"
    nombre: str
    descripcion: str
    estado_ejecucion: str  # p.ej. "finalizada", "en curso", "pendiente"
    tareas_pendientes_anualidades_futuras: Optional[str] = None
    clasificacion_idi: TipoActividadIDi = TipoActividadIDi.PENDIENTE_CLASIFICAR
    justificacion_clasificacion: Optional[str] = None  # rellenado por el Agente I+D+i
    evidencia_ids: list[str] = Field(default_factory=list)


class Resultado(BaseModel):
    id: str
    descripcion: str
    actividad_id: str  # referencia a Actividad.id
    evidencia_ids: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Económico (mínimo para el MVP -- se ampliará en la fase económica)
# ---------------------------------------------------------------------------

class PartidaEconomica(BaseModel):
    id: str
    tipo_partida: str  # "personal", "colaboraciones_externas", "activos", "fungibles", "otros"
    fase: Optional[str] = None
    anualidad: int
    importe: float
    empresa_cooperante: Optional[str] = None
    justificantes: list[str] = Field(default_factory=list)  # referencias a documentos


# ---------------------------------------------------------------------------
# Incidencias
# ---------------------------------------------------------------------------

class Incidencia(BaseModel):
    id: str  # p.ej. "INCIDENCIA_034"
    tipo: TipoIncidencia
    apartado_afectado: str  # p.ej. "1.3"
    problema: str
    accion_recomendada: str
    prioridad: PrioridadIncidencia
    estado: EstadoIncidencia = EstadoIncidencia.ABIERTA
    resolucion: Optional[str] = None  # cómo se resolvió, si ya está resuelta


# ---------------------------------------------------------------------------
# Expediente completo
# ---------------------------------------------------------------------------

class ExpedienteEstructurado(BaseModel):
    datos_generales: DatosGenerales
    contexto: str = ""
    objetivos: list[Objetivo] = Field(default_factory=list)
    estado_del_arte: Optional[EstadoDelArte] = None
    novedades_tecnologicas: list[NovedadTecnologica] = Field(default_factory=list)
    actividades: list[Actividad] = Field(default_factory=list)
    resultados: list[Resultado] = Field(default_factory=list)
    evidencias: list[Evidencia] = Field(default_factory=list)
    partidas_economicas: list[PartidaEconomica] = Field(default_factory=list)
    incidencias: list[Incidencia] = Field(default_factory=list)

    # -- Métodos de utilidad --------------------------------------------

    def incidencias_altas_abiertas(self, apartado: Optional[str] = None) -> list[Incidencia]:
        """
        Devuelve las incidencias de prioridad ALTA que siguen abiertas,
        opcionalmente filtradas por apartado. Es la comprobación que debe
        hacer código (no un LLM) antes de lanzar cualquier redactor.
        """
        resultado = [
            inc for inc in self.incidencias
            if inc.prioridad == PrioridadIncidencia.ALTA
            and inc.estado == EstadoIncidencia.ABIERTA
        ]
        if apartado is not None:
            resultado = [inc for inc in resultado if inc.apartado_afectado == apartado]
        return resultado

    def puede_redactarse(self, apartado: str) -> bool:
        """True si no hay incidencias ALTA abiertas que bloqueen este apartado."""
        return len(self.incidencias_altas_abiertas(apartado)) == 0

    def evidencia_por_id(self, evidencia_id: str) -> Optional[Evidencia]:
        return next((e for e in self.evidencias if e.id == evidencia_id), None)
