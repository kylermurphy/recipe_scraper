"""
recipe_scraper
==============
Extract structured recipe data from Instagram posts and recipe websites.

100% open-source — no API keys, no paid services.

SOURCES
-------
  Instagram posts  — Fetch captions via instaloader
  Recipe websites  — Fetch HTML, extract schema.org JSON-LD or parse text

PARSERS
-------
  Structured data (schema.org JSON-LD)  — Fast, accurate (websites only)
  Regex parser                          — Offline, no external services
  Ollama LLM parser                     — Robust on messy unstructured text

Quick start
-----------
    from recipe_scraper import get_recipe_from_url

    # Instagram post:
    recipe = get_recipe_from_url("https://www.instagram.com/p/SHORTCODE/")

    # Recipe website:
    recipe = get_recipe_from_url("https://cooking.nytimes.com/recipes/...")

    # With Ollama for better parsing:
    recipe = get_recipe_from_url(
        url,
        ollama_url="http://localhost:11434",
        ollama_model="llama3.1:8b",
    )

    print(recipe)
    recipe.to_markdown("_recipes/")
"""

from typing import Optional

from .core import Recipe
from .fetchers import fetch_instagram_caption, fetch_website_recipe
from .parsers.ollama import parse_recipe_with_ollama
from .parsers.regex import parse_recipe_from_text

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = [
    "Recipe",
    "get_recipe_from_url",
    "get_recipe_from_caption",
    "fetch_instagram_caption",
    "fetch_website_recipe",
    "parse_recipe_from_text",
    "parse_recipe_with_ollama",
]


def get_recipe_from_url(
    url: str,
    *,
    instagram_username: Optional[str] = None,
    instagram_password: Optional[str] = None,
    ollama_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    ollama_timeout: int = 120,
) -> Recipe:
    """
    Fetch a recipe from any URL — Instagram or a recipe website.

    The function detects the source and uses the appropriate method:
      - Instagram: fetch caption via instaloader, parse with Ollama or regex
      - Websites:  try JSON-LD structured data, fall back to text parsing

    Parameters
    ----------
    url : str
        Full URL (Instagram post or recipe website).
    instagram_username : str, optional
        For Instagram only. Avoids rate-limiting; required for private posts.
    instagram_password : str, optional
        For Instagram only. Required if username is set.
    ollama_url : str, optional
        Ollama server URL, e.g. "http://localhost:11434". Enables LLM parsing.
    ollama_model : str, optional
        Ollama model, e.g. "llama3.1:8b". Required if ollama_url is set.
    ollama_timeout : int, optional
        Timeout in seconds for Ollama and HTTP requests (default 120).

    Returns
    -------
    Recipe
        The _source attribute indicates the extraction method used:
        "schema.org", "ollama", "regex", or "regex_fallback".

    Examples
    --------
    # Instagram post with Ollama:
    recipe = get_recipe_from_url(
        "https://www.instagram.com/p/ABC123/",
        ollama_url="http://localhost:11434",
        ollama_model="llama3.1:8b",
    )

    # Recipe website (tries JSON-LD first):
    recipe = get_recipe_from_url("https://cooking.nytimes.com/recipes/...")

    # Save to Jekyll site:
    recipe.to_markdown("_recipes/")
    """
    if "instagram.com" in url:
        caption = fetch_instagram_caption(url, instagram_username, instagram_password)
        if ollama_url and ollama_model:
            recipe = parse_recipe_with_ollama(caption, ollama_url, ollama_model, ollama_timeout)
        else:
            recipe = parse_recipe_from_text(caption)
    else:
        recipe =fetch_website_recipe(url, ollama_url, ollama_model, ollama_timeout)

    recipe.src_url = url
    return recipe


def get_recipe_from_caption(
    caption: str,
    *,
    ollama_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    ollama_timeout: int = 120,
    url: Optional[str] = None,
) -> Recipe:
    """
    Parse a recipe from raw text.

    Useful for testing or when you have already scraped the caption by
    other means and just want the structured output.

    Parameters
    ----------
    caption : str
        Any text that may contain a recipe.
    ollama_url : str, optional
        Ollama server URL for LLM parsing.
    ollama_model : str, optional
        Ollama model name for LLM parsing.
    ollama_timeout : int, optional
        Timeout for Ollama in seconds (default 120).

    Returns
    -------
    Recipe
    """
    if ollama_url and ollama_model:
        recipe = parse_recipe_with_ollama(caption, ollama_url, ollama_model, ollama_timeout)
    else:
        recipe = parse_recipe_from_text(caption)

    recipe.src_url = url
    return recipe
