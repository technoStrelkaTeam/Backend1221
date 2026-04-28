# методы: 1. получить информацию о пользователе (с диалогом) 2. сделать запрос к ИИ и добавить к истории диалога
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from api.database import SessionDep, get_history, clear_history, add_message, get_all_dialog_user, engine
from api.schemas.user import *
from api.models.user import User
from sqlmodel import select
from typing import Annotated
from api.utils import hash_password, check_password
import datetime
import threading
import time
from datetime import datetime
from sqlmodel import Session
from api.config import time_to_clear

def do_action():
    while True:
        with Session(engine) as session: # TODO: отрефакторить, чтобы было в database.py
            for email in get_all_dialog_user():
                user_data = get_user_by_email(email, session)
                
                if user_data and user_data.last_visit:
                    if (datetime.now() - user_data.last_visit).total_seconds() > time_to_clear:
                        clear_history(email)
        
        time.sleep(10)

thread = threading.Thread(target=do_action, daemon=True)

thread.start()

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

security = HTTPBasic()



def get_user(credentials, session):
    user = session.get(User, credentials.username)
    if not user:
        user = session.exec(select(User).filter(User.email == credentials.username)).first()
    if user:
        if check_password(credentials.password, user.password):
            return user
        else:
            return None
    return None

def get_user_by_email(email: str, session: SessionDep):
    return session.exec(select(User).filter(User.email == email)).first()

@router.get("/login")
async def login(credentials: Annotated[HTTPBasicCredentials, Depends(security)], session: SessionDep):
    user = get_user(credentials, session)

    if user:
        user.last_visit = datetime.now()
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"user_data": user, "history": get_history(user.email)} # + история переписки
    else:
        raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")

@router.post("/add", response_model=UserPublic)
async def add_user(user_data: UserRegister, session: SessionDep):
    user_data.password = hash_password(user_data.password)
    user = User.model_validate(user_data)
    user.last_visit = datetime.now()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/answer")
async def answer(session: SessionDep, credentials: Annotated[HTTPBasicCredentials, Depends(security)], message: str | None = None, ):
    user = get_user(credentials, session)
    if user:
        response_from_ai = "ответ от ИИ"
        add_message(user.email, message)
        add_message(user.email, response_from_ai)

        return response_from_ai
    else:
        raise HTTPException(status_code=404, detail="Неверный табельный номер/почта или пароль!")
