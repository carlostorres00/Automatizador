# Memorias Técnico-Económicas I+D+i — Sistema multiagente

Sistema multiagente en Python que automatiza (con supervisión humana integrada, no eliminada)
la elaboración de la **Memoria Técnico-Económica para deducciones fiscales por actividades de
I+D+i** en España (Art. 35 Ley 27/2014 del Impuesto de Sociedades).

**Alcance de esta v1**: únicamente el documento Word de la Memoria Técnica. No incluye el Anexo
Económico, las Fichas de Ampliación ni el Formulario Software.

## Principio fundamental de diseño: REDACTAR ≠ DECIDIR

Ningún agente que redacta texto de la memoria decide por su cuenta si una actividad es I+D,
inventa una evidencia, o rellena un dato ausente. La redacción parte siempre de decisiones y
datos que ya existen en el expediente, tomados por agentes de análisis específicos o confirmados
por el consultor humano. Este principio (**analizar → decidir → redactar → revisar**) no se
rompe por conveniencia en ninguna fase.

## Flujo general

```
ZIP con documentación
   → Ingesta + extracción
   → Expediente Estructurado
   → Análisis (técnico, evidencias, económico, I+D+i — en paralelo)
   → Consultor/Supervisor (detecta contradicciones, huecos, riesgos → incidencias)
   → Resolución humana de incidencias
   → Redacción especializada (un agente por apartado)
   → Revisión (coherencia, técnico, I+D+i, evidencias, económico)
   → Integración en plantilla Word
   → Memoria Técnico-Económica .docx
```

## Estructura del repositorio

```
config/               Configuración de modelos/proveedores por agente (llm_config.yaml)
expediente/            Schema y persistencia del Expediente Estructurado
ingesta/               Extracción de PDF/DOCX/XLSX/imágenes, OCR, clasificación de documentos
analistas/             Agentes de análisis: técnico, evidencias, económico, I+D+i
consultor/             Agente consultor/supervisor — genera incidencias
incidencias/           Tipos de incidencia, prioridades, resolución
redactores/            Un agente por apartado de la memoria (1.1.1, 1.1.2, 1.2, 1.3, 1.4)
revisores/             Revisores especializados (coherencia, técnico, I+D+i, evidencias, económico)
integrador/            Ensamblado final en la plantilla Word oficial (código, no LLM)
prompts/               Prompts de cada agente, como archivos propios (no generados sobre la marcha)
casos_prueba/          Casos sintéticos/reducidos para pruebas por capas
llm_cache/             Respuestas de LLM cacheadas en modo prueba (evita llamadas repetidas)
tests/                 unit/ (código puro) e integration/ (flujo completo sobre caso sintético)
```

## Mapeo de apartados (numeración granular → oficial)

| Apartado oficial | Contenido |
|---|---|
| 1.1.1 Resumen | Datos generales, contexto, objetivos (tecnológico y empresarial) |
| 1.1.2 Innovación/novedad/avances | Estado del arte, problemas/limitaciones, novedades tecnológicas |
| 1.2 Planificación | Actividades por fase, ejecución, resultados y evidencias — narrativa integrada por fase |
| 1.3 Justificación I+D+i | Clasificación Art. 35 (I+D / IT / no deducible) y su defensa |
| 1.4 Presupuesto | Presupuesto, desviaciones, procedencia de recursos, otros gastos |

## Estado del proyecto

En construcción por fases. Ver historial de commits para seguir la evolución.

- [x] Arquitectura definida y mapeo de apartados confirmado
- [ ] Schema del Expediente Estructurado
- [ ] Caso de prueba sintético
- [ ] Ingesta mínima (MVP)
- [ ] Agente técnico (MVP)
- [ ] Consultor simplificado (MVP)
- [ ] Redactor 1.1.1 (MVP)
- [ ] Integración mínima a .docx (MVP)

## Notas

- Nunca se inventan cifras, normativa o contenido de documentos fuente. Si falta información,
  se crea una incidencia; no se rellena con contenido plausible.
- Las sumas y cuadres económicos se calculan siempre con código (pandas), nunca con LLM.
- Ningún apartado se redacta mientras existan incidencias de prioridad ALTA que le afecten.
- La arquitectura es agnóstica de proveedor de LLM (ver `config/llm_config.yaml`).
