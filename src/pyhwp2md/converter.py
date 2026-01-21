"""Main converter interface - unified API for HWP and HWPX."""

from pathlib import Path
from typing import Optional

from .detector import detect_file_type
from .exceptions import ConversionError
from .hwp_converter import HwpToMarkdownConverter
from .hwpx_converter import HwpxToMarkdownConverter


def convert(
    file_path: str | Path,
    output_path: Optional[str | Path] = None,
) -> str:
    """
    Convert HWP or HWPX file to Markdown.

    Args:
        file_path: Path to input HWP/HWPX file
        output_path: Optional path to save output. If None, returns string only.

    Returns:
        Markdown content as string

    Raises:
        ConversionError: If conversion fails
        FileTypeError: If file type cannot be determined
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise ConversionError(f"Input file not found: {file_path}")

    # Detect file type
    file_type = detect_file_type(file_path)

    # Choose appropriate converter
    if file_type == "hwp":
        converter = HwpToMarkdownConverter(file_path)
    else:  # hwpx
        converter = HwpxToMarkdownConverter(file_path)

    # Convert to markdown
    try:
        markdown = converter.convert()
    except Exception as e:
        raise ConversionError(f"Failed to convert {file_path}: {e}") from e

    # Save to file if output path is provided
    if output_path:
        output_path = Path(output_path)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
        except Exception as e:
            raise ConversionError(f"Failed to write output to {output_path}: {e}") from e

    return markdown
