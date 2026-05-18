"""Tests for recipe_scraper.parsers."""

import json

import pytest

from recipe_scraper.parsers.regex import parse_recipe_from_text
from recipe_scraper.parsers.schema import extract_json_ld_recipe, schema_to_recipe
from recipe_scraper.utils import parse_iso_duration

from .fixtures import (
    SAMPLE_HTML_NO_SCHEMA,
    SAMPLE_HTML_WITH_SCHEMA,
    SAMPLE_INSTAGRAM_CAPTION,
    SAMPLE_SCHEMA_JSON_LD,
)


class TestRegexParser:
    """Test regex-based recipe parser."""

    def test_parse_instagram_caption(self):
        """Test parsing an Instagram caption."""
        recipe = parse_recipe_from_text(SAMPLE_INSTAGRAM_CAPTION)

        assert recipe.title.lower().__contains__("banana bread")
        assert len(recipe.ingredients) >= 6
        assert len(recipe.instructions) >= 5
        assert recipe.servings is not None
        assert recipe.prep_time is not None
        assert recipe.cook_time is not None
        assert recipe._source == "regex"

    def test_parse_simple_recipe(self):
        """Test parsing a simple recipe."""
        text = """
        Simple Pasta

        Ingredients:
        - 200g pasta
        - 400g tomatoes
        - 3 cloves garlic

        Instructions:
        1. Boil water
        2. Cook pasta
        3. Mix with sauce
        """
        recipe = parse_recipe_from_text(text)

        assert "Pasta" in recipe.title or "pasta" in recipe.title.lower()
        assert len(recipe.ingredients) == 3
        assert len(recipe.instructions) == 3

    def test_parse_recipe_with_times(self):
        """Test time extraction."""
        text = """
        Quick Recipe
        Prep time: 15 minutes
        Cook time: 30 minutes

        Ingredients:
        - flour

        Instructions:
        1. Mix
        2. Bake
        """
        recipe = parse_recipe_from_text(text)

        assert recipe.prep_time is not None
        assert "15" in recipe.prep_time
        assert recipe.cook_time is not None
        assert "30" in recipe.cook_time

    def test_parse_empty_caption(self):
        """Test parsing empty/minimal text."""
        recipe = parse_recipe_from_text("")
        assert recipe.title == "Untitled Recipe"
        assert recipe.ingredients == []
        assert recipe.instructions == []


class TestSchemaParser:
    """Test schema.org JSON-LD parser."""

    def test_extract_json_ld_from_html(self):
        """Test extracting JSON-LD from HTML."""
        schema = extract_json_ld_recipe(SAMPLE_HTML_WITH_SCHEMA)

        assert schema is not None
        assert schema["@type"] == "Recipe"
        assert schema["name"] == "Pasta al Pomodoro"

    def test_extract_json_ld_no_recipe(self):
        """Test extraction when no recipe schema exists."""
        schema = extract_json_ld_recipe(SAMPLE_HTML_NO_SCHEMA)
        assert schema is None

    def test_schema_to_recipe(self):
        """Test converting schema.org JSON to Recipe."""
        data = json.loads(SAMPLE_SCHEMA_JSON_LD)
        recipe = schema_to_recipe(data)

        assert recipe.title == "Pasta al Pomodoro"
        assert recipe.description is not None
        assert len(recipe.ingredients) == 5
        assert len(recipe.instructions) == 4
        assert "pasta" in recipe.tags or "Pasta" in recipe.tags
        assert recipe.prep_time == "5 minutes"
        assert recipe.cook_time == "25 minutes"
        assert recipe._source == "schema.org"

    def test_schema_with_array_instructions(self):
        """Test parsing schema with HowToStep array."""
        data = json.loads(SAMPLE_SCHEMA_JSON_LD)
        recipe = schema_to_recipe(data)

        assert len(recipe.instructions) == 4
        assert "Bring water" in recipe.instructions[0]

    def test_schema_with_string_instructions(self):
        """Test parsing schema with string instructions."""
        data = {
            "name": "Test",
            "recipeIngredient": ["flour"],
            "recipeInstructions": "Just mix and bake",
        }
        recipe = schema_to_recipe(data)

        assert len(recipe.instructions) == 1
        assert recipe.instructions[0] == "Just mix and bake"


class TestUtilFunctions:
    """Test utility functions."""

    def test_parse_iso_duration_minutes(self):
        """Test parsing ISO 8601 minutes."""
        assert parse_iso_duration("PT15M") == "15 minutes"
        assert parse_iso_duration("PT1M") == "1 minute"

    def test_parse_iso_duration_hours(self):
        """Test parsing ISO 8601 hours."""
        assert parse_iso_duration("PT1H") == "1 hour"
        assert parse_iso_duration("PT2H") == "2 hours"

    def test_parse_iso_duration_combined(self):
        """Test parsing ISO 8601 combined."""
        assert parse_iso_duration("PT1H30M") == "1 hour 30 minutes"
        assert parse_iso_duration("PT2H15M") == "2 hours 15 minutes"

    def test_parse_iso_duration_invalid(self):
        """Test parsing invalid ISO durations."""
        assert parse_iso_duration("invalid") is None
        assert parse_iso_duration(None) is None
        assert parse_iso_duration("") is None
