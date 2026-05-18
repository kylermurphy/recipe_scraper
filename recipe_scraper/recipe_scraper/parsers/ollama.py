"""Ollama LLM-based recipe parser."""

import json
import re
from typing import Optional

import requests

from ..core import Recipe
from ..utils import get_logger
from .regex import parse_recipe_from_text

logger = get_logger("parsers.ollama")

_SYSTEM_PROMPT = """
You are a recipe extraction assistant. Read the provided text and extract
any recipe it contains. Return ONLY a valid JSON object — no explanation,
no markdown fences, no preamble. Use null for any field you cannot find.

Required JSON shape:
{
  "title":        string,
  "description":  string or null,
  "tags":         [string, ...],
  "servings":     string or null,
  "prep_time":    string or null,
  "cook_time":    string or null,
  "total_time":   string or null,
  "ingredients":  [string, ...],
  "instructions": [string, ...],
  "notes":        string or null
}

If no recipe is found, return: {"error": "No recipe found"}
""".strip()


def parse_recipe_with_ollama(
    caption: str,
    ollama_url: str,
    ollama_model: str,
    timeout: int = 120,
) -> Recipe:
    """
    Parse using a local Ollama LLM, falling back to regex on any failure.

    Parameters
    ----------
    caption : str
        Raw text to parse.
    ollama_url : str
        Base URL of Ollama server, e.g. "http://localhost:11434".
    ollama_model : str
        Model name, e.g. "llama3.1:8b".
    timeout : int
        Request timeout in seconds.

    Returns
    -------
    Recipe
        Parsed by Ollama if successful, else by regex parser.
        The _source attribute indicates which was used.
    """
    logger.debug(f"Attempting Ollama parse with {ollama_model}...")

    endpoint = ollama_url.rstrip("/") + "/api/generate"
    payload = {
        "model": ollama_model,
        "prompt": f"Extract the recipe from this text:\n\n{caption}",
        "system": _SYSTEM_PROMPT,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        logger.warning(
            f"Could not connect to Ollama at {ollama_url}. Falling back to regex."
        )
        recipe = parse_recipe_from_text(caption)
        recipe._source = "regex_fallback"
        return recipe
    except requests.exceptions.Timeout:
        logger.warning(f"Ollama timed out after {timeout}s. Falling back to regex.")
        recipe = parse_recipe_from_text(caption)
        recipe._source = "regex_fallback"
        return recipe
    except requests.exceptions.RequestException as exc:
        logger.warning(f"Ollama request failed: {exc}. Falling back to regex.")
        recipe = parse_recipe_from_text(caption)
        recipe._source = "regex_fallback"
        return recipe

    # Parse response
    raw_text = response.json().get("response", "").strip()
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("Ollama returned invalid JSON. Falling back to regex.")
        logger.debug(f"Raw response: {raw_text[:200]!r}")
        recipe = parse_recipe_from_text(caption)
        recipe._source = "regex_fallback"
        return recipe

    if "error" in data:
        logger.info(f"Ollama: {data['error']}. Falling back to regex.")
        recipe = parse_recipe_from_text(caption)
        recipe._source = "regex_fallback"
        return recipe

    logger.info("Ollama extraction successful.")
    recipe = Recipe(
        title=data.get("title") or "Untitled Recipe",
        description=data.get("description"),
        tags=data.get("tags") or [],
        servings=data.get("servings"),
        prep_time=data.get("prep_time"),
        cook_time=data.get("cook_time"),
        total_time=data.get("total_time"),
        ingredients=data.get("ingredients") or [],
        instructions=data.get("instructions") or [],
        notes=data.get("notes"),
    )
    recipe._source = "ollama"
    return recipe
