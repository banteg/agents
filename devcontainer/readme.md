# devcontainer template

a devcontainer for running claude code and codex in yolo mode.

based on anthropic's claude code devcontainer, modified to install codex and tmux, enable passwordless sudo, and remove firewall restrictions.

## requirements

- docker (or orbstack)
- devcontainer cli (`npm install -g @devcontainers/cli`)

## use

copy the contents to `.devcontainer/` in your repo, or use the helper script.

### devc helper

from this repo:

```sh
./devcontainer/install.sh self-install
devc path/to/repo  # ← you are in tmux with claude and codex
```

`devc path/to/repo` installs the template, runs `devcontainer up`, and drops you into tmux with claude and codex installed and configured with yolo defaults.
`devc` overwrites `.devcontainer/` on every run. if you want to customize, fork the template and set `DEVC_TEMPLATE_DIR=/path/to/template`.
if a global gitignore is configured on the host, it is copied to `.devcontainer/.gitignore_global`.
the template includes `.dockerignore` to keep large or sensitive files out of the build context.
build context defaults to `.devcontainer/`, so only the template files are sent to docker.

notes:
- the gitconfig mount expects `~/.gitconfig` to exist on the host. if it doesn't, create it or remove the mount in `devcontainer.json`.
- if you want your host gitignore to stay live, add a bind mount for it and update `post_install.py` to prefer that path.

env knobs:
- `DEVC_TEMPLATE_DIR` — template override

### post-install

on container create, `.devcontainer/post_install.py`:

- sets `worktree.useRelativePaths` in the repo so host + container worktrees stay compatible
- sets `core.excludesfile` if `.devcontainer/.gitignore_global` exists
- installs `.devcontainer/tmux.conf` as `~/.tmux.conf` if missing
- configures codex/claude defaults to skip permission prompts inside the container

### vscode

open in vscode and run "reopen in container".

```sh
claude
codex
```

### cli

install the [devcontainer cli](https://github.com/devcontainers/cli):

```sh
npm install -g @devcontainers/cli
```

then:

```sh
devc .
```

auth is persisted across rebuilds — `~/.codex/` and `~/.claude/` are mounted as docker volumes.

### reset state

if you want to wipe persisted state:

```sh
docker volume rm commandhistory claude-code-config codex-config gh-config
```
