# syntax=docker/dockerfile:1.7

# Based on Anthropic's Claude Code devcontainer template, with:
# - Codex CLI installed
# - Passwordless sudo for the non-root user
# - NO firewall / network restrictions (internet enabled)
# - tmux installed

ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE} AS node

FROM ubuntu:25.10

ARG TZ
ENV TZ="${TZ}"

ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest
ARG GIT_DELTA_VERSION=0.18.2
ARG USERNAME=node

# Install common dev tools.
# Note: we intentionally do NOT install iptables/ipset or ship a firewall script.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    less \
    procps \
    sudo \
    zsh \
    man-db \
    unzip \
    gnupg2 \
    openssh-client \
    gh \
    jq \
    nano \
    vim \
    tmux \
    ncurses-term \
    dnsutils \
    git \
    python3 \
  && rm -rf /var/lib/apt/lists/*

# Bring in node + npm from the official node image (fast, no apt deps).
COPY --from=node /usr/local/ /usr/local/
RUN node -v && npm -v

# Ensure git worktrees use relative paths by default.
RUN git config --system worktree.useRelativePaths true

RUN if ! id -u "$USERNAME" >/dev/null 2>&1; then \
    useradd -m -s /bin/zsh "$USERNAME"; \
  fi

# Ensure default node user has access to the global npm prefix.
RUN mkdir -p /usr/local/share/npm-global \
  && chown -R "$USERNAME:$USERNAME" /usr/local/share

# Persist bash history across container rebuilds.
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  && mkdir -p /commandhistory \
  && touch /commandhistory/.bash_history \
  && chown -R "${USERNAME}" /commandhistory

# Helpful marker for shell prompts / scripts.
ENV DEVCONTAINER=true

# Create workspace + agent config dirs and set permissions.
RUN mkdir -p /workspace /home/node/.claude /home/node/.codex \
  && chown -R node:node /workspace /home/node/.claude /home/node/.codex

WORKDIR /workspace

# Install git-delta (nice diffs in reviews).
RUN ARCH="$(dpkg --print-architecture)" \
  && wget -q "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" \
  && dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" \
  && rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# Switch to non-root for normal dev + npm global installs.
USER node

# Install global packages.
ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
ENV PATH="${PATH}:/usr/local/share/npm-global/bin"

# Default shell + editor.
ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano

# Make npm installs faster + more cache-friendly.
ENV NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_PROGRESS=false

# Install Claude Code + Codex CLI + pnpm.
RUN --mount=type=cache,target=/home/node/.npm \
  npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
                 "@openai/codex@${CODEX_VERSION}" \
  && corepack enable \
  && corepack prepare pnpm@latest --activate

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is on PATH for the node user.
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Passwordless sudo for the non-root user (for unattended / automation workflows).
USER root
RUN echo "node ALL=(root) NOPASSWD: ALL" > /etc/sudoers.d/yolo \
  && chmod 0440 /etc/sudoers.d/yolo

USER node
