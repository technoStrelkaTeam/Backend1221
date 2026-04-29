import asyncio
import json
import sys
from pathlib import Path
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import postgres_url
from api.models.ai import Document
from migration.readers import get_reader
from api.services.splitter import split_document_with_llm


session_engine = create_async_engine(postgres_url, echo=False)
session_maker = async_sessionmaker(session_engine, class_=AsyncSession, expire_on_commit=False)


async def import_document(file_path: str, update_existing: bool = True, use_llm_split: bool = True) -> dict:
    path = Path(file_path)
    
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    
    reader = get_reader(str(path))
    if not reader:
        return {"error": f"Unsupported file format: {path.suffix}"}
    
    try:
        chunks = await reader.read(path)
    except Exception as e:
        return {"error": f"Error reading file: {e}"}
    
    full_text = "\n\n".join(chunk.text for chunk in chunks if chunk.text)
    
    if use_llm_split:
        try:
            blocks = await split_document_with_llm(full_text, path.stem)
        except Exception as e:
            print(f"LLM split error: {e}, using raw chunks")
            blocks = [{"title": chunk.title, "text": chunk.text, "key": chunk.key} for chunk in chunks]
    else:
        blocks = [{"title": chunk.title, "text": chunk.text, "key": chunk.key} for chunk in chunks]
    
    async with session_maker() as session:
        imported = 0
        skipped = 0
        
        for i, block in enumerate(blocks):
            title = block.get("title", "")
            text = block.get("text", "")
            key = block.get("key", "")
            
            if not title or not text:
                continue
            
            if not key:
                key = block.get("key", f"doc_{i+1}")
            
            key = key.strip()
            
            result = await session.exec(
                select(Document).where(Document.key == key)
            )
            existing = result.first()
            
            if existing:
                if update_existing:
                    existing.title = title
                    existing.text = text
                    existing.source_file = str(path)
                    existing.source_type = path.suffix.lower()
                    imported += 1
                else:
                    skipped += 1
            else:
                doc = Document(
                    key=key,
                    title=title,
                    text=text,
                    source_file=str(path),
                    source_type=path.suffix.lower()
                )
                session.add(doc)
                imported += 1
        
        await session.commit()
    
    return {
        "file": str(path),
        "imported": imported,
        "skipped": skipped,
        "total_blocks": len(blocks)
    }


async def import_document_simple(file_path: str, update_existing: bool = True) -> dict:
    return await import_document(file_path, update_existing, use_llm_split=True)


async def import_directory(directory: str, extensions: list[str] = None, update_existing: bool = True) -> dict:
    dir_path = Path(directory)
    
    if not dir_path.exists() or not dir_path.is_dir():
        return {"error": f"Directory not found: {directory}"}
    
    if extensions is None:
        extensions = [".txt", ".md", ".pdf", ".xlsx", ".xls", ".docx", ".doc"]
    
    results = []
    total_imported = 0
    total_skipped = 0
    
    for ext in extensions:
        for file_path in dir_path.rglob(f"*{ext}"):
            result = await import_document(str(file_path), update_existing)
            if "error" not in result:
                total_imported += result.get("imported", 0)
                total_skipped += result.get("skipped", 0)
            results.append(result)
    
    return {
        "directory": directory,
        "total_imported": total_imported,
        "total_skipped": total_skipped,
        "files": results
    }


async def list_documents() -> list[dict]:
    async with session_maker() as session:
        result = await session.exec(select(Document))
        docs = result.all()
        return [
            {
                "id": doc.id,
                "key": doc.key,
                "title": doc.title,
                "source_type": doc.source_type,
                "source_file": doc.source_file,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in docs
        ]


async def get_document_by_key(key: str) -> dict | None:
    async with session_maker() as session:
        result = await session.exec(select(Document).where(Document.key == key))
        doc = result.first()
        if doc:
            return {
                "id": doc.id,
                "key": doc.key,
                "title": doc.title,
                "text": doc.text,
                "source_type": doc.source_type,
                "source_file": doc.source_file
            }
        return None


async def delete_document(key: str) -> bool:
    async with session_maker() as session:
        result = await session.exec(select(Document).where(Document.key == key))
        doc = result.first()
        if doc:
            await session.delete(doc)
            await session.commit()
            return True
        return False


async def clear_all_documents() -> int:
    async with session_maker() as session:
        result = await session.exec(select(Document))
        docs = result.all()
        count = len(docs)
        for doc in docs:
            await session.delete(doc)
        await session.commit()
        return count