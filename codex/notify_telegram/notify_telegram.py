#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "markdown-it-py", "sulguk>=0.11.1"]
# ///
import json
import re
import sys
import tomllib
from pathlib import Path

import requests
from markdown_it import MarkdownIt
from sulguk import transform_html

CREDS_PATH = Path.home() / ".codex" / "telegram.toml"
ERR_PATH = Path.home() / ".codex" / "telegram_last_error.txt"

_MD_RENDERER = MarkdownIt("commonmark", {"html": False})
_BULLET_RE = re.compile(r"(?m)^(\s*)•")
_LIST_PARA_RE = re.compile(r"(?s)<li([^>]*)>\s*<p>(.*?)</p>\s*</li>")


def _tighten_list_paragraphs(html: str) -> str:
    return _LIST_PARA_RE.sub(r"<li\1>\2</li>", html)


def main() -> None:
    creds = tomllib.loads(CREDS_PATH.read_text(encoding="utf-8"))
    bot_token = creds["bot_token"]
    chat_id = creds["chat_id"]

    event = json.loads(sys.argv[1])

    md = event["last-assistant-message"].rstrip()
    thread_id = event.get("thread-id")
    if thread_id:
        md += f"\n\n`codex resume {thread_id}`"

    html = _MD_RENDERER.render(md)
    html = _tighten_list_paragraphs(html)
    rendered = transform_html(html)

    text = _BULLET_RE.sub(r"\1-", rendered.text)
    entities = [dict(e) for e in rendered.entities]

    r = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "entities": entities,
            "disable_web_page_preview": True,
        },
        timeout=15,
    )

    try:
        data = r.json()
    except Exception:
        data = {"ok": False, "description": r.text}

    if not (r.status_code == 200 and data.get("ok") is True):
        ERR_PATH.write_text(
            f"{r.status_code}\n{data.get('description', '')}\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
