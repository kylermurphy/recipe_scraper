"""Fetch recipes from websites using structured data or text parsing."""

from typing import Optional

import requests
from bs4 import BeautifulSoup

from ..core import Recipe
from ..parsers.ollama import parse_recipe_with_ollama
from ..parsers.regex import parse_recipe_from_text
from ..parsers.schema import extract_json_ld_recipe, schema_to_recipe
from ..utils import get_logger

logger = get_logger("fetchers.website")


def extract_text_from_html(html: str) -> str:
    """
    Extract clean text from HTML for parsing.

    Removes navigation, footers, scripts, and styles.

    Parameters
    ----------
    html : str
        HTML content of the page.

    Returns
    -------
    str
        Extracted text.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Clean up: collapse whitespace, remove blank lines
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def fetch_website_recipe(
    url: str,
    ollama_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    timeout: int = 120,
) -> Recipe:
    """
    Fetch a recipe from a website.

    Strategy:
      1. Fetch HTML
      2. Try to extract schema.org JSON-LD (fast, accurate)
      3. If not found, extract text and parse with Ollama or regex

    Parameters
    ----------
    url : str
        Full URL of the recipe page.
    ollama_url : str, optional
        Ollama server URL for text parsing fallback.
    ollama_model : str, optional
        Ollama model name for text parsing fallback.
    timeout : int, optional
        Timeout for both HTTP fetch and Ollama (default 120s).

    Returns
    -------
    Recipe
        The _source attribute indicates extraction method:
        "schema.org", "ollama", "regex", or "regex_fallback".

    Raises
    ------
    ValueError
        If the URL cannot be fetched or no text can be extracted.
    """
    logger.debug(f"Fetching website: {url}")

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; recipe_scraper/0.1.0)"},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Failed to fetch {url}: {exc}") from exc

    html = response.text
    logger.info(f"Fetched {len(html)} bytes from {url}")

    # ── Try JSON-LD first ─────────────────────────────────────────────────
    schema_data = extract_json_ld_recipe(html)
    if schema_data:
        logger.info("Using schema.org Recipe JSON-LD")
        return schema_to_recipe(schema_data)

    # ── Fall back to text extraction + parsing ────────────────────────────
    logger.debug("No JSON-LD found. Extracting text for parsing...")
    text = extract_text_from_html(html)

    if not text.strip():
        raise ValueError(f"Could not extract any text from {url}")

    logger.info(f"Extracted {len(text)} chars of text")

    if ollama_url and ollama_model:
        logger.debug("Using Ollama parser for text")
        return parse_recipe_with_ollama(text, ollama_url, ollama_model, timeout)
    else:
        logger.debug("Using regex parser for text")
        return parse_recipe_from_text(text)
