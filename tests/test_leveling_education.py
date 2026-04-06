"""
Phase 8 — Resource Leveling Educational Enhancements: Tests
Covers LevelingStep dataclass, step recording in both algorithms,
leveling_step_generator functions, before/after metrics, and demo data.
"""

import pytest
import json
import os
from src.pmhelper.core.resource_leveling import (
    Activity,
    LevelingStep,
    ResourceProfile,
    MinimumMomentLeveling,
    BurgessLeveling,
    ResourceLevelingFactory,
)
from src.pmhelper.core.leveling_step_generator import (
    leveling_concepts_steps,
    float_analysis_steps,
    minimum_moment_algorithm_steps,
    burgess_algorithm_steps,
    before_after_comparison_steps,
)
from pmhelper.core.step_generators_edu import Step


# ════════════════════════════════════════════════════════════════════
#  Fixtures
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def levelable_activities():
    """6-activity project with clear leveling opportunity."""
    return [
        Activity("A", duration=3, resource_demand=2, es=0, ef=3,
                 ls=0, lf=3, float=0, predecessors=[], successors=["C", "D"]),
        Activity("B", duration=2, resource_demand=3, es=0, ef=2,
                 ls=5, lf=7, float=5, predecessors=[], successors=["E"]),
        Activity("C", duration=3, resource_demand=2, es=3, ef=6,
                 ls=3, lf=6, float=0, predecessors=["A"], successors=["F"]),
        Activity("D", duration=2, resource_demand=2, es=3, ef=5,
                 ls=5, lf=7, float=2, predecessors=["A"], successors=["F"]),
        Activity("E", duration=2, resource_demand=1, es=7, ef=9,
                 ls=7, lf=9, float=0, predecessors=["B"], successors=[]),
        Activity("F", duration=1, resource_demand=1, es=6, ef=7,
                 ls=9, lf=10, float=3, predecessors=["C", "D"], successors=[]),
    ]


@pytest.fixture
def all_critical_activities():
    """Activities with no float — leveling should be a no-op."""
    return [
        Activity("X", duration=3, resource_demand=2, es=0, ef=3,
                 ls=0, lf=3, float=0, predecessors=[], successors=["Y"]),
        Activity("Y", duration=3, resource_demand=2, es=3, ef=6,
                 ls=3, lf=6, float=0, predecessors=["X"], successors=[]),
    ]


@pytest.fixture
def mm_result(levelable_activities):
    """MinimumMoment result with steps recorded."""
    leveler = MinimumMomentLeveling(levelable_activities)
    return leveler.level(record_steps=True)


@pytest.fixture
def burgess_result(levelable_activities):
    """Burgess result with steps recorded."""
    leveler = BurgessLeveling(levelable_activities)
    return leveler.level(record_steps=True)


# ════════════════════════════════════════════════════════════════════
#  TestLevelingStep — dataclass
# ════════════════════════════════════════════════════════════════════

class TestLevelingStep:
    def test_creation(self):
        step = LevelingStep(
            step_number=1,
            activity_id="B",
            from_start=0,
            to_start=3,
            metric_before=12.5,
            metric_after=8.2,
            reason="Shifted to reduce moment",
            profile={0: 2.0, 1: 2.0, 2: 2.0, 3: 5.0},
        )
        assert step.step_number == 1
        assert step.activity_id == "B"
        assert step.from_start == 0
        assert step.to_start == 3
        assert step.metric_before == pytest.approx(12.5)
        assert step.metric_after == pytest.approx(8.2)
        assert "Shifted" in step.reason
        assert isinstance(step.profile, dict)

    def test_fields_accessible(self):
        step = LevelingStep(2, "C", 4, 6, 10.0, 7.0, "test reason", {4: 1.0})
        assert step.step_number == 2
        assert step.activity_id == "C"
        assert step.profile == {4: 1.0}

    def test_profile_is_dict(self):
        step = LevelingStep(1, "A", 0, 2, 5.0, 4.0, "r", {0: 1.0, 1: 2.0})
        assert isinstance(step.profile, dict)
        assert step.profile[0] == pytest.approx(1.0)


# ════════════════════════════════════════════════════════════════════
#  TestMinimumMomentStepRecording
# ════════════════════════════════════════════════════════════════════

class TestMinimumMomentStepRecording:
    def test_steps_key_in_result(self, mm_result):
        assert "steps" in mm_result

    def test_steps_is_list(self, mm_result):
        assert isinstance(mm_result["steps"], list)

    def test_steps_are_leveling_step_objects(self, mm_result):
        for step in mm_result["steps"]:
            assert isinstance(step, LevelingStep)

    def test_step_numbers_sequential(self, mm_result):
        steps = mm_result["steps"]
        for i, step in enumerate(steps, start=1):
            assert step.step_number == i

    def test_step_has_profile_snapshot(self, mm_result):
        for step in mm_result["steps"]:
            assert isinstance(step.profile, dict)
            assert len(step.profile) > 0

    def test_metric_improves_per_step(self, mm_result):
        for step in mm_result["steps"]:
            assert step.metric_after <= step.metric_before + 1e-9

    def test_from_start_differs_from_to_start(self, mm_result):
        """Every recorded step must represent an actual move."""
        for step in mm_result["steps"]:
            assert step.from_start != step.to_start

    def test_no_steps_without_flag(self, levelable_activities):
        leveler = MinimumMomentLeveling(levelable_activities)
        result = leveler.level(record_steps=False)
        assert result["steps"] == []

    def test_leveling_improves_moment(self, mm_result):
        assert mm_result["leveled_moment"] <= mm_result["original_moment"]

    def test_improvement_pct_non_negative(self, mm_result):
        assert mm_result["improvement_pct"] >= 0


# ════════════════════════════════════════════════════════════════════
#  TestBurgessStepRecording
# ════════════════════════════════════════════════════════════════════

class TestBurgessStepRecording:
    def test_steps_key_in_result(self, burgess_result):
        assert "steps" in burgess_result

    def test_steps_are_leveling_step_objects(self, burgess_result):
        for step in burgess_result["steps"]:
            assert isinstance(step, LevelingStep)

    def test_step_numbers_sequential(self, burgess_result):
        steps = burgess_result["steps"]
        for i, step in enumerate(steps, start=1):
            assert step.step_number == i

    def test_metric_improves_per_step(self, burgess_result):
        for step in burgess_result["steps"]:
            assert step.metric_after <= step.metric_before + 1e-9

    def test_no_steps_without_flag(self, levelable_activities):
        leveler = BurgessLeveling(levelable_activities)
        result = leveler.level(record_steps=False)
        assert result["steps"] == []

    def test_burgess_improves_cost(self, burgess_result):
        assert burgess_result["leveled_cost"] <= burgess_result["original_cost"]

    def test_improvement_pct_non_negative(self, burgess_result):
        assert burgess_result["improvement_pct"] >= 0


# ════════════════════════════════════════════════════════════════════
#  TestStepRecordingNoOp
# ════════════════════════════════════════════════════════════════════

class TestStepRecordingNoOp:
    def test_mm_no_steps_all_critical(self, all_critical_activities):
        leveler = MinimumMomentLeveling(all_critical_activities)
        result = leveler.level(record_steps=True)
        assert result["steps"] == []

    def test_burgess_no_steps_all_critical(self, all_critical_activities):
        leveler = BurgessLeveling(all_critical_activities)
        result = leveler.level(record_steps=True)
        assert result["steps"] == []

    def test_mm_result_still_valid_all_critical(self, all_critical_activities):
        leveler = MinimumMomentLeveling(all_critical_activities)
        result = leveler.level(record_steps=True)
        assert "leveled_schedule" in result
        assert "original_moment" in result

    def test_burgess_result_still_valid_all_critical(self, all_critical_activities):
        leveler = BurgessLeveling(all_critical_activities)
        result = leveler.level(record_steps=True)
        assert "leveled_schedule" in result
        assert "original_cost" in result


# ════════════════════════════════════════════════════════════════════
#  TestLevelingStepGenerator
# ════════════════════════════════════════════════════════════════════

class TestLevelingStepGenerator:
    def test_concepts_returns_list(self):
        steps = leveling_concepts_steps()
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_concepts_are_step_objects(self):
        steps = leveling_concepts_steps()
        for s in steps:
            assert isinstance(s, Step)

    def test_concepts_have_titles(self):
        steps = leveling_concepts_steps()
        for s in steps:
            assert s.title.strip() != ""

    def test_float_analysis_all_critical(self, all_critical_activities):
        schedule = {"X": 0, "Y": 3}
        steps = float_analysis_steps(all_critical_activities, schedule)
        assert isinstance(steps, list)
        assert len(steps) >= 1

    def test_float_analysis_non_critical(self, levelable_activities):
        schedule = {"A": 0, "B": 0, "C": 3, "D": 3, "E": 7, "F": 6}
        steps = float_analysis_steps(levelable_activities, schedule)
        # Should include step per non-critical activity (B, D, F have float > 0)
        non_crit_count = sum(1 for a in levelable_activities if a.float > 0)
        assert len(steps) >= non_crit_count

    def test_mm_algorithm_steps(self, mm_result):
        steps = minimum_moment_algorithm_steps(mm_result)
        assert isinstance(steps, list)
        assert len(steps) >= 2

    def test_mm_algorithm_steps_are_step_objects(self, mm_result):
        steps = minimum_moment_algorithm_steps(mm_result)
        for s in steps:
            assert isinstance(s, Step)

    def test_burgess_algorithm_steps(self, burgess_result):
        steps = burgess_algorithm_steps(burgess_result)
        assert isinstance(steps, list)
        assert len(steps) >= 2

    def test_before_after_comparison_steps(self, mm_result):
        steps = before_after_comparison_steps(mm_result)
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_before_after_steps_are_step_objects(self, mm_result):
        steps = before_after_comparison_steps(mm_result)
        for s in steps:
            assert isinstance(s, Step)


# ════════════════════════════════════════════════════════════════════
#  TestBeforeAfterMetrics
# ════════════════════════════════════════════════════════════════════

class TestBeforeAfterMetrics:
    def test_mm_peak_does_not_increase(self, mm_result):
        assert mm_result["peak_usage_leveled"] <= mm_result["peak_usage_original"]

    def test_burgess_peak_does_not_increase(self, burgess_result):
        assert burgess_result["peak_usage_leveled"] <= burgess_result["peak_usage_original"]

    def test_mm_result_contains_profiles(self, mm_result):
        assert mm_result["original_profile"] is not None
        assert mm_result["leveled_profile"] is not None

    def test_burgess_result_contains_profiles(self, burgess_result):
        assert burgess_result["original_profile"] is not None
        assert burgess_result["leveled_profile"] is not None

    def test_improvement_pct_matches_moments(self, mm_result):
        orig = mm_result["original_moment"]
        lev = mm_result["leveled_moment"]
        expected_pct = (orig - lev) / orig * 100 if orig > 0 else 0.0
        assert mm_result["improvement_pct"] == pytest.approx(expected_pct, abs=0.01)

    def test_mm_profile_has_data(self, mm_result):
        lev_profile = mm_result["leveled_profile"]
        assert len(lev_profile.profile) > 0


# ════════════════════════════════════════════════════════════════════
#  TestSmoothingConstraint
# ════════════════════════════════════════════════════════════════════

class TestSmoothingConstraint:
    def test_smoothing_preserves_project_duration(self, levelable_activities):
        """Smoothing (no resource limit) must not extend project end."""
        leveler = MinimumMomentLeveling(levelable_activities, resource_limit=None)
        result = leveler.level(record_steps=True)
        schedule = result["leveled_schedule"]

        # Calculate leveled project end
        leveled_end = max(
            schedule[act.id] + act.duration
            for act in levelable_activities
        )
        # Calculate original project end
        original_end = max(act.ef for act in levelable_activities)
        assert leveled_end <= original_end

    def test_smoothing_shifts_within_float(self, levelable_activities):
        """Every moved activity must still stay within ES–LS bounds."""
        leveler = MinimumMomentLeveling(levelable_activities, resource_limit=None)
        result = leveler.level(record_steps=True)
        schedule = result["leveled_schedule"]
        act_by_id = {a.id: a for a in levelable_activities}

        for act_id, start in schedule.items():
            act = act_by_id[act_id]
            assert act.es <= start <= act.ls, (
                f"Activity {act_id} start {start} outside [{act.es}, {act.ls}]"
            )

    def test_constrained_mode_feasible(self, levelable_activities):
        """With a generous limit, schedule should be feasible."""
        leveler = MinimumMomentLeveling(levelable_activities, resource_limit=6)
        result = leveler.level(record_steps=True)
        assert result["feasible"] is True


# ════════════════════════════════════════════════════════════════════
#  TestDemoFile
# ════════════════════════════════════════════════════════════════════

class TestDemoFile:
    @pytest.fixture
    def demo_data(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "data", "demos", "v2", "resource_leveling_demo.json",
        )
        with open(os.path.normpath(path)) as f:
            return json.load(f)

    def test_demo_file_exists(self, demo_data):
        assert demo_data is not None

    def test_demo_has_activities(self, demo_data):
        assert "activities" in demo_data
        assert len(demo_data["activities"]) >= 5

    def test_demo_activities_have_required_fields(self, demo_data):
        required = {"id", "duration", "resource_demand", "es", "ef",
                    "ls", "lf", "float"}
        for act in demo_data["activities"]:
            for field in required:
                assert field in act, f"Activity {act.get('id')} missing field '{field}'"

    def test_demo_has_resource_limit(self, demo_data):
        assert "resource_limit" in demo_data

    def test_demo_activities_loadable(self, demo_data):
        """Demo activities can be passed directly to the leveler."""
        from src.pmhelper.core.resource_leveling import Activity, MinimumMomentLeveling

        activities = [
            Activity(
                id=a["id"],
                duration=a["duration"],
                resource_demand=a["resource_demand"],
                es=a["es"],
                ef=a["ef"],
                ls=a["ls"],
                lf=a["lf"],
                float=a["float"],
                predecessors=a.get("predecessors", []),
                successors=a.get("successors", []),
            )
            for a in demo_data["activities"]
        ]
        leveler = MinimumMomentLeveling(activities)
        result = leveler.level(record_steps=True)
        assert "leveled_schedule" in result

    def test_demo_shows_leveling_improvement(self, demo_data):
        """Demo should produce measurable improvement (designed for this)."""
        from src.pmhelper.core.resource_leveling import Activity, MinimumMomentLeveling

        activities = [
            Activity(
                id=a["id"],
                duration=a["duration"],
                resource_demand=a["resource_demand"],
                es=a["es"],
                ef=a["ef"],
                ls=a["ls"],
                lf=a["lf"],
                float=a["float"],
                predecessors=a.get("predecessors", []),
                successors=a.get("successors", []),
            )
            for a in demo_data["activities"]
        ]
        leveler = MinimumMomentLeveling(activities)
        result = leveler.level(record_steps=True)
        assert result["improvement_pct"] > 0
