#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Install this repo's devcontainer template into a target repository.

Usage:
  devcontainer/install.sh /path/to/repo

This will copy:
  - devcontainer/Dockerfile
  - devcontainer/devcontainer.json
  - devcontainer/post_install.sh

Into:
  /path/to/repo/.devcontainer/

CLI (optional):
  npm install -g @devcontainers/cli
  devcontainer up --workspace-folder /path/to/repo
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

echo "✓ Devcontainer installed to: $DEST_DIR" >&2
echo "  Next: open the repo in VS Code and run 'Reopen in Container'." >&2
echo "  CLI: npm install -g @devcontainers/cli" >&2
echo "       devcontainer up --workspace-folder $REPO_PATH" >&2
