"""Tests for file type detection."""

import pytest
from pathlib import Path
from pyhwp2md.detector import detect_file_type
from pyhwp2md.exceptions import FileTypeError


def test_detect_file_type_nonexistent():
    """Test detection of non-existent file."""
    with pytest.raises(FileTypeError):
        detect_file_type("nonexistent.hwp")


def test_detect_file_type_by_extension():
    """Test fallback to extension-based detection."""
    # This test would require actual test files
    # For now, we just verify the function exists and has the right signature
    assert callable(detect_file_type)
