from __future__ import annotations
from datetime import datetime

from sqlmodel import Field

from api.schemas.user import UserBase


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    last_visit: datetime | None = Field(default=None)
