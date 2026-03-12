"""
PMhelper Edu — WBS Export.
Export WBS tree to CSV, JSON, Excel (openpyxl), PNG/PDF (Matplotlib).
"""

from __future__ import annotations
import csv
import json
import io
import os
from typing import Optional

from pmhelper.core.wbs_models_edu import WBSTree, WBSNode, WBS_STATUS_COLOURS

try:
    from matplotlib.figure import Figure
    from matplotlib.patches import FancyBboxPatch
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class WBSExporter:
    """Export WBS tree to various formats."""

    @staticmethod
    def to_csv(tree: WBSTree, filepath: str) -> None:
        """Export WBS to CSV."""
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "WBS_Code", "Name", "Parent_WBS_Code", "Duration",
                "Cost", "Progress", "Status", "Responsible", "Description"
            ])

            # Build id→code map
            code_map = {n.id: n.wbs_code for n in tree.nodes}

            for node in sorted(tree.nodes, key=lambda n: n.wbs_code):
                parent_code = code_map.get(node.parent_id, "")
                writer.writerow([
                    node.wbs_code,
                    node.name,
                    parent_code,
                    f"{node.duration:.1f}",
                    f"{node.cost:.2f}",
                    f"{node.progress:.1f}",
                    node.status.value,
                    node.responsible,
                    node.description,
                ])

    @staticmethod
    def to_json(tree: WBSTree, filepath: str) -> None:
        """Export WBS to JSON."""
        data = tree.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def to_excel(tree: WBSTree, filepath: str) -> None:
        """Export WBS to Excel with formatting."""
        if not HAS_OPENPYXL:
            raise ImportError("openpyxl is required for Excel export.")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "WBS"

        # Header
        headers = ["WBS Code", "Name", "Parent Code", "Duration (days)",
                    "Cost ($)", "Progress (%)", "Status", "Responsible", "Description"]
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border

        # Data
        code_map = {n.id: n.wbs_code for n in tree.nodes}

        # Status colour fills
        status_fills = {
            "Not Started": PatternFill(start_color="E0E0E0", fill_type="solid"),
            "In Progress": PatternFill(start_color="CCE5FF", fill_type="solid"),
            "Completed":   PatternFill(start_color="D4EDDA", fill_type="solid"),
            "Delayed":     PatternFill(start_color="F8D7DA", fill_type="solid"),
            "On Hold":     PatternFill(start_color="FFF3CD", fill_type="solid"),
        }

        for row_idx, node in enumerate(sorted(tree.nodes, key=lambda n: n.wbs_code), 2):
            parent_code = code_map.get(node.parent_id, "")
            values = [
                node.wbs_code, node.name, parent_code,
                node.duration, node.cost, node.progress,
                node.status.value, node.responsible, node.description
            ]
            for col, val in enumerate(values, 1):
                cell = ws.cell(row=row_idx, column=col, value=val)
                cell.border = thin_border
                # Indent name based on depth
                if col == 2:
                    depth = node.wbs_code.count(".")
                    cell.alignment = Alignment(indent=depth)
                # Colour status column
                if col == 7:
                    fill = status_fills.get(str(val))
                    if fill:
                        cell.fill = fill

        # Auto-width
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[chr(64 + col) if col <= 26 else 'A'].width = 18

        wb.save(filepath)

    @staticmethod
    def to_image(tree: WBSTree, filepath: str, dpi: int = 150) -> None:
        """Export WBS diagram as PNG or PDF using Matplotlib."""
        if not HAS_MATPLOTLIB:
            raise ImportError("Matplotlib is required for image export.")

        from pmhelper.utils.wbs_layout_edu import WBSLayoutEngine, NodeLayout

        engine = WBSLayoutEngine(node_width=140, node_height=50, h_gap=20, v_gap=60)
        layouts = engine.compute(tree)

        if not layouts:
            return

        min_x, min_y, max_x, max_y = engine.get_bounds()
        fig_w = max((max_x - min_x + 60) / 72, 8)
        fig_h = max((max_y - min_y + 60) / 72, 4)
        fig = Figure(figsize=(fig_w, fig_h))
        ax = fig.add_subplot(111)
        ax.set_xlim(min_x - 20, max_x + 20)
        ax.set_ylim(max_y + 20, min_y - 20)  # invert y for top-down
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(tree.project_name, fontsize=14, fontweight="bold")

        # Draw edges
        for node in tree.nodes:
            if node.parent_id and node.parent_id in layouts:
                parent_layout = layouts[node.parent_id]
                child_layout = layouts[node.id]
                px = parent_layout.x + parent_layout.width / 2
                py = parent_layout.y + parent_layout.height
                cx = child_layout.x + child_layout.width / 2
                cy = child_layout.y
                # Elbow connector
                mid_y = (py + cy) / 2
                ax.plot([px, px, cx, cx], [py, mid_y, mid_y, cy],
                        color="#666666", linewidth=1.2)

        # Draw nodes
        for node in tree.nodes:
            if node.id not in layouts:
                continue
            layout = layouts[node.id]
            colour = WBS_STATUS_COLOURS.get(node.status, "#e0e0e0")

            rect = FancyBboxPatch(
                (layout.x, layout.y), layout.width, layout.height,
                boxstyle="round,pad=3",
                facecolor=colour, edgecolor="#333333", linewidth=1.2,
            )
            ax.add_patch(rect)

            # Text
            cx = layout.x + layout.width / 2
            cy_code = layout.y + layout.height * 0.3
            cy_name = layout.y + layout.height * 0.65

            ax.text(cx, cy_code, node.wbs_code, ha="center", va="center",
                    fontsize=7, fontweight="bold", color="#333")
            name_display = node.name[:16] + "..." if len(node.name) > 16 else node.name
            ax.text(cx, cy_name, name_display, ha="center", va="center",
                    fontsize=7, color="#333")

        fig.tight_layout()
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
