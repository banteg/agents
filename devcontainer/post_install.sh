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

node - "$claude_config" <<'NODE'
const fs = require("fs");
const path = require("path");

const settingsPath = process.argv[1];
let data = {};

if (fs.existsSync(settingsPath)) {
  try {
    data = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  } catch (err) {
    const backupPath = `${settingsPath}.bak.${Date.now()}`;
    fs.copyFileSync(settingsPath, backupPath);
    data = {};
    console.error(`post-install: invalid JSON in ${settingsPath}, backed up to ${backupPath}`);
  }
}

if (typeof data !== "object" || data === null) {
  data = {};
}

data.permissions = Object.assign({}, data.permissions, {
  defaultMode: "bypassPermissions",
});

fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
fs.writeFileSync(settingsPath, JSON.stringify(data, null, 2) + "\n");
NODE

log "configured codex and claude defaults for container use"
