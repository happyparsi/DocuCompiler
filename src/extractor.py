import os # Files aur Directories (folder path etc.) manage karne ke liye
import fitz  # PyMuPDF library (PDF files ko open aur read karne ke liye)
import docx # python-docx library (Microsoft Word .docx files padhne ke liye)
from typing import Dict, Optional # Functions ko saaf (type-hinted) bananey ke liye

class BaseExtractor:
    """Base class for document extractors."""
    # Ye ek khaali "Blueprint" / Parent class hai. Har naya Extractor iske usool maangay ga!
    def extract(self, file_path: str) -> Dict[str, str]:
        # Agar isey directly call kiya toh Error do! (Isey use nahi karna, iske bacchon ko use karna hai)
        raise NotImplementedError("Subclasses must implement extract method.")

class PDFExtractor(BaseExtractor):
    """Extractor for PDF files using PyMuPDF."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            # PyMuPDF ka method use kar ke PDF file load ki
            doc = fitz.open(file_path)
            text = ""
            # Kitne bhi safay (pages) hon PDF mein, sab par Loop chalai
            for page in doc:
                text += page.get_text() # Har safay ka likha hua text nikala aur Strings me jorrtay gay
            return {"raw_text": text} # Pura lamba paragraph Dictionary mein bhej dia wapis!
        except Exception as e:
            # File corrupt hui ya khuli ni toh Console Error
            raise ValueError(f"Failed to extract text from PDF: {e}")

class DOCXExtractor(BaseExtractor):
    """Extractor for DOCX files using python-docx."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            # DocX library se Word ki file system mein load karai
            doc = docx.Document(file_path)
            # Sari lines (paragraphs) ek List mein ayengi, unko "\n" (Enter) se jod kr ek String bna diya.
            text = "\n".join([para.text for para in doc.paragraphs])
            return {"raw_text": text}
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}")

class TXTExtractor(BaseExtractor):
    """Extractor for TXT files."""
    def extract(self, file_path: str) -> Dict[str, str]:
        try:
            # Normal aam Text files ko UTF-8 format mein read karo
            with open(file_path, 'r', encoding='utf-8') as f:
                return {"raw_text": f.read()} 
        except UnicodeDecodeError:
            # Fallback: Agar kisi ney boht poorani Windows formatting use ki ho aur utf-8 toot jaye:
            try:
                # Toh file dobara error diye bina "latin-1" format p padhne ki koshish karo!
                with open(file_path, 'r', encoding='latin-1') as f:
                    return {"raw_text": f.read()}
            except Exception as e:
                raise ValueError(f"Failed to extract text from TXT: {e}")
        except Exception as e:
            raise ValueError(f"Failed to extract text from TXT: {e}")

class SourceReader:
    """Unified interface for extracting text from supported file types."""
    # FACTORY PATTERN: Client (app.py) ko nhe malum kon si doc hy, ye khud decide krti h!!
    
    # Ye mapping register kardi files ki extensions se classes k sath!
    _EXTRACTORS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.txt': TXTExtractor
    }

    @classmethod
    def get_extractor(cls, file_path: str) -> BaseExtractor:
        # File name se Akhri hissa (.pdf wagera) nikalo (os.path.splitext se) aur small letters me krdoh
        ext = os.path.splitext(file_path)[1].lower() 
        # Dictionary _EXTRACTORS mein dheko k kaya extension mojod hn hmayary paas?
        extractor_class = cls._EXTRACTORS.get(ext)
        
        if extractor_class:
            return extractor_class() # Wo specific Extractor ka Object Model (instance) bana kar dedena.
        else:
            raise ValueError(f"Unsupported file type: {ext}") # Nai mili tu Error do

    @staticmethod
    def read(file_path: str) -> Dict[str, str]:
        """Reads a file and returns the extracted text."""
        # 1. Start: File waqee OS me ha na ??
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # 2. Sahi tool manga (e.g. PDFExtracter aya ga file deker unse text laana hai)
        extractor = SourceReader.get_extractor(file_path)
        
        # 3. Method call karkey text rawat kr leya gya :)
        return extractor.extract(file_path)

if __name__ == "__main__":
    # Test kr lenge Agar kisi ko sirf ye file chla ke dekhni ho!!
    pass
