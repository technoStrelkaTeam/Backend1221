from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.database import create_db_and_tables
from api.routers import user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)

@app.get("/test")
async def root():
    return {"message": "Hello"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
