try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


def img_to_str(src: str, path_to_tesseract: str) -> str:
    """Extract text from image via Tesseract OCR.

    Args:
        src: Path to image file.
        path_to_tesseract: Path to Tesseract executable.

    Returns:
        Recognized text in Russian and English modes.
    """
    pytesseract.pytesseract.tesseract_cmd = path_to_tesseract
    return pytesseract.image_to_string(Image.open(src), lang='rus+eng')
