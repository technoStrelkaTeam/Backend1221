from pathlib import Path
from typing import List
from migration.readers.base import DocumentReader, DocumentChunk


class ExcelDocumentReader(DocumentReader):
    extension = ".xlsx"
    
    extensions = {".xlsx", ".xls"}
    
    def read(self, file_path: Path) -> List[DocumentChunk]:
        try:
            import openpyxl
        except ImportError:
            raise ImportError("pip install openpyxl")
        
        chunks = []
        
        wb = openpyxl.load_workbook(file_path, data_only=True)
        
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            rows = list(sheet.rows)
            
            if not rows:
                continue
            
            for i, row in enumerate(rows):
                cells = [cell.value for cell in row if cell.value is not None]
                if cells:
                    row_text = " | ".join(str(c) for c in cells)
                    
                    key = f"{sheet_name}_{i+1}" if sheet_name != "Sheet1" else f"row_{i+1}"
                    
                    chunks.append(DocumentChunk(
                        key=key,
                        title=f"{sheet_name} - Row {i+1}",
                        text=row_text
                    ))
        
        wb.close()
        
        if not chunks:
            chunks.append(DocumentChunk(
                key=self.get_key(file_path.stem),
                title=file_path.stem,
                text="Empty Excel file"
            ))
        
        return chunks