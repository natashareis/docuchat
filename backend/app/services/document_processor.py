from typing import BinaryIO
from pathlib import Path
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from app.core.config import settings


_SUPPORTED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}


class DocumentProcessor:
    """Service for processing different document types."""

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Check if file extension is supported."""
        ext = Path(filename).suffix.lower()
        return ext in _SUPPORTED_EXTENSIONS

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text from document."""
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == '.pdf':
                elements = partition_pdf(filename=file_path)
            elif ext in ['.doc', '.docx']:
                elements = partition_docx(filename=file_path)
            elif ext == '.txt':
                elements = partition_text(filename=file_path)
            else:
                elements = partition(filename=file_path)
            
            text = "\n\n".join([str(el) for el in elements])
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text: {str(e)}") from e

    @classmethod
    def save_upload(cls, file: BinaryIO, filename: str) -> str:
        """Save uploaded file to disk."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / filename
        
        counter = 1
        while file_path.exists():
            name = Path(filename).stem
            ext = Path(filename).suffix
            file_path = upload_dir / f"{name}_{counter}{ext}"
            counter += 1
        
        with open(file_path, "wb") as f:
            content = file.read()
            f.write(content)
        
        return str(file_path)
