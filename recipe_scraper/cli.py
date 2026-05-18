"""Command-line interface for recipe_scraper."""

import argparse
import logging
import sys

import instaloader

from . import get_recipe_from_url


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(name)s] %(levelname)s: %(message)s",
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract recipes from Instagram posts or recipe websites.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Instagram post:
  recipe-scraper https://www.instagram.com/p/ABC123/

  # Recipe website (tries JSON-LD first):
  recipe-scraper https://cooking.nytimes.com/recipes/...

  # With Ollama, save to Jekyll:
  recipe-scraper <url> \\
      --ollama-url http://localhost:11434 \\
      --ollama-model llama3.1:8b \\
      --save _recipes/

  # Instagram with login:
  recipe-scraper <instagram_url> \\
      --username me --password secret
        """,
    )
    parser.add_argument("url", help="URL (Instagram post or recipe website)")
    parser.add_argument(
        "--ollama-url", metavar="URL", help="Ollama server URL, e.g. http://localhost:11434"
    )
    parser.add_argument(
        "--ollama-model", metavar="MODEL", help="Ollama model, e.g. llama3.1:8b"
    )
    parser.add_argument(
        "--ollama-timeout",
        metavar="SECS",
        type=int,
        default=120,
        help="Timeout for Ollama/HTTP requests (default: 120)",
    )
    parser.add_argument(
        "--save",
        metavar="DIR",
        help="Save as Jekyll markdown in this directory (e.g. _recipes/)",
    )
    parser.add_argument("--username", help="Instagram username (optional)")
    parser.add_argument("--password", help="Instagram password (required if --username is set)")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        recipe = get_recipe_from_url(
            args.url,
            instagram_username=args.username,
            instagram_password=args.password,
            ollama_url=args.ollama_url,
            ollama_model=args.ollama_model,
            ollama_timeout=args.ollama_timeout,
        )

        # Print recipe summary and markdown
        print(recipe)
        print()
        recipe.print_markdown()

        # Optionally save to disk
        if args.save:
            path = recipe.to_markdown(args.save)
            print(f"\n✓ Saved to {path}")

        # Show which parser was used
        source = getattr(recipe, "_source", "unknown")
        print(f"[recipe_scraper] Extracted via: {source}")

    except (ValueError, instaloader.exceptions.InstaloaderException) as exc:
        print(f"[Error] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
