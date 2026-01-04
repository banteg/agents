# devcontainer template

a devcontainer for running claude code and codex in yolo mode.

based on anthropic's claude code devcontainer, modified to install codex and tmux, enable passwordless sudo, and remove firewall restrictions.

## use

copy the contents to `.devcontainer/` in your repo, or use the helper script.

### devc helper

from this repo:

```sh
./devcontainer/install.sh self-install
devc path/to/repo  # ← you are in tmux with claude and codex
```

`devc path/to/repo` installs the template, runs `devcontainer up`, and drops you into tmux with claude and codex installed and configured with yolo defaults.
if a global gitignore is configured on the host, it is copied to `.devcontainer/.gitignore_global`.
the template includes `.dockerignore` to keep large or sensitive files out of the build context.

### post-install

on container create, `.devcontainer/post_install.py`:

- sets `worktree.useRelativePaths` in the repo so host + container worktrees stay compatible
- sets `core.excludesfile` if `.devcontainer/.gitignore_global` exists
- installs `.devcontainer/tmux.conf` as `~/.tmux.conf` if missing
- configures codex/claude defaults to skip permission prompts inside the container
- removes a `TERM=xterm-256color` override from `~/.zshrc` if present

### vscode

open in vscode and run "reopen in container".

```sh
claude
codex
```

### cli

the helper expects the [devcontainer cli](https://github.com/devcontainers/cli).

```sh
npm install -g @devcontainers/cli
devc .
devc exec . -- tmux new -As agent
```

auth is persisted across rebuilds — `~/.codex/` and `~/.claude/` are mounted as docker volumes.
