# PMHelper skills

Project-specific skills for learning this codebase and getting work done. Invoke a
skill by its name (e.g. `/understand-this-codebase`), or just describe your task and
the matching skill will be used. Each skill is grounded in real PMHelper file paths
and commands.

## Working ethos (applies to every skill): be suggestive
Don't just execute the literal request — **help make it better.** While doing any
task, keep an eye out for improvements and *say something*: a cleaner approach, a
bug or gap nearby, a missing test, a simpler design, a naming or structure fix. Offer
them as concrete suggestions with the trade-offs, recommend one, and let the user
decide. A good suggestion the user can decline is more valuable than silently doing
only what was asked. When a suggestion is small, safe, and clearly right, just do it
and mention it; when it's bigger or uncertain, propose it and ask (see
[[capture-patterns]] and the "Check your assumptions" notes in the skills).

## Learn the project
- **understand-this-codebase** — the map: layers, where logic lives, how GUI/server/web/CLI/core fit together. *Start here.*
- **pm-concepts-explained** — each PM concept (CPM, PERT, EVM, AHP, risk, WBS…) → its source module.
- **navigating-tech-for-beginners** — orientation and mental models for a light technical background.
- **coding-fundamentals** — Python building blocks explained with real code from this repo.

## Do the work
- **run-and-debug** — launch the GUI, server, web, or a CLI; read and fix common errors.
- **add-a-feature** — add a tab/calc/CLI/endpoint the PMHelper way (pure core + Step generator + tests).
- **run-tests** — run the pytest suite, read failures, write a new test.
- **git-workflow** — branch, commit small, push, PR; keep track of your work safely.

## Automate & grow
- **loop-automation** — use Claude Code `/loop` and scheduled agents for recurring tasks.
- **capture-patterns** — the convention: turn any reusable pattern into a new skill.

## For the paper
- **writing-the-paper** — map the repo's algorithms, validation reports, and teaching design into paper sections.

---
Add new skills with **capture-patterns**. Keep this index updated when you do.
