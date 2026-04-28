from migration.readers.text import TextDocumentReader
from migration.readers.pdf import PDFDocumentReader
from migration.readers.excel import ExcelDocumentReader
from migration.readers.word import WordDocumentReader

READERS = {
    ".txt": TextDocumentReader(),
    ".md": TextDocumentReader(),
    ".pdf": PDFDocumentReader(),
    ".xlsx": ExcelDocumentReader(),
    ".xls": ExcelDocumentReader(),
    ".docx": WordDocumentReader(),
    ".doc": WordDocumentReader(),
}


def get_reader(file_path: str):
    from pathlib import Path
    path = Path(file_path)
    ext = path.suffix.lower()
    return READERS.get(ext)