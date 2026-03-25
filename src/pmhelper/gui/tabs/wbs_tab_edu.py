"""
PMhelper Edu — WBS Tab (PG-only).
Interactive Canvas-based WBS diagram with tree editor,
expand/collapse, reparent, CRUD, CSV import, and export.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from pmhelper.core.wbs_models_edu import WBSTree, WBSNode, WBSStatus, WBS_STATUS_COLOURS
from pmhelper.core.wbs_validator_edu import WBSValidator
from pmhelper.utils.wbs_builder_edu import WBSBuilder, WBSAggregator
from pmhelper.utils.wbs_layout_edu import WBSLayoutEngine, NodeLayout
from pmhelper.utils.wbs_export_edu import WBSExporter


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
        self._canvas_node_rects: dict[str, int] = {}   # node_id → canvas item id
        self._drag_data: dict = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(toolbar, text="WBS Diagram", font=("TkDefaultFont", 11, "bold")).pack(side=tk.LEFT)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Add Child", command=self._add_child).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Sibling", command=self._add_sibling).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Node", command=self._edit_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Node", command=self._delete_node).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Undo", command=self._undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Redo", command=self._redo).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Import CSV", command=self._import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Validate", command=self._validate).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Aggregate", command=self._aggregate).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Export PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export Excel", command=self._export_excel).pack(side=tk.LEFT, padx=2)

        # Main area: PanedWindow with tree list (left) + canvas (right)
        pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: tree list
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        cols = ("wbs", "name", "dur", "cost", "prog", "status")
        self._tree_view = ttk.Treeview(left, columns=cols, show="tree headings",
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

        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree_view.yview)
        self._tree_view.configure(yscrollcommand=sb.set)
        self._tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree_view.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right: Canvas for WBS diagram
        right = ttk.Frame(pane)
        pane.add(right, weight=3)

        self._canvas = tk.Canvas(right, bg="white", highlightthickness=0)
        h_scroll = ttk.Scrollbar(right, orient=tk.HORIZONTAL, command=self._canvas.xview)
        v_scroll = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

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
        ttk.Label(self.frame, textvariable=self._footer_var,
                  font=("TkDefaultFont", 9, "italic")).pack(fill=tk.X, padx=5, pady=(0, 5))

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

    def _insert_tree_children(self, tree: WBSTree, parent_id: str, treeview_parent: str):
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
            if not messagebox.askyesno("Delete Node", f"Delete '{node.name}'?"):
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

    def _import_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv")],
            title="Import WBS from CSV",
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = WBSBuilder.import_csv(f, project_name=os.path.splitext(os.path.basename(path))[0])
            WBSAggregator.aggregate(tree)
            self.state.wbs_tree = tree
            self._collapsed.clear()
            self._selected_id = ""
            self.state.mark_dirty()
            self._refresh_all()
            messagebox.showinfo("WBS", f"Imported {tree.node_count()} nodes from {os.path.basename(path)}")
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
        messagebox.showinfo("WBS", "Aggregation complete (duration, cost, progress, status).")

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
        ttk.Label(self, text="Name:").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._name_var = tk.StringVar(value=existing.name if existing else "")
        ttk.Entry(self, textvariable=self._name_var, width=35).grid(row=row, column=1, padx=8, pady=4)
        row += 1

        # Duration
        ttk.Label(self, text="Duration (days):").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._dur_var = tk.StringVar(value=str(existing.duration) if existing else "0")
        ttk.Entry(self, textvariable=self._dur_var, width=10).grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        row += 1

        # Cost
        ttk.Label(self, text="Cost ($):").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._cost_var = tk.StringVar(value=str(existing.cost) if existing else "0")
        ttk.Entry(self, textvariable=self._cost_var, width=10).grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        row += 1

        # Progress
        ttk.Label(self, text="Progress (%):").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._prog_var = tk.StringVar(value=str(existing.progress) if existing else "0")
        ttk.Entry(self, textvariable=self._prog_var, width=10).grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        row += 1

        # Status
        ttk.Label(self, text="Status:").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._status_var = tk.StringVar(value=existing.status.value if existing else "Not Started")
        ttk.Combobox(self, textvariable=self._status_var,
                     values=[s.value for s in WBSStatus],
                     state="readonly", width=15).grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        row += 1

        # Responsible
        ttk.Label(self, text="Responsible:").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._resp_var = tk.StringVar(value=existing.responsible if existing else "")
        ttk.Entry(self, textvariable=self._resp_var, width=25).grid(row=row, column=1, padx=8, pady=4, sticky=tk.W)
        row += 1

        # Description
        ttk.Label(self, text="Description:").grid(row=row, column=0, padx=8, pady=4, sticky=tk.W)
        self._desc_var = tk.StringVar(value=existing.description if existing else "")
        ttk.Entry(self, textvariable=self._desc_var, width=35).grid(row=row, column=1, padx=8, pady=4)
        row += 1

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)

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
            messagebox.showerror("Error", "Duration must be non-negative.", parent=self)
            return
        try:
            cost = float(self._cost_var.get())
            if cost < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cost must be non-negative.", parent=self)
            return
        try:
            prog = float(self._prog_var.get())
            if not 0 <= prog <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Progress must be 0-100.", parent=self)
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
