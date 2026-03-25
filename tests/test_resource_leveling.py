"""
Tests for Resource Leveling Module

Tests ResourceProfile, MinimumMomentLeveling, and BurgessLeveling functionality.
"""

import pytest
import pandas as pd
import numpy as np
from src.pmhelper.core.resource_leveling import (
    Activity,
    ResourceProfile,
    MinimumMomentLeveling,
    BurgessLeveling,
    ResourceLevelingFactory,
    activities_from_cpm
)


@pytest.fixture
def sample_activities():
    """Create sample activities for testing"""
    return [
        Activity('A', duration=4, resource_demand=5.0, es=0, ef=4, ls=0, lf=4, 
                float=0, predecessors=[], successors=['B', 'C']),
        Activity('B', duration=3, resource_demand=3.0, es=4, ef=7, ls=5, lf=8,
                float=1, predecessors=['A'], successors=['D']),
        Activity('C', duration=2, resource_demand=2.0, es=4, ef=6, ls=6, lf=8,
                float=2, predecessors=['A'], successors=['D']),
        Activity('D', duration=4, resource_demand=4.0, es=7, ef=11, ls=8, lf=12,
                float=1, predecessors=['B', 'C'], successors=[])
    ]


@pytest.fixture
def early_start_schedule():
    """Early start schedule for sample activities"""
    return {'A': 0, 'B': 4, 'C': 4, 'D': 7}


class TestActivity:
    """Test Activity dataclass"""
    
    def test_activity_creation(self):
        """Test creating an Activity"""
        act = Activity('A', 5, 10.0, 0, 5, 0, 5, 0, [], ['B'])
        
        assert act.id == 'A'
        assert act.duration == 5
        assert act.resource_demand == 10.0
        assert act.es == 0
        assert act.float == 0


class TestResourceProfile:
    """Test ResourceProfile class"""
    
    def test_profile_initialization(self, sample_activities, early_start_schedule):
        """Test ResourceProfile initialization"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        
        assert profile.schedule == early_start_schedule
        assert len(profile.activities) == 4
        assert isinstance(profile.profile, dict)
    
    def test_calculate_profile(self, sample_activities, early_start_schedule):
        """Test resource profile calculation"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        
        # At time 0-3: only A is active (5 units)
        assert profile.profile[0] == 5.0
        assert profile.profile[1] == 5.0
        assert profile.profile[2] == 5.0
        assert profile.profile[3] == 5.0
        
        # At time 4-6: B and C are active (3 + 2 = 5 units)
        assert profile.profile[4] == 5.0
        assert profile.profile[5] == 5.0
        
        # At time 6: only B is active (3 units)
        assert profile.profile[6] == 3.0
    
    def test_calculate_moment(self, sample_activities, early_start_schedule):
        """Test moment calculation"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        moment = profile.calculate_moment()
        
        assert moment >= 0
        assert isinstance(moment, float)
    
    def test_get_peak_usage(self, sample_activities, early_start_schedule):
        """Test peak usage calculation"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        peak = profile.get_peak_usage()
        
        assert peak == 5.0  # Maximum usage from the schedule
    
    def test_get_utilization(self, sample_activities, early_start_schedule):
        """Test utilization calculation"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        utilization = profile.get_utilization(resource_limit=10.0)
        
        assert 0 <= utilization <= 100
        assert isinstance(utilization, float)
    
    def test_to_dataframe(self, sample_activities, early_start_schedule):
        """Test DataFrame conversion"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        df = profile.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert 'time' in df.columns
        assert 'resource_usage' in df.columns
        assert len(df) > 0
    
    def test_is_feasible(self, sample_activities, early_start_schedule):
        """Test feasibility check"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        
        assert profile.is_feasible(resource_limit=10.0) is True
        assert profile.is_feasible(resource_limit=4.0) is False
    
    def test_get_overutilized_periods(self, sample_activities, early_start_schedule):
        """Test overutilization detection"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        
        # With limit of 4, periods with usage 5 should be overutilized
        overutilized = profile.get_overutilized_periods(resource_limit=4.0)
        
        assert len(overutilized) > 0
        assert all(profile.profile[t] > 4.0 for t in overutilized)
    
    def test_empty_schedule(self):
        """Test profile with empty schedule"""
        profile = ResourceProfile({}, [])
        
        assert profile.calculate_moment() == 0.0
        assert profile.get_peak_usage() == 0.0


class TestMinimumMomentLeveling:
    """Test MinimumMomentLeveling algorithm"""
    
    def test_initialization(self, sample_activities):
        """Test leveling initialization"""
        leveling = MinimumMomentLeveling(sample_activities, resource_limit=10.0)
        
        assert len(leveling.activities) == 4
        assert leveling.resource_limit == 10.0
        assert len(leveling.original_schedule) == 4
    
    def test_level_basic(self, sample_activities):
        """Test basic leveling"""
        leveling = MinimumMomentLeveling(sample_activities)
        result = leveling.level()
        
        assert 'leveled_schedule' in result
        assert 'original_moment' in result
        assert 'leveled_moment' in result
        assert 'improvement_pct' in result
        assert 'iterations' in result
        
        # Leveled moment should be <= original
        assert result['leveled_moment'] <= result['original_moment']
    
    def test_level_with_resource_limit(self, sample_activities):
        """Test leveling with resource constraint"""
        leveling = MinimumMomentLeveling(sample_activities, resource_limit=10.0)
        result = leveling.level()
        
        assert result['feasible'] is True
        
        # Check that leveled schedule respects resource limit
        leveled_profile = result['leveled_profile']
        assert leveled_profile.is_feasible(10.0)
    
    def test_level_no_noncritical_activities(self):
        """Test leveling when all activities are critical"""
        activities = [
            Activity('A', 4, 5.0, 0, 4, 0, 4, 0, [], ['B']),
            Activity('B', 3, 3.0, 4, 7, 4, 7, 0, ['A'], [])
        ]
        
        leveling = MinimumMomentLeveling(activities)
        result = leveling.level()
        
        # No improvement should occur
        assert result['improvement_pct'] == 0.0
        assert result['iterations'] == 0
    
    def test_level_improvement(self, sample_activities):
        """Test that leveling improves moment"""
        leveling = MinimumMomentLeveling(sample_activities)
        result = leveling.level()
        
        # Should have some improvement or be already optimal
        assert result['improvement_pct'] >= 0.0
    
    def test_max_iterations_limit(self, sample_activities):
        """Test max iterations limit"""
        leveling = MinimumMomentLeveling(sample_activities)
        result = leveling.level(max_iterations=5)
        
        # Should stop within max iterations
        assert result['iterations'] <= 5


class TestBurgessLeveling:
    """Test BurgessLeveling algorithm"""
    
    def test_initialization(self, sample_activities):
        """Test Burgess initialization"""
        leveling = BurgessLeveling(sample_activities, resource_limit=10.0)
        
        assert len(leveling.activities) == 4
        assert leveling.resource_limit == 10.0
    
    def test_level_basic(self, sample_activities):
        """Test basic Burgess leveling"""
        leveling = BurgessLeveling(sample_activities)
        result = leveling.level()
        
        assert 'leveled_schedule' in result
        assert 'original_cost' in result
        assert 'leveled_cost' in result
        assert 'improvement_pct' in result
        
        # Leveled cost should be <= original
        assert result['leveled_cost'] <= result['original_cost']
    
    def test_level_with_resource_limit(self, sample_activities):
        """Test Burgess with resource constraint"""
        leveling = BurgessLeveling(sample_activities, resource_limit=10.0)
        result = leveling.level()
        
        assert result['feasible'] is True
        leveled_profile = result['leveled_profile']
        assert leveled_profile.is_feasible(10.0)
    
    def test_burgess_cost_calculation(self, sample_activities, early_start_schedule):
        """Test Burgess cost calculation"""
        profile = ResourceProfile(early_start_schedule, sample_activities)
        leveling = BurgessLeveling(sample_activities)
        
        cost = leveling._calculate_burgess_cost(profile)
        
        # Cost should be sum of squares
        expected = sum(usage ** 2 for usage in profile.profile.values())
        assert cost == expected
    
    def test_burgess_vs_minimum_moment(self, sample_activities):
        """Test that both methods produce valid results"""
        mm_leveling = MinimumMomentLeveling(sample_activities)
        mm_result = mm_leveling.level()
        
        burgess_leveling = BurgessLeveling(sample_activities)
        burgess_result = burgess_leveling.level()
        
        # Both should improve or maintain
        assert mm_result['improvement_pct'] >= 0
        assert burgess_result['improvement_pct'] >= 0


class TestResourceLevelingFactory:
    """Test ResourceLevelingFactory"""
    
    def test_create_minimum_moment(self, sample_activities):
        """Test creating minimum moment leveler"""
        leveler = ResourceLevelingFactory.create('minimum_moment', sample_activities, 10.0)
        
        assert isinstance(leveler, MinimumMomentLeveling)
        assert leveler.resource_limit == 10.0
    
    def test_create_burgess(self, sample_activities):
        """Test creating Burgess leveler"""
        leveler = ResourceLevelingFactory.create('burgess', sample_activities, 10.0)
        
        assert isinstance(leveler, BurgessLeveling)
        assert leveler.resource_limit == 10.0
    
    def test_create_invalid_method(self, sample_activities):
        """Test that invalid method raises error"""
        with pytest.raises(ValueError, match="Unknown method"):
            ResourceLevelingFactory.create('invalid_method', sample_activities)
    
    def test_factory_methods_work(self, sample_activities):
        """Test that factory-created instances work"""
        leveler = ResourceLevelingFactory.create('minimum_moment', sample_activities)
        result = leveler.level()
        
        assert 'leveled_schedule' in result
        assert result['iterations'] >= 0


class MockCPMAnalyzer:
    """Mock CPM analyzer for testing activities_from_cpm"""
    
    def __init__(self):
        import networkx as nx
        self.G = nx.DiGraph()
        
        # Add activities
        self.G.add_node('A', duration=4, resource_demand=5, ES=0, EF=4, 
                       LS=0, LF=4, float=0)
        self.G.add_node('B', duration=3, resource_demand=3, ES=4, EF=7,
                       LS=5, LF=8, float=1)
        
        # Add edges
        self.G.add_edge('START', 'A')
        self.G.add_edge('A', 'B')
        self.G.add_edge('B', 'END')


class TestActivitiesFromCPM:
    """Test activities_from_cpm conversion function"""
    
    def test_basic_conversion(self):
        """Test converting CPM analyzer to activities"""
        cpm = MockCPMAnalyzer()
        activities = activities_from_cpm(cpm)
        
        assert len(activities) == 2  # A and B (excluding START/END)
        assert all(isinstance(act, Activity) for act in activities)
    
    def test_activity_properties(self):
        """Test that converted activities have correct properties"""
        cpm = MockCPMAnalyzer()
        activities = activities_from_cpm(cpm)
        
        act_a = next(act for act in activities if act.id == 'A')
        
        assert act_a.duration == 4
        assert act_a.resource_demand == 5.0
        assert act_a.es == 0
        assert act_a.float == 0
    
    def test_conversion_without_analysis(self):
        """Test that conversion fails without CPM analysis"""
        class EmptyCPM:
            pass
        
        cpm = EmptyCPM()
        
        with pytest.raises(ValueError, match="CPM analysis must be performed"):
            activities_from_cpm(cpm)


class TestIntegration:
    """Integration tests for resource leveling"""
    
    def test_end_to_end_leveling(self, sample_activities):
        """Test complete leveling workflow"""
        # Create leveler
        leveler = ResourceLevelingFactory.create('minimum_moment', 
                                                 sample_activities, 
                                                 resource_limit=10.0)
        
        # Perform leveling
        result = leveler.level()
        
        # Verify result structure
        assert 'leveled_schedule' in result
        assert 'original_profile' in result
        assert 'leveled_profile' in result
        
        # Verify profiles are different (unless already optimal)
        original_df = result['original_profile'].to_dataframe()
        leveled_df = result['leveled_profile'].to_dataframe()
        
        assert len(original_df) > 0
        assert len(leveled_df) > 0
    
    def test_leveling_preserves_precedence(self, sample_activities):
        """Test that leveling preserves precedence relationships"""
        leveler = MinimumMomentLeveling(sample_activities)
        result = leveler.level()
        
        schedule = result['leveled_schedule']
        
        # Activity B cannot start before A finishes
        act_a = next(act for act in sample_activities if act.id == 'A')
        assert schedule['B'] >= schedule['A'] + act_a.duration
    
    def test_multiple_leveling_methods_comparison(self, sample_activities):
        """Test and compare different leveling methods"""
        mm_leveler = MinimumMomentLeveling(sample_activities)
        mm_result = mm_leveler.level()
        
        burgess_leveler = BurgessLeveling(sample_activities)
        burgess_result = burgess_leveler.level()
        
        # Both should produce valid schedules
        assert len(mm_result['leveled_schedule']) == len(sample_activities)
        assert len(burgess_result['leveled_schedule']) == len(sample_activities)
        
        # Both should respect activity constraints
        for act in sample_activities:
            # Start time should be within ES and LS
            assert act.es <= mm_result['leveled_schedule'][act.id] <= act.ls
            assert act.es <= burgess_result['leveled_schedule'][act.id] <= act.ls


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
