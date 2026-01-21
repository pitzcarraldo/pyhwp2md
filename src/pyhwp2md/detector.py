"""File type detection for HWP and HWPX files."""

from pathlib import Path
from zipfile import ZipFile, is_zipfile

from .exceptions import FileTypeError


def detect_file_type(file_path: str | Path) -> str:
    """
    Detect if file is HWP or HWPX.

    HWP: OLE2 compound document with signature 'HWP Document File'
    HWPX: ZIP archive containing 'mimetype' or 'Contents/content.hpf'

    Args:
        file_path: Path to the file to check

    Returns:
        'hwp' for HWP binary files, 'hwpx' for HWPX XML files

    Raises:
        FileTypeError: If file type cannot be determined
    """
    path = Path(file_path)

    if not path.exists():
        raise FileTypeError(f"File not found: {path}")

    # Check extension first as hint
    ext = path.suffix.lower()

    # Try HWPX detection (ZIP-based)
    if is_zipfile(path):
        try:
            with ZipFile(path, "r") as zf:
                filelist = zf.namelist()
                # Check for mimetype file
                if "mimetype" in filelist:
                    mimetype = zf.read("mimetype").decode("utf-8").strip()
                    if "hwp" in mimetype.lower():
                        return "hwpx"
                # Check for Contents/content.hpf (HWPX manifest)
                if "Contents/content.hpf" in filelist:
                    return "hwpx"
        except Exception:
            pass  # Not a valid ZIP or HWPX

    # Try HWP detection (OLE2 compound document)
    try:
        with open(path, "rb") as f:
            # Check for OLE2 magic number
            magic = f.read(8)
            if magic[:4] == b"\xd0\xcf\x11\xe0":  # OLE2 signature
                return "hwp"
    except Exception:
        pass  # Not a valid HWP

    # Fallback to extension
    if ext == ".hwp":
        return "hwp"
    elif ext == ".hwpx":
        return "hwpx"

    raise FileTypeError(f"Cannot determine file type for: {path}")
