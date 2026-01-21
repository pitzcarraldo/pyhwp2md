# pyhwp2md

[![PyPI version](https://badge.fury.io/py/pyhwp2md.svg)](https://badge.fury.io/py/pyhwp2md)
[![Python Support](https://img.shields.io/pypi/pyversions/pyhwp2md.svg)](https://pypi.org/project/pyhwp2md/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert HWP (Hangul Word Processor) and HWPX files to Markdown format.

## Features

- 🔄 Convert both HWP (binary) and HWPX (XML) files
- 📝 Extracts text, paragraphs, and tables
- 📊 Converts tables to Markdown pipe format
- 🎯 Simple CLI interface
- 🐍 Python 3.10+ support

## Quick Start

### Run without installation (uvx)

```bash
# Convert directly without installing
uvx pyhwp2md document.hwp

# Save to file
uvx pyhwp2md document.hwp -s

# Specify output path
uvx pyhwp2md document.hwpx -o output.md
```

## Installation

### Using pip

```bash
pip install pyhwp2md
```

### Using uv

```bash
uv pip install pyhwp2md
```

### From source

```bash
git clone https://github.com/pitzcarraldo/pyhwp2md.git
cd pyhwp2md
pip install -e .
```

## Usage

### Command Line

```bash
# Output to stdout (default)
pyhwp2md document.hwp

# Save to .md file in same directory
pyhwp2md document.hwp -s
pyhwp2md document.hwpx --save

# Specify output path
pyhwp2md document.hwp -o output.md
```

### Python API

```python
from pyhwp2md import convert

# Convert and get markdown string
markdown = convert("document.hwp")
print(markdown)

# Convert and save to file
markdown = convert("document.hwpx", output_path="output.md")
```

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| HWP | `.hwp` | Binary format (HWP 5.0+) |
| HWPX | `.hwpx` | XML-based format |

## Supported Elements

- ✅ Paragraphs
- ✅ Headings (H1-H6)
- ✅ Tables
- ✅ Lists (bulleted/numbered)
- ✅ Line breaks
- ⚠️ Images (coming soon)
- ⚠️ Links (partial support)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/pitzcarraldo/pyhwp2md.git
cd pyhwp2md

# Install with dev dependencies
pip install -e .[dev]
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=pyhwp2md

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/
```

## Dependencies

- [pyhwp](https://github.com/mete0r/pyhwp) - HWP binary file parser
- [python-hwpx](https://github.com/airmang/python-hwpx) - HWPX XML file parser

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- [pyhwp](https://github.com/mete0r/pyhwp) by mete0r
- [python-hwpx](https://github.com/airmang/python-hwpx) by airmang

## Links

- [PyPI Package](https://pypi.org/project/pyhwp2md/)
- [GitHub Repository](https://github.com/pitzcarraldo/pyhwp2md)
- [Issue Tracker](https://github.com/pitzcarraldo/pyhwp2md/issues)
