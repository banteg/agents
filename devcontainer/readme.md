# Devcontainer template (Claude Code + Codex)

This template is based on Anthropic's Claude Code devcontainer, but modified to:

- install **Codex CLI** (`codex`)
- install **tmux**
- enable **passwordless sudo** for the `node` user
- **remove firewall** scripts/capabilities (internet access is enabled by default)

## Use in a repo

Copy `.devcontainer/` to the root of the repo you want to work in:

```bash
cp -r path/to/this-template/.devcontainer ./  # from your repo root
```

Then open in VS Code and run **Dev Containers: Reopen in Container**.

## Quick commands inside the container

```bash
claude --dangerously-skip-permissions
codex --yolo --search
tmux new -s agent
```

Tip: Codex stores config in `~/.codex/` and Claude in `~/.claude/` — this template mounts both as Docker volumes so auth persists across rebuilds.
