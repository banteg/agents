#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def log(message: str) -> None:
    print(f"post-install: {message}", file=os.sys.stderr)


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


def ensure_gitconfig_includes_host() -> None:
    home = Path.home()
    host = home / ".gitconfig_host"
    if not host.exists():
        return

    target = home / ".gitconfig"
    marker = "path = ~/.gitconfig_host"
    snippet = "[include]\n\tpath = ~/.gitconfig_host\n"

    if target.exists():
        content = target.read_text(encoding="utf-8")
        if marker in content:
            log("skipping gitconfig include (already present)")
            return
        target.write_text(content.rstrip() + "\n\n" + snippet + "\n", encoding="utf-8")
    else:
        target.write_text(snippet + "\n", encoding="utf-8")

    log("ensured ~/.gitconfig includes ~/.gitconfig_host")


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


def install_tmux_config(workspace: Path) -> None:
    tmux_src = workspace / ".devcontainer" / "tmux.conf"
    if not tmux_src.exists():
        return

    tmux_dest = Path.home() / ".tmux.conf"
    if tmux_dest.exists():
        log(f"skipping tmux config (already exists at {tmux_dest})")
        return

    tmux_dest.write_text(tmux_src.read_text(encoding="utf-8"), encoding="utf-8")
    log(f"installed tmux config to {tmux_dest}")


def cleanup_zshrc() -> None:
    zshrc = Path.home() / ".zshrc"
    if not zshrc.exists():
        return

    lines = zshrc.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines if line != "export TERM=xterm-256color"]
    if filtered == lines:
        return

    zshrc.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    log(f"removed TERM override from {zshrc}")


def main() -> None:
    workspace = resolve_workspace()
    ensure_gitconfig_includes_host()
    if is_git_repo(workspace):
        configure_git(workspace)
    else:
        log(f"skipping git config (no repo at {workspace})")

    install_tmux_config(workspace)
    ensure_codex_config()
    ensure_claude_config()
    cleanup_zshrc()
    log("configured defaults for container use")


if __name__ == "__main__":
    main()
