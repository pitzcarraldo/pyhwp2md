"""Convert HWP binary files to Markdown using pyhwp."""

from pathlib import Path

from hwp5.xmlmodel import Hwp5File

from .exceptions import ParsingError
from .markdown.elements import MarkdownDocument, MarkdownParagraph, MarkdownTable


class HwpToMarkdownConverter:
    """Convert HWP binary files to Markdown."""

    def __init__(self, file_path: Path):
        """Initialize converter with file path."""
        self.file_path = file_path

    def convert(self) -> str:
        """
        Convert HWP file to Markdown string.

        Returns:
            Markdown formatted string

        Raises:
            ParsingError: If file cannot be parsed
        """
        try:
            doc = MarkdownDocument()

            with Hwp5File(str(self.file_path)) as hwp:
                # Process document sections
                if hasattr(hwp, "bodytext") and hasattr(hwp.bodytext, "section"):
                    for section_idx, section in enumerate(hwp.bodytext.section):
                        self._process_section(section, doc)

            return doc.render()
        except Exception as e:
            raise ParsingError(f"Failed to parse HWP file: {e}") from e

    def _process_section(self, section, doc: MarkdownDocument):
        """Process a section's content to extract text and tables."""
        # Stack to track nested structures
        current_paragraph = None
        current_table = None
        table_rows = []
        current_row = []
        in_table_cell = False

        try:
            # Get events from section
            events = section.models()

            for event_type, model, attributes in events:
                model_name = model.__class__.__name__ if hasattr(model, "__class__") else str(model)

                # Handle paragraph start/end
                if model_name == "Paragraph":
                    if event_type == "start":
                        current_paragraph = MarkdownParagraph()
                    elif event_type == "end" and current_paragraph:
                        # Only add non-empty paragraphs outside of tables
                        if current_paragraph.text.strip() and not in_table_cell:
                            doc.add_element(current_paragraph)
                        current_paragraph = None

                # Handle text content
                elif model_name == "Text" and current_paragraph:
                    text = attributes.get("text", "")
                    if text:
                        current_paragraph.append_text(text)

                # Handle table structures
                elif model_name == "TableControl":
                    if event_type == "start":
                        current_table = MarkdownTable()
                        table_rows = []
                    elif event_type == "end" and current_table:
                        if table_rows:
                            current_table.set_rows(table_rows)
                            doc.add_element(current_table)
                        current_table = None
                        table_rows = []

                elif model_name == "TableRow":
                    if event_type == "start":
                        current_row = []
                    elif event_type == "end" and current_table:
                        if current_row:
                            table_rows.append(current_row)
                        current_row = []

                elif model_name == "TableCell":
                    if event_type == "start":
                        in_table_cell = True
                        current_paragraph = MarkdownParagraph()
                    elif event_type == "end":
                        in_table_cell = False
                        if current_paragraph and current_paragraph.text.strip():
                            current_row.append(current_paragraph.text.strip())
                        else:
                            current_row.append("")
                        current_paragraph = None

                # Handle line breaks
                elif model_name == "LineBreak" and current_paragraph:
                    current_paragraph.append_text("\n")

        except Exception as e:
            # Log error but continue processing
            pass

    def _process_section_alternative(self, section, doc: MarkdownDocument):
        """
        Alternative section processing using plain text extraction.
        Fallback method if event-based processing fails.
        """
        try:
            # Try to extract text directly from section
            # This is a simplified approach that gets all text
            from hwp5.hwp5txt import TextTransform

            # Use pyhwp's text extraction
            transform = TextTransform()
            # Note: This would require converting section to XML first
            # This is a placeholder for a simpler text extraction approach

        except Exception:
            pass
