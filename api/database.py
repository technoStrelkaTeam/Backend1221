from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
temp_dialog_db = {}


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

def add_message(username: str, message: str):
    if username in temp_dialog_db:
        temp_dialog_db[username].append(message)
    else:
        temp_dialog_db[username] = [message]

def clear_history(username: str):
    temp_dialog_db[username].clear()

def get_history(username: str):
    if username in temp_dialog_db:
        return temp_dialog_db[username]
    else:
        return []
    
def get_all_dialog_user():
    return temp_dialog_db.keys()


SessionDep = Annotated[Session, Depends(get_session)]