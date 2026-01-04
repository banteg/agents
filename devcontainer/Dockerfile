# syntax=docker/dockerfile:1.7

# Based on Anthropic's Claude Code devcontainer template, with:
# - Codex CLI installed
# - Passwordless sudo for the non-root user
# - NO firewall / network restrictions (internet enabled)
# - tmux installed

ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE} AS node

ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest

# Build-time npm defaults.
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_PROGRESS=false \
    NPM_CONFIG_CACHE=/root/.npm \
    PATH="/usr/local/share/npm-global/bin:${PATH}"

RUN mkdir -p /usr/local/share/npm-global

# Install Claude Code + Codex CLI + pnpm in the node stage for faster rebuilds.
RUN --mount=type=cache,target=/root/.npm \
  npm install -g \
    "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
    "@openai/codex@${CODEX_VERSION}" \
  && corepack enable --install-directory /usr/local/share/npm-global/bin \
  && corepack prepare pnpm@latest --activate

FROM ubuntu:25.10

ARG TZ
ENV TZ="${TZ}"

ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest

# Install common dev tools.
# Note: we intentionally do NOT install iptables/ipset or ship a firewall script.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    less \
    procps \
    sudo \
    zsh \
    fish \
    unzip \
    openssh-client \
    gh \
    jq \
    vim \
    tmux \
    ncurses-term \
    git \
    ripgrep \
    zoxide \
    fd-find \
  && rm -rf /var/lib/apt/lists/*
RUN if command -v fdfind >/dev/null 2>&1 && [ ! -e /usr/local/bin/fd ]; then \
    ln -s /usr/bin/fdfind /usr/local/bin/fd; \
  fi

# Bring in node + npm from the official node image (fast, no apt deps).
COPY --from=node /usr/local/ /usr/local/
RUN node -v && npm -v

# Ensure git worktrees use relative paths by default.
RUN git config --system worktree.useRelativePaths true \
  && git config --system --add safe.directory /workspace

RUN if ! id -u "node" >/dev/null 2>&1; then \
    useradd -m -s /usr/bin/fish "node"; \
  fi

# Ensure default node user has access to the global npm prefix.
RUN mkdir -p /usr/local/share/npm-global \
  && chown -R "node:node" /usr/local/share

# Persist shell history across container rebuilds.
RUN mkdir -p /commandhistory \
  && touch /commandhistory/.bash_history /commandhistory/.zsh_history \
  && chown -R "node:node" /commandhistory \
  && cat >/etc/profile.d/00-commandhistory.sh <<'EOF'
# Persist interactive shell history in /commandhistory.
if [ -d /commandhistory ]; then
  export HISTSIZE=100000
  export HISTFILESIZE=200000

  if [ -n "${BASH_VERSION:-}" ]; then
    export HISTFILE=/commandhistory/.bash_history
    shopt -s histappend 2>/dev/null || true
    PROMPT_COMMAND="history -a; ${PROMPT_COMMAND:-}"
  fi

  if [ -n "${ZSH_VERSION:-}" ]; then
    export HISTFILE=/commandhistory/.zsh_history
    export SAVEHIST=200000
    setopt APPEND_HISTORY INC_APPEND_HISTORY SHARE_HISTORY HIST_IGNORE_ALL_DUPS HIST_REDUCE_BLANKS
  fi
fi
EOF

RUN echo '. /etc/profile.d/00-commandhistory.sh' >> /etc/bash.bashrc \
  && touch /etc/zsh/zshrc \
  && echo 'source /etc/profile.d/00-commandhistory.sh' >> /etc/zsh/zshrc

# Helpful marker for shell prompts / scripts.
ENV DEVCONTAINER=true

# Create workspace + agent config dirs and set permissions.
RUN mkdir -p /workspace /home/node/.claude /home/node/.codex /home/node/.npm /home/node/.config/fish \
  && touch /home/node/.zshrc \
  && chown -R node:node /workspace /home/node/.claude /home/node/.codex /home/node/.npm /home/node/.config /home/node/.zshrc

WORKDIR /workspace

# Install global packages.
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH="${PATH}:/usr/local/share/npm-global/bin"
ENV NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_PROGRESS=false

# Switch to non-root for normal dev.
USER node

# Runtime npm cache should be writable by node.
ENV NPM_CONFIG_CACHE=/home/node/.npm

# Default shell + editor.
ENV HOME=/home/node
ENV XDG_CONFIG_HOME=/home/node/.config
ENV SHELL=/usr/bin/fish
ENV EDITOR=vim
ENV VISUAL=vim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Ensure uv is on PATH for the node user.
ENV PATH="/home/node/.local/bin:${PATH}"

# Preinstall managed Python for uv.
RUN uv python install 3.14

# Passwordless sudo for the non-root user (for unattended / automation workflows).
USER root
RUN echo "node ALL=(root) NOPASSWD: ALL" > /etc/sudoers.d/yolo \
  && chmod 0440 /etc/sudoers.d/yolo

USER node
