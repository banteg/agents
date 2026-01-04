#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

FISH_CONFIG = """\
# default fish config for the devcontainer
function fish_greeting
  echo "https://github.com/banteg/agents 2026-01-04"
end

function fish_prompt
  set -g __fish_git_prompt_showdirtystate 1
  set -g __fish_git_prompt_showuntrackedfiles 1
  set -g __fish_git_prompt_showupstream auto

  set_color cyan
  echo -n (prompt_pwd)
  set_color normal
  fish_vcs_prompt
  echo -n " > "
end
"""

TMUX_CONFIG = """\
set -g default-terminal "tmux-256color"
set -g focus-events on
set -sg escape-time 10
set -g mouse on
set -g history-limit 200000
set -g renumber-windows on
setw -g mode-keys vi

# Keep new panes/windows in the same cwd
bind c new-window -c "#{pane_current_path}"
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %

# Reload config
bind r source-file ~/.tmux.conf \\; display-message "tmux.conf reloaded"

# Terminal features
set -as terminal-features ",xterm-ghostty:RGB"
set -ga terminal-overrides '*:Ss=\\E[%p1%d q:Se=\\E[ q'
"""


def log(message: str) -> None:
    print(f"post-install: {message}", file=sys.stderr)


def run_git(args: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def resolve_workspace() -> Path:
    env_workspace = os.environ.get("WORKSPACE_FOLDER")
    if env_workspace:
        workspace = Path(env_workspace)
    else:
        workspace = Path("/workspace")
    if workspace.exists():
        return workspace
    return Path.cwd()


def is_git_repo(cwd: Path) -> bool:
    result = run_git(["rev-parse", "--is-inside-work-tree"], cwd)
    return result.returncode == 0 and result.stdout.strip() == "true"


def configure_git(cwd: Path) -> None:
    run_git(["config", "--local", "worktree.useRelativePaths", "true"], cwd, check=True)
    log(f"enabled git worktree.useRelativePaths in {cwd}")

    result = run_git(["config", "--local", "--get", "core.excludesfile"], cwd)
    if result.returncode == 0 and result.stdout.strip():
        log("skipping core.excludesfile (already set)")
        return

    home_ignore = Path.home() / ".gitignore_global"
    if home_ignore.exists():
        run_git(["config", "--local", "core.excludesfile", str(home_ignore)], cwd, check=True)
        log("set core.excludesfile to ~/.gitignore_global")
        return

    gitignore_global = cwd / ".devcontainer" / ".gitignore_global"
    if gitignore_global.exists():
        run_git(["config", "--local", "core.excludesfile", ".devcontainer/.gitignore_global"], cwd, check=True)
        log("set core.excludesfile to .devcontainer/.gitignore_global")


def ensure_codex_config() -> None:
    codex_dir = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    codex_dir.mkdir(parents=True, exist_ok=True)
    codex_config = codex_dir / "config.toml"
    if codex_config.exists():
        log(f"skipping codex config (already exists at {codex_config})")
        return

    codex_config.write_text(
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )
    log(f"wrote default codex config to {codex_config}")


def ensure_claude_config() -> None:
    claude_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    claude_dir.mkdir(parents=True, exist_ok=True)
    claude_config = claude_dir / "settings.json"
    if claude_config.exists():
        log(f"skipping claude settings (already exists at {claude_config})")
        return

    data = {"permissions": {"defaultMode": "bypassPermissions"}}
    claude_config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    log(f"wrote default claude settings to {claude_config}")


def ensure_fish_config() -> None:
    fish_config_dir = Path(
        os.environ.get(
            "XDG_CONFIG_HOME",
            str(Path.home() / ".config"),
        )
    ) / "fish"
    fish_config_dir.mkdir(parents=True, exist_ok=True)
    fish_config = fish_config_dir / "config.fish"
    if fish_config.exists():
        existing = fish_config.read_text(encoding="utf-8")
        if existing.lstrip().startswith("# default fish config for the devcontainer"):
            fish_config.write_text(FISH_CONFIG, encoding="utf-8")
            log(f"updated default fish config at {fish_config}")
            return
        log(f"skipping fish config (already exists at {fish_config})")
        return

    fish_config.write_text(FISH_CONFIG, encoding="utf-8")
    log(f"wrote default fish config to {fish_config}")


def install_tmux_config() -> None:
    tmux_dest = Path.home() / ".tmux.conf"
    if tmux_dest.exists():
        log(f"skipping tmux config (already exists at {tmux_dest})")
        return

    tmux_dest.write_text(TMUX_CONFIG, encoding="utf-8")
    log(f"installed tmux config to {tmux_dest}")


def main() -> None:
    workspace = resolve_workspace()
    if is_git_repo(workspace):
        configure_git(workspace)
    else:
        log(f"skipping git config (no repo at {workspace})")

    install_tmux_config()
    ensure_codex_config()
    ensure_claude_config()
    ensure_fish_config()
    log("configured defaults for container use")


if __name__ == "__main__":
    main()
