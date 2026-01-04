# autonomous coding sandbox

a devcontainer for running claude code and codex in yolo mode.

based on anthropic's claude code devcontainer.

## requirements

- docker (or [orbstack](https://orbstack.dev/))
- devcontainer cli (`npm install -g @devcontainers/cli`)

## quickstart

install `./devcontainer/install.sh self-install`

run `devc <repo>` or `devc .` inside project folder.

you're now in tmux with claude and codex ready to go, with permissions preconfigured.

to use with vscode, run `devc install <repo>` and choose "reopen in container" in the editor.
the built in terminal would login inside the container.

## notes

- **overwrites `.devcontainer/`** on every run
- default shell is fish, zsh available for agents
- auth and history persist across rebuilds via docker volumes
