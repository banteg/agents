# Based on Anthropic's Claude Code devcontainer template, with:
# - Codex CLI installed
# - Passwordless sudo for the non-root user
# - NO firewall / network restrictions (internet enabled)
# - tmux installed

FROM ubuntu:25.10

ARG TZ
ENV TZ="${TZ}"

ARG CLAUDE_CODE_VERSION=latest
ARG CODEX_VERSION=latest
ARG GIT_DELTA_VERSION=0.18.2
ARG USERNAME=node

# Install common dev tools.
# Note: we intentionally do NOT install iptables/ipset or ship a firewall script.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    less \
    procps \
    sudo \
    fzf \
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
    nodejs \
    npm \
    python3 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

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

# Install Claude Code + Codex CLI + pnpm
RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  && npm install -g "@openai/codex@${CODEX_VERSION}" \
  && npm install -g pnpm

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is on PATH for the node user.
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Passwordless sudo for the non-root user (for unattended / automation workflows).
USER root
RUN echo "node ALL=(root) NOPASSWD: ALL" > /etc/sudoers.d/yolo \
  && chmod 0440 /etc/sudoers.d/yolo

USER node
