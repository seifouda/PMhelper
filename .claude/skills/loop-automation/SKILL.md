---
name: loop-automation
description: Use to set up recurring or self-paced automation with Claude Code's /loop feature and scheduled agents — e.g. re-run tests every few minutes, watch a build, or repeat a checklist. Reach for this when you want something to run repeatedly without re-typing it.
---

# Automating recurring work with /loop

Claude Code can repeat a prompt or slash-command on a schedule so you don't babysit
it. Two flavors:

## 1. Fixed-interval loop
Run something every N minutes:
```
/loop 5m /run-tests
/loop 10m check the dev server is still responding and summarize any errors
```
- The interval accepts `s`/`m`/`h` (e.g. `30s`, `5m`, `1h`).
- The task after the interval can be another slash-command or a plain instruction.
- It keeps running until you stop it.

## 2. Self-paced (dynamic) loop
Omit the interval and let the model decide when to check back — good for "watch this
until it's done" work:
```
/loop keep an eye on the build and tell me when it finishes or breaks
```
The model schedules its own next wake-up based on what it's waiting for.

## Good uses in this project
- `/loop 5m /run-tests` while you refactor `core/` — catch breakage early.
- Watch a long `ng build` or a server start-up and report when ready.
- Re-run a smoke checklist (`docs/reports/UI_SMOKE_TEST_CHECKLIST_EDU.md`) after each
  change.

## When NOT to loop
- One-off tasks — just run them once.
- Tight polling of something the tool already notifies you about (e.g. a background
  command you launched) — that's wasted work; you'll be told when it's done.

## Stopping a loop
Tell Claude to stop the loop, or interrupt it. A dynamic loop also ends when you say
it's finished.

## Scheduled (cloud) agents
For tasks that should run even when you're away (e.g. a nightly test run), the
`/schedule` skill creates cron-scheduled cloud agents. Use `/loop` for
"while I'm working"; use `/schedule` for "on a clock, unattended."

## Related skills
[[run-tests]] is the most common thing to loop. [[capture-patterns]] — if you find a
loop you reuse often, save it.
