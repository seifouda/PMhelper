---
name: capture-patterns
description: Use whenever a reusable pattern, workflow, convention, or "how we do X here" emerges during work — turn it into a new skill so it's reusable next time. This is the meta-skill for growing the skill library as the project evolves.
---

# Capture patterns as skills (meta-skill)

**The convention for this project:** when you notice a pattern, a repeatable
workflow, a convention, or a lesson learned — don't let it evaporate. Write it up as
a new skill. The skill library should grow as the project does.

## When to capture
Trigger a capture when any of these is true:
- You explained the same "how to do X here" more than once.
- You discovered a non-obvious convention (e.g. the pure-`core`/`Step`-generator
  pattern, the UG/PG tab gating).
- You hit a gotcha and found the fix (e.g. "database locked" → raise SQLite timeout).
- You built a workflow worth repeating (a debugging routine, a release checklist).
- The user says "remember this" or "do it this way from now on."

## How to create a new skill
1. Pick a short kebab-case name, e.g. `release-checklist`.
2. Create `.claude/skills/<name>/SKILL.md` with this frontmatter:
   ```markdown
   ---
   name: <name>
   description: Use when <trigger>. <what it gives you>.
   ---

   # Title
   ...concrete, project-grounded steps with real file paths...
   ```
3. Make the `description` **trigger-oriented** — it's how the skill gets found
   ("Use when…"). Be specific about the situation, not just the topic.
4. Ground it in *this* repo: real commands, real file paths, real gotchas. A skill
   that could apply to any project isn't as useful as one that names
   `core/step_generators_edu.py`.
5. Link related skills with `[[skill-name]]`.
6. Add a line for it in `.claude/skills/README.md` (the index).
7. Commit it ([[git-workflow]]) — skills are shared with the whole project.

## What makes a good skill
- **Focused:** one job. If it's growing two heads, split it.
- **Actionable:** commands and steps, not essays.
- **Honest:** note known issues and pre-existing breakage.
- **Discoverable:** the description matches how someone would ask for it.

## Anti-patterns
- Don't duplicate what a doc already says — link to the doc instead.
- Don't capture one-off trivia; capture *repeatable* knowledge.
- Don't let a skill drift out of date — when the code moves, update the skill.

## Related skills
Every other skill is an example. Start from [[understand-this-codebase]] for tone.
