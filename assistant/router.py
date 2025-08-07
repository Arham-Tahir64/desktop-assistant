from __future__ import annotations

import json
from typing import Dict, List

from .config import Settings
from .llm import LMStudioClient
from .actions import (
    ActionResult,
    open_file,
    search_web,
    search_youtube,
    open_in_brave,
    launch_app,
)


SYSTEM_PROMPT = (
    "You are a desktop assistant that decides one action to perform based on the user request. "
    "Respond ONLY with compact JSON of the form: {\"action\": <one of 'open_file'|'search_web'|'search_youtube'|'open_url'|'launch_app'>, \"args\": { ... }}. "
    "Do not include any other text. If unsure, pick 'search_web'. For files, prefer absolute Windows paths if provided."
)


def _try_direct_app_launch(settings: Settings, user_text: str) -> ActionResult | None:
    text = user_text.strip().strip(".")
    lower = text.lower()
    # Accept simple patterns: "open notepad", "launch code", "start chrome"
    verbs = ("open ", "launch ", "start ")
    if not any(lower.startswith(v) for v in verbs):
        return None

    # Extract the part after the verb
    for v in verbs:
        if lower.startswith(v):
            remainder = text[len(v):].strip().strip('"').strip()
            break
    else:
        return None

    # Known apps to avoid routing normal sentences like "open youtube and search ..."
    known_apps = {
        "notepad",
        "code",
        "vscode",
        "chrome",
        "brave",
        "explorer",
        "file explorer",
        "calc",
        "calculator",
        "cmd",
        "powershell",
        "pwsh",
    }
    remainder_lower = remainder.lower()
    if any(app in remainder_lower for app in known_apps) or remainder_lower.endswith(".exe"):
        return launch_app(settings, remainder)

    return None


def route_command(settings: Settings, client: LMStudioClient, user_text: str) -> ActionResult:
    # Fast-path for app launches
    direct = _try_direct_app_launch(settings, user_text)
    if direct is not None:
        return direct

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
    if action == "launch_app":
        return launch_app(settings, args.get("app", ""))

    return search_web(settings, user_text)


