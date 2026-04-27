"""
PMhelper Edu — RACI Step Generator (V2 Phase 4).

Generates an educational :class:`~pmhelper.core.step_generators_edu.Step`
tree that teaches RACI matrix theory and walks through a completed matrix.

Two entry points
----------------
:func:`raci_theory_steps`
    Pure educational steps — definitions, rules, common mistakes.
    No matrix input required.

:func:`raci_matrix_steps`
    Worked-solution steps for a specific :class:`~pmhelper.core.raci_model.RACIMatrix`.
    Shows each row's role assignments and verifies PM rules.
"""

from __future__ import annotations

from typing import List

from pmhelper.core.step_generators_edu import Step
from pmhelper.core.raci_model import RACIMatrix


# ════════════════════════════════════════════════════════════════════
#  Theory steps (no matrix needed)
# ════════════════════════════════════════════════════════════════════

def raci_theory_steps() -> List[Step]:
    """
    Return educational steps explaining RACI theory.

    Suitable as the "Worked Solution" content when no project matrix
    has been built yet.
    """
    steps: List[Step] = []

    # ── Step 1: What is a RACI matrix? ──────────────────────────
    steps.append(Step(
        title="Step 1 — What is a RACI Matrix?",
        formula="Rows = Activities/Deliverables  |  Columns = Roles/People",
        interpretation=(
            "A RACI matrix (Responsibility Assignment Matrix) maps every "
            "project activity to a team member with a clear role designation.\n\n"
            "It answers: 'Who is responsible for what?' in a single structured table."
        ),
    ))

    # ── Step 2: The four letters ─────────────────────────────────
    letter_children = [
        Step(
            title="R — Responsible",
            formula="Who does the work?",
            interpretation=(
                "The person or role who EXECUTES the task. "
                "Multiple team members can share responsibility (multiple R's per row)."
            ),
            rag="blue",
        ),
        Step(
            title="A — Accountable",
            formula="Who owns the outcome?",
            interpretation=(
                "The single person who is ultimately ANSWERABLE for the result. "
                "There must be EXACTLY ONE A per activity — no more, no less. "
                "Often the project manager, department head, or work-package owner."
            ),
            rag="red",
        ),
        Step(
            title="C — Consulted",
            formula="Who provides input?",
            interpretation=(
                "Those whose EXPERTISE is needed before the work is done. "
                "This is two-way communication — they give feedback and it is acted on. "
                "Examples: subject-matter experts, legal/compliance reviewers."
            ),
            rag="amber",
        ),
        Step(
            title="I — Informed",
            formula="Who is kept in the loop?",
            interpretation=(
                "Those who need to KNOW the outcome but are not involved in execution. "
                "This is one-way communication — they receive status updates only. "
                "Examples: executive sponsors, external stakeholders."
            ),
            rag="green",
        ),
    ]

    steps.append(Step(
        title="Step 2 — The Four RACI Letters",
        formula="R / A / C / I",
        children=letter_children,
    ))

    # ── Step 3: PM Rules ─────────────────────────────────────────
    rule_children = [
        Step(
            title="Rule 1 — Exactly ONE A per row",
            formula="Count(A in row) = 1",
            interpretation=(
                "If there is NO Accountable: nobody owns the outcome — leads to confusion "
                "and finger-pointing when things go wrong.\n"
                "If there are MULTIPLE Accountable: accountability is diluted — everyone "
                "assumes someone else will take responsibility."
            ),
            rag="red",
        ),
        Step(
            title="Rule 2 — At least ONE R per row",
            formula="Count(R in row) ≥ 1",
            interpretation=(
                "If no one is Responsible, the activity will simply not get done. "
                "Multiple R's are acceptable — shared responsibility with a single A."
            ),
            rag="blue",
        ),
        Step(
            title="Rule 3 — Avoid overloading a single column",
            formula="No column should be all-R or all-A",
            interpretation=(
                "If one person is overwhelmed with assignments they are a bottleneck and "
                "single point of failure. Spread responsibility across the team."
            ),
        ),
        Step(
            title="Rule 4 — Agree, don't assume",
            formula="All assignments must be negotiated",
            interpretation=(
                "RACI matrices are only effective if the team has reviewed and agreed to "
                "every assignment. Never fill the matrix without stakeholder buy-in."
            ),
        ),
    ]

    steps.append(Step(
        title="Step 3 — PM Rules for a Valid RACI",
        formula="Exactly 1 A per row  |  At least 1 R per row",
        children=rule_children,
    ))

    # ── Step 4: Common Mistakes ──────────────────────────────────
    mistake_children = [
        Step(
            title="Mistake 1 — Multiple Accountable",
            formula="2 or more A's in one row",
            result="Fix: Discuss & agree who truly owns the outcome; demote others to C or I.",
            rag="red",
        ),
        Step(
            title="Mistake 2 — Missing Accountable",
            formula="0 A's in one row",
            result="Fix: Identify the work-package owner or escalate to project manager.",
            rag="red",
        ),
        Step(
            title="Mistake 3 — Confusing R and A",
            formula="A ≠ R (the doer ≠ the owner)",
            result="Fix: The A may also do the work (assign R and A to the same person), "
                   "but they are fundamentally different responsibilities.",
        ),
        Step(
            title="Mistake 4 — Too many C's",
            formula="Every role is listed as C",
            result="Fix: C implies action — the Consulted party must have time to respond. "
                   "If no real consultation is needed, use I instead.",
        ),
    ]

    steps.append(Step(
        title="Step 4 — Common Mistakes to Avoid",
        formula="—",
        children=mistake_children,
    ))

    return steps


# ════════════════════════════════════════════════════════════════════
#  Matrix worked solution
# ════════════════════════════════════════════════════════════════════

def raci_matrix_steps(matrix: RACIMatrix,
                      matrix_title: str = "RACI Matrix") -> List[Step]:
    """
    Generate worked-solution steps for a specific completed *matrix*.

    Parameters
    ----------
    matrix : RACIMatrix
    matrix_title : str
        Label shown in the first step heading.

    Returns
    -------
    list[Step]
    """
    if not matrix.rows or not matrix.cols:
        # Fall back to theory if matrix is empty
        return raci_theory_steps()

    steps: List[Step] = []

    # ── Step 1: Matrix overview ──────────────────────────────────
    counts = matrix.count_by_type()
    total_cells = len(matrix.rows) * len(matrix.cols)
    assigned = total_cells - counts.get("", 0)
    fill_pct = round(assigned / total_cells * 100) if total_cells > 0 else 0

    steps.append(Step(
        title=f"Step 1 — {matrix_title} Overview",
        formula=f"{len(matrix.rows)} activities  ×  {len(matrix.cols)} roles",
        result=(
            f"Assigned cells: {assigned}/{total_cells} ({fill_pct}%)  |  "
            + matrix.summary_text()
        ),
        interpretation=(
            "Review the matrix size and fill rate first. "
            "A well-formed matrix has every activity covered (no empty rows) and "
            "every role carrying at least one assignment."
        ),
    ))

    # ── Step 2: Row-by-row analysis ──────────────────────────────
    row_children: List[Step] = []
    for r_idx, row_name in enumerate(matrix.rows):
        row = matrix.get_row(r_idx)
        assignments = [
            f"{matrix.cols[c_idx]}={v}"
            for c_idx, v in enumerate(row) if v
        ]
        a_count = row.count("A")
        r_count = row.count("R")

        ok = (a_count == 1 and r_count >= 1)
        rag = "green" if ok else "red"

        row_children.append(
            Step(
                title=f"Activity: {row_name}",
                substitution="  |  ".join(assignments) if assignments else "(no assignments)",
                result=(
                    f"A={a_count}, R={r_count}  → " + (
                        "✓ Valid" if ok else "✗ Invalid (see rules)")),
                rag=rag,
            ))

    steps.append(Step(
        title="Step 2 — Analyse Each Activity Row",
        formula="Each row: Count(A) = 1  AND  Count(R) ≥ 1",
        children=row_children,
    ))

    # ── Step 3: Column-by-column analysis ────────────────────────
    col_children: List[Step] = []
    for c_idx, col_name in enumerate(matrix.cols):
        col = matrix.get_col(c_idx)
        assigned_cells = [v for v in col if v]
        a_count = col.count("A")
        r_count = col.count("R")

        col_children.append(
            Step(
                title=f"Role: {col_name}",
                result=(
                    f"Total assignments: {
                        len(assigned_cells)}  (R={r_count}, A={a_count}, " f"C={
                        col.count('C')}, I={
                        col.count('I')})"),
                rag="green" if assigned_cells else "amber",
                interpretation=(
                    "No assignments — consider removing this role." if not assigned_cells else ""),
            ))

    steps.append(Step(
        title="Step 3 — Analyse Each Role Column",
        formula="Each column should have at least one assignment",
        children=col_children,
    ))

    # ── Step 4: Validation summary ───────────────────────────────
    issues = matrix.validate()
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if not issues:
        val_step = Step(
            title="Step 4 — Validation",
            result="✓ Matrix is fully valid — no PM rule violations found.",
            rag="green",
        )
    else:
        issue_children = [
            Step(
                title=f"{'✗' if i.level == 'error' else '⚠'} {i.message[:60]}",
                rag="red" if i.level == "error" else "amber",
            )
            for i in issues
        ]
        val_step = Step(
            title=(
                "Step 4 — Validation — "
                f"{len(errors)} error(s), {len(warnings)} warning(s)"
            ),
            formula="Fix all errors before finalising the matrix.",
            rag="red" if errors else "amber",
            children=issue_children,
        )

    steps.append(val_step)

    return steps
