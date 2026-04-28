import json
import httpx
from typing import Optional
from config import ollama_model, ollama_host


class OllamaService:
    def __init__(self):
        self.model = ollama_model
        self.host = ollama_host

    async def generate(self, system_prompt: str, user_message: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "system": system_prompt,
                    "prompt": user_message,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()


ollama_service = OllamaService()


async def ask_ollama(system_prompt: str, user_message: str) -> str:
    return await ollama_service.generate(system_prompt, user_message)