"""
Prueba rápida y manual del schema. No es un test formal con pytest todavía
(eso vendrá en tests/unit/) -- es solo para confirmar, a ojo, que el schema
se comporta como esperamos antes de seguir construyendo encima.

Ejecútalo con:
    python prueba_schema.py
"""

from datetime import date

from schema import (
    Actividad,
    DatosGenerales,
    Evidencia,
    ExpedienteEstructurado,
    Incidencia,
    Objetivo,
    PrioridadIncidencia,
    TipoActividadIDi,
    TipoEvidencia,
    TipoIncidencia,
    TipoObjetivo,
)

# 1. Construimos un expediente mínimo, con datos ficticios.
datos_generales = DatosGenerales(
    titulo_proyecto="SISTEMA DE OPTIMIZACION DE PROCESOS INDUSTRIALES",
    acronimo="SOPIND0001",
    empresa_principal="Empresa Ficticia S.L.",
    cif_empresa_principal="B00000000",
    fecha_inicio_proyecto=date(2025, 1, 1),
    ejercicio_fiscal_inicio=date(2025, 1, 1),
    ejercicio_fiscal_fin=date(2025, 12, 31),
    codigo_unesco="3304.99",
)

evidencia_1 = Evidencia(
    id="EVIDENCIA_001",
    numero=1,
    descripcion="Captura de pantalla del prototipo de simulación",
    tipo=TipoEvidencia.IMAGEN_SIN_TEXTO,
    fase_asociada="Fase 1",
    documento_origen="capturas_prototipo.pdf",
    pagina_o_ubicacion="página 3",
    ruta_archivo_conservado="evidencias/evidencia_001.png",
)

objetivo_1 = Objetivo(
    id="OBJ_001",
    tipo=TipoObjetivo.TECNOLOGICO,
    descripcion="Desarrollar un algoritmo de optimización no lineal para el proceso X",
    evidencia_ids=["EVIDENCIA_001"],
)

actividad_1 = Actividad(
    id="ACT_001",
    fase="Fase 1: Análisis y Diseño",
    nombre="Diseño del modelo de optimización",
    descripcion="Diseño del algoritmo y su arquitectura de datos",
    estado_ejecucion="finalizada",
    clasificacion_idi=TipoActividadIDi.DESARROLLO,
    evidencia_ids=["EVIDENCIA_001"],
)

expediente = ExpedienteEstructurado(
    datos_generales=datos_generales,
    objetivos=[objetivo_1],
    actividades=[actividad_1],
    evidencias=[evidencia_1],
)

print("Expediente creado correctamente.")
print(f"  Título: {expediente.datos_generales.titulo_proyecto}")
print(f"  Objetivos: {len(expediente.objetivos)}")
print(f"  Evidencia asociada al objetivo 1: {expediente.evidencia_por_id('EVIDENCIA_001').descripcion}")

# 2. Comprobamos que, sin incidencias, el apartado 1.1.1 se puede redactar.
print(f"\n¿Se puede redactar 1.1.1 sin incidencias? {expediente.puede_redactarse('1.1.1')}")

# 3. Sembramos una incidencia ALTA sobre el apartado 1.3 y comprobamos el bloqueo.
incidencia_bloqueante = Incidencia(
    id="INCIDENCIA_001",
    tipo=TipoIncidencia.EVIDENCIA_FALTANTE,
    apartado_afectado="1.3",
    problema="Se afirma que se realizaron pruebas experimentales, pero no hay documentación que las evidencie.",
    accion_recomendada="Buscar o solicitar evidencias de las pruebas realizadas.",
    prioridad=PrioridadIncidencia.ALTA,
)
expediente.incidencias.append(incidencia_bloqueante)

print(f"¿Se puede redactar 1.3 con la incidencia ALTA abierta? {expediente.puede_redactarse('1.3')}")
print(f"¿Se puede redactar 1.1.1 (no afectado por esa incidencia)? {expediente.puede_redactarse('1.1.1')}")

# 4. Serialización a JSON -- así es como se guardará y se pasará entre agentes.
print("\n--- Expediente serializado a JSON (primeras líneas) ---")
json_str = expediente.model_dump_json(indent=2)
print(json_str[:500] + "\n... (truncado)")
