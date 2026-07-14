---
name: coding-fundamentals
description: Use when you want the core Python building blocks explained — variables, functions, control flow (if / for / while loops), data structures, classes — grounded in real examples from this codebase. For learners strengthening the basics while working on PMHelper.
---

# Coding fundamentals — with real PMHelper examples

Python is the language of this project's brain (`src/pmhelper/core/`). Here are the
building blocks, each pointing at real code you can open.

## Variables — named boxes for values
```python
optimistic = 4      # int
duration = 12.5     # float
name = "Design"     # str
is_critical = True  # bool
```

## Functions — reusable recipes (inputs → output)
```python
def expected_pert(o, m, p):
    """PERT-Beta expected duration = (O + 4M + P) / 6"""
    return (o + 4 * m + p) / 6
```
Real one: `ThreePointEngine.expected_pert(o, m, p)` in
`src/pmhelper/core/three_point_engine.py`. **Pure functions** (same input → same
output, no side effects) are the heart of `core/`.

## Control flow — decisions and repetition
**if / elif / else** — choose a path:
```python
if cpi >= 1:      status = "on/under budget"
elif cpi >= 0.9:  status = "watch"
else:             status = "over budget"     # this is the RAG idea
```
**for loop** — do something for each item:
```python
total = 0
for task in project.tasks:
    total += task.duration        # sum every task's duration
```
**while loop** — repeat until a condition changes:
```python
while not converged:
    step()                        # e.g. iterative leveling/optimization
```
Loops power CPM's forward/backward pass (`core/cpm_analyzer.py`) and the
optimizers (`core/multi_objective.py`). *(For automating repeated **commands**, see
[[loop-automation]] — different kind of loop.)*

## Data structures — how you hold many values
- **list** `[...]` ordered, changeable: `steps = [step1, step2]`
- **dict** `{key: value}` lookups by name: `params = {"method": "CPM"}`
- **tuple** `(...)` fixed group; **set** `{...}` unique items (e.g. `_PG_ONLY_TABS`).

## Classes & dataclasses — bundle data with behavior
```python
from dataclasses import dataclass

@dataclass
class Step:
    title: str
    formula: str
    result: float
```
Real one: the `Step` dataclass in `core/step_generators_edu.py`. This project uses
`@dataclass` with **manual validation** (no pydantic in core — see `DECISIONS.md`).

## How to actually learn it
Open a `core/*_edu.py` file, pick one function, and in a Python shell:
```python
from pmhelper.core.three_point_engine import ThreePointEngine
ThreePointEngine.expected_pert(2, 4, 12)   # try values, see the result
```
Change inputs, predict the output, check yourself. That loop *is* learning to code.

## Related skills
[[navigating-tech-for-beginners]] for orientation · [[understand-this-codebase]] for
where these live · [[pm-concepts-explained]] for what the math means.
