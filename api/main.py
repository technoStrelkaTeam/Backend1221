from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.database import create_db_and_tables
from api.routers import user

app = FastAPI()
app.include_router(user.router)

@app.get("/test")
async def root():
    return {"message": "Hello"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
