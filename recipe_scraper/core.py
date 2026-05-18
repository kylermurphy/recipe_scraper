"""Core Recipe data model and utilities."""

import datetime
import pathlib
import textwrap
from dataclasses import asdict, dataclass, field
from typing import Optional

from .utils import escape_yaml


@dataclass
class Recipe:
    """
    Structured recipe representation.

    Field names match Jekyll front matter schema for seamless integration
    with the recipe website.
    """

    title: str
    ingredients: list = field(default_factory=list)
    instructions: list = field(default_factory=list)
    description: Optional[str] = None
    tags: list = field(default_factory=list)
    servings: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    notes: Optional[str] = None

    # Track where this recipe came from (for debugging/transparency)
    _source: Optional[str] = field(default=None, repr=False, compare=False)

    def __str__(self) -> str:
        """Compact, readable terminal view."""
        lines = [f"{'═' * 54}", f"  {self.title.upper()}", f"{'═' * 54}"]

        if self.tags:
            lines.append(f"Tags      : {', '.join(self.tags)}")
        if self.servings:
            lines.append(f"Servings  : {self.servings}")
        if self.prep_time:
            lines.append(f"Prep      : {self.prep_time}")
        if self.cook_time:
            lines.append(f"Cook      : {self.cook_time}")
        if self.total_time:
            lines.append(f"Total     : {self.total_time}")
        if self.description:
            lines.append(f"\n  {self.description}")

        lines += ["\nINGREDIENTS", "─" * 30]
        for item in self.ingredients:
            lines.append(f"  - {item}")

        lines += ["\nINSTRUCTIONS", "─" * 30]
        for i, step in enumerate(self.instructions, 1):
            wrapped = textwrap.fill(step, width=68, subsequent_indent="      ")
            lines.append(f"  {i:>2}. {wrapped}")

        if self.notes:
            lines += ["\nNOTES", "─" * 30, f"  {self.notes}"]

        lines.append("═" * 54)
        return "\n".join(lines)

    def to_markdown_str(self) -> str:
        """Return the recipe as Jekyll-compatible markdown."""
        if self.tags:
            tags_block = "tags:\n" + "\n".join(f"  - {t}" for t in self.tags)
        else:
            tags_block = "tags: []"

        front_matter = "\n".join(
            [
                "---",
                f'title: "{escape_yaml(self.title)}"',
                f'description: "{escape_yaml(self.description or "")}"',
                f"date: {datetime.date.today().isoformat()}",
                tags_block,
                f'servings: "{self.servings or ""}"',
                f'prep_time: "{self.prep_time or ""}"',
                f'cook_time: "{self.cook_time or ""}"',
                f'total_time: "{self.total_time or ""}"',
                "---",
            ]
        )

        ingredients_block = "\n".join(f"- {i}" for i in self.ingredients)
        instructions_block = "\n".join(
            f"{n}. {step}" for n, step in enumerate(self.instructions, 1)
        )

        if self.notes:
            wrapped = textwrap.fill(self.notes, width=76)
            notes_block = "\n## Notes\n\n" + "\n".join(
                f"> {ln}" for ln in wrapped.splitlines()
            ) + "\n"
        else:
            notes_block = ""

        return (
            front_matter
            + f"\n\n## Ingredients\n\n{ingredients_block}\n"
            + f"\n## Instructions\n\n{instructions_block}\n"
            + notes_block
        )

    def print_markdown(self) -> None:
        """Print the Jekyll markdown to stdout."""
        print(self.to_markdown_str())

    def to_markdown(self, output_dir: str = ".") -> pathlib.Path:
        """
        Write the recipe as a Jekyll markdown file.

        Filename is derived from the title:
            "Classic Banana Bread" → classic-banana-bread.md
        """
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        dest = pathlib.Path(output_dir)
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"{slug}.md"
        path.write_text(self.to_markdown_str(), encoding="utf-8")
        return path

    def to_dict(self) -> dict:
        """Return as a plain dict, suitable for json.dump()."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Reconstruct from a dict (e.g. loaded from JSON)."""
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})
