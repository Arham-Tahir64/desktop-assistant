from __future__ import annotations

import json
from typing import List, Dict, Any

import requests

from .config import Settings


class LMStudioClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.lmstudio_base_url.rstrip("/")
        self._model = settings.lmstudio_model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int | None = 512) -> str:
        url = f"{self._base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


