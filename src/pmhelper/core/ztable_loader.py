"""
PMhelper Edu — Z-Score Table Loader (V2 Phase 10).

Parses ``ztable.csv`` (semicolon-delimited, Z from −3.9 to +3.9) into a
lookup structure.  Provides forward lookup (Z → probability) and reverse
lookup (probability → nearest Z).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════════
#  Data containers
# ════════════════════════════════════════════════════════════════════

@dataclass
class ZTableData:
    """Parsed Z-table ready for lookups."""

    row_labels: List[str] = field(default_factory=list)
    """Row headers as strings, e.g. ['-3.9', '-3.8', ..., '3.9']."""

    col_labels: List[str] = field(default_factory=list)
    """Column headers as strings, e.g. ['.00', '.01', ..., '.09']."""

    cells: Dict[Tuple[str, str], float] = field(default_factory=dict)
    """Mapping (row_label, col_label) → probability value."""

    positive_rows: List[str] = field(default_factory=list)
    """Row labels for Z ≥ 0.0 (positive table)."""

    negative_rows: List[str] = field(default_factory=list)
    """Row labels for Z ≤ 0.0 (negative table, including -0.0)."""

    # Pre-built sorted list for reverse lookup: (probability, row, col)
    _reverse_index: List[Tuple[float, str, str]] = field(default_factory=list)

    @property
    def z_min(self) -> float:
        """Minimum Z value in the table."""
        return float(self.row_labels[0]) if self.row_labels else -3.9

    @property
    def z_max(self) -> float:
        """Maximum Z value in the table plus 0.09."""
        if not self.row_labels:
            return 3.99
        return float(self.row_labels[-1]) + 0.09


@dataclass
class ZLookupResult:
    """Result of a forward or reverse Z-table lookup."""

    z_value: float
    """The Z score (rounded to 2 decimals)."""

    row_label: str
    """Row header that was matched, e.g. '1.9'."""

    col_label: str
    """Column header that was matched, e.g. '.06'."""

    probability: float
    """The probability P(Z ≤ z)."""

    is_exact: bool = True
    """True if the lookup was exact; False if nearest-match (reverse)."""


# ════════════════════════════════════════════════════════════════════
#  Loader
# ════════════════════════════════════════════════════════════════════

def _default_csv_path() -> str:
    """Return the path to ``ztable.csv`` shipped with the package."""
    # ztable.csv ships inside the package (src/pmhelper/ztable.csv)
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(pkg_dir, "..", "ztable.csv"),               # packaged (pmhelper/ztable.csv)
        os.path.join(pkg_dir, "..", "..", "..", "ztable.csv"),   # legacy: repo root
        os.path.join(os.getcwd(), "ztable.csv"),                 # CWD fallback
    ]
    for p in candidates:
        resolved = os.path.normpath(p)
        if os.path.isfile(resolved):
            return resolved
    return os.path.join(os.getcwd(), "ztable.csv")


def load_ztable(csv_path: Optional[str] = None) -> ZTableData:
    """Parse ``ztable.csv`` and return a :class:`ZTableData`.

    Parameters
    ----------
    csv_path : str, optional
        Explicit path to the CSV.  If *None*, searches standard locations.

    Returns
    -------
    ZTableData

    Raises
    ------
    FileNotFoundError
        If the CSV cannot be found.
    ValueError
        If the CSV is malformed.
    """
    if csv_path is None:
        csv_path = _default_csv_path()

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Z-table CSV not found: {csv_path}")

    data = ZTableData()
    reverse: List[Tuple[float, str, str]] = []

    with open(csv_path, "r", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter=";")
        header = next(reader)

        # col_labels: ['.00', '.01', ..., '.09']
        data.col_labels = [h.strip() for h in header[1:]]

        for row in reader:
            if not row or not row[0].strip():
                continue
            row_label = row[0].strip()
            data.row_labels.append(row_label)

            z_base = float(row_label)
            if z_base <= 0.0:
                data.negative_rows.append(row_label)
            if z_base >= 0.0:
                data.positive_rows.append(row_label)

            for i, col_label in enumerate(data.col_labels):
                val_str = row[i + 1].strip() if (i + 1) < len(row) else ""
                try:
                    val = float(val_str)
                except (ValueError, IndexError):
                    val = 0.0
                data.cells[(row_label, col_label)] = val
                reverse.append((val, row_label, col_label))

    data._reverse_index = sorted(reverse, key=lambda t: t[0])
    return data


# ════════════════════════════════════════════════════════════════════
#  Forward lookup: Z → Probability
# ════════════════════════════════════════════════════════════════════

def lookup_forward(table: ZTableData, z: float) -> Optional[ZLookupResult]:
    """Look up a Z-score and return the probability with row/col path.

    Parameters
    ----------
    table : ZTableData
        Parsed Z-table.
    z : float
        Z-score to look up.  Will be rounded to 2 decimals.

    Returns
    -------
    ZLookupResult or None
        *None* if *z* is outside the table range.
    """
    z_rounded = round(z, 2)

    # Split into row and column components
    # For Z = 1.23:  row = "1.2", col = ".03"
    # For Z = -1.23: row = "-1.2", col = ".03"
    if z_rounded >= 0:
        row_val = int(z_rounded * 10) / 10       # 1.2
        col_val = round(z_rounded - row_val, 2)   # 0.03
    else:
        # For negative: -1.23 → row = -1.2, col = .03
        abs_z = abs(z_rounded)
        row_abs = int(abs_z * 10) / 10            # 1.2
        col_val = round(abs_z - row_abs, 2)       # 0.03
        row_val = -row_abs                        # -1.2

    # Format labels
    if row_val == 0.0 and z_rounded < 0:
        row_label = "-0.0"
    elif row_val == 0.0:
        row_label = "0.0"
    else:
        row_label = f"{row_val:.1f}"
        # Remove trailing "0" issues: ensure "-0.0" not "-0"
        if row_val < 0 and row_label == "-0.0":
            pass  # already correct

    col_label = f".{int(round(col_val * 100)):02d}"

    key = (row_label, col_label)
    prob = table.cells.get(key)
    if prob is None:
        return None

    return ZLookupResult(
        z_value=z_rounded,
        row_label=row_label,
        col_label=col_label,
        probability=prob,
        is_exact=True,
    )


# ════════════════════════════════════════════════════════════════════
#  Reverse lookup: Probability → Z (nearest)
# ════════════════════════════════════════════════════════════════════

def lookup_reverse(
        table: ZTableData,
        probability: float) -> Optional[ZLookupResult]:
    """Find the Z-score closest to a given probability.

    Parameters
    ----------
    table : ZTableData
        Parsed Z-table.
    probability : float
        Target cumulative probability (0 < p < 1).

    Returns
    -------
    ZLookupResult or None
        *None* if the table is empty.  ``is_exact`` is *True* only when
        the cell value matches *probability* exactly.
    """
    if not table._reverse_index:
        return None

    if probability <= 0 or probability >= 1:
        return None

    # Binary search for nearest value
    idx = _bisect_nearest(table._reverse_index, probability)
    val, row_label, col_label = table._reverse_index[idx]

    # Reconstruct Z from row + col
    z_val = float(row_label) + float(col_label)

    return ZLookupResult(
        z_value=round(z_val, 2),
        row_label=row_label,
        col_label=col_label,
        probability=val,
        is_exact=(abs(val - probability) < 1e-7),
    )


def _bisect_nearest(
    index: List[Tuple[float, str, str]], target: float
) -> int:
    """Return the index of the entry closest to *target* by value."""
    lo, hi = 0, len(index) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if index[mid][0] < target:
            lo = mid + 1
        else:
            hi = mid
    # lo is the insertion point; check neighbours
    best = lo
    if lo > 0 and abs(index[lo - 1][0] - target) < abs(index[lo][0] - target):
        best = lo - 1
    return best
