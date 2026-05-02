# notify telegram

send codex completion summaries to telegram with safe markdown rendering.

## install

copy the script to `~/.codex/notify_telegram.py`.

create your [telegram creds](https://t.me/botfather) file at `~/.codex/telegram.toml`:

```toml
bot_token = "123456:ABCDEF..."
chat_id = 462722
```

## config

add a `notify` entry to `~/.codex/config.toml`:

```toml
notify = ["uv", "run", "-q", "/home/user/.codex/notify_telegram.py"]
```

## notes

- reads `last-assistant-message` and treats it as markdown
- renders markdown to html, converts to telegram text/entities via `sulguk`, then posts with `requests`
- normalizes list bullets from `•` to `-` for consistent telegram output
- skips auto-approve review summaries emitted by Codex approval auto-review agents
