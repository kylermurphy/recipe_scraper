# recipe_scraper Module Structure

This is a complete, production-ready Python module for scraping recipes from Instagram posts and recipe websites.

## Quick Overview

```
recipe_scraper/
├── recipe_scraper/              # Main package
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # Recipe dataclass (core model)
│   ├── utils.py                 # Shared utilities (logging, parsing)
│   ├── cli.py                   # Command-line interface
│   ├── parsers/                 # Parsing modules
│   │   ├── __init__.py
│   │   ├── regex.py            # Heuristic regex parser
│   │   ├── ollama.py           # LLM-based parser
│   │   └── schema.py           # JSON-LD schema.org parser
│   └── fetchers/               # Data source modules
│       ├── __init__.py
│       ├── instagram.py        # Instagram caption fetcher
│       └── website.py          # Website HTML fetcher
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── fixtures.py             # Test data
│   ├── test_core.py            # Recipe tests
│   ├── test_parsers.py         # Parser tests
│   └── test_fetchers.py        # Fetcher tests
├── .github/
│   └── workflows/
│       └── tests.yml           # GitHub Actions CI
├── pyproject.toml              # Build & dependency config
├── README.md                   # User documentation
├── LICENSE                     # MIT License
└── .gitignore                 # Git ignore patterns
```

## Key Files Explained

### Core Module (`recipe_scraper/`)

**`__init__.py`** — Public API
- Exports: `Recipe`, `get_recipe_from_url()`, `get_recipe_from_caption()`
- Dispatcher that detects Instagram vs. websites and routes accordingly

**`core.py`** — Data Model
- `Recipe` dataclass: title, ingredients, instructions, tags, times, etc.
- Methods: `__str__()`, `to_markdown_str()`, `to_markdown()`, `to_dict()`, `from_dict()`
- Integrates with Jekyll front matter for static site generation

**`utils.py`** — Shared Utilities
- `get_logger()` — Consistent logging
- `escape_yaml()` — YAML escaping for front matter
- `parse_iso_duration()` — PT15M → "15 minutes"

**`cli.py`** — Command-Line Interface
- Entry point: `recipe-scraper <url>`
- Options: `--ollama-url`, `--ollama-model`, `--save`, `--username`, `--password`, `--verbose`
- Installed via `[project.scripts]` in pyproject.toml

### Parsers Subpackage (`recipe_scraper/parsers/`)

**`regex.py`** — Heuristic regex parser
- `parse_recipe_from_text(caption: str) -> Recipe`
- Detects section headers (Ingredients:, Instructions:, etc.)
- Extracts times via regex patterns
- Works offline, no dependencies beyond standard library
- Source: `"regex"`

**`ollama.py`** — LLM-based parser
- `parse_recipe_with_ollama(caption, ollama_url, ollama_model, timeout) -> Recipe`
- Sends text to local Ollama server
- Falls back to regex on any failure (connection, timeout, invalid JSON, etc.)
- Requires: `requests` library
- Source: `"ollama"` or `"regex_fallback"`

**`schema.py`** — JSON-LD structured data parser
- `extract_json_ld_recipe(html: str) -> Optional[dict]` — Find Recipe in HTML
- `schema_to_recipe(data: dict) -> Recipe` — Convert schema.org to Recipe
- Parses ISO 8601 durations (PT15M, PT1H30M, etc.)
- Handles HowToStep arrays and nested @graph structures
- Source: `"schema.org"`

### Fetchers Subpackage (`recipe_scraper/fetchers/`)

**`instagram.py`** — Instagram fetcher
- `fetch_instagram_caption(post_url, username, password) -> str`
- Uses `instaloader` to fetch post captions
- Supports login for avoiding rate-limits and accessing private posts
- Raises `ValueError` if no caption found

**`website.py`** — Website fetcher
- `fetch_website_recipe(url, ollama_url, ollama_model, timeout) -> Recipe`
- Orchestrates three-tier parsing strategy:
  1. Try JSON-LD schema.org (fast)
  2. If not found, extract text
  3. Parse text with Ollama or regex
- `extract_text_from_html(html) -> str` — Removes nav, footer, scripts, styles

## Dependencies

### Required (`pyproject.toml` `dependencies`)
- `instaloader>=4.10.0` — Instagram caption fetching
- `requests>=2.31.0` — HTTP requests for websites
- `beautifulsoup4>=4.12.0` — HTML parsing

### Optional (`[dev]`)
- `pytest>=7.4.0` — Testing framework
- `pytest-cov>=4.1.0` — Coverage reporting
- `black>=23.0.0` — Code formatter
- `ruff>=0.1.0` — Linter

## Installation & Usage

### As a package

```bash
# Install from GitHub
pip install git+https://github.com/yourusername/recipe_scraper.git

# Install with dev dependencies
pip install git+https://github.com/yourusername/recipe_scraper.git#egg=recipe_scraper[dev]

# Install locally (for development)
git clone https://github.com/yourusername/recipe_scraper.git
cd recipe_scraper
pip install -e ".[dev]"
```

### As a library

```python
from recipe_scraper import get_recipe_from_url, Recipe

# Fetch and parse
recipe = get_recipe_from_url("https://www.instagram.com/p/ABC123/")

# Or from a website
recipe = get_recipe_from_url("https://cooking.nytimes.com/recipes/...")

# With Ollama
recipe = get_recipe_from_url(
    url,
    ollama_url="http://localhost:11434",
    ollama_model="llama3.1:8b",
)

# Save to Jekyll
recipe.to_markdown("_recipes/")
```

### From command line

```bash
recipe-scraper "https://www.instagram.com/p/ABC123/"

recipe-scraper <url> \
    --ollama-url http://localhost:11434 \
    --ollama-model llama3.1:8b \
    --save _recipes/

recipe-scraper <url> --verbose
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=recipe_scraper

# Specific test file
pytest tests/test_parsers.py

# Specific test
pytest tests/test_core.py::TestRecipe::test_recipe_to_markdown_file
```

## How to Extend

### Add a new parser

1. Create `recipe_scraper/parsers/myparser.py`
2. Implement: `parse_recipe_with_myparser(text: str) -> Recipe`
3. Set `recipe._source = "myparser"`
4. Add tests in `tests/test_parsers.py`
5. Export from `recipe_scraper/parsers/__init__.py`

### Add a new fetcher

1. Create `recipe_scraper/fetchers/mysource.py`
2. Implement: `fetch_recipe_from_mysource(url: str, ...) -> Recipe`
3. Add tests in `tests/test_fetchers.py`
4. Integrate into `get_recipe_from_url()` in `recipe_scraper/__init__.py`

## GitHub Setup

1. Create repo: `https://github.com/yourusername/recipe_scraper`
2. Clone and add files
3. Update `pyproject.toml` with your GitHub URLs
4. Push to main branch
5. GitHub Actions will automatically run tests on every push

## Key Design Decisions

- **Dataclass over Pydantic**: Simple, no extra dependencies, easy to extend
- **Lazy imports**: `requests` and `beautifulsoup4` only imported when needed
- **Fallback strategy**: Always provide a usable result (Ollama → regex → minimal)
- **Source tracking**: Every `Recipe` has a `_source` attribute showing which parser was used
- **No configuration files**: All settings via function arguments or CLI flags
- **Structured data first**: Try JSON-LD before falling back to text parsing
- **Logging throughout**: DEBUG logs for troubleshooting, INFO for results

## Production Checklist

- [x] All core functionality implemented
- [x] Comprehensive unit tests (3 test files, 20+ test cases)
- [x] GitHub Actions CI/CD configured
- [x] README with examples and docs
- [x] MIT License included
- [x] .gitignore for Python projects
- [x] pyproject.toml with all metadata
- [x] Proper Python packaging (namespace, imports, etc.)
- [x] Type hints throughout
- [x] Logging configuration
- [x] Error handling and graceful fallbacks
- [x] CLI entry point
- [x] Documentation strings on all public functions
