"""Command-line interface for pyhwp2md."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .converter import convert
from .exceptions import ConversionError, FileTypeError, Pyhwp2mdError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="pyhwp2md",
        description="Convert HWP/HWPX files to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run without installation (uvx)
  uvx pyhwp2md document.hwp
  uvx pyhwp2md document.hwp -s

  # Output to stdout (default)
  pyhwp2md document.hwp

  # Save to same directory as .md file
  pyhwp2md document.hwp -s
  pyhwp2md document.hwp --save

  # Specify output path
  pyhwp2md document.hwp -o output.md
  pyhwp2md document.hwpx --output result.md
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input HWP or HWPX file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output Markdown file. If not specified, prints to stdout.",
    )

    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save output as .md file in same directory as input",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    output_path = args.output
    if args.save and not output_path:
        output_path = args.input.with_suffix(".md")

    # Convert the file
    try:
        markdown = convert(
            args.input,
            output_path=output_path,
        )

        # Print to stdout if no output file specified
        if not output_path:
            print(markdown)
        else:
            print(f"✓ Converted: {args.input} → {output_path}", file=sys.stderr)

    except FileTypeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConversionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Pyhwp2mdError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
