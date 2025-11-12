from __future__ import annotations

import aiohttp
from typing import Any, Dict, List, Optional


class OpenRouterError(Exception):
    """Raised when the OpenRouter API returns an error."""


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str, timeout: int = 60):
        if not api_key:
            raise OpenRouterError("Missing OpenRouter API key.")
        if not model:
            raise OpenRouterError("Model is required.")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if extra_payload:
            payload.update(extra_payload)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.BASE_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]

                detail = await resp.text()
                if resp.status == 402:
                    raise OpenRouterError(
                        "Insufficient credits or request too large. "
                        "Reduce message size or upgrade your OpenRouter plan."
                    )
                raise OpenRouterError(f"OpenRouter error {resp.status}: {detail}")


__all__ = ["OpenRouterClient", "OpenRouterError"]
