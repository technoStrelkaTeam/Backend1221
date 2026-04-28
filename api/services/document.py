from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models.ai import Document
from database import session_maker
from typing import Optional


async def init_documents():
    docs_data = {
        "1.2": {"title": "Пользовательское соглашение", "text": "Документ определяющий правила использования сервиса..."},
        "3.6": {"title": "Об увольнении сотрудника", "text": "Порядок и условия расторжения трудового договора..."},
        "2.1": {"title": "Правила внутреннего трудового распорядка", "text": "Режим работы, отпуска, дисциплина..."},
        "4.5": {"title": "Оплата труда", "text": "Порядок начисления заработной платы, премии, надбавки..."},
        "5.3": {"title": "Охрана труда", "text": "Техника безопасности, медицинские осмотры, расследование несчастных случаев..."},
        "1.1": {"title": "Устав предприятия", "text": "Основные положения, цели, задачи организации..."},
        "2.5": {"title": "Отпуска", "text": "Виды отпусков, порядок предоставления, компенсации..."},
    }
    
    async with session_maker() as session:
        for key, data in docs_data.items():
            result = await session.execute(select(Document).where(Document.key == key))
            existing = result.scalar_one_or_none()
            if not existing:
                doc = Document(key=key, title=data["title"], text=data["text"])
                session.add(doc)
        await session.commit()


async def get_document(key: str) -> Optional[dict]:
    async with session_maker() as session:
        result = await session.execute(select(Document).where(Document.key == key))
        doc = result.first()
        if doc:
            return {"key": doc.key, "text": doc.text}
        return None


async def get_documents_by_keys(keys: list[str]) -> list[dict]:
    async with session_maker() as session:
        result = await session.execute(select(Document).where(Document.key.in_(keys)))
        docs = result.all()
        return [{"key": doc.key, "text": doc.text} for doc in docs]


async def get_all_documents_keys() -> list[str]:
    async with session_maker() as session:
        result = await session.execute(select(Document.key))
        return result.all()


async def get_all_documents() -> list[dict]:
    async with session_maker() as session:
        result = await session.execute(select(Document))
        docs = result.all()
        return [{"key": doc.key, "text": doc.text} for doc in docs]