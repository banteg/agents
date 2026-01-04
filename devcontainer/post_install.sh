#!/usr/bin/env bash
set -euo pipefail

log() {
  echo "post-install: $*" >&2
}

workspace_dir="${WORKSPACE_FOLDER:-/workspace}"
if [[ ! -d "$workspace_dir" ]]; then
  workspace_dir="$PWD"
fi

if git -C "$workspace_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$workspace_dir" config --local worktree.useRelativePaths true
  log "enabled git worktree.useRelativePaths in $workspace_dir"

  gitignore_global="$workspace_dir/.devcontainer/.gitignore_global"
  if [[ -f "$gitignore_global" ]]; then
    if git -C "$workspace_dir" config --local --get core.excludesfile >/dev/null 2>&1; then
      log "skipping core.excludesfile (already set)"
    else
      git -C "$workspace_dir" config --local core.excludesfile ".devcontainer/.gitignore_global"
      log "set core.excludesfile to .devcontainer/.gitignore_global"
    fi
  fi
else
  log "skipping git config (no repo at $workspace_dir)"
fi

codex_dir="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_dir"
codex_config="$codex_dir/config.toml"
if [[ ! -f "$codex_config" ]]; then
  cat >"$codex_config" <<'TOML'
approval_policy = "never"
sandbox_mode = "danger-full-access"
TOML
  log "wrote default codex config to $codex_config"
else
  log "skipping codex config (already exists at $codex_config)"
fi

claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$claude_dir"
claude_config="$claude_dir/settings.json"

if [[ ! -f "$claude_config" ]]; then
  cat >"$claude_config" <<'JSON'
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
JSON
  log "wrote default claude settings to $claude_config"
else
  log "skipping claude settings (already exists at $claude_config)"
fi

log "configured defaults for container use"
