"""
PMhelper Edu — WBS Tab (PG-only).
Interactive Canvas-based WBS diagram with tree editor,
expand/collapse, reparent, CRUD, CSV import, and export.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

from pmhelper.core.wbs_models_edu import WBSTree, WBSNode, WBSStatus, WBS_STATUS_COLOURS
from pmhelper.core.wbs_validator_edu import WBSValidator
from pmhelper.utils.wbs_builder_edu import WBSBuilder, WBSAggregator
from pmhelper.utils.wbs_layout_edu import WBSLayoutEngine, NodeLayout
from pmhelper.utils.wbs_export_edu import WBSExporter
from pmhelper.gui.widgets.sortable_treeview import enhance_treeview


class WBSTabEdu:
    """WBS tab with Canvas diagram and tree-list editor."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)

        if not hasattr(self.state, 'wbs_tree') or self.state.wbs_tree is None:
            self.state.wbs_tree = WBSBuilder.create_default_tree("Project")

        self._engine = WBSLayoutEngine()
        self._layouts: dict[str, NodeLayout] = {}
        self._collapsed: set[str] = set()      # IDs of collapsed nodes
        self._selected_id: str = ""
        # node_id → canvas item id
        self._canvas_node_rects: dict[str, int] = {}
        self._drag_data: dict = {}
        self._view_mode: str = "interactive"  # B3: "interactive" | "horizontal"

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(
            toolbar,
            text="WBS Diagram",
            font=(
                "TkDefaultFont",
                11,
                "bold")).pack(
            side=tk.LEFT)

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="📂 Load Demo",
            command=self._load_demo).pack(
            side=tk.LEFT,
            padx=2)

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="Add Child",
            command=self._add_child).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Add Sibling",
            command=self._add_sibling).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Edit Node",
            command=self._edit_node).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Delete Node",
            command=self._delete_node).pack(
            side=tk.LEFT,
            padx=2)

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="Undo",
            command=self._undo).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Redo",
            command=self._redo).pack(
            side=tk.LEFT,
            padx=2)

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="Import CSV",
            command=self._import_csv).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Validate",
            command=self._validate).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Aggregate",
            command=self._aggregate).pack(
            side=tk.LEFT,
            padx=2)

        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="Export PNG",
            command=self._export_png).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export CSV",
            command=self._export_csv).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export Excel",
            command=self._export_excel).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="🌐 Interactive View",
            command=self._open_interactive_view).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        # B3: Horizontal Tree / Interactive View toggle
        self._view_toggle_btn = ttk.Button(toolbar, text="🌿 Horizontal Tree",
                                           command=self._toggle_view_mode)
        self._view_toggle_btn.pack(side=tk.LEFT, padx=2)

        # Cost controls
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        self._cost_toggle_btn = ttk.Button(toolbar, text="💰 Show Costs",
                                           command=self._toggle_cost_column)
        self._cost_toggle_btn.pack(side=tk.LEFT, padx=2)
        self._cost_visible = True

        self._load_costs_btn = ttk.Button(
            toolbar,
            text="Load Costs from Estimation",
            command=self._load_costs_from_estimation)
        self._load_costs_btn.pack(side=tk.LEFT, padx=2)

        # Main area: PanedWindow with tree list (left) + canvas (right)
        pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: tree list
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        cols = ("wbs", "name", "dur", "cost", "prog", "status")
        self._tree_view = ttk.Treeview(
            left,
            columns=cols,
            show="tree headings",
            selectmode="browse")
        self._tree_view.heading("#0", text="")
        self._tree_view.heading("wbs", text="WBS")
        self._tree_view.heading("name", text="Name")
        self._tree_view.heading("dur", text="Dur")
        self._tree_view.heading("cost", text="Cost")
        self._tree_view.heading("prog", text="Prog%")
        self._tree_view.heading("status", text="Status")

        self._tree_view.column("#0", width=30)
        self._tree_view.column("wbs", width=60)
        self._tree_view.column("name", width=120)
        self._tree_view.column("dur", width=40, anchor=tk.E)
        self._tree_view.column("cost", width=60, anchor=tk.E)
        self._tree_view.column("prog", width=40, anchor=tk.E)
        self._tree_view.column("status", width=80, anchor=tk.CENTER)

        sb = ttk.Scrollbar(
            left,
            orient=tk.VERTICAL,
            command=self._tree_view.yview)
        self._tree_view.configure(yscrollcommand=sb.set)
        self._tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        enhance_treeview(self._tree_view)

        self._tree_view.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._tree_view.bind("<Button-3>", self._on_tree_right_click)

        # Right: Canvas for WBS diagram
        right = ttk.Frame(pane)
        pane.add(right, weight=3)

        self._canvas = tk.Canvas(right, bg="white", highlightthickness=0)
        h_scroll = ttk.Scrollbar(
            right,
            orient=tk.HORIZONTAL,
            command=self._canvas.xview)
        v_scroll = ttk.Scrollbar(
            right,
            orient=tk.VERTICAL,
            command=self._canvas.yview)
        self._canvas.configure(
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # Canvas events
        self._canvas.bind("<Button-1>", self._on_canvas_click)
        self._canvas.bind("<Double-Button-1>", self._on_canvas_dblclick)

        # Footer
        self._footer_var = tk.StringVar(value="Nodes: 0")
        ttk.Label(
            self.frame,
            textvariable=self._footer_var,
            font=(
                "TkDefaultFont",
                9,
                "italic")).pack(
            fill=tk.X,
            padx=5,
            pady=(
                0,
                5))

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def on_tab_selected(self):
        self._refresh_all()

    def _refresh_all(self):
        tree = self.state.wbs_tree
        if tree is None:
            tree = WBSBuilder.create_default_tree("Project")
            self.state.wbs_tree = tree

        tree.regenerate_codes()
        self._refresh_tree_list(tree)
        self._refresh_canvas(tree)

        n = tree.node_count()
        self._footer_var.set(f"Nodes: {n}")

    def _refresh_tree_list(self, tree: WBSTree):
        """Refresh the left-hand Treeview list."""
        self._tree_view.delete(*self._tree_view.get_children())
        # Insert nodes recursively
        self._insert_tree_children(tree, "", "")

    def _insert_tree_children(
            self,
            tree: WBSTree,
            parent_id: str,
            treeview_parent: str):
        """Recursively insert children into the Treeview."""
        children = tree.get_children(parent_id)
        for node in children:
            iid = self._tree_view.insert(
                treeview_parent, tk.END,
                iid=node.id,
                text="",
                values=(
                    node.wbs_code,
                    node.name,
                    f"{node.duration:.0f}",
                    f"${node.cost:,.0f}",
                    f"{node.progress:.0f}%",
                    node.status.value,
                ),
                open=node.id not in self._collapsed,
            )
            self._insert_tree_children(tree, node.id, iid)

    def _refresh_canvas(self, tree: WBSTree):
        """Recompute layout and redraw the canvas."""
        # B3: dispatch to horizontal renderer
        if getattr(self, '_view_mode', 'interactive') == 'horizontal':
            self._refresh_canvas_horizontal(tree)
            return

        self._canvas.delete("all")
        self._canvas_node_rects.clear()

        if tree.node_count() == 0:
            return

        # Build a filtered tree excluding collapsed subtrees' children
        visible_tree = self._build_visible_tree(tree)
        self._layouts = self._engine.compute(visible_tree)

        if not self._layouts:
            return

        min_x, min_y, max_x, max_y = self._engine.get_bounds()
        padding = 40
        self._canvas.configure(scrollregion=(
            min_x - padding, min_y - padding,
            max_x + padding, max_y + padding
        ))

        # Draw edges
        for node in visible_tree.nodes:
            if node.parent_id and node.parent_id in self._layouts and node.id in self._layouts:
                pl = self._layouts[node.parent_id]
                cl = self._layouts[node.id]
                px = pl.x + pl.width / 2
                py = pl.y + pl.height
                cx = cl.x + cl.width / 2
                cy = cl.y
                mid_y = (py + cy) / 2
                self._canvas.create_line(px, py, px, mid_y, cx, mid_y, cx, cy,
                                         fill="#888888", width=1.5)

        # Draw nodes
        for node in visible_tree.nodes:
            if node.id not in self._layouts:
                continue
            layout = self._layouts[node.id]
            colour = WBS_STATUS_COLOURS.get(node.status, "#e0e0e0")
            outline = "#0066cc" if node.id == self._selected_id else "#333333"
            width_ = 3 if node.id == self._selected_id else 1.5

            rect_id = self._canvas.create_rectangle(
                layout.x, layout.y,
                layout.x + layout.width, layout.y + layout.height,
                fill=colour, outline=outline, width=width_,
                tags=("node", node.id),
            )
            self._canvas_node_rects[node.id] = rect_id

            # WBS code (top)
            self._canvas.create_text(
                layout.x + layout.width / 2,
                layout.y + 14,
                text=node.wbs_code, font=("TkDefaultFont", 8, "bold"),
                fill="#333", tags=("node", node.id),
            )

            # Name (bottom)
            name = node.name[:16] + "..." if len(node.name) > 16 else node.name
            self._canvas.create_text(
                layout.x + layout.width / 2,
                layout.y + 32,
                text=name, font=("TkDefaultFont", 8),
                fill="#333", tags=("node", node.id),
            )

            # Expand/collapse indicator
            actual_children = tree.get_children(node.id)
            if actual_children:
                indicator = "−" if node.id not in self._collapsed else "+"
                self._canvas.create_text(
                    layout.x + layout.width - 10,
                    layout.y + 10,
                    text=indicator, font=("TkDefaultFont", 10, "bold"),
                    fill="#0066cc", tags=("toggle", node.id),
                )

    # ------------------------------------------------------------------
    # B3: View toggle — Horizontal Tree
    # ------------------------------------------------------------------

    def _toggle_view_mode(self):
        """Switch between top-down (interactive) and left-to-right (horizontal) canvas."""
        if self._view_mode == "interactive":
            self._view_mode = "horizontal"
            self._view_toggle_btn.config(text="📐 Interactive View")
        else:
            self._view_mode = "interactive"
            self._view_toggle_btn.config(text="🌿 Horizontal Tree")
        self._refresh_canvas(self.state.wbs_tree)

    def _refresh_canvas_horizontal(self, tree: WBSTree):
        """Left-to-right tree canvas: WBS code, Name, Duration, Cost, Progress bar."""
        self._canvas.delete("all")
        self._canvas_node_rects.clear()

        if tree.node_count() == 0:
            return

        visible_tree = self._build_visible_tree(tree)
        if not visible_tree.nodes:
            return

        NODE_W, NODE_H = 172, 88
        H_GAP, V_UNIT, PAD = 52, 108, 22

        # --- vertical span (leaf-count) per subtree ---
        def _span(nid):
            ch = visible_tree.get_children(nid)
            return max(sum(_span(c.id) for c in ch), 1)

        # --- recursively assign top-left (x, y) ---
        node_pos: dict[str, tuple[float, float]] = {}

        def _place(nid, x, y_top, y_bot):
            cy = (y_top + y_bot) / 2
            node_pos[nid] = (x, cy - NODE_H / 2)
            children = visible_tree.get_children(nid)
            if not children:
                return
            spans = [_span(c.id) for c in children]
            total = sum(spans)
            cur = y_top
            for child, sp in zip(children, spans):
                share = (y_bot - y_top) * sp / total
                _place(child.id, x + NODE_W + H_GAP, cur, cur + share)
                cur += share

        roots = visible_tree.get_roots()
        root_spans = [_span(r.id) for r in roots]
        total_h = sum(root_spans) * V_UNIT
        cur_y = PAD
        for root, sp in zip(roots, root_spans):
            share = total_h * sp / sum(root_spans)
            _place(root.id, PAD, cur_y, cur_y + share)
            cur_y += share

        # --- edges ---
        for node in visible_tree.nodes:
            if node.parent_id in node_pos and node.id in node_pos:
                px, py = node_pos[node.parent_id]
                cx, cy = node_pos[node.id]
                p_rx = px + NODE_W
                p_my = py + NODE_H / 2
                c_lx = cx
                c_my = cy + NODE_H / 2
                mid_x = (p_rx + c_lx) / 2
                self._canvas.create_line(
                    p_rx, p_my, mid_x, p_my, mid_x, c_my, c_lx, c_my,
                    fill="#888888", width=1.5)

        # --- nodes ---
        for node in visible_tree.nodes:
            if node.id not in node_pos:
                continue
            nx, ny = node_pos[node.id]
            colour = WBS_STATUS_COLOURS.get(node.status, "#e0e0e0")
            outline = "#0066cc" if node.id == self._selected_id else "#555555"
            lw = 2.5 if node.id == self._selected_id else 1.5

            rect_id = self._canvas.create_rectangle(
                nx, ny, nx + NODE_W, ny + NODE_H,
                fill=colour, outline=outline, width=lw,
                tags=("node", node.id))
            self._canvas_node_rects[node.id] = rect_id

            # WBS code (top-left, bold)
            self._canvas.create_text(
                nx + 8, ny + 13, anchor=tk.W,
                text=node.wbs_code or "",
                font=("TkDefaultFont", 8, "bold"), fill="#333",
                tags=("node", node.id))

            # Name (centred)
            name = node.name[:23] + "…" if len(node.name) > 23 else node.name
            self._canvas.create_text(
                nx + NODE_W / 2, ny + 31, anchor=tk.CENTER,
                text=name,
                font=("TkDefaultFont", 9), fill="#111",
                tags=("node", node.id))

            # Duration | Cost
            dur_txt = f"{node.duration:.0f}d"
            cost_txt = f"${node.cost:,.0f}" if node.cost else "\u2014"
            self._canvas.create_text(
                nx + NODE_W / 2, ny + 50, anchor=tk.CENTER,
                text=f"{dur_txt}  \u2502  {cost_txt}",
                font=("TkDefaultFont", 8), fill="#444",
                tags=("node", node.id))

            # Progress bar (nx+8 … nx+NODE_W-8)
            bx0, by0 = nx + 8, ny + 64
            bx1, by1 = nx + NODE_W - 8, ny + 74
            bw = bx1 - bx0
            self._canvas.create_rectangle(
                bx0, by0, bx1, by1, fill="#e0e0e0", outline="#bbb")
            fill_x = bx0 + bw * min(max(node.progress, 0), 100) / 100
            if fill_x > bx0:
                self._canvas.create_rectangle(
                    bx0, by0, fill_x, by1, fill="#4caf50", outline="")
            self._canvas.create_text(
                bx1 + 2, (by0 + by1) / 2, anchor=tk.W,
                text=f"{node.progress:.0f}%",
                font=("TkDefaultFont", 7), fill="#333",
                tags=("node", node.id))

            # Expand/collapse indicator
            if tree.get_children(node.id):
                ind = "−" if node.id not in self._collapsed else "+"
                self._canvas.create_text(
                    nx + NODE_W - 8, ny + 13, anchor=tk.CENTER,
                    text=ind,
                    font=("TkDefaultFont", 10, "bold"), fill="#0066cc",
                    tags=("toggle", node.id))

        # update scroll region
        if node_pos:
            xs = [p[0] for p in node_pos.values()]
            ys = [p[1] for p in node_pos.values()]
            self._canvas.configure(scrollregion=(
                min(xs) - PAD, min(ys) - PAD,
                max(xs) + NODE_W + PAD, max(ys) + NODE_H + PAD))

    def _build_visible_tree(self, tree: WBSTree) -> WBSTree:
        """Build a tree with only visible nodes (not under collapsed parents)."""
        visible = WBSTree(project_name=tree.project_name)
        hidden_parents: set[str] = set()

        # BFS to find visible nodes
        def _add_visible(parent_id: str):
            if parent_id in hidden_parents:
                return
            children = tree.get_children(parent_id)
            for child in children:
                visible.nodes.append(child)
                if child.id in self._collapsed:
                    hidden_parents.add(child.id)
                else:
                    _add_visible(child.id)

        # Add roots
        for root in tree.get_roots():
            visible.nodes.append(root)
            if root.id not in self._collapsed:
                _add_visible(root.id)

        return visible

    # ------------------------------------------------------------------
    # Canvas events
    # ------------------------------------------------------------------

    def _on_canvas_click(self, event):
        """Select a node on click."""
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)

        items = self._canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
        for item in items:
            tags = self._canvas.gettags(item)
            if "toggle" in tags:
                # Toggle expand/collapse
                node_id = tags[1] if len(tags) > 1 else ""
                if node_id:
                    if node_id in self._collapsed:
                        self._collapsed.discard(node_id)
                    else:
                        self._collapsed.add(node_id)
                    self._refresh_all()
                return
            if "node" in tags:
                node_id = tags[1] if len(tags) > 1 else ""
                if node_id:
                    self._selected_id = node_id
                    self._refresh_all()
                    # Also select in treeview
                    try:
                        self._tree_view.selection_set(node_id)
                        self._tree_view.see(node_id)
                    except tk.TclError:
                        pass
                return

    def _on_canvas_dblclick(self, event):
        """Edit node on double click."""
        x = self._canvas.canvasx(event.x)
        y = self._canvas.canvasy(event.y)
        items = self._canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
        for item in items:
            tags = self._canvas.gettags(item)
            if "node" in tags:
                node_id = tags[1] if len(tags) > 1 else ""
                if node_id:
                    self._selected_id = node_id
                    self._edit_node()
                return

    def _on_tree_select(self, event):
        sel = self._tree_view.selection()
        if sel:
            self._selected_id = sel[0]
            self._refresh_canvas(self.state.wbs_tree)

    def _on_tree_right_click(self, event):
        """Show context menu on right-click."""
        item = self._tree_view.identify_row(event.y)
        if not item:
            return
        self._tree_view.selection_set(item)
        self._selected_id = item
        menu = tk.Menu(self._tree_view, tearoff=0)
        menu.add_command(label="Add Child", command=self._add_child)
        menu.add_command(label="Edit Node", command=self._edit_node)
        menu.add_command(label="Delete Node", command=self._delete_node)
        menu.add_separator()
        menu.add_command(
            label="Allocate Budget to Children",
            command=self._allocate_budget)
        menu.tk_popup(event.x_root, event.y_root)

    # ------------------------------------------------------------------
    # Mode, Cost Toggle, Load Costs
    # ------------------------------------------------------------------

    def set_mode(self, mode: str):
        """Toggle UG/PG mode."""
        self._mode = mode.upper()

    def _toggle_cost_column(self):
        """Show/hide the cost column."""
        if self._cost_visible:
            self._tree_view.column("cost", width=0, minwidth=0)
            self._cost_toggle_btn.configure(text="💰 Show Costs")
            self._cost_visible = False
        else:
            self._tree_view.column("cost", width=60, minwidth=40)
            self._cost_toggle_btn.configure(text="💰 Hide Costs")
            self._cost_visible = True

    def _update_cost_toggle_state(self):
        """Gray out cost toggle if no node has cost > 0."""
        tree = self.state.wbs_tree
        has_costs = any(n.cost > 0 for n in tree.nodes) if tree else False
        self._cost_toggle_btn.configure(
            state="normal" if has_costs else "disabled")

    def _load_costs_from_estimation(self):
        """Load cost estimates from the Cost Estimation tab into WBS leaf nodes."""
        mw = getattr(self, 'main_window', None)
        if not mw:
            messagebox.showinfo("Load Costs",
                                "Main window reference not available.")
            return
        # Find the cost estimation tab
        ce_tab = None
        for tab in getattr(mw, '_tabs', {}).values():
            if hasattr(tab, '_results') and hasattr(tab, '_mode'):
                ce_tab = tab
                break
        if ce_tab is None or not ce_tab._results:
            messagebox.showinfo(
                "Load Costs",
                "No cost estimation results found.\n"
                "Run a cost estimation first.")
            return
        # Pick the first result that has per-item data
        tree = self.state.wbs_tree
        loaded = 0
        for key, result in ce_tab._results.items():
            items = getattr(
                result,
                'items',
                None) or getattr(
                result,
                'line_items',
                [])
            if not items:
                continue
            for item in items:
                name = getattr(
                    item,
                    'name',
                    '') or item.get(
                    'name',
                    '') if isinstance(
                    item,
                    dict) else ''
                cost = getattr(
                    item,
                    'total',
                    0) or (
                    item.get(
                        'total',
                        0) if isinstance(
                        item,
                        dict) else 0)
                if not name or not cost:
                    continue
                # Match by name to WBS leaf nodes
                for node in tree.nodes:
                    if node.name.lower() == name.lower() and not tree.get_children(node.id):
                        node.cost = float(cost)
                        loaded += 1
                        break
        if loaded:
            self._refresh_all()
            self._update_cost_toggle_state()
            messagebox.showinfo("Load Costs",
                                f"Updated costs for {loaded} node(s).")
        else:
            messagebox.showinfo(
                "Load Costs",
                "No matching WBS leaf nodes found.")

    def _allocate_budget(self):
        """Allocate selected node's budget equally among zero-cost children."""
        node_id = self._selected_id
        tree = self.state.wbs_tree
        if not node_id or not tree:
            return
        node = tree.get_node(node_id)
        if not node:
            return
        children = tree.get_children(node_id)
        if not children:
            messagebox.showinfo("Allocate", "No children to allocate to.")
            return
        if node.cost <= 0:
            messagebox.showinfo("Allocate",
                                "Parent node has no budget to allocate.")
            return
        # Sum existing child costs
        existing = sum(c.cost for c in children)
        remaining = node.cost - existing
        if remaining <= 0:
            messagebox.showinfo(
                "Allocate",
                "No remaining budget to allocate.\n" f"Children already total ${
                    existing:,.0f} " f"against parent ${
                    node.cost:,.0f}.")
            return
        # Find zero-cost children
        zero_kids = [c for c in children if c.cost <= 0]
        if not zero_kids:
            messagebox.showinfo("Allocate",
                                "All children already have costs assigned.")
            return
        share = remaining / len(zero_kids)
        for c in zero_kids:
            c.cost = share
        self._refresh_all()
        self._update_cost_toggle_state()
        messagebox.showinfo(
            "Allocate", f"${
                remaining:,.0f} split equally among {
                len(zero_kids)} children " f"(${
                share:,.0f} each).")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def _add_child(self):
        parent_id = self._selected_id
        if not parent_id:
            roots = self.state.wbs_tree.get_roots()
            parent_id = roots[0].id if roots else ""
        if not parent_id:
            messagebox.showinfo("WBS", "No node selected.")
            return

        dialog = _WBSNodeDialog(self.frame, "Add Child Node")
        if dialog.result:
            node = dialog.result
            node.parent_id = parent_id
            self.state.wbs_tree.add_node(node)
            self.state.wbs_tree.regenerate_codes()
            self._collapsed.discard(parent_id)  # expand parent
            self.state.mark_dirty()
            self._refresh_all()

    def _add_sibling(self):
        if not self._selected_id:
            messagebox.showinfo("WBS", "No node selected.")
            return
        node = self.state.wbs_tree.get_node(self._selected_id)
        if node is None:
            return

        dialog = _WBSNodeDialog(self.frame, "Add Sibling Node")
        if dialog.result:
            new_node = dialog.result
            new_node.parent_id = node.parent_id
            self.state.wbs_tree.add_node(new_node)
            self.state.wbs_tree.regenerate_codes()
            self.state.mark_dirty()
            self._refresh_all()

    def _edit_node(self):
        if not self._selected_id:
            messagebox.showinfo("WBS", "No node selected.")
            return
        node = self.state.wbs_tree.get_node(self._selected_id)
        if node is None:
            return

        dialog = _WBSNodeDialog(self.frame, "Edit Node", node)
        if dialog.result:
            edited = dialog.result
            node.name = edited.name
            node.duration = edited.duration
            node.cost = edited.cost
            node.progress = edited.progress
            node.status = edited.status
            node.responsible = edited.responsible
            node.description = edited.description
            self.state.mark_dirty()
            self._refresh_all()

    def _delete_node(self):
        if not self._selected_id:
            messagebox.showinfo("WBS", "No node selected.")
            return
        node = self.state.wbs_tree.get_node(self._selected_id)
        if node is None:
            return

        children = self.state.wbs_tree.get_children(self._selected_id)
        if children:
            answer = messagebox.askyesnocancel(
                "Delete Node",
                f"Node '{node.name}' has {len(children)} children.\n\n"
                f"Yes = Delete children too (cascade)\n"
                f"No = Promote children to parent\n"
                f"Cancel = Abort"
            )
            if answer is None:
                return
            cascade = answer
        else:
            if not messagebox.askyesno(
                "Delete Node", f"Delete '{
                    node.name}'?"):
                return
            cascade = True

        self.state.wbs_tree.delete_node(self._selected_id, cascade=cascade)
        self.state.wbs_tree.regenerate_codes()
        self._selected_id = ""
        self.state.mark_dirty()
        self._refresh_all()

    def _undo(self):
        if self.state.wbs_tree.undo():
            self.state.wbs_tree.regenerate_codes()
            self._refresh_all()
        else:
            messagebox.showinfo("WBS", "Nothing to undo.")

    def _redo(self):
        if self.state.wbs_tree.redo():
            self.state.wbs_tree.regenerate_codes()
            self._refresh_all()
        else:
            messagebox.showinfo("WBS", "Nothing to redo.")

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def _load_demo(self):
        """Load the WBS demo project from wbs_demo.json."""
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..", "data", "demos", "v2", "wbs_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "wbs_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror(
                "Load Demo", f"Demo file not found:\n{demo_path}")
            return

        try:
            with open(demo_path, encoding="utf-8") as fh:
                demo = json.load(fh)
            tree = WBSTree.from_dict(demo)
            WBSAggregator.aggregate(tree)
            self.state.wbs_tree = tree
            self._collapsed.clear()
            self._refresh_all()
            messagebox.showinfo(
                "Load Demo",
                f"Loaded: {demo.get('name', 'WBS Demo')}\n\n"
                f"{demo.get('description', '')}")
        except Exception as exc:
            messagebox.showerror("Load Demo", f"Error loading demo:\n{exc}")

    def _import_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv")],
            title="Import WBS from CSV",
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = WBSBuilder.import_csv(
                    f, project_name=os.path.splitext(
                        os.path.basename(path))[0])
            WBSAggregator.aggregate(tree)
            self.state.wbs_tree = tree
            self._collapsed.clear()
            self._selected_id = ""
            self.state.mark_dirty()
            self._refresh_all()
            messagebox.showinfo(
                "WBS", f"Imported {
                    tree.node_count()} nodes from {
                    os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    # ------------------------------------------------------------------
    # Validate & Aggregate
    # ------------------------------------------------------------------

    def _validate(self):
        tree = self.state.wbs_tree
        errors = WBSValidator.validate(tree)
        if not errors:
            messagebox.showinfo("WBS Validation", "No issues found.")
        else:
            msg = "\n".join(str(e) for e in errors[:15])
            if len(errors) > 15:
                msg += f"\n... and {len(errors) - 15} more"
            messagebox.showwarning("WBS Validation", msg)

    def _aggregate(self):
        WBSAggregator.aggregate(self.state.wbs_tree)
        self.state.mark_dirty()
        self._refresh_all()
        messagebox.showinfo(
            "WBS", "Aggregation complete (duration, cost, progress, status).")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export_png(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")],
            title="Export WBS Diagram",
        )
        if not path:
            return
        try:
            WBSExporter.to_image(self.state.wbs_tree, path)
            messagebox.showinfo("Export", f"Saved to {os.path.basename(path)}")
        except ImportError as e:
            messagebox.showerror("Export", str(e))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export WBS to CSV",
        )
        if not path:
            return
        WBSExporter.to_csv(self.state.wbs_tree, path)
        messagebox.showinfo("Export", f"Saved to {os.path.basename(path)}")

    def _export_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Export WBS to Excel",
        )
        if not path:
            return
        try:
            WBSExporter.to_excel(self.state.wbs_tree, path)
            messagebox.showinfo("Export", f"Saved to {os.path.basename(path)}")
        except ImportError as e:
            messagebox.showerror("Export", str(e))

    def _open_interactive_view(self):
        """Open an interactive Plotly Sunburst view of the WBS in the browser."""
        tree = self.state.wbs_tree
        if not tree or not tree.nodes:
            messagebox.showwarning("WBS", "No WBS data to display.")
            return
        try:
            import plotly.graph_objects as go
        except ImportError:
            messagebox.showerror(
                "WBS", "Plotly is required for interactive view.\npip install plotly")
            return

        ids, labels, parents, values, colors = [], [], [], [], []
        for node in tree.nodes:
            ids.append(node.id)
            label = f"{
                node.wbs_code}<br>{
                node.name}" if node.wbs_code else node.name
            labels.append(label)
            parents.append(node.parent_id if node.parent_id else "")
            values.append(max(node.cost, 1))
            colors.append(WBS_STATUS_COLOURS.get(node.status, "#e0e0e0"))

        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            branchvalues="total",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Cost: $%{value:,.0f}<br>"
                "<extra></extra>"
            ),
        ))
        fig.update_layout(
            title=dict(text=f"WBS — {tree.project_name}", font=dict(size=18)),
            margin=dict(t=50, l=10, r=10, b=10),
        )

        import tempfile
        from pmhelper.utils.interactive_network import _open_in_browser
        tmp = tempfile.NamedTemporaryFile(
            suffix='.html',
            prefix='pmhelper_wbs_',
            delete=False,
            mode='w',
            encoding='utf-8')
        tmp.close()
        fig.write_html(
            tmp.name,
            include_plotlyjs='cdn',
            full_html=True,
            auto_open=False)
        _open_in_browser(tmp.name)


class _WBSNodeDialog(tk.Toplevel):
    """Dialog for adding/editing a WBS node."""

    def __init__(self, parent, title: str, existing: WBSNode | None = None):
        super().__init__(parent)
        self.title(title)
        self.result: WBSNode | None = None
        self.resizable(False, False)
        self.grab_set()

        row = 0

        # Name
        ttk.Label(
            self,
            text="Name:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._name_var = tk.StringVar(value=existing.name if existing else "")
        ttk.Entry(
            self,
            textvariable=self._name_var,
            width=35).grid(
            row=row,
            column=1,
            padx=8,
            pady=4)
        row += 1

        # Duration
        ttk.Label(
            self,
            text="Duration (days):").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._dur_var = tk.StringVar(
            value=str(existing.duration) if existing else "0")
        ttk.Entry(
            self,
            textvariable=self._dur_var,
            width=10).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Cost
        ttk.Label(
            self,
            text="Cost ($):").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._cost_var = tk.StringVar(
            value=str(existing.cost) if existing else "0")
        ttk.Entry(
            self,
            textvariable=self._cost_var,
            width=10).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Progress
        ttk.Label(
            self,
            text="Progress (%):").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._prog_var = tk.StringVar(
            value=str(existing.progress) if existing else "0")
        ttk.Entry(
            self,
            textvariable=self._prog_var,
            width=10).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Status
        ttk.Label(
            self,
            text="Status:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._status_var = tk.StringVar(
            value=existing.status.value if existing else "Not Started")
        ttk.Combobox(
            self,
            textvariable=self._status_var,
            values=[
                s.value for s in WBSStatus],
            state="readonly",
            width=15).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Responsible
        ttk.Label(
            self,
            text="Responsible:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._resp_var = tk.StringVar(
            value=existing.responsible if existing else "")
        ttk.Entry(
            self,
            textvariable=self._resp_var,
            width=25).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Description
        ttk.Label(
            self,
            text="Description:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._desc_var = tk.StringVar(
            value=existing.description if existing else "")
        ttk.Entry(
            self,
            textvariable=self._desc_var,
            width=35).grid(
            row=row,
            column=1,
            padx=8,
            pady=4)
        row += 1

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=8)
        ttk.Button(
            btn_frame,
            text="OK",
            command=self._on_ok).pack(
            side=tk.LEFT,
            padx=4)
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy).pack(
            side=tk.LEFT,
            padx=4)

        self.wait_window()

    def _on_ok(self):
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.", parent=self)
            return
        try:
            dur = float(self._dur_var.get())
            if dur < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Duration must be non-negative.",
                parent=self)
            return
        try:
            cost = float(self._cost_var.get())
            if cost < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Cost must be non-negative.",
                parent=self)
            return
        try:
            prog = float(self._prog_var.get())
            if not 0 <= prog <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Progress must be 0-100.", parent=self)
            return

        self.result = WBSNode(
            name=name,
            duration=dur,
            cost=cost,
            progress=prog,
            status=WBSStatus(self._status_var.get()),
            responsible=self._resp_var.get().strip(),
            description=self._desc_var.get().strip(),
        )
        self.destroy()
