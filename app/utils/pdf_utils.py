import os
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file and return as a single string.
    """
    if not os.path.exists(pdf_path):
        return ""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text
