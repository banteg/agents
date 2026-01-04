# agents

bunny-approved agent workflows

## git worktrees

ai agents don't like files changing under them as they carry out their plans. it helps to isolate them in separate directories so they don't touch each other's changes.

the workflow i use: create a worktree, make some commits, then either discard it or open a pull request. for this i use `gh pr create` or just ask `claude`. once merged, discard the worktree and prune the branch.

git has a [`git worktree`](https://git-scm.com/docs/git-worktree) subcommand for checking out a branch into a separate directory, but its ux isn't great. here are a couple of wrappers i use.

### [git wt](https://github.com/k1LoW/git-wt)

a simple wrapper that handles the common cases well.

####  install

`brew install k1LoW/tap/git-wt`

#### config

i put worktrees under `.worktrees` in the repo. add this to `~/.gitignore_global`, then configure the path:

```
git config wt.basedir .worktrees
```

#### use

`git wt` — list all worktrees

`git wt feat/branch` — switch to a worktree, creating the branch if needed

`git wt -d feat/branch` — soft delete worktree and branch

`git wt -D feat/branch` — hard delete worktree and branch

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

## notifications

i created [takopi](https://github.com/banteg/takopi) to run agents from telegram when i'm away from the computer. it bridges codex, claude code, opencode, and pi. it streams progress, and supports resumable sessions so i can start a task on my phone and pick it up in the terminal later. install with `uv tool install takopi` and run it in your repo.

i also use this codex `notify` [script](codex/notify_telegram/readme.md) to send a telegram message at the end of each turn.

## uninstall beads (assuming you can)

beads is often recommended, but removal requires [a 730-line shell script](https://gist.github.com/banteg/1a539b88b3c8945cd71e4b958f319d8d). it installs hooks in places you didn't know existed.
