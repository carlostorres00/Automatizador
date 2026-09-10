"""
Prueba rápida y manual de llm_client.py -- no es un test formal con pytest
todavía (eso vendrá en tests/unit/). Comprueba tres cosas sin gastar ninguna
llamada real a un proveedor:

  1. Un agente que no existe en la config lanza AgenteNoConfiguradoError.
  2. Un agente que sí existe pero sigue con proveedor/modelo a null lanza
     ProveedorNoConfiguradoError (comportamiento esperado en el estado
     actual del proyecto: nada configurado todavía).
  3. Si se escribe manualmente una entrada de caché con la misma clave que
     generaría una llamada real, esa llamada se sirve desde caché y NO
     lanza ProveedorNoConfiguradoError -- así se puede seguir construyendo
     agentes ya mismo, sin esperar a tener una API key.

Ejecútalo con:
    python prueba_llm_client.py
"""

from llm_client import (
    AgenteNoConfiguradoError,
    ProveedorNoConfiguradoError,
    call,
    _clave_cache,
    _ruta_cache,
    _escribir_cache,
    _cargar_config,
    BASE_DIR,
)

# 1. Agente inexistente.
try:
    call(agente="agente_que_no_existe", prompt="hola")
    print("FALLO: debería haber lanzado AgenteNoConfiguradoError")
except AgenteNoConfiguradoError as e:
    print(f"OK -- agente inexistente detectado: {e}")

# 2. Agente real, pero sin proveedor/modelo configurado (estado actual del proyecto).
try:
    call(agente="redactor_1_1_1", prompt="hola")
    print("FALLO: debería haber lanzado ProveedorNoConfiguradoError")
except ProveedorNoConfiguradoError as e:
    print(f"OK -- proveedor no configurado detectado: {e}")

# 3. Simulamos una entrada de caché para ese mismo agente/prompt y comprobamos
#    que la llamada se sirve desde ahí, sin tocar ningún proveedor real.
config = _cargar_config()
modo_prueba = config.get("modo_prueba", {})
directorio_cache = BASE_DIR / modo_prueba.get("directorio_cache", "llm_cache/")

prompt_prueba = "Extrae los objetivos tecnológicos del proyecto SORRA."
clave = _clave_cache(
    agente="redactor_1_1_1",
    modelo=None,  # el modelo sigue siendo null en la config real -> misma clave
    prompt=prompt_prueba,
    system=None,
    temperature=0.0,
    max_tokens=4096,
)
ruta_cache = _ruta_cache(directorio_cache, "redactor_1_1_1", clave)
_escribir_cache(ruta_cache, {
    "agente": "redactor_1_1_1",
    "proveedor": None,
    "modelo": None,
    "system": None,
    "prompt": prompt_prueba,
    "respuesta": "[RESPUESTA CACHEADA DE PRUEBA] Objetivo tecnológico: ...",
})

respuesta = call(agente="redactor_1_1_1", prompt=prompt_prueba)
print(f"OK -- respuesta servida desde caché: {respuesta}")

# Limpieza: no dejar basura de prueba en llm_cache/.
ruta_cache.unlink()
if not any(ruta_cache.parent.iterdir()):
    ruta_cache.parent.rmdir()
print("\nCaché de prueba limpiada.")
