from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from typing import Optional

from .config import Settings


@dataclass
class ActionResult:
    ok: bool
    message: str


def open_file(path: str) -> ActionResult:
    if not path:
        return ActionResult(False, "No file path provided")
    expanded = os.path.expandvars(os.path.expanduser(path))
    if not os.path.exists(expanded):
        return ActionResult(False, f"Path not found: {expanded}")
    try:
        os.startfile(expanded)  # type: ignore[attr-defined]
        return ActionResult(True, f"Opened: {expanded}")
    except Exception as exc:  # noqa: BLE001
        return ActionResult(False, f"Failed to open file: {exc}")


def _build_brave_command(brave_path: Optional[str], url: str) -> list[str]:
    if brave_path and os.path.isfile(brave_path):
        return [brave_path, url]
    return []


def open_in_brave(settings: Settings, url: str) -> ActionResult:
    if not url:
        return ActionResult(False, "No URL provided")
    cmd = _build_brave_command(settings.brave_path, url)
    try:
        if cmd:
            subprocess.Popen(cmd, shell=False)
        else:
            webbrowser.open(url)
        return ActionResult(True, f"Opened in browser: {url}")
    except Exception as exc:  # noqa: BLE001
        return ActionResult(False, f"Failed to open browser: {exc}")


def search_web(settings: Settings, query: str) -> ActionResult:
    if not query:
        return ActionResult(False, "No search query provided")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return open_in_brave(settings, url)


def search_youtube(settings: Settings, query: str) -> ActionResult:
    if not query:
        return ActionResult(False, "No YouTube query provided")
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    return open_in_brave(settings, url)


