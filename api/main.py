from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables
from services.session import start_cleanup_task
from services.document import init_documents
from routers.user import router as user_router
from routers.ai import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await init_documents()
    start_cleanup_task()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(ai_router)


@app.get("/test")
async def root():
    return {"message": "Hello"}