from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class DocumentChunk:
    key: str
    title: str
    text: str


class DocumentReader(ABC):
    extension: str
    
    @abstractmethod
    def read(self, file_path: str | Path) -> List[DocumentChunk]:
        pass
    
    @staticmethod
    def can_read(file_path: str | Path) -> bool:
        path = Path(file_path)
        return path.suffix.lower() in cls.extensions if hasattr(cls, 'extensions') else path.suffix.lower() == cls.extension
    
    @classmethod
    def get_key(cls, title: str) -> str:
        import re
        key_match = re.match(r'^(\d+\.\d+)', title.strip())
        if key_match:
            return key_match.group(1)
        return title.split()[0] if title else "unknown"