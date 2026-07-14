---
name: navigating-tech-for-beginners
description: Use when you have a light technical background and feel lost in a codebase or the tooling around it. Gives mental models for reading unfamiliar code, finding where things are, and decoding the terminal, files, and jargon — so you can move without fear.
---

# Navigating tech with a light background

You don't need to understand *everything* to make progress. You need to find the
one file that matters and understand *that*. This skill is about orientation.

## The core mindset
- **Code is read far more than written.** Being slow at reading is normal.
- **You can always undo.** With git ([[git-workflow]]) nothing you try is permanent.
- **Follow the data, not the whole program.** Ask "where does this number come
  from?" and trace backward one step at a time.

## Where am I? (the terminal)
- `pwd` — print working directory (where you are). `ls` — list files. `cd folder` —
  go in; `cd ..` — go up.
- A **path** like `src/pmhelper/core/cpm_analyzer.py` is just folder→folder→file.
- Red text isn't always fatal — read it; often it names the exact file and line.
- Ctrl+C stops a running command. Closing the terminal doesn't delete anything.

## Find things fast (don't scroll — search)
- "Where is X defined/used?" → search the whole repo for the word `X`. In this
  editor use the search tool; on the command line, `grep -rn "X" src/`.
- "What runs when I start the app?" → find the entry point (here:
  `python -m pmhelper.edu_main`) and open that file first. See
  [[understand-this-codebase]].
- File names are clues: `*_edu.py` = education layer, `*_step_generator.py` = the
  "show your work" logic, `test_*.py` = tests, `*_tab_edu.py` = a screen/tab.

## Decoding a file you've never seen
1. Read the top: imports tell you what it depends on.
2. Read function/class **names** and docstrings — skip the bodies first.
3. Find the one function related to your task; read only that.
4. Change one small thing, run it ([[run-and-debug]]), see what happens.

## Jargon decoder (just enough)
- **Function** = a named recipe that takes inputs and returns an output.
- **Class** = a blueprint bundling data + functions (methods).
- **Import** = "use code from another file."
- **API / endpoint** = a URL the frontend calls to get data from the server.
- **Editable install** (`pip install -e .`) = "let Python find this project's code
  by name anywhere."
- **Traceback** = the error's breadcrumb trail; read it bottom-up.

## When you're stuck
Write down (a) what you did, (b) what you expected, (c) what happened, including
the exact error text. That framing usually reveals the answer — and if you ask for
help, it's the fastest way to get it. **Asking is a skill, not a failure.**

## Related skills
[[coding-fundamentals]] for the language basics · [[run-and-debug]] to run things ·
[[understand-this-codebase]] for the map.
