"""Tests for recipe_scraper.core."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from recipe_scraper.core import Recipe


class TestRecipe:
    """Test Recipe dataclass."""

    def test_recipe_creation(self):
        """Test creating a Recipe object."""
        recipe = Recipe(
            title="Test Recipe",
            ingredients=["1 cup flour", "2 eggs"],
            instructions=["Mix ingredients", "Bake"],
        )
        assert recipe.title == "Test Recipe"
        assert len(recipe.ingredients) == 2
        assert len(recipe.instructions) == 2

    def test_recipe_str(self):
        """Test Recipe __str__ representation."""
        recipe = Recipe(
            title="Banana Bread",
            ingredients=["3 bananas", "1 cup flour"],
            instructions=["Preheat oven", "Mix ingredients"],
            servings="8 slices",
            prep_time="10 minutes",
            cook_time="50 minutes",
        )
        output = str(recipe)
        assert "BANANA BREAD" in output
        assert "Servings" in output
        assert "Prep" in output
        assert "Cook" in output

    def test_recipe_to_markdown_str(self):
        """Test converting Recipe to markdown string."""
        recipe = Recipe(
            title="Test Recipe",
            description="A test recipe",
            ingredients=["1 cup flour"],
            instructions=["Mix and bake"],
            tags=["test", "quick"],
            servings="4",
            prep_time="5 minutes",
            cook_time="20 minutes",
            notes="No notes",
        )
        markdown = recipe.to_markdown_str()

        assert "---" in markdown  # Front matter
        assert 'title: "Test Recipe"' in markdown
        assert 'description: "A test recipe"' in markdown
        assert "- test" in markdown  # Tag in YAML list
        assert "## Ingredients" in markdown
        assert "## Instructions" in markdown
        assert "## Notes" in markdown
        assert "1 cup flour" in markdown
        assert "Mix and bake" in markdown

    def test_recipe_to_markdown_file(self):
        """Test saving Recipe to a markdown file."""
        recipe = Recipe(
            title="Banana Bread",
            ingredients=["3 bananas"],
            instructions=["Bake"],
        )

        with TemporaryDirectory() as tmpdir:
            path = recipe.to_markdown(tmpdir)
            assert path.exists()
            assert path.name == "banana-bread.md"
            content = path.read_text()
            assert "Banana Bread" in content
            assert "3 bananas" in content

    def test_recipe_to_dict(self):
        """Test converting Recipe to dict."""
        recipe = Recipe(
            title="Test",
            ingredients=["flour"],
            instructions=["bake"],
        )
        data = recipe.to_dict()

        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["ingredients"] == ["flour"]
        assert data["instructions"] == ["bake"]

    def test_recipe_from_dict(self):
        """Test reconstructing Recipe from dict."""
        original = Recipe(
            title="Test",
            ingredients=["flour", "sugar"],
            instructions=["mix", "bake"],
            servings="4",
        )
        data = original.to_dict()
        reconstructed = Recipe.from_dict(data)

        assert reconstructed.title == original.title
        assert reconstructed.ingredients == original.ingredients
        assert reconstructed.instructions == original.instructions
        assert reconstructed.servings == original.servings
