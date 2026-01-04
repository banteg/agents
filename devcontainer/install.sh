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

cli (optional):
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

echo "✓ devcontainer installed to: $DEST_DIR" >&2
echo "  next: open the repo in vscode and run 'reopen in container'." >&2
echo "  cli: npm install -g @devcontainers/cli" >&2
echo "       devcontainer up --workspace-folder $REPO_PATH" >&2
