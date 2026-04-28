import asyncio
from datetime import datetime
from typing import Optional
from config import session_timeout
import uuid


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.timestamp = datetime.now()


class AISession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[Message] = []
        self.last_activity = datetime.now()
        self.references: list[str] = []

    def is_expired(self) -> bool:
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed > session_timeout


ai_sessions: dict[str, AISession] = {}


async def cleanup_loop():
    while True:
        await asyncio.sleep(60)
        expired = [
            sid for sid, session in ai_sessions.items() 
            if session.is_expired()
        ]
        for sid in expired:
            del ai_sessions[sid]


def start_cleanup_task():
    """Start the cleanup task. Call this when the app starts."""
    asyncio.create_task(cleanup_loop())


def create_session() -> str:
    session_id = str(uuid.uuid4())
    ai_sessions[session_id] = AISession(session_id)
    return session_id


def get_session(session_id: str) -> Optional[AISession]:
    return ai_sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    if session_id in ai_sessions:
        del ai_sessions[session_id]
        return True
    return False


def add_user_message(session_id: str, content: str):
    session = ai_sessions.get(session_id)
    if session:
        session.messages.append(Message("user", content))
        session.last_activity = datetime.now()


def add_ai_message(session_id: str, content: str):
    session = ai_sessions.get(session_id)
    if session:
        session.messages.append(Message("assistant", content))
        session.last_activity = datetime.now()


def add_references(session_id: str, keys: list[str]):
    session = ai_sessions.get(session_id)
    if session:
        session.references.extend(keys)


def get_messages_for_ollama(session_id: str) -> list[dict]:
    session = ai_sessions.get(session_id)
    if not session:
        return []
    return [{"role": m.role, "content": m.content} for m in session.messages]


def get_references(session_id: str) -> list[str]:
    session = ai_sessions.get(session_id)
    if not session:
        return []
    return session.references