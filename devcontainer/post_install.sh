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
else
  log "skipping git config (no repo at $workspace_dir)"
fi

ensure_toml_key() {
  local file="$1"
  local key="$2"
  local value="$3"

  if [[ -f "$file" ]]; then
    if grep -Eq "^[[:space:]]*${key}[[:space:]]*=" "$file"; then
      perl -0pi -e "s/^[ \\t]*${key}\\s*=.*$/${key} = \\\"${value}\\\"/m" "$file"
      return
    fi
    printf '\n%s = "%s"\n' "$key" "$value" >>"$file"
    return
  fi

  printf '%s = "%s"\n' "$key" "$value" >"$file"
}

codex_dir="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_dir"
codex_config="$codex_dir/config.toml"
ensure_toml_key "$codex_config" "approval_policy" "never"
ensure_toml_key "$codex_config" "sandbox_mode" "danger-full-access"

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

log "configured codex defaults for container use"
