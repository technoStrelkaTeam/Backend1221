from pathlib import Path
from typing import List
from migration.readers.base import DocumentReader, DocumentChunk


class PDFDocumentReader(DocumentReader):
    extension = ".pdf"
    
    def read(self, file_path: Path) -> List[DocumentChunk]:
        try:
            import pypdf
        except ImportError:
            raise ImportError("pip install pypdf")
        
        chunks = []
        
        reader = pypdf.PdfReader(file_path)
        full_text = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        
        all_text = "\n".join(full_text)
        
        if all_text.strip():
            chunks.append(DocumentChunk(
                key=self.get_key(file_path.stem),
                title=file_path.stem,
                text=all_text.strip()
            ))
        
        return chunks