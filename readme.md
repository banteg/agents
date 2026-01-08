# agents

bunny-approved agent workflows

## git worktrees

ai agents don't like files changing under them as they carry out their plans. it helps to isolate them in separate directories so they don't touch each other's changes.

the workflow i use: create a worktree, make some commits, then either discard it or open a pull request. for this i use `gh pr create` or just ask `claude`. once merged, discard the worktree and prune the branch.

git has a [`git worktree`](https://git-scm.com/docs/git-worktree) subcommand for checking out a branch into a separate directory, but its ux isn't great. here are a couple of wrappers i use.

### [git wt](https://github.com/k1LoW/git-wt)

a simple wrapper that handles the common cases well.

#### install

`brew install k1LoW/tap/git-wt`

#### config

i put worktrees under `.worktrees` in the repo. add this to `~/.gitignore_global`, then configure the path:

```
git config wt.basedir .worktrees
```

#### use

- `git wt` — list all worktrees
- `git wt feat/branch` — switch to a worktree, creating the branch if needed
- `git wt -d feat/branch` — soft delete worktree and branch
- `git wt -D feat/branch` — hard delete worktree and branch

### [worktrunk](https://worktrunk.dev/)

a more full-featured option. it closely matches the create → pr → merge → cleanup cycle and has nice extras like auto-running install scripts or generating commits with [llm](https://llm.datasette.io/en/stable/) cli.

#### config

to match my naming structure, i put this in `~/.config/worktrunk/config.toml`:

```toml
worktree-path = ".worktrees/{{ branch }}"
```

#### use

- `wt switch -c -x codex feat/branch` — switch to a worktree and run codex
- `wt merge` — squash, rebase, merge into master, remove worktree and branch
- `wt step commit` — commit based on the diff and previous commit style
- `wt remove` — remove worktree and prune branch
- `wt select` — interactive switcher showing all worktrees and diff from master

### relative worktrees

by default, git stores absolute paths in worktree metadata. this breaks if you use devcontainer. git 2.48+ added relative path support.

enable with `git config --global worktree.useRelativePaths true`

new worktrees will use relative paths in all repos. to migrate existing worktrees to relative paths `git worktree repair`

## seatbelt sandbox

if you keep getting permission prompts in claude code and want it to behave more like codex, enable macos seatbelt sandboxing. this runs bash commands inside macos's seatbelt sandbox, which restricts file writes to the project directory and limits network access. combined with auto-approval, this lets you skip most permission prompts while staying protected.

add this to `~/.claude/settings.json`:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true
  }
}
```

## devcontainer

running agents unattended (yolo mode) is best done in a devcontainer. it provides isolation and lets you skip permission prompts. you will need docker, i prefer [orbstack](https://orbstack.dev/) as a drop-in replacement.

i made a handy devcontainer script:

```sh
./devcontainer/install.sh self-install
devc /path/to/repo  # ← you are in tmux with claude and codex
```

read more [devcontainer/readme.md](devcontainer/readme.md).

## plan and review

for architecture, refactors, debugging, or "tell me what to fix next" reviews, just give the model the repo.

most people reach for repomix / code2prompt and feed the model a giant xml/md. that's outdated practice.

upload a zip made directly by git:

```sh
git archive HEAD -o code.zip
# if you need only part of the repo:
git archive HEAD:src -o src.zip
```

this works with gpt pro, claude, and gemini.

if you want context from commit messages, prior attempts, regressions, gpt and claude can also understand a git bundle:

```sh
git bundle create repo.bundle --all
```

## notifications

for full telegram control of agents, use [takopi](https://github.com/banteg/takopi). it bridges codex, claude code, opencode, and pi, streams progress, and supports resumable sessions so you can start a task on your phone and pick it up in the terminal later. install with `uv tool install takopi` and run it in your repo.

for simple completion notifications, use this codex `notify` [script](codex/notify_telegram/readme.md) to send a telegram message at the end of each turn.

## uninstall beads (assuming you can)

beads is often recommended, but removal requires [a 730-line shell script](https://gist.github.com/banteg/1a539b88b3c8945cd71e4b958f319d8d). it installs hooks in places you didn't know existed.
