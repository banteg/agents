# Based on Anthropic's Claude Code devcontainer template, with:
# - Codex CLI installed
# - Passwordless sudo for the non-root user
# - NO firewall / network restrictions (internet enabled)
# - tmux installed

FROM node:20

ARG TZ
ENV TZ="${TZ}"

ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest
ARG GIT_VERSION=2.48.0
ARG GIT_DELTA_VERSION=0.18.2
ARG ZSH_IN_DOCKER_VERSION=1.2.0

# Install common dev tools.
# Note: we intentionally do NOT install iptables/ipset or ship a firewall script.
#
# Git >= 2.48 is required for worktree.useRelativePaths (relative worktrees).
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    less \
    build-essential \
    gettext \
    libcurl4-gnutls-dev \
    libexpat1-dev \
    libpcre2-dev \
    libssl-dev \
    zlib1g-dev \
    perl \
    procps \
    sudo \
    fzf \
    zsh \
    man-db \
    unzip \
    xz-utils \
    gnupg2 \
    openssh-client \
    gh \
    jq \
    nano \
    vim \
    tmux \
    dnsutils \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install a modern Git (>= 2.48) so relative worktrees work inside devcontainers.
# Debian's stock Git can lag behind; building from source keeps this template portable.
RUN set -eux; \
  curl -fsSL "https://www.kernel.org/pub/software/scm/git/git-${GIT_VERSION}.tar.xz" -o /tmp/git.tar.xz; \
  tar -xJf /tmp/git.tar.xz -C /tmp; \
  make -C "/tmp/git-${GIT_VERSION}" prefix=/usr/local NO_TCLTK=YesPlease USE_LIBPCRE2=YesPlease all; \
  make -C "/tmp/git-${GIT_VERSION}" prefix=/usr/local NO_TCLTK=YesPlease USE_LIBPCRE2=YesPlease install; \
  rm -rf /tmp/git.tar.xz "/tmp/git-${GIT_VERSION}"; \
  git --version; \
  git config --system worktree.useRelativePaths true

# Ensure default node user has access to the global npm prefix.
RUN mkdir -p /usr/local/share/npm-global \
  && chown -R node:node /usr/local/share

ARG USERNAME=node

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

# ZSH enhancements (same as Claude's template).
RUN sh -c "$(wget -qO- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
    -p git \
    -p fzf \
    -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
    -a "source /usr/share/doc/fzf/examples/completion.zsh" \
    -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    -x

# Install Claude Code + Codex CLI + pnpm
RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  && npm install -g "@openai/codex@${CODEX_VERSION}" \
  && npm install -g pnpm

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Passwordless sudo for the non-root user (for unattended / automation workflows).
USER root
RUN echo "node ALL=(root) NOPASSWD: ALL" > /etc/sudoers.d/yolo \
  && chmod 0440 /etc/sudoers.d/yolo

USER node
