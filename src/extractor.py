import os
import fitz  # PyMuPDF
import docx
from typing import Dict, Optional

class BaseExtractor:
    """Base class for document extractors."""
    def extract(self, file_path: str) -> Dict[str, str]:
        raise NotImplementedError("Subclasses must implement extract method.")

class PDFExtractor(BaseExtractor):
    """Extractor for PDF files using PyMuPDF."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return {"raw_text": text}
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

class DOCXExtractor(BaseExtractor):
    """Extractor for DOCX files using python-docx."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return {"raw_text": text}
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}")

class TXTExtractor(BaseExtractor):
    """Extractor for TXT files."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return {"raw_text": f.read()}
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return {"raw_text": f.read()}
            except Exception as e:
                raise ValueError(f"Failed to extract text from TXT: {e}")
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT: {e}")

class SourceReader:
    """Unified interface for extracting text from supported file types."""
    
    _EXTRACTORS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.txt': TXTExtractor
    }

    @classmethod
    def get_extractor(cls, file_path: str) -> BaseExtractor:
        ext = os.path.splitext(file_path)[1].lower()
        extractor_class = cls._EXTRACTORS.get(ext)
        if extractor_class:
            return extractor_class()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def read(file_path: str) -> Dict[str, str]:
        """Reads a file and returns the extracted text."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        extractor = SourceReader.get_extractor(file_path)
        return extractor.extract(file_path)

if __name__ == "__main__":
    # Simple test
    try:
        # Create a dummy txt file for testing
        test_file = "test_doc.txt"
        with open(test_file, "w") as f:
            f.write("This is a test document.\nIt has two lines.")
        
        result = SourceReader.read(test_file)
        print(f"Test Extraction Result: {result}")
        
        os.remove(test_file)
    except Exception as e:
        print(f"Test failed: {e}")
