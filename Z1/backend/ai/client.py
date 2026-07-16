from collections.abc import Sequence

import httpx

from api.config import settings


class OpenAICompatibleClient:
    def __init__(self) -> None:
        self.base_url = settings.openai_api_base.rstrip("/")
        self.api_key = settings.openai_api_key

    async def chat(self, messages: Sequence[dict[str, str]], model: str = "gpt-4o-mini") -> dict:
        if not self.api_key:
            return {
                "model": model,
                "content": "Kein OPENAI_API_KEY gesetzt. Antwort im Mock-Modus.",
                "mock": True,
            }

        headers = {"Authorization": "Bearer " + self.api_key}
        payload = {"model": model, "messages": list(messages)}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
