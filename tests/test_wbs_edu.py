"""
Tests for WBS — models, validator, builder, aggregator, layout.
"""

import pytest
from pmhelper.core.wbs_models_edu import WBSTree, WBSNode, WBSStatus
from pmhelper.core.wbs_validator_edu import WBSValidator
from pmhelper.utils.wbs_builder_edu import WBSBuilder, WBSAggregator
from pmhelper.utils.wbs_layout_edu import WBSLayoutEngine


# ---------------------------------------------------------------------------
# WBSNode tests
# ---------------------------------------------------------------------------

class TestWBSNode:
    def test_create_node(self):
        n = WBSNode(name="Design", wbs_code="1.1")
        assert n.name == "Design"
        assert n.wbs_code == "1.1"
        assert n.is_root is True  # no parent_id
        assert len(n.id) == 8

    def test_validate_ok(self):
        n = WBSNode(name="Task A", duration=5, cost=1000, progress=50)
        assert n.validate() == []

    def test_validate_no_name(self):
        n = WBSNode(name="", duration=5)
        errors = n.validate()
        assert len(errors) == 1

    def test_validate_negative_duration(self):
        n = WBSNode(name="X", duration=-1)
        errors = n.validate()
        assert any("duration" in e.lower() for e in errors)

    def test_validate_bad_progress(self):
        n = WBSNode(name="X", progress=150)
        errors = n.validate()
        assert any("progress" in e.lower() for e in errors)

    def test_to_from_dict(self):
        n = WBSNode(name="Build", wbs_code="1.2", duration=10,
                    cost=5000, progress=30, status=WBSStatus.IN_PROGRESS,
                    responsible="Alice", description="Build phase")
        d = n.to_dict()
        n2 = WBSNode.from_dict(d)
        assert n2.name == n.name
        assert n2.wbs_code == n.wbs_code
        assert n2.duration == n.duration
        assert n2.cost == n.cost
        assert n2.status == n.status
        assert n2.responsible == n.responsible


# ---------------------------------------------------------------------------
# WBSTree tests
# ---------------------------------------------------------------------------

class TestWBSTree:
    def _sample_tree(self) -> WBSTree:
        tree = WBSTree(project_name="Test")
        root = WBSNode(id="R", name="Project", wbs_code="1", parent_id="")
        c1 = WBSNode(id="C1", name="Phase 1", parent_id="R", cost=1000, duration=10)
        c2 = WBSNode(id="C2", name="Phase 2", parent_id="R", cost=2000, duration=15)
        c1a = WBSNode(id="C1A", name="Design", parent_id="C1", cost=500, duration=5)
        c1b = WBSNode(id="C1B", name="Build", parent_id="C1", cost=500, duration=8)
        tree.nodes = [root, c1, c2, c1a, c1b]
        tree.regenerate_codes()
        return tree

    def test_get_children(self):
        tree = self._sample_tree()
        children = tree.get_children("R")
        assert len(children) == 2

    def test_get_roots(self):
        tree = self._sample_tree()
        roots = tree.get_roots()
        assert len(roots) == 1
        assert roots[0].name == "Project"

    def test_is_leaf(self):
        tree = self._sample_tree()
        assert tree.is_leaf("C1A") is True
        assert tree.is_leaf("C1") is False
        assert tree.is_leaf("R") is False

    def test_get_depth(self):
        tree = self._sample_tree()
        assert tree.get_depth("R") == 0
        assert tree.get_depth("C1") == 1
        assert tree.get_depth("C1A") == 2

    def test_get_descendants(self):
        tree = self._sample_tree()
        desc = tree.get_descendants("R")
        assert len(desc) == 4  # C1, C2, C1A, C1B

    def test_add_node(self):
        tree = self._sample_tree()
        new = WBSNode(id="C3", name="Phase 3", parent_id="R")
        tree.add_node(new)
        assert tree.node_count() == 6
        children = tree.get_children("R")
        assert len(children) == 3

    def test_delete_node_cascade(self):
        tree = self._sample_tree()
        deleted = tree.delete_node("C1", cascade=True)
        assert len(deleted) == 3  # C1, C1A, C1B
        assert tree.node_count() == 2  # R, C2

    def test_delete_node_promote(self):
        tree = self._sample_tree()
        deleted = tree.delete_node("C1", cascade=False)
        assert len(deleted) == 1  # just C1
        # C1A and C1B should now be children of R
        children = tree.get_children("R")
        assert len(children) == 3  # C2, C1A, C1B

    def test_reparent_node(self):
        tree = self._sample_tree()
        result = tree.reparent_node("C1A", "C2")
        assert result is True
        assert tree.get_node("C1A").parent_id == "C2"
        children_c2 = tree.get_children("C2")
        assert any(c.id == "C1A" for c in children_c2)

    def test_reparent_prevents_cycle(self):
        tree = self._sample_tree()
        # Try to move R under its descendant C1A — should fail
        result = tree.reparent_node("R", "C1A")
        assert result is False

    def test_undo_redo(self):
        tree = self._sample_tree()
        original_count = tree.node_count()
        tree.delete_node("C2", cascade=True)
        assert tree.node_count() == original_count - 1
        assert tree.undo() is True
        assert tree.node_count() == original_count
        assert tree.redo() is True
        assert tree.node_count() == original_count - 1

    def test_regenerate_codes(self):
        tree = self._sample_tree()
        tree.regenerate_codes()
        root = tree.get_roots()[0]
        assert root.wbs_code == "1"
        children = tree.get_children(root.id)
        assert children[0].wbs_code == "1.1"
        assert children[1].wbs_code == "1.2"

    def test_to_from_dict(self):
        tree = self._sample_tree()
        d = tree.to_dict()
        tree2 = WBSTree.from_dict(d)
        assert tree2.node_count() == tree.node_count()
        assert tree2.project_name == tree.project_name


# ---------------------------------------------------------------------------
# WBSValidator tests
# ---------------------------------------------------------------------------

class TestWBSValidator:
    def test_valid_tree(self):
        tree = TestWBSTree()._sample_tree()
        errors = WBSValidator.validate(tree)
        assert len(errors) == 0

    def test_orphan_detection(self):
        tree = WBSTree()
        tree.nodes.append(WBSNode(id="X", name="Orphan", parent_id="nonexistent"))
        errors = WBSValidator.validate(tree)
        error_msgs = [e.message for e in errors if e.level == "ERROR"]
        assert any("orphan" in m.lower() for m in error_msgs)

    def test_duplicate_ids(self):
        tree = WBSTree()
        tree.nodes.append(WBSNode(id="DUP", name="A", parent_id=""))
        tree.nodes.append(WBSNode(id="DUP", name="B", parent_id=""))
        errors = WBSValidator.validate(tree)
        error_msgs = [e.message for e in errors if e.level == "ERROR"]
        assert any("duplicate" in m.lower() for m in error_msgs)

    def test_empty_name(self):
        tree = WBSTree()
        tree.nodes.append(WBSNode(id="X", name="", parent_id=""))
        errors = WBSValidator.validate(tree)
        error_msgs = [e.message for e in errors if e.level == "ERROR"]
        assert any("name" in m.lower() for m in error_msgs)


# ---------------------------------------------------------------------------
# WBSBuilder tests
# ---------------------------------------------------------------------------

class TestWBSBuilder:
    def test_create_default(self):
        tree = WBSBuilder.create_default_tree("My Project")
        assert tree.node_count() == 1
        assert tree.project_name == "My Project"
        assert tree.get_roots()[0].name == "My Project"

    def test_import_csv(self):
        csv_text = """WBS_Code,Name,Parent_WBS_Code,Duration,Cost,Status
1,Project,,0,0,Not Started
1.1,Design,1,5,1000,In Progress
1.2,Build,1,10,3000,Not Started
1.2.1,Backend,1.2,8,2000,Not Started
"""
        tree = WBSBuilder.import_csv(csv_text, "CSV Test")
        assert tree.node_count() == 4
        assert tree.project_name == "CSV Test"

        roots = tree.get_roots()
        assert len(roots) == 1
        assert roots[0].name == "Project"

        children = tree.get_children(roots[0].id)
        assert len(children) == 2

    def test_import_csv_empty(self):
        csv_text = "WBS_Code,Name,Parent_WBS_Code\n"
        tree = WBSBuilder.import_csv(csv_text)
        assert tree.node_count() == 0

    def test_add_child(self):
        tree = WBSBuilder.create_default_tree("P")
        root = tree.get_roots()[0]
        child = WBSBuilder.add_child(tree, root.id, "Task 1", cost=500)
        assert child.parent_id == root.id
        assert child.name == "Task 1"
        assert tree.node_count() == 2

    def test_add_sibling(self):
        tree = WBSBuilder.create_default_tree("P")
        root = tree.get_roots()[0]
        c1 = WBSBuilder.add_child(tree, root.id, "T1")
        c2 = WBSBuilder.add_sibling(tree, c1.id, "T2")
        assert c2 is not None
        assert c2.parent_id == root.id
        assert tree.node_count() == 3


# ---------------------------------------------------------------------------
# WBSAggregator tests
# ---------------------------------------------------------------------------

class TestWBSAggregator:
    def test_aggregate_duration_max(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R", duration=5, cost=100)
        c2 = WBSNode(id="C2", name="B", parent_id="R", duration=10, cost=200)
        tree.nodes = [root, c1, c2]

        WBSAggregator.aggregate(tree)
        r = tree.get_node("R")
        assert r.duration == 10  # max(5, 10)

    def test_aggregate_cost_sum(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R", cost=1000)
        c2 = WBSNode(id="C2", name="B", parent_id="R", cost=2000)
        tree.nodes = [root, c1, c2]

        WBSAggregator.aggregate(tree)
        r = tree.get_node("R")
        assert r.cost == 3000

    def test_aggregate_progress_weighted(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R", cost=1000, progress=100)
        c2 = WBSNode(id="C2", name="B", parent_id="R", cost=3000, progress=0)
        tree.nodes = [root, c1, c2]

        WBSAggregator.aggregate(tree)
        r = tree.get_node("R")
        # Weighted: (100*1000 + 0*3000) / 4000 = 25
        assert r.progress == pytest.approx(25.0)

    def test_aggregate_status_all_complete(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R", status=WBSStatus.COMPLETED)
        c2 = WBSNode(id="C2", name="B", parent_id="R", status=WBSStatus.COMPLETED)
        tree.nodes = [root, c1, c2]

        WBSAggregator.aggregate(tree)
        assert tree.get_node("R").status == WBSStatus.COMPLETED

    def test_aggregate_status_delayed(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R", status=WBSStatus.IN_PROGRESS)
        c2 = WBSNode(id="C2", name="B", parent_id="R", status=WBSStatus.DELAYED)
        tree.nodes = [root, c1, c2]

        WBSAggregator.aggregate(tree)
        assert tree.get_node("R").status == WBSStatus.DELAYED


# ---------------------------------------------------------------------------
# WBSLayoutEngine tests
# ---------------------------------------------------------------------------

class TestWBSLayout:
    def test_empty_tree(self):
        engine = WBSLayoutEngine()
        tree = WBSTree()
        layouts = engine.compute(tree)
        assert layouts == {}

    def test_single_node(self):
        engine = WBSLayoutEngine()
        tree = WBSBuilder.create_default_tree("P")
        layouts = engine.compute(tree)
        assert len(layouts) == 1
        root_id = tree.get_roots()[0].id
        assert root_id in layouts
        assert layouts[root_id].y == 0

    def test_three_levels(self):
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        c1 = WBSNode(id="C1", name="A", parent_id="R")
        c2 = WBSNode(id="C2", name="B", parent_id="R")
        c1a = WBSNode(id="C1A", name="A1", parent_id="C1")
        tree.nodes = [root, c1, c2, c1a]

        engine = WBSLayoutEngine()
        layouts = engine.compute(tree)
        assert len(layouts) == 4

        # Root at top
        assert layouts["R"].y == 0
        # Children one level down
        assert layouts["C1"].y > layouts["R"].y
        assert layouts["C2"].y > layouts["R"].y
        # Grandchild two levels down
        assert layouts["C1A"].y > layouts["C1"].y

    def test_no_overlap(self):
        """Sibling nodes should not overlap horizontally."""
        tree = WBSTree()
        root = WBSNode(id="R", name="Root", parent_id="")
        for i in range(5):
            tree.nodes.append(WBSNode(id=f"C{i}", name=f"Child {i}", parent_id="R"))
        tree.nodes.insert(0, root)

        engine = WBSLayoutEngine(node_width=100, h_gap=20)
        layouts = engine.compute(tree)

        children_layouts = [layouts[f"C{i}"] for i in range(5)]
        for i in range(len(children_layouts) - 1):
            # Right edge of node i should be left of left edge of node i+1
            right_i = children_layouts[i].x + children_layouts[i].width
            left_next = children_layouts[i + 1].x
            assert right_i <= left_next, (
                f"Node C{i} overlaps with C{i+1}: "
                f"right={right_i}, left={left_next}"
            )

    def test_bounds(self):
        tree = WBSBuilder.create_default_tree("P")
        engine = WBSLayoutEngine()
        engine.compute(tree)
        bounds = engine.get_bounds()
        assert len(bounds) == 4
        assert bounds[2] > bounds[0]  # max_x > min_x
        assert bounds[3] > bounds[1]  # max_y > min_y
