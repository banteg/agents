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
_AUTO_APPROVE_KEYS = {"risk_level", "user_authorization", "outcome", "rationale"}


def _tighten_list_paragraphs(html: str) -> str:
    return _LIST_PARA_RE.sub(r"<li\1>\2</li>", html)


def _json_object(value: object) -> dict[str, object] | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not (text.startswith("{") and text.endswith("}")):
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _is_ignored_json_message(value: object) -> bool:
    data = _json_object(value)
    if data is None:
        return False

    is_auto_approve = (
        data.get("outcome") == "allow"
        and data.keys() <= _AUTO_APPROVE_KEYS
    )
    is_title_only = isinstance(data.get("title"), str) and set(data) == {"title"}
    is_empty_exclude = data == {"exclude": []}
    return is_auto_approve or is_title_only or is_empty_exclude


def _should_skip_event(event: dict[str, object]) -> bool:
    return _is_ignored_json_message(event.get("last-assistant-message"))


def main() -> None:
    event = json.loads(sys.argv[1])
    if _should_skip_event(event):
        return

    creds = tomllib.loads(CREDS_PATH.read_text(encoding="utf-8"))
    bot_token = creds["bot_token"]
    chat_id = creds["chat_id"]

    md = str(event["last-assistant-message"]).rstrip()
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
