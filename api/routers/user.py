# методы: 1. получить информацию о пользователе (с диалогом) 2. сделать запрос к ИИ и добавить к истории диалога
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from api.database import SessionDep
from api.schemas.user import *
from api.models.user import User
from sqlmodel import select
from typing import Annotated
from api.utils import hash_password, check_password
import datetime

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

security = HTTPBasic()

@router.get("/login", response_model=UserPublic)
async def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)], session: SessionDep):
    user = session.get(User, credentials.username)
    if not user:
        user = session.exec(select(User).filter(User.email == credentials.username)).first()

    if user:
        if check_password(credentials.password, user.password):
            user.last_visit = datetime.datetime.now()
            session.add(user)
            session.commit()
            session.refresh(user)
            return user # + история переписки
        else:
            raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")
    else:
        raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")

@router.post("/add", response_model=UserPublic)
async def add_user(user_data: UserRegister, session: SessionDep):
    user_data.password = hash_password(user_data.password)
    user = User.model_validate(user_data)
    user.last_visit = datetime.datetime.now()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
