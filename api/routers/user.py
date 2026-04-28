from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import SessionDep, session_maker
from services.history import get_history, clear_history, add_message, get_all_dialog_user
from schemas.user import *
from models.user import User
from sqlmodel import select
from typing import Annotated
from utils import hash_password, check_password
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from config import time_to_clear


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

security = HTTPBasic()


async def get_user(credentials: HTTPBasicCredentials, session: AsyncSession):
    user = await session.get(User, credentials.username)
    if not user:
        user = await session.execute(select(User).filter(User.email == credentials.username)).first()
    if user:
        if check_password(credentials.password, user.password):
            return user
        else:
            return None
    return None


async def get_user_by_email(email: str, session: AsyncSession):
    result = await session.execute(select(User).filter(User.email == email))
    return result.first()


@router.get("/login")
async def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)], session: SessionDep):
    user = await get_user(credentials, session)
    
    if user:
        user.last_visit = datetime.now()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {"user_data": user, "history": await get_history(user.email)}
    else:
        raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")


@router.post("/add", response_model=UserPublic)
async def add_user(user_data: UserRegister, session: SessionDep):
    user_data.password = hash_password(user_data.password)
    user = User.model_validate(user_data)
    user.last_visit = datetime.now()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/answer")
async def answer(session: SessionDep, credentials: Annotated[HTTPBasicCredentials, Depends(security)], message: str | None = None):
    user = await get_user(credentials, session)
    if user:
        response_from_ai = "ответ от ИИ"
        await add_message(user.email, message)
        await add_message(user.email, response_from_ai)
        
        return response_from_ai
    else:
        raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")