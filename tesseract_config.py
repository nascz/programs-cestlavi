"""
tesseract_config.py
Helper that detects a Tesseract installation on Windows and returns sensible defaults
for pytesseract.pytesseract.tesseract_cmd and the TESSDATA_PREFIX path.

This centralizes detection so both `main.py` and `ocr_funcoes.py` use the same logic
and falls back gracefully if Tesseract is not installed or not found.
"""
import os
import shutil


def find_tesseract():
    """Return a tuple (tesseract_cmd, tessdata_dir).

    Looks for a tesseract binary in common locations on Windows and in PATH.
    If none found returns (None, None).
    """
    # Check PATH first
    path_from_which = shutil.which("tesseract")
    candidates = []
    if path_from_which:
        candidates.append(path_from_which)

    # Common installed locations on Windows
    candidates += [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.path.expanduser("~"), r"AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            # tessdata is usually under the same parent directory
            tesseract_dir = os.path.dirname(candidate)
            tessdata_dir = os.path.join(tesseract_dir, "tessdata")
            return candidate, tessdata_dir

    return None, None


def apply_to_environment():
    """Attempt to set the environment and return a message explaining what was configured.

    This function is intended to be imported and run at module import time by the
    project's entry points so they adapt to the local machine.
    """
    tesseract_cmd, tessdata_dir = find_tesseract()

    if tesseract_cmd:
        # Set the Tesseract executable for pytesseract if available
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        except Exception:
            # If pytesseract isn't installed yet we do not raise here
            pass

    if tessdata_dir and os.path.isdir(tessdata_dir):
        os.environ.setdefault("TESSDATA_PREFIX", tessdata_dir)

    return tesseract_cmd, os.environ.get("TESSDATA_PREFIX")
