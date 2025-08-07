from __future__ import annotations

import json
from typing import Dict, List

from .config import Settings
from .llm import LMStudioClient
from .actions import ActionResult, open_file, search_web, search_youtube, open_in_brave


SYSTEM_PROMPT = (
    "You are a desktop assistant that decides one action to perform based on the user request. "
    "Respond ONLY with compact JSON of the form: {\"action\": <one of 'open_file'|'search_web'|'search_youtube'|'open_url'>, \"args\": { ... }}. "
    "Do not include any other text. If unsure, pick 'search_web'. For files, prefer absolute Windows paths if provided."
)


def route_command(settings: Settings, client: LMStudioClient, user_text: str) -> ActionResult:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    raw = client.chat(messages, temperature=0.0, max_tokens=256)
    try:
        data = json.loads(raw)
        action = data.get("action")
        args = data.get("args", {}) or {}
    except Exception:
        # Fall back to web search
        return search_web(settings, user_text)

    if action == "open_file":
        return open_file(args.get("path", ""))
    if action == "search_web":
        return search_web(settings, args.get("query", user_text))
    if action == "search_youtube":
        return search_youtube(settings, args.get("query", user_text))
    if action == "open_url":
        return open_in_brave(settings, args.get("url", ""))

    return search_web(settings, user_text)


