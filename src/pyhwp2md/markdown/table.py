"""Table extraction and conversion utilities."""

from xml.etree import ElementTree as ET


def extract_table_data(
    table_element: ET.Element,
    namespaces: dict[str, str],
) -> list[list[str]]:
    """
    Extract table data from HWPX table element.

    Args:
        table_element: XML Element representing the table
        namespaces: XML namespace mappings

    Returns:
        List of rows, each row is a list of cell text content.
    """
    rows = []

    # Find table rows (tr elements)
    for tr in table_element.findall(".//hp:tr", namespaces=namespaces):
        row = []
        for tc in tr.findall("hp:tc", namespaces=namespaces):
            # Extract text from all paragraphs in cell
            cell_text = []
            for p in tc.findall(".//hp:p", namespaces=namespaces):
                para_text = extract_paragraph_text(p, namespaces)
                if para_text:
                    cell_text.append(para_text)
            row.append(" ".join(cell_text))
        rows.append(row)

    return rows


def extract_paragraph_text(p: ET.Element, namespaces: dict[str, str]) -> str:
    """
    Extract text content from a paragraph element.

    Args:
        p: Paragraph XML element
        namespaces: XML namespace mappings

    Returns:
        Combined text content from all runs in the paragraph
    """
    texts = []
    for run in p.findall("hp:run", namespaces=namespaces):
        for t in run.findall("hp:t", namespaces=namespaces):
            if t.text:
                texts.append(t.text)
    return "".join(texts)
