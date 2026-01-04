#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
devcontainer helper for this template.

usage:
  devc <repo>            install template, devcontainer up, then tmux
  devc install <repo>    install template only
  devc rebuild <repo>    clear build cache, then up + tmux
  devc exec <repo> -- <cmd>
  devc self-install      install devc + template into ~/.local

notes:
  - install and default run overwrite .devcontainer in the target repo
  - rebuild keeps named volumes (history, auth) intact
  - if devcontainer cli is missing, we suggest how to install it
  - set DEVC_TEMPLATE_DIR to override the template source
USAGE
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILES=(Dockerfile devcontainer.json post_install.py)

die() {
  echo "error: $*" >&2
  exit 1
}

ensure_repo() {
  local repo_path="$1"
  [[ -d "$repo_path" ]] || die "repo path does not exist or is not a directory: $repo_path"
}

find_template_dir() {
  if [[ -n "${DEVC_TEMPLATE_DIR:-}" && -d "$DEVC_TEMPLATE_DIR" ]]; then
    echo "$DEVC_TEMPLATE_DIR"
    return
  fi

  if [[ -f "$SCRIPT_DIR/Dockerfile" && -f "$SCRIPT_DIR/devcontainer.json" ]]; then
    echo "$SCRIPT_DIR"
    return
  fi

  if [[ -d "$HOME/.local/share/devc/template" ]]; then
    echo "$HOME/.local/share/devc/template"
    return
  fi

  die "template dir not found (set DEVC_TEMPLATE_DIR or run devc self-install)"
}

copy_template() {
  local repo_path="$1"
  local src_dir="$2"
  local dest_dir="$repo_path/.devcontainer"

  mkdir -p "$dest_dir"

  for f in "${TEMPLATE_FILES[@]}"; do
    [[ -f "$src_dir/$f" ]] || die "missing template file: $src_dir/$f"
    cp -f "$src_dir/$f" "$dest_dir/$f"
  done

  local global_ignore=""
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
    cp -f "$global_ignore" "$dest_dir/.gitignore_global"
    echo "  copied global gitignore from $global_ignore" >&2
  fi

  echo "✓ devcontainer installed to: $dest_dir" >&2
}

require_devcontainer_cli() {
  if ! command -v devcontainer >/dev/null 2>&1; then
    echo "error: devcontainer cli not found" >&2
    echo "hint: npm install -g @devcontainers/cli" >&2
    exit 1
  fi
}

self_install() {
  local bin_dir="$HOME/.local/bin"
  local share_dir="$HOME/.local/share/devc/template"
  local template_src

  template_src="$(find_template_dir)"

  mkdir -p "$bin_dir" "$share_dir"

  cp -f "$SCRIPT_DIR/$(basename -- "$0")" "$bin_dir/devc"
  chmod +x "$bin_dir/devc"

  rm -rf "$share_dir"
  mkdir -p "$share_dir"
  for f in "${TEMPLATE_FILES[@]}"; do
    [[ -f "$template_src/$f" ]] || die "missing template file: $template_src/$f"
    cp -f "$template_src/$f" "$share_dir/$f"
  done

  echo "✓ installed devc to $bin_dir/devc" >&2
  echo "✓ installed template to $share_dir" >&2
  echo "note: ensure $bin_dir is on your PATH" >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
shift

case "$cmd" in
  help|-h|--help)
    usage
    exit 0
    ;;
  self-install)
    self_install
    exit 0
    ;;
  install|rebuild|exec)
    ;;
  *)
    set -- "$cmd" "$@"
    cmd="up"
    ;;
esac

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

REPO_PATH="$1"
shift

ensure_repo "$REPO_PATH"
TEMPLATE_DIR="$(find_template_dir)"

case "$cmd" in
  install)
    copy_template "$REPO_PATH" "$TEMPLATE_DIR"
    exit 0
    ;;
  rebuild)
    copy_template "$REPO_PATH" "$TEMPLATE_DIR"
    require_devcontainer_cli
    devcontainer up --workspace-folder "$REPO_PATH" --remove-existing-container
    devcontainer exec --workspace-folder "$REPO_PATH" tmux new -As agent
    ;;
  up)
    copy_template "$REPO_PATH" "$TEMPLATE_DIR"
    require_devcontainer_cli
    devcontainer up --workspace-folder "$REPO_PATH"
    devcontainer exec --workspace-folder "$REPO_PATH" tmux new -As agent
    ;;
  exec)
    copy_template "$REPO_PATH" "$TEMPLATE_DIR"
    require_devcontainer_cli
    if [[ $# -gt 0 && "$1" == "--" ]]; then
      shift
    fi
    [[ $# -gt 0 ]] || die "exec requires a command"
    devcontainer exec --workspace-folder "$REPO_PATH" "$@"
    ;;
esac
