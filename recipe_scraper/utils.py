"""Shared utilities for recipe scraping."""

import logging
import re
from typing import Optional

# Configure module logger
logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a submodule."""
    return logging.getLogger(f"recipe_scraper.{name}")


def escape_yaml(s: str) -> str:
    """Escape double-quotes for safe embedding in YAML."""
    return s.replace('"', '\\"')


def parse_iso_duration(duration: Optional[str]) -> Optional[str]:
    """
    Convert ISO 8601 duration to human-readable string.

    PT15M           → "15 minutes"
    PT1H30M         → "1 hour 30 minutes"
    PT45M           → "45 minutes"
    P1DT2H          → "1 day 2 hours"
    """
    if not duration or not isinstance(duration, str):
        return None

    match = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return None

    days, hours, minutes, seconds = match.groups()
    parts = []

    if days:
        d = int(days)
        parts.append(f"{d} day" if d == 1 else f"{d} days")
    if hours:
        h = int(hours)
        parts.append(f"{h} hour" if h == 1 else f"{h} hours")
    if minutes:
        m = int(minutes)
        parts.append(f"{m} minute" if m == 1 else f"{m} minutes")
    if seconds:
        s = int(seconds)
        parts.append(f"{s} second" if s == 1 else f"{s} seconds")

    return " ".join(parts) if parts else None
