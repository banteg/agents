# devcontainer template

a devcontainer for running claude code and codex in yolo mode.

based on anthropic's claude code devcontainer, modified to install codex and tmux, enable passwordless sudo, and remove firewall restrictions.

## use

copy the contents to `.devcontainer/` in your repo.

### install script

from this repo:

```sh
./devcontainer/install.sh path/to/repo
```

or manually:

```sh
cp -r devcontainer path/to/repo/.devcontainer
```

### post-install

on container create, `.devcontainer/post_install.sh`:

- sets `worktree.useRelativePaths` in the repo so host + container worktrees stay compatible
- configures codex/claude defaults to skip permission prompts inside the container

### vscode

open in vscode and run "reopen in container".

```sh
claude --dangerously-skip-permissions
codex --yolo
```

### cli

you can also run devcontainers from the terminal using the [devcontainer cli](https://github.com/devcontainers/cli).

```sh
npm install -g @devcontainers/cli
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . tmux new -s agent
# inside:
claude --dangerously-skip-permissions
codex --yolo
# reattach with:
devcontainer exec --workspace-folder . tmux attach -t agent
```

auth is persisted across rebuilds — `~/.codex/` and `~/.claude/` are mounted as docker volumes.
