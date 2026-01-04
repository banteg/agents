#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
install this repo's devcontainer template into a target repository.

usage:
  devcontainer/install.sh /path/to/repo

this will copy:
  - devcontainer/Dockerfile
  - devcontainer/devcontainer.json
  - devcontainer/post_install.sh

into:
  /path/to/repo/.devcontainer/

if a global gitignore is configured on this host, it will be copied to:
  /path/to/repo/.devcontainer/.gitignore_global

cli (optional):
  npm install -g @devcontainers/cli
  devcontainer up --workspace-folder /path/to/repo
  devcontainer exec --workspace-folder /path/to/repo bash
USAGE
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

REPO_PATH="$1"

if [[ ! -d "$REPO_PATH" ]]; then
  echo "error: repo path does not exist or is not a directory: $REPO_PATH" >&2
  exit 1
fi

SRC_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="$REPO_PATH/.devcontainer"

mkdir -p "$DEST_DIR"

for f in Dockerfile devcontainer.json post_install.sh; do
  if [[ ! -f "$SRC_DIR/$f" ]]; then
    echo "error: missing template file: $SRC_DIR/$f" >&2
    exit 1
  fi
  cp -f "$SRC_DIR/$f" "$DEST_DIR/$f"
done

global_ignore=""
if command -v git >/dev/null 2>&1; then
  global_ignore="$(git config --global --path core.excludesfile 2>/dev/null || true)"
fi

if [[ -z "$global_ignore" ]]; then
  if [[ -n "${XDG_CONFIG_HOME:-}" && -f "$XDG_CONFIG_HOME/git/ignore" ]]; then
    global_ignore="$XDG_CONFIG_HOME/git/ignore"
  elif [[ -f "$HOME/.config/git/ignore" ]]; then
    global_ignore="$HOME/.config/git/ignore"
  elif [[ -f "$HOME/.gitignore_global" ]]; then
    global_ignore="$HOME/.gitignore_global"
  fi
fi

if [[ -n "$global_ignore" && -f "$global_ignore" ]]; then
  cp -f "$global_ignore" "$DEST_DIR/.gitignore_global"
  echo "  copied global gitignore from $global_ignore" >&2
fi

echo "✓ devcontainer installed to: $DEST_DIR" >&2
echo "  next: open the repo in vscode and run 'reopen in container'." >&2
echo "  cli: npm install -g @devcontainers/cli" >&2
echo "       devcontainer up --workspace-folder $REPO_PATH" >&2
echo "       devcontainer exec --workspace-folder $REPO_PATH bash" >&2
