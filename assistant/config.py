from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    lmstudio_base_url: str
    lmstudio_model: str
    brave_path: str | None


def _detect_brave_path() -> str | None:
    candidates = [
        r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        r"C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def load_settings() -> Settings:
    # Load from environment; .env can be used by python-dotenv via importing in main
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    model = os.getenv("LMSTUDIO_MODEL", "local-model")
    brave_path = os.getenv("BRAVE_PATH") or _detect_brave_path()
    return Settings(
        lmstudio_base_url=base_url,
        lmstudio_model=model,
        brave_path=brave_path,
    )


