import re
from pathlib import Path
from typing import List
from migration.readers.base import DocumentReader, DocumentChunk


class TextDocumentReader(DocumentReader):
    extension = ".txt"

    extensions = {".txt", ".md"}

    async def read(self, file_path: Path) -> List[DocumentChunk]:
        content = await self._run_sync(file_path.read_text, encoding="utf-8")
        chunks = []

        lines = content.split("\n")
        current_title = file_path.stem
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.match(r"^\d+\.\d+", line):
                if current_text:
                    chunks.append(DocumentChunk(
                        key=self.get_key(current_title),
                        title=current_title,
                        text="\n".join(current_text).strip()
                    ))
                    current_text = []

                match = re.match(r"^(\d+\.\d+)\s+(.+)", line)
                if match:
                    current_title = match.group(2) or match.group(1)
                    current_text.append(match.group(2))
                else:
                    current_text.append(line)
            else:
                current_text.append(line)

        if current_text:
            chunks.append(DocumentChunk(
                key=self.get_key(current_title),
                title=current_title,
                text="\n".join(current_text).strip()
            ))

        if not chunks:
            chunks.append(DocumentChunk(
                key=self.get_key(current_title),
                title=current_title,
                text=content.strip()
            ))

        return chunks