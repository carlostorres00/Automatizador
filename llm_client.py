"""
Punto de entrada único para que cualquier agente pida una respuesta a un LLM.

Ningún agente debe saber qué proveedor o modelo hay detrás -- solo llama a
`llm_client.call(agente="analista_tecnico", prompt=..., system=...)` y este
módulo decide el resto a partir de `config/llm_config.yaml`.

Dos cosas más que hace, siempre:
  1. Caché en modo prueba: si `modo_prueba.usar_cache` está activo, cada
     llamada (agente + modelo + prompt + system + parámetros) se guarda en
     `llm_cache/<agente>/<hash>.json`. Si esa misma llamada ya se hizo antes,
     se devuelve la respuesta cacheada sin gastar ni una llamada real. Esto
     es lo que permite ejecutar el caso sintético una y otra vez sin coste.
  2. Falla explícitamente si un agente no tiene proveedor/modelo configurado
     todavía, en vez de devolver una respuesta silenciosa o inventada -- el
     mismo principio de "nunca rellenar con contenido plausible" del schema.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import yaml

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
RUTA_CONFIG_POR_DEFECTO = BASE_DIR / "config" / "llm_config.yaml"


# ---------------------------------------------------------------------------
# Errores explícitos
# ---------------------------------------------------------------------------

class AgenteNoConfiguradoError(KeyError):
    """El nombre de agente no existe en config/llm_config.yaml."""


class ProveedorNoConfiguradoError(RuntimeError):
    """El agente existe en la config, pero aún no tiene proveedor/modelo (placeholder null)."""


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class ConfigAgente:
    nivel: str
    proveedor: Optional[str]
    modelo: Optional[str]


def _cargar_config(ruta_config: Path = RUTA_CONFIG_POR_DEFECTO) -> dict:
    with open(ruta_config, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolver_config_agente(config: dict, agente: str) -> ConfigAgente:
    agentes = config.get("agentes", {})
    if agente not in agentes:
        disponibles = ", ".join(sorted(agentes))
        raise AgenteNoConfiguradoError(
            f"'{agente}' no existe en config/llm_config.yaml. "
            f"Agentes configurados: {disponibles}"
        )
    datos = agentes[agente] or {}
    return ConfigAgente(
        nivel=datos.get("nivel"),
        proveedor=datos.get("proveedor"),
        modelo=datos.get("modelo"),
    )


# ---------------------------------------------------------------------------
# Caché (modo_prueba)
# ---------------------------------------------------------------------------

def _clave_cache(agente: str, modelo: Optional[str], prompt: str,
                  system: Optional[str], temperature: float, max_tokens: int) -> str:
    payload = json.dumps(
        {
            "agente": agente,
            "modelo": modelo,
            "prompt": prompt,
            "system": system,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _ruta_cache(directorio_cache: Path, agente: str, clave: str) -> Path:
    return directorio_cache / agente / f"{clave}.json"


def _leer_cache(ruta: Path) -> Optional[dict]:
    if not ruta.exists():
        return None
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Caché ilegible en '{ruta}', se ignora: {e}")
        return None


def _escribir_cache(ruta: Path, contenido: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Proveedores
# ---------------------------------------------------------------------------

def _llamar_anthropic(modelo: str, prompt: str, system: Optional[str],
                       temperature: float, max_tokens: int) -> str:
    import anthropic  # import perezoso: solo si de verdad se usa este proveedor

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProveedorNoConfiguradoError(
            "Falta la variable de entorno ANTHROPIC_API_KEY para llamar a Anthropic."
        )

    cliente = anthropic.Anthropic(api_key=api_key)
    respuesta = cliente.messages.create(
        model=modelo,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system or "",
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(bloque.text for bloque in respuesta.content if bloque.type == "text")


def _llamar_google(modelo: str, prompt: str, system: Optional[str],
                    temperature: float, max_tokens: int) -> str:
    import google.generativeai as genai  # import perezoso

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ProveedorNoConfiguradoError(
            "Falta la variable de entorno GOOGLE_API_KEY para llamar a Google."
        )

    genai.configure(api_key=api_key)
    cliente = genai.GenerativeModel(modelo, system_instruction=system or None)
    respuesta = cliente.generate_content(
        prompt,
        generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
    )
    return respuesta.text


_PROVEEDORES: dict[str, Callable[[str, str, Optional[str], float, int], str]] = {
    "anthropic": _llamar_anthropic,
    "google": _llamar_google,
}


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def call(
    agente: str,
    prompt: str,
    *,
    system: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    forzar_llamada: bool = False,
    ruta_config: Path = RUTA_CONFIG_POR_DEFECTO,
) -> str:
    """
    Pide una respuesta de texto al LLM configurado para `agente`.

    - `forzar_llamada=True` ignora la caché aunque `modo_prueba.usar_cache`
      esté activo (útil para regenerar una respuesta cacheada a propósito).
    - Lanza `AgenteNoConfiguradoError` si `agente` no está en la config.
    - Lanza `ProveedorNoConfiguradoError` si el agente existe pero su
      proveedor/modelo siguen a `null` (o si falta la API key), y no hay
      nada cacheado que sirva -- nunca se devuelve una respuesta inventada.
    """
    config = _cargar_config(ruta_config)
    cfg_agente = _resolver_config_agente(config, agente)

    modo_prueba = config.get("modo_prueba", {})
    usar_cache = bool(modo_prueba.get("usar_cache", False))
    directorio_cache = BASE_DIR / modo_prueba.get("directorio_cache", "llm_cache/")

    clave = _clave_cache(agente, cfg_agente.modelo, prompt, system, temperature, max_tokens)
    ruta_cache = _ruta_cache(directorio_cache, agente, clave)

    if usar_cache and not forzar_llamada:
        cacheado = _leer_cache(ruta_cache)
        if cacheado is not None:
            logger.info(f"[{agente}] respuesta servida desde caché ({ruta_cache.name})")
            return cacheado["respuesta"]

    if not cfg_agente.proveedor or not cfg_agente.modelo:
        raise ProveedorNoConfiguradoError(
            f"El agente '{agente}' todavía no tiene 'proveedor' ni 'modelo' en "
            f"config/llm_config.yaml (nivel configurado: '{cfg_agente.nivel}'). "
            "Rellénalos antes de llamarlo, o añade una respuesta a la caché "
            "para poder seguir desarrollando sin proveedor real."
        )

    proveedor_fn = _PROVEEDORES.get(cfg_agente.proveedor)
    if proveedor_fn is None:
        raise ValueError(
            f"Proveedor '{cfg_agente.proveedor}' no soportado. "
            f"Soportados: {sorted(_PROVEEDORES)}"
        )

    logger.info(f"[{agente}] llamando a {cfg_agente.proveedor}/{cfg_agente.modelo}")
    respuesta = proveedor_fn(cfg_agente.modelo, prompt, system, temperature, max_tokens)

    if usar_cache:
        _escribir_cache(ruta_cache, {
            "agente": agente,
            "proveedor": cfg_agente.proveedor,
            "modelo": cfg_agente.modelo,
            "system": system,
            "prompt": prompt,
            "respuesta": respuesta,
        })

    return respuesta
