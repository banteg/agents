#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import shutil
from pathlib import Path

FISH_CONFIG = """\
# default fish config for the devcontainer
set -g __fish_git_prompt_showdirtystate 0
set -g __fish_git_prompt_showuntrackedfiles 0
set -g __fish_git_prompt_showupstream none

function fish_greeting
  echo "banteg/agents · autonomous coding sandbox"
end

function fish_prompt
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


def run_git(
    args: list[str], cwd: Path, check: bool = False
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def run_sudo(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sudo", *args],
        check=False,
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


def ensure_global_gitignore(workspace: Path) -> None:
    result = run_git(["config", "--global", "--path", "core.excludesfile"], workspace)
    if result.returncode != 0:
        log("no global core.excludesfile configured")
        return

    raw_path = result.stdout.strip()
    if not raw_path:
        log("no global core.excludesfile configured")
        return

    excludes_path = Path(raw_path).expanduser()
    if not excludes_path.is_absolute():
        excludes_path = (Path.home() / excludes_path).resolve()

    if excludes_path.exists():
        log(f"global core.excludesfile exists at {excludes_path}")
        return

    source = workspace / ".devcontainer" / ".gitignore_global"
    if not source.exists():
        log(
            f"global core.excludesfile missing at {excludes_path} and no template copy found"
        )
        return

    excludes_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, excludes_path)
    log(f"copied gitignore to {excludes_path}")


def ensure_codex_config() -> None:
    codex_dir = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    codex_dir.mkdir(parents=True, exist_ok=True)
    codex_config = codex_dir / "config.toml"
    if codex_config.exists():
        log(f"skipping codex config (already exists at {codex_config})")
        return

    codex_config.write_text(
        'approval_policy = "never"\nsandbox_mode = "danger-full-access"\n',
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
    fish_config_dir = (
        Path(
            os.environ.get(
                "XDG_CONFIG_HOME",
                str(Path.home() / ".config"),
            )
        )
        / "fish"
    )
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


def ensure_fish_history() -> None:
    history_volume = Path("/commandhistory")
    history_volume.mkdir(parents=True, exist_ok=True)
    target = history_volume / ".fish_history"

    fish_history = Path.home() / ".local" / "share" / "fish" / "fish_history"
    fish_history.parent.mkdir(parents=True, exist_ok=True)

    if fish_history.is_symlink():
        if fish_history.resolve() == target:
            return
        fish_history.unlink()
        fish_history.symlink_to(target)
        log(f"updated fish history symlink at {fish_history}")
        return

    if fish_history.exists():
        if not target.exists():
            fish_history.replace(target)
            log(f"moved fish history to {target}")
        else:
            log(f"existing fish history left at {fish_history}")
            return

    fish_history.symlink_to(target)
    log(f"linked fish history to {target}")


def ensure_dir_ownership(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        stat = path.stat()
    except OSError as exc:
        log(f"unable to stat {path}: {exc}")
        return

    uid = os.getuid()
    gid = os.getgid()
    if stat.st_uid == uid and stat.st_gid == gid:
        return

    result = run_sudo(["chown", "-R", f"{uid}:{gid}", str(path)])
    if result.returncode != 0:
        log(f"failed to chown {path}: {result.stderr.strip()}")
        return
    log(f"fixed ownership for {path}")


def install_tmux_config() -> None:
    tmux_dest = Path.home() / ".tmux.conf"
    if tmux_dest.exists():
        log(f"skipping tmux config (already exists at {tmux_dest})")
        return

    tmux_dest.write_text(TMUX_CONFIG, encoding="utf-8")
    log(f"installed tmux config to {tmux_dest}")


def main() -> None:
    workspace = resolve_workspace()
    if not is_git_repo(workspace):
        log(f"skipping git repo checks (no repo at {workspace})")

    install_tmux_config()
    ensure_dir_ownership(Path("/commandhistory"))
    ensure_dir_ownership(Path.home() / ".claude")
    ensure_dir_ownership(Path.home() / ".codex")
    ensure_dir_ownership(Path.home() / ".config" / "gh")
    ensure_fish_history()
    ensure_global_gitignore(workspace)
    ensure_codex_config()
    ensure_claude_config()
    ensure_fish_config()
    log("configured defaults for container use")


if __name__ == "__main__":
    main()
