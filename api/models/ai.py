from __future__ import annotations
from datetime import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class AISession(SQLModel, table=True):
    __tablename__ = "ai_sessions"
    
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)


class AIMessage(SQLModel, table=True):
    __tablename__ = "ai_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    
    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    title: str
    text: str
    source_type: str | None = Field(default=None)
    source_file: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)