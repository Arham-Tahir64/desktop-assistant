from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .config import load_settings
from .llm import LMStudioClient
from .router import route_command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Desktop Assistant (LM Studio)")
    parser.add_argument(
        "--text",
        type=str,
        help="One-off text command (non-interactive)",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()  # load .env if present
    args = parse_args()
    settings = load_settings()
    client = LMStudioClient(settings)

    if args.text:
        result = route_command(settings, client, args.text)
        print(result.message)
        return 0 if result.ok else 1

    # Simple REPL for now
    print("Desktop Assistant (LM Studio). Type 'exit' to quit.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.lower() in {"exit", "quit"}:
            break
        result = route_command(settings, client, text)
        print(result.message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


