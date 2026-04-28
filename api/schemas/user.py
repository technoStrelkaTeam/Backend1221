from __future__ import annotations
from sqlmodel import Field, SQLModel
from models.enum import StatusOfUser


class UserBase(SQLModel): # тот же для добавления пользователей
    email: str = Field(default=None, unique=True, nullable=False)
    role: StatusOfUser

class UserPublic(UserBase):
    id: int

class UserRegister(UserBase):
    password: str
