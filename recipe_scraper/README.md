# recipe_scraper

Extract structured recipe data from Instagram posts and recipe websites.

[![Tests](https://github.com/yourusername/recipe_scraper/actions/workflows/tests.yml/badge.svg)](https://github.com/yourusername/recipe_scraper/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Instagram posts**: Extract recipes from post captions via `instaloader`
- **Recipe websites**: Try schema.org JSON-LD first, fall back to text parsing
- **Multiple parsers**: 
  - Schema.org (fast, accurate for modern recipe sites)
  - Regex heuristics (offline, no external services)
  - Ollama LLM (robust on messy unstructured text)
- **Jekyll export**: Save recipes as frontmatter + markdown for static sites
- **No API keys**: Fully open-source, no paid services

## Installation

```bash
pip install recipe_scraper
```

Or from GitHub:

```bash
pip install git+https://github.com/yourusername/recipe_scraper.git
```

## Quick Start

### As a library

```python
from recipe_scraper import get_recipe_from_url

# Instagram post
recipe = get_recipe_from_url("https://www.instagram.com/p/ABC123/")

# Recipe website (tries JSON-LD first)
recipe = get_recipe_from_url("https://cooking.nytimes.com/recipes/...")

# Save as Jekyll markdown
recipe.to_markdown("_recipes/")

# Print to terminal
print(recipe)
```

### With Ollama (optional, for better text parsing)

```python
recipe = get_recipe_from_url(
    url,
    ollama_url="http://localhost:11434",
    ollama_model="llama3.1:8b",
)
```

### From the command line

```bash
# Basic usage
recipe-scraper "https://www.instagram.com/p/ABC123/"

# With Ollama and save to Jekyll
recipe-scraper <url> \
    --ollama-url http://localhost:11434 \
    --ollama-model llama3.1:8b \
    --save _recipes/

# Instagram with login (avoids rate-limiting)
recipe-scraper <instagram_url> \
    --username myaccount --password mypassword

# Verbose logging
recipe-scraper <url> --verbose
```

## How It Works

### For Websites

1. Fetch HTML
2. Try to extract schema.org Recipe JSON-LD (fast, accurate)
3. If not found, extract text and parse with Ollama or regex

### For Instagram

1. Fetch caption via `instaloader`
2. Parse with Ollama (if configured) or regex

### Parsers

**Schema.org JSON-LD** — Fastest and most accurate
- Works on ~80% of modern recipe sites (NYT Cooking, Serious Eats, AllRecipes, BBC)
- Extracts title, description, ingredients, instructions, times, servings, tags, cuisine

**Regex Parser** — Offline, no external services
- Works well on structured captions/pages with clear section headers
- Detects ingredients, instructions, time, servings heuristically
- Falls back gracefully on ambiguous input

**Ollama Parser** — LLM-based, robust on messy text
- Requires local Ollama server: https://ollama.com
- Handles unstructured prose, blogs, non-English text
- Automatically falls back to regex on connection failure

## Development

### Clone and install

```bash
git clone https://github.com/yourusername/recipe_scraper.git
cd recipe_scraper
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
pytest --cov  # With coverage
```

### Format code

```bash
black recipe_scraper tests
ruff check recipe_scraper tests --fix
```

## License

MIT
