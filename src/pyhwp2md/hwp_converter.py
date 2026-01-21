"""Convert HWP binary files to Markdown using pyhwp."""

import io
import subprocess
import sys
from pathlib import Path

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
            # Use hwp5txt command-line tool for reliable text extraction
            result = subprocess.run(
                [sys.executable, "-m", "hwp5.hwp5txt", str(self.file_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                # Fallback to direct API if CLI fails
                return self._convert_with_api()

            text = result.stdout
            # If CLI returns empty output, try API method
            if not text.strip():
                return self._convert_with_api()

            return self._text_to_markdown(text)

        except subprocess.TimeoutExpired:
            raise ParsingError("HWP file conversion timed out")
        except FileNotFoundError:
            return self._convert_with_api()
        except Exception as e:
            raise ParsingError(f"Failed to parse HWP file: {e}") from e

    def _convert_with_api(self) -> str:
        """Fallback conversion using direct API."""
        try:
            from hwp5.xmlmodel import Hwp5File

            doc = MarkdownDocument()
            hwp = Hwp5File(str(self.file_path))

            try:
                # Process document sections
                if hasattr(hwp, "bodytext"):
                    bodytext = hwp.bodytext
                    # section_indexes() returns section indices
                    if hasattr(bodytext, "section_indexes"):
                        for idx in bodytext.section_indexes():
                            section = bodytext.section(idx)
                            self._process_section_models(section, doc)
            finally:
                # Clean up
                if hasattr(hwp, "close"):
                    hwp.close()

            return doc.render()
        except Exception as e:
            raise ParsingError(f"Failed to parse HWP file with API: {e}") from e

    def _process_section_models(self, section, doc: MarkdownDocument):
        """Process a section using models() to extract text."""
        try:
            models = list(section.models())
            current_table_rows: list[list[str]] = []
            current_row: list[str] = []
            in_table = False

            for model in models:
                tagname = model.get("tagname", "")

                if tagname == "HWPTAG_PARA_TEXT":
                    content = model.get("content", {})
                    chunks = content.get("chunks", [])

                    para_texts = []
                    for chunk in chunks:
                        if len(chunk) >= 2:
                            text_part = chunk[1]
                            if isinstance(text_part, str):
                                para_texts.append(text_part)

                    if para_texts:
                        text = "".join(para_texts).strip()
                        if text:
                            if in_table:
                                # Accumulate text for table cell
                                current_row.append(text)
                            else:
                                para = MarkdownParagraph()
                                para.set_text(text)
                                doc.add_element(para)

                elif tagname == "HWPTAG_TABLE":
                    in_table = True
                    current_table_rows = []

                elif tagname == "HWPTAG_LIST_HEADER":
                    # List header indicates start of a new row or cell context
                    content = model.get("content", {})
                    # Check if this is a new row (simplified heuristic)
                    if current_row and in_table:
                        current_table_rows.append(current_row)
                        current_row = []

            # Finalize any remaining table
            if in_table and current_table_rows:
                table = MarkdownTable()
                table.set_rows(current_table_rows)
                doc.add_element(table)

        except Exception:
            # Continue on error
            pass

    def _text_to_markdown(self, text: str) -> str:
        """Convert plain text to basic Markdown format."""
        if not text.strip():
            return ""

        doc = MarkdownDocument()
        lines = text.split("\n")
        current_paragraph = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                current_paragraph.append(stripped)
            else:
                if current_paragraph:
                    para = MarkdownParagraph()
                    para.set_text(" ".join(current_paragraph))
                    doc.add_element(para)
                    current_paragraph = []

        # Add remaining paragraph
        if current_paragraph:
            para = MarkdownParagraph()
            para.set_text(" ".join(current_paragraph))
            doc.add_element(para)

        return doc.render()

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
