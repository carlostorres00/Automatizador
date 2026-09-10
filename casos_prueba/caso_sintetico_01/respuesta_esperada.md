# Caso sintético 01 — SORRA (Sistema de Optimización de Rutas de Reparto)

Proyecto ficticio de software (optimización de rutas de reparto con aprendizaje por
refuerzo), diseñado desde cero para pruebas — sin relación con ningún cliente real.

## Contenido de `entrada/` (esto es lo que "llega" en el ZIP del cliente)

- `doc_tecnico.pdf` — memoria descriptiva del proyecto: contexto, objetivos, dos fases
  (Análisis y diseño / Desarrollo y pruebas) con sus actividades.
- `presupuesto.xlsx` — presupuesto simplificado por partidas.
- `captura_prototipo.png` — captura simulada del panel de monitorización de rutas
  (evidencia visual sin texto, referenciada en el PDF como "Figura 1").

## Trampas sembradas a propósito (respuesta esperada)

Esto es la clave de verificación — **no** forma parte de lo que "recibe" el sistema,
es lo que usamos nosotros para comprobar que cada agente detecta lo que debe detectar.

### 1. Contradicción de fechas → incidencia `CONTRADICCION`
- `doc_tecnico.pdf` dice: fecha de inicio del proyecto **15/01/2025**.
- `presupuesto.xlsx` dice: ejercicio fiscal **01/02/2025 - 31/12/2025**.
- El Consultor debería detectar que el inicio del proyecto (enero) cae fuera del
  ejercicio fiscal declarado en el presupuesto (que empieza en febrero).

### 2. Evidencia faltante → incidencia `EVIDENCIA_FALTANTE`, prioridad ALTA
- El PDF afirma: *"Se realizaron pruebas experimentales de validación del modelo con
  datos reales de tres semanas de operación, evidenciando una mejora del 12%..."*
- No hay ningún documento en `entrada/` que respalde esa afirmación (ni logs, ni
  informe de resultados, ni captura de las pruebas).
- Esta es la incidencia que, si se marca ALTA sobre el apartado 1.3, debería
  **bloquear** la redacción de ese apartado (`puede_redactarse("1.3") == False`,
  tal y como probamos con el schema).

### 3. Palabra "prohibida" sin justificar → riesgo para el Agente I+D+i
- El PDF incluye textualmente: *"Se realizó la parametrización del sistema para
  adaptarlo a los requisitos particulares de la flota del cliente."*
- "Parametrización" está en la lista de palabras de riesgo para proyectos TIC según
  el PDF de formación, salvo que se justifique claramente su carácter innovador — y
  aquí no se justifica. El Agente I+D+i (y luego el revisor de I+D+i) deberían
  señalarlo como riesgo, no como actividad deducible sin más.

### Evidencia que SÍ está bien resuelta (para contraste)
- `captura_prototipo.png` sí está referenciada en el texto ("Figura 1") y sí existe
  como archivo — esta NO debería generar ninguna incidencia. Sirve para comprobar
  que el sistema no marca falsos positivos.

## Qué NO incluye este caso (a propósito)
- Nada de Anexo Económico, Fichas de Ampliación ni Formulario Software — fuera de
  alcance de esta v1.
- Sin texto manuscrito ni necesidad de OCR con fallback multimodal — se deja para
  un caso sintético posterior, cuando toque esa parte de la Ingesta.
