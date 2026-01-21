"""Markdown document elements."""

from abc import ABC, abstractmethod
from typing import Optional


class MarkdownElement(ABC):
    """Base class for Markdown elements."""

    @abstractmethod
    def render(self) -> str:
        """Render element to Markdown string."""
        pass


class MarkdownParagraph(MarkdownElement):
    """A paragraph of text."""

    def __init__(self):
        self.text = ""
        self.heading_level: Optional[int] = None
        self.is_list_item = False
        self.list_marker = "-"

    def append_text(self, text: str):
        """Append text to paragraph."""
        self.text += text

    def set_text(self, text: str):
        """Set paragraph text."""
        self.text = text

    def set_heading_level(self, level: int):
        """Set heading level (1-6)."""
        self.heading_level = min(max(level, 1), 6)

    def render(self) -> str:
        """Render paragraph to Markdown."""
        text = self.text.strip()
        if not text:
            return ""

        if self.heading_level:
            return f"{'#' * self.heading_level} {text}"
        elif self.is_list_item:
            return f"{self.list_marker} {text}"
        else:
            return text


class MarkdownTable(MarkdownElement):
    """A table structure."""

    def __init__(self):
        self.rows: list[list[str]] = []
        self.has_header = True

    def set_rows(self, rows: list[list[str]]):
        """Set table rows."""
        self.rows = rows

    def render(self) -> str:
        """Render table to Markdown pipe table format."""
        if not self.rows:
            return ""

        lines = []

        # Determine column widths
        col_count = max(len(row) for row in self.rows) if self.rows else 0

        # Normalize rows to same column count
        normalized_rows = []
        for row in self.rows:
            normalized = list(row) + [""] * (col_count - len(row))
            normalized_rows.append(normalized)

        if not normalized_rows:
            return ""

        # Header row
        header = normalized_rows[0]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in header) + " |")

        # Separator
        lines.append("| " + " | ".join("---" for _ in header) + " |")

        # Data rows
        for row in normalized_rows[1:]:
            lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")

        return "\n".join(lines)


class MarkdownDocument:
    """A complete Markdown document."""

    def __init__(self):
        self.elements: list[MarkdownElement] = []

    def add_element(self, element: MarkdownElement):
        """Add an element to the document."""
        self.elements.append(element)

    def render(self) -> str:
        """Render all elements to a complete Markdown document."""
        parts = []
        for element in self.elements:
            rendered = element.render()
            if rendered:
                parts.append(rendered)
        return "\n\n".join(parts)
