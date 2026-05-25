#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "markdown-it-py", "sulguk>=0.12.0"]
# ///
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from markdown_it import MarkdownIt
from sulguk import transform_html

CREDS_PATH = Path.home() / ".codex" / "telegram.toml"
ERR_PATH = Path.home() / ".codex" / "telegram_last_error.txt"

_MD_RENDERER = MarkdownIt("commonmark", {"html": False})
_BULLET_RE = re.compile(r"(?m)^(\s*)•")
_FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>[`~]{3,})(?P<info>.*)$")
_ORDERED_ITEM_RE = re.compile(r"^(?P<indent>[ \t]{0,3})(?P<marker>\d+[.)])\s+")
_UNORDERED_ITEM_RE = re.compile(r"^(?P<indent>[ \t]{0,3})[-+*]\s+")
_AUTO_APPROVE_KEYS = {"risk_level", "user_authorization", "outcome", "rationale"}


@dataclass(frozen=True, slots=True)
class _FenceState:
    fence: str
    indent: str
    header: str


def _render_markdown(md: str) -> tuple[str, list[dict[str, Any]]]:
    html = _MD_RENDERER.render(_normalize_nested_list_markers(md or ""))
    rendered = transform_html(html)

    text = _BULLET_RE.sub(r"\1-", rendered.text)
    return text, _sanitize_entities(rendered.entities)


def _normalize_nested_list_markers(md: str) -> str:
    if not md:
        return md

    lines: list[str] = []
    ordered_indent: str | None = None
    fence_state: _FenceState | None = None

    for raw_line in md.splitlines(keepends=True):
        line, ending = _split_line_ending(raw_line)
        fence_state = _update_fence_state(line, fence_state)
        if fence_state is not None:
            ordered_indent = None
            lines.append(raw_line)
            continue

        if not line.strip():
            ordered_indent = None
            lines.append(raw_line)
            continue

        ordered_match = _ORDERED_ITEM_RE.match(line)
        if ordered_match is not None:
            ordered_indent = ordered_match.group("indent")
            lines.append(raw_line)
            continue

        if ordered_indent is not None:
            unordered_match = _UNORDERED_ITEM_RE.match(line)
            if (
                unordered_match is not None
                and unordered_match.group("indent") == ordered_indent
            ):
                lines.append(f"{ordered_indent}   {line}{ending}")
                continue

            if line.startswith(ordered_indent) and len(line) > len(ordered_indent):
                lines.append(raw_line)
                continue

            ordered_indent = None

        lines.append(raw_line)

    return "".join(lines)

def _sanitize_entities(entities: list[Any]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for raw in entities:
        entity = dict(raw)
        if entity.get("type") == "text_link":
            url = entity.get("url")
            if not isinstance(url, str) or not _is_supported_text_link_url(url):
                continue
        sanitized.append(entity)
    return sanitized


def _is_supported_text_link_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and bool(parsed.netloc):
        return True
    return parsed.scheme == "tg" and (bool(parsed.netloc) or bool(parsed.path))


def _split_line_ending(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    if line.endswith("\r"):
        return line[:-1], "\r"
    return line, ""


def _update_fence_state(line: str, state: _FenceState | None) -> _FenceState | None:
    match = _FENCE_RE.match(line)
    if match is None:
        return state

    fence = match.group("fence")
    if state is None:
        return _FenceState(
            fence=fence,
            indent=match.group("indent"),
            header=match.group("info"),
        )

    if (
        line.startswith(state.indent)
        and fence.startswith(state.fence[0])
        and len(fence) >= len(state.fence)
    ):
        return None

    return state


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

    text, entities = _render_markdown(md)

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
