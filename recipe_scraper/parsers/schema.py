"""Schema.org Recipe JSON-LD parser for structured recipe data."""

import json
from typing import Optional

from bs4 import BeautifulSoup

from ..core import Recipe
from ..utils import get_logger, parse_iso_duration

logger = get_logger("parsers.schema")


def extract_json_ld_recipe(html: str) -> Optional[dict]:
    """
    Find and return schema.org Recipe JSON-LD from HTML.

    Most modern recipe websites embed structured data as JSON-LD in
    <script type="application/ld+json"> tags.

    Parameters
    ----------
    html : str
        HTML content of the page.

    Returns
    -------
    Optional[dict]
        Recipe JSON-LD object if found, else None.
    """
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    logger.debug(f"Found {len(scripts)} JSON-LD script tags")

    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)

            # JSON-LD can be a single object or an array
            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                # Top-level Recipe
                if item.get("@type") == "Recipe":
                    logger.debug("Found Recipe in JSON-LD")
                    return item

                # Recipe nested inside @graph (common pattern)
                if "@graph" in item:
                    graph = item["@graph"]
                    if isinstance(graph, list):
                        for node in graph:
                            if isinstance(node, dict) and node.get("@type") == "Recipe":
                                logger.debug("Found Recipe in @graph")
                                return node

        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.debug(f"Error parsing JSON-LD: {exc}")
            continue

    logger.debug("No Recipe JSON-LD found")
    return None


def schema_to_recipe(data: dict) -> Recipe:
    """
    Convert a schema.org Recipe object to our Recipe dataclass.

    Parameters
    ----------
    data : dict
        Schema.org Recipe JSON object.

    Returns
    -------
    Recipe
    """
    logger.debug(f"Converting schema.org Recipe: {data.get('name', 'Unnamed')}")

    # ── Instructions ──────────────────────────────────────────────────────
    raw_instructions = data.get("recipeInstructions", [])
    instructions = []

    if isinstance(raw_instructions, str):
        instructions = [raw_instructions]
    elif isinstance(raw_instructions, list):
        for step in raw_instructions:
            if isinstance(step, str):
                instructions.append(step)
            elif isinstance(step, dict):
                if step.get("@type") == "HowToStep":
                    text = step.get("text") or step.get("itemListElement", "")
                    if text:
                        instructions.append(text)
                elif step.get("@type") == "HowToSection":
                    for substep in step.get("itemListElement", []):
                        if isinstance(substep, dict):
                            text = substep.get("text", "")
                            if text:
                                instructions.append(text)

    # ── Ingredients ───────────────────────────────────────────────────────
    ingredients = data.get("recipeIngredient", [])
    if isinstance(ingredients, str):
        ingredients = [ingredients]

    # ── Tags ──────────────────────────────────────────────────────────────
    tags = []
    keywords = data.get("keywords", "")
    if isinstance(keywords, str):
        tags = [k.strip() for k in keywords.split(",") if k.strip()]
    elif isinstance(keywords, list):
        tags = keywords

    category = data.get("recipeCategory")
    cuisine = data.get("recipeCuisine")
    if category and category not in tags:
        tags.append(category)
    if cuisine and cuisine not in tags:
        tags.append(cuisine)

    # ── Servings ──────────────────────────────────────────────────────────
    servings = data.get("recipeYield")
    if isinstance(servings, list) and servings:
        servings = servings[0]
    if isinstance(servings, int):
        servings = str(servings)

    # ── Build Recipe ──────────────────────────────────────────────────────
    recipe = Recipe(
        title=data.get("name", "Untitled Recipe"),
        description=data.get("description"),
        ingredients=ingredients,
        instructions=instructions,
        servings=servings,
        prep_time=parse_iso_duration(data.get("prepTime")),
        cook_time=parse_iso_duration(data.get("cookTime")),
        total_time=parse_iso_duration(data.get("totalTime")),
        tags=tags,
        notes=None,
    )
    recipe._source = "schema.org"
    logger.info(
        f"Converted recipe: {recipe.title} ({len(recipe.ingredients)} ingredients, "
        f"{len(recipe.instructions)} steps)"
    )
    return recipe
