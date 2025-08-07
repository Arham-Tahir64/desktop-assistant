from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from typing import Optional
import shutil

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
        os.startfile(expanded)
        return ActionResult(True, f"Opened: {expanded}")
    except Exception as exc:
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
    except Exception as exc:
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


def _find_vscode_path() -> Optional[str]:
    candidates = [
        r"C:\\Program Files\\Microsoft VS Code\\Code.exe",
        r"C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _resolve_app_to_command(settings: Settings, app: str) -> Optional[list[str]]:
    app_lower = app.strip().strip('"').lower()
    if not app_lower:
        return None

    # If it's an explicit existing path, run it
    expanded = os.path.expandvars(os.path.expanduser(app))
    if os.path.isfile(expanded):
        return [expanded]

    # Known apps
    if app_lower in {"notepad"}:
        return [r"C:\\Windows\\System32\\notepad.exe"]
    if app_lower in {"calculator", "calc"}:
        return ["calc.exe"]
    if app_lower in {"vscode", "code"}:
        vs = _find_vscode_path()
        return [vs] if vs else ["Code.exe"]
    if app_lower in {"brave", "brave browser"}:
        if settings.brave_path and os.path.isfile(settings.brave_path):
            return [settings.brave_path]
        # fallback to webbrowser default if not found, by opening about:blank
        return None
    if app_lower in {"chrome", "google chrome"}:
        candidates = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return [path]
        return ["chrome.exe"]
    if app_lower in {"explorer", "file explorer"}:
        return ["explorer.exe"]
    if app_lower in {"cmd", "command prompt"}:
        return [r"C:\\Windows\\System32\\cmd.exe"]
    if app_lower in {"powershell", "pwsh"}:
        # Try Windows PowerShell first, then pwsh if available
        candidates = [
            r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            r"C:\\Program Files\\PowerShell\\7\\pwsh.exe",
        ]
        for path in candidates:
            if os.path.isfile(path):
                return [path]
        return ["powershell.exe"]

    # Last resort: try as an executable name on PATH
    if not app_lower.endswith(".exe"):
        exe_guess = f"{app_lower}.exe"
    else:
        exe_guess = app_lower
    which = shutil.which(exe_guess)
    if which:
        return [which]

    # Try token-based guesses on PATH (e.g., "visual studio code" -> "code.exe")
    tokens = [t for t in app_lower.replace("-", " ").split() if t]
    for candidate in [
        "".join(tokens) + ".exe",
        tokens[-1] + ".exe" if tokens else "",
    ]:
        if not candidate:
            continue
        path = shutil.which(candidate)
        if path:
            return [path]

    # Search Start Menu shortcuts (.lnk)
    lnk = _find_start_menu_shortcut(app_lower)
    if lnk:
        return [lnk]

    return [exe_guess]


def _find_start_menu_shortcut(app_lower: str) -> Optional[str]:
    def normalize(text: str) -> str:
        return "".join(ch for ch in text.lower() if ch.isalnum())

    start_menu_dirs = [
        os.path.expandvars(r"%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.expandvars(r"%AppData%\\Microsoft\\Windows\\Start Menu\\Programs"),
    ]
    target_norm = normalize(app_lower)
    for base in start_menu_dirs:
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for name in files:
                if not name.lower().endswith(".lnk"):
                    continue
                stem = os.path.splitext(name)[0]
                stem_norm = normalize(stem)
                # Simple contains or startswith match
                if target_norm in stem_norm or stem_norm.startswith(target_norm):
                    return os.path.join(root, name)
    return None


def launch_app(settings: Settings, app: str) -> ActionResult:
    if not app:
        return ActionResult(False, "No app name provided")
    cmd = _resolve_app_to_command(settings, app)
    try:
        if cmd is None:
            return ActionResult(False, f"Could not resolve app: {app}")
        # Handle Start Menu shortcut directly via Shell
        if len(cmd) == 1 and cmd[0].lower().endswith(".lnk"):
            os.startfile(cmd[0])  # type: ignore[attr-defined]
            return ActionResult(True, f"Launched: {app}")

        # For simple exe names, shell=True lets Windows resolve via PATH
        use_shell = len(cmd) == 1 and not os.path.isabs(cmd[0])
        subprocess.Popen(cmd, shell=use_shell)
        return ActionResult(True, f"Launched: {app}")
    except Exception as exc:  # noqa: BLE001
        return ActionResult(False, f"Failed to launch '{app}': {exc}")


