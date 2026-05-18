"""Regex-based recipe parser for unstructured text."""

import re
from typing import Optional

from ..core import Recipe
from ..utils import get_logger

logger = get_logger("parsers.regex")

# ── Section headers ───────────────────────────────────────────────────────
_HEADER_INGREDIENT = re.compile(
    r"^\W*(ingredients?|you.?ll need|you need|what you need|"
    r"for the\b|for this recipe|shopping list)\W*$",
    re.IGNORECASE,
)
_HEADER_INSTRUCTION = re.compile(
    r"^\W*(instructions?|directions?|methods?|steps?|"
    r"how to (?:make|cook|prepare)|let.?s (?:make|cook))\W*$",
    re.IGNORECASE,
)
_HEADER_NOTE = re.compile(
    r"^\W*(notes?|tips?|tricks?|variations?|storage|"
    r"make.?ahead|substitutions?)\W*$",
    re.IGNORECASE,
)

# ── Ingredient detection ──────────────────────────────────────────────────
_UNITS = (
    r"cups?|tbsps?|tsps?|tablespoons?|teaspoons?|"
    r"oz|ounces?|lbs?|pounds?|grams?|g\b|kg\b|"
    r"ml\b|litres?|liters?|l\b|"
    r"pinch(?:es)?|handful|cloves?|slices?|pieces?|"
    r"cans?|packages?|pkgs?|sticks?|bunches?|heads?"
)
_QUANTITY = r"[\d]+(?:[./][\d]+)?"
_QUANTITY_UNICODE = r"[¼½¾⅓⅔⅛⅜⅝⅞]"

_RE_INGREDIENT = re.compile(
    rf"(?:{_QUANTITY}\s*(?:{_UNITS})\b)"
    rf"|^[\s]*[*\-\u2022\u2023\u25E6]"
    rf"|^[\s]*(?:{_QUANTITY})\s+\w",
    re.IGNORECASE | re.MULTILINE,
)
_RE_FRACTION_UNICODE = re.compile(_QUANTITY_UNICODE)

# ── Instruction detection ──────────────────────────────────────────────────
_RE_NUMBERED_STEP = re.compile(r"^\s*(?:step\s*)?\d+[.):\-]\s+", re.IGNORECASE)
_COOKING_VERBS = (
    r"add|mix|stir|fold|combine|whisk|beat|blend|pour|place|put|"
    r"heat|cook|bake|boil|simmer|fry|saut[eé]|roast|grill|broil|"
    r"chop|dice|slice|mince|grate|peel|wash|rinse|drain|strain|"
    r"preheat|prepare|season|taste|serve|remove|transfer|let|allow|"
    r"refrigerate|freeze|rest|cool|bring|reduce|thicken|spread|layer"
)
_RE_COOKING_VERB = re.compile(rf"^\s*(?:{_COOKING_VERBS})\b", re.IGNORECASE)

# ── Time & servings ──────────────────────────────────────────────────────
_RE_PREP_TIME = re.compile(
    r"prep(?:aration)?\s*(?:time)?\s*[:\-]?\s*"
    r"(\d+\s*(?:hour|hr|minute|min)s?(?:\s*\d+\s*(?:minute|min)s?)?)",
    re.IGNORECASE,
)
_RE_COOK_TIME = re.compile(
    r"cook(?:ing)?\s*(?:time)?\s*[:\-]?\s*"
    r"(\d+\s*(?:hour|hr|minute|min)s?(?:\s*\d+\s*(?:minute|min)s?)?)",
    re.IGNORECASE,
)
_RE_BAKE_TIME = re.compile(
    r"(?:bake|cook|roast|fry|simmer)\s+for\s+"
    r"(\d+(?:[–\-]\d+)?\s*(?:hour|hr|minute|min)s?)",
    re.IGNORECASE,
)
_RE_TOTAL_TIME = re.compile(
    r"(?:ready|done|total)\s+in\s+(\d+\s*(?:hour|hr|minute|min)s?)",
    re.IGNORECASE,
)
_RE_SERVINGS = re.compile(
    r"(?:serves?|servings?|makes?|yields?|portions?)\s*[:\-]?\s*"
    r"(\d+(?:[–\-]\d+)?(?:\s*\w+)?)",
    re.IGNORECASE,
)

# ── Noise ────────────────────────────────────────────────────────────────
_RE_HASHTAGS = re.compile(r"#\w+")
_RE_MENTIONS = re.compile(r"@\w+")
_RE_EMOJI_ONLY = re.compile(r"^[\s\U0001F000-\U0001FFFF\u2600-\u26FF\u2700-\u27BF]+$")
_RE_LEADING_EMOJI = re.compile(r"^[\U0001F000-\U0001FFFF\u2600-\u26FF\u2700-\u27BF\s]+")


def parse_recipe_from_text(caption: str) -> Recipe:
    """
    Parse a recipe from text using regex heuristics.

    Works in two passes:
      1. Segment — classify each line into zones using headers + heuristics
      2. Extract — clean each zone and pull metadata from full text

    Parameters
    ----------
    caption : str
        Raw text, e.g. an Instagram post caption.

    Returns
    -------
    Recipe
        Missing fields are None or [] — the parser never raises.
    """
    logger.debug(f"Parsing recipe from text ({len(caption)} chars)")

    cleaned = _clean_caption(caption)
    zones = _segment_caption(cleaned)
    prep_time, cook_time = _extract_times(cleaned)

    recipe = Recipe(
        title=_extract_title(zones["title"], cleaned),
        ingredients=_extract_ingredients(zones["ingredients"]),
        instructions=_extract_instructions(zones["instructions"]),
        notes=_extract_notes(zones["notes"]),
        servings=_extract_servings(cleaned),
        prep_time=prep_time,
        cook_time=cook_time,
        total_time=None,
        tags=[],
    )
    recipe._source = "regex"
    logger.info(
        f"Parsed recipe: {recipe.title} ({len(recipe.ingredients)} ingredients, "
        f"{len(recipe.instructions)} steps)"
    )
    return recipe


def _clean_caption(caption: str) -> str:
    """Remove hashtags, @mentions, collapse excess blank lines."""
    text = _RE_HASHTAGS.sub("", caption)
    text = _RE_MENTIONS.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_bullet(line: str) -> str:
    """Remove leading bullets and decorative emoji."""
    line = re.sub(r"^[\s\*\-\u2022\u2023\u25E6]+", "", line)
    line = _RE_LEADING_EMOJI.sub("", line, count=1)
    return line.strip()


def _strip_step_number(line: str) -> str:
    """Remove a leading step number."""
    return _RE_NUMBERED_STEP.sub("", line).strip()


def _looks_like_ingredient(line: str) -> bool:
    if not line.strip():
        return False
    return bool(_RE_INGREDIENT.search(line) or _RE_FRACTION_UNICODE.search(line))


def _looks_like_instruction(line: str) -> bool:
    if not line.strip():
        return False
    return bool(_RE_NUMBERED_STEP.match(line) or _RE_COOKING_VERB.match(line))


def _segment_caption(caption: str) -> dict:
    """Divide caption into named zones."""
    zones = {k: [] for k in ("title", "ingredients", "instructions", "notes", "misc")}
    current_zone = "misc"
    found_explicit_header = False

    for line in caption.splitlines():
        stripped = line.strip()
        if _RE_EMOJI_ONLY.match(stripped) and len(stripped) < 5:
            continue
        if _HEADER_INGREDIENT.match(stripped):
            current_zone, found_explicit_header = "ingredients", True
            continue
        if _HEADER_INSTRUCTION.match(stripped):
            current_zone, found_explicit_header = "instructions", True
            continue
        if _HEADER_NOTE.match(stripped):
            current_zone, found_explicit_header = "notes", True
            continue
        if not found_explicit_header:
            if _looks_like_ingredient(stripped):
                current_zone = "ingredients"
            elif _looks_like_instruction(stripped):
                current_zone = "instructions"
        zones[current_zone].append(stripped)

    misc = [ln for ln in zones["misc"] if ln]
    if misc:
        zones["title"] = [misc[0]]
        zones["misc"] = misc[1:]
    return zones


def _extract_title(title_lines: list, raw: str) -> str:
    """Extract recipe title."""
    candidates = [ln.strip() for ln in title_lines if ln.strip()]
    if candidates:
        t = _strip_bullet(candidates[0])
        if len(t) <= 80:
            return t
        sentence = re.split(r"[.!?]", t)[0].strip()
        if sentence:
            return sentence
    for line in raw.splitlines():
        s = line.strip()
        if s and len(s) <= 80:
            return _strip_bullet(s)
    return "Untitled Recipe"


def _extract_ingredients(lines: list) -> list:
    """Extract ingredients from lines."""
    return [_strip_bullet(ln) for ln in lines if _strip_bullet(ln)]


def _extract_instructions(lines: list) -> list:
    """Extract instructions from lines."""
    result = []
    for line in lines:
        cleaned = _strip_bullet(_strip_step_number(line))
        if len(cleaned) >= 10:
            result.append(cleaned)
    return result


def _extract_times(caption: str) -> tuple:
    """Extract prep and cook times."""
    prep_time = cook_time = None
    m = _RE_PREP_TIME.search(caption)
    if m:
        prep_time = m.group(1).strip()
    m = _RE_COOK_TIME.search(caption)
    if m:
        cook_time = m.group(1).strip()
    if not cook_time:
        m = _RE_BAKE_TIME.search(caption)
        if m:
            cook_time = m.group(1).strip()
    if not prep_time and not cook_time:
        m = _RE_TOTAL_TIME.search(caption)
        if m:
            cook_time = m.group(1).strip()
    return prep_time, cook_time


def _extract_servings(caption: str) -> Optional[str]:
    """Extract servings."""
    m = _RE_SERVINGS.search(caption)
    return m.group(0).strip() if m else None


def _extract_notes(lines: list) -> Optional[str]:
    """Extract notes from lines."""
    text = " ".join(ln.strip() for ln in lines if ln.strip())
    return text or None
