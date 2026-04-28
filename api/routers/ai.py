import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ollama import ask_ollama
from services.prompts import get_system_prompt, INVALID_JSON_PROMPT, ERROR_TEMPLATE
from services.session import (
    create_session, get_session, delete_session,
    add_user_message, add_ai_message, add_references, get_messages_for_ollama, get_references
)
from services.document import get_documents_by_keys, get_all_documents_keys
import logging

logger = logging.getLogger(__name__)


class MessageRequest(BaseModel):
    message: str


class AIResponse(BaseModel):
    method: str
    message: str | None = None
    keys: list[str] | None = None
    error: str | None = None


class NewSessionResponse(BaseModel):
    session_id: str


class ErrorResponse(BaseModel):
    error: str


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


async def process_ollama_response(response_text: str) -> AIResponse:
    try:
        data = json.loads(response_text)
        return AIResponse(**data)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


async def ask_with_retry(prompt: str, attempts: int = 3) -> AIResponse:
    last_error = None
    system = await get_system_prompt()
    
    for attempt in range(attempts):
        try:
            response_text = await ask_ollama(system, prompt)
            return await process_ollama_response(response_text)
        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(f"Invalid JSON attempt {attempt + 1}, retrying...")
            prompt = INVALID_JSON_PROMPT
    
    raise ValueError(f"Failed after {attempts} attempts: {last_error}")


@router.post("/new", response_model=NewSessionResponse)
async def new_session():
    session_id = create_session()
    return NewSessionResponse(session_id=session_id)


@router.post("/chat/{session_id}")
async def chat(session_id: str, request: MessageRequest):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    add_user_message(session_id, request.message)
    
    context = get_messages_for_ollama(session_id)
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in context])
    
    try:
        result = await ask_with_retry(conversation)
        
        if result.method == "error":
            add_ai_message(session_id, ERROR_TEMPLATE)
            return {"response": ERROR_TEMPLATE, "method": "error"}
        
        if result.method == "read" and result.keys:
            docs = await get_documents_by_keys(result.keys)
            if not docs:
                add_ai_message(session_id, ERROR_TEMPLATE)
                return {"response": ERROR_TEMPLATE, "method": "error"}
            
            read_context = "Найденная информация:\n" + "\n".join([
                f"{d['key']}: {d['text']}" for d in docs
            ])
            
            result = await ask_with_retry(read_context + "\n\nТеперь дай финальный ответ на основе найденной информации.")
            add_references(session_id, result.keys or [])
        
        if result.method == "answer" and result.message:
            add_ai_message(session_id, result.message)
            return {
                "response": result.message,
                "method": "answer",
                "keys": result.keys or []
            }
        
        add_ai_message(session_id, ERROR_TEMPLATE)
        return {"response": ERROR_TEMPLATE, "method": "error"}
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        add_ai_message(session_id, ERROR_TEMPLATE)
        return {"response": ERROR_TEMPLATE, "method": "error"}


@router.delete("/close/{session_id}")
async def close_session(session_id: str):
    if delete_session(session_id):
        return {"message": "Сессия закрыта"}
    raise HTTPException(status_code=404, detail="Сессия не найдена")