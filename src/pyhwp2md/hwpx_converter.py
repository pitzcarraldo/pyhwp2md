"""Convert HWPX XML files to Markdown using python-hwpx."""

from pathlib import Path
from typing import Optional

from hwpx.document import HwpxDocument
from hwpx.tools.object_finder import ObjectFinder
from hwpx.tools.text_extractor import ParagraphInfo, TextExtractor

from .exceptions import ParsingError
from .markdown.elements import MarkdownDocument, MarkdownParagraph, MarkdownTable
from .markdown.table import extract_table_data


class HwpxToMarkdownConverter:
    """Convert HWPX XML files to Markdown."""

    NAMESPACES = {
        "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
        "hs": "http://www.hancom.co.kr/hwpml/2011/section",
        "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    }

    def __init__(self, file_path: Path):
        """Initialize converter with file path."""
        self.file_path = file_path

    def convert(self) -> str:
        """
        Convert HWPX file to Markdown string.

        Returns:
            Markdown formatted string

        Raises:
            ParsingError: If file cannot be parsed
        """
        try:
            doc = MarkdownDocument()

            with TextExtractor(str(self.file_path)) as extractor:
                for section_idx, section in enumerate(extractor.iter_sections()):
                    self._process_section(extractor, section, doc, section_idx)

            return doc.render()
        except Exception as e:
            raise ParsingError(f"Failed to parse HWPX file: {e}") from e

    def _process_section(
        self, extractor: TextExtractor, section, doc: MarkdownDocument, section_idx: int
    ):
        """Process a section to extract paragraphs and tables."""
        # Find all tables in this section
        finder = ObjectFinder(str(self.file_path))
        try:
            tables = list(finder.iter(tag="hp:tbl"))
            table_ids = {id(t.element) for t in tables}
        except Exception:
            tables = []
            table_ids = set()

        # Track tables we've already processed
        processed_tables = set()

        for para_info in extractor.iter_paragraphs(section, include_nested=False):
            # Skip paragraphs inside tables (we'll process tables separately)
            if self._is_in_table(para_info):
                continue

            # Extract paragraph text
            text = self._extract_paragraph_text(para_info)

            if text.strip():
                para = MarkdownParagraph()
                para.set_text(text)

                # Detect heading level from style
                heading_level = self._detect_heading_level(para_info)
                if heading_level:
                    para.set_heading_level(heading_level)

                doc.add_element(para)

        # Process tables
        for table_found in tables:
            table_id = id(table_found.element)
            if table_id not in processed_tables:
                md_table = self._convert_table(table_found.element)
                if md_table:
                    doc.add_element(md_table)
                    processed_tables.add(table_id)

    def _is_in_table(self, para_info: ParagraphInfo) -> bool:
        """Check if paragraph is nested inside a table."""
        # Check if any ancestor is a table
        element = para_info.element
        parent = element
        while parent is not None:
            if parent.tag.endswith("}tbl") or parent.tag == "tbl":
                return True
            parent = parent.getparent() if hasattr(parent, "getparent") else None
        return False

    def _extract_paragraph_text(self, para_info: ParagraphInfo) -> str:
        """Extract text from paragraph info."""
        try:
            # Try to use the text method if available
            if hasattr(para_info, "text"):
                return para_info.text
            # Fallback to extracting from element
            element = para_info.element
            texts = []
            for run in element.findall(".//hp:run", namespaces=self.NAMESPACES):
                for t in run.findall("hp:t", namespaces=self.NAMESPACES):
                    if t.text:
                        texts.append(t.text)
            return "".join(texts)
        except Exception:
            return ""

    def _detect_heading_level(self, para_info: ParagraphInfo) -> Optional[int]:
        """
        Detect if paragraph is a heading based on style.

        Returns:
            Heading level (1-6) or None if not a heading
        """
        element = para_info.element
        style_id = element.get("styleIDRef", "")

        # Common heading style patterns in HWPX
        # Style IDs often correspond to heading levels, but this may vary
        # We'll use a simple heuristic: styles 1-6 are headings
        try:
            level = int(style_id)
            if 1 <= level <= 6:
                return level
        except (ValueError, TypeError):
            pass

        # Check paragraph property for heading style
        para_pr = element.find("hp:parapr", namespaces=self.NAMESPACES)
        if para_pr is not None:
            # Look for heading-related attributes
            pass

        return None

    def _convert_table(self, table_element) -> Optional[MarkdownTable]:
        """Convert a table element to MarkdownTable."""
        try:
            rows_data = extract_table_data(table_element, self.NAMESPACES)
            if rows_data:
                table = MarkdownTable()
                table.set_rows(rows_data)
                return table
        except Exception:
            pass
        return None
