import io
from PyPDF2 import PdfReader
from PIL import Image

def validate_document(file_name: str, file_content: bytes, mime_type: str) -> dict:
    """
    Validates the uploaded document based on requirements:
    - Supported formats: PDF, JPG, PNG
    - Page limit: max 3 pages
    - File integrity: Not empty, not corrupted
    """
    is_supported = mime_type in ["application/pdf", "image/jpeg", "image/png"]
    is_readable = True
    page_count = 1
    status = "PASS"
    error_message = None

    if len(file_content) == 0:
        return {
            "file_type": mime_type,
            "is_supported": is_supported,
            "is_readable": False,
            "page_count": 0,
            "status": "FAILED"
        }

    if is_supported:
        try:
            if mime_type == "application/pdf":
                reader = PdfReader(io.BytesIO(file_content))
                page_count = len(reader.pages)
            else:
                # For images, we try to open them to ensure they are not corrupted
                img = Image.open(io.BytesIO(file_content))
                img.verify()
                page_count = 1
                
            if page_count > 3:
                status = "FAILED"
                is_readable = True
        except Exception as e:
            is_readable = False
            status = "FAILED"
    else:
        status = "FAILED"

    return {
        "file_type": mime_type,
        "is_supported": is_supported,
        "is_readable": is_readable,
        "page_count": page_count,
        "status": status
    }
