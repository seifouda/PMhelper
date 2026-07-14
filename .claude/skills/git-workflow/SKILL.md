---
name: git-workflow
description: Use to track your work safely with git in the PMHelper repo — branching before you change things, making small clear commits, pushing, and opening a PR. Reach for this whenever you're about to start, save, or share work.
---

# Git workflow — keep track of your work

Git is your undo button and your notebook. The habit: **branch → change → commit
often → push → PR**.

## Before you start changing anything: branch
Never build on `main` directly. This repo's long-lived branch for the education
build is `EDU_PROD`.
```bash
git status                       # see where you are and what's dirty
git checkout -b feat/<short-name>   # e.g. feat/gantt-tooltips
```
Branch names: `feat/...` new feature, `fix/...` bug fix, `docs/...` docs.

## Save your work: commit in small logical chunks
```bash
git add -A                       # stage everything (or name files to be selective)
git status                       # ALWAYS look before committing
git commit -m "feat: add tooltip to Gantt bars"
```
Good messages: start with a type (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
`chore:`) and say *what changed and why* in one line. Commit when a thought is
complete — many small commits beat one giant one, because each is a restore point.

## See your history
```bash
git log --oneline -10            # recent commits
git diff                         # unstaged changes
git diff --cached                # staged changes (what will commit)
```

## Share it: push and open a PR
```bash
git push -u origin feat/<short-name>
gh pr create --fill              # opens a pull request on GitHub
```

## Undo safely (least destructive first)
- Unstage a file: `git restore --staged <file>`
- Discard uncommitted changes to a file: `git restore <file>` (**loses** those edits)
- Undo the last commit but keep the changes: `git reset --soft HEAD~1`
- Made a mess? `git stash` parks your changes; `git stash pop` brings them back.

**Ask before** anything with `--force`, `reset --hard`, or deleting a branch —
those can lose work that isn't recoverable.

## Rules of thumb
- Pull/rebase before you start if others share the branch.
- Don't commit generated files (charts, `*.db`) — `.gitignore` already excludes
  `outputs/` and databases here.
- If a commit "feels big," it's two commits.

## Related skills
[[run-tests]] before you commit. [[add-a-feature]] for the change itself.
