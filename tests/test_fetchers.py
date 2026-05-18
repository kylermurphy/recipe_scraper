"""Tests for recipe_scraper.fetchers."""

import pytest

from recipe_scraper.fetchers.website import extract_text_from_html

from .fixtures import SAMPLE_HTML_NO_SCHEMA, SAMPLE_HTML_WITH_SCHEMA


class TestWebsiteFetcher:
    """Test website fetching and text extraction."""

    def test_extract_text_from_html(self):
        """Test extracting clean text from HTML."""
        text = extract_text_from_html(SAMPLE_HTML_NO_SCHEMA)

        # Should remove nav and footer
        assert "Navigation stuff" not in text
        assert "Footer content" not in text

        # Should keep recipe content
        assert "Quick Pasta" in text
        assert "Ingredients" in text
        assert "200g pasta" in text

    def test_extract_text_removes_scripts(self):
        """Test that script tags are removed."""
        html = """
        <html>
        <body>
        <script>var x = 'should be removed';</script>
        <h1>Recipe Title</h1>
        </body>
        </html>
        """
        text = extract_text_from_html(html)

        assert "var x" not in text
        assert "Recipe Title" in text

    def test_extract_text_collapses_whitespace(self):
        """Test that extra whitespace is collapsed."""
        html = """
        <html>
        <body>
        <h1>Title</h1>


        <p>Content</p>
        </body>
        </html>
        """
        text = extract_text_from_html(html)
        lines = text.split("\n")

        # Should not have multiple blank lines
        blank_count = sum(1 for line in lines if line == "")
        assert blank_count <= 1

    def test_extract_text_from_empty_html(self):
        """Test extraction from minimal HTML."""
        html = "<html><body></body></html>"
        text = extract_text_from_html(html)

        assert text == ""

    def test_extract_text_from_html_with_schema(self):
        """Test extraction from HTML with schema."""
        text = extract_text_from_html(SAMPLE_HTML_WITH_SCHEMA)

        # Should remove script tags containing JSON-LD
        assert "@type" not in text
        assert "HowToStep" not in text

        # Should keep visible content
        assert "Pasta al Pomodoro" in text
        assert "A simple pasta recipe" in text
