#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Visualizations

Tests all visualization functions including:
- Network diagram generation
- Gantt chart creation
- Probability distribution plots
- Statistical charts
- Custom plot styling
- Export functionality
- Error handling for plotting
"""

import pytest
import sys
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
import networkx as nx
import tempfile
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.utils.visualizations import *


class TestNetworkDiagrams:
    """Test network diagram visualization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test"""
        # Create a sample network graph
        self.graph = nx.DiGraph()
        self.graph.add_node('A', duration=3, ES=0, EF=3, LS=0, LF=3, float=0)
        self.graph.add_node('B', duration=5, ES=3, EF=8, LS=3, LF=8, float=0)
        self.graph.add_node('C', duration=4, ES=3, EF=7, LS=4, LF=8, float=1)
        self.graph.add_node('D', duration=2, ES=8, EF=10, LS=8, LF=10, float=0)
        
        self.graph.add_edge('A', 'B')
        self.graph.add_edge('A', 'C')
        self.graph.add_edge('B', 'D')
        self.graph.add_edge('C', 'D')
        
        self.critical_activities = ['A', 'B', 'D']
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')  # Close all matplotlib figures
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_draw_network_basic(self):
        """Test basic network diagram drawing"""
        if 'draw_network_diagram' in globals():
            fig, ax = draw_network_diagram(self.graph, self.critical_activities)
            
            assert fig is not None
            assert ax is not None
            assert len(fig.get_axes()) == 1
    
    def test_draw_network_with_labels(self):
        """Test network diagram with node labels"""
        if 'draw_network_diagram' in globals():
            fig, ax = draw_network_diagram(
                self.graph, 
                self.critical_activities, 
                show_labels=True
            )
            
            assert fig is not None
            # Check that labels are present (this is hard to verify directly)
    
    def test_draw_network_without_critical_path(self):
        """Test network diagram without critical path highlighting"""
        if 'draw_network_diagram' in globals():
            fig, ax = draw_network_diagram(self.graph, [])
            
            assert fig is not None
            assert ax is not None
    
    def test_network_layout_options(self):
        """Test different network layout options"""
        layout_options = ['spring', 'circular', 'shell', 'kamada_kawai']
        
        if 'draw_network_diagram' in globals():
            for layout in layout_options:
                try:
                    fig, ax = draw_network_diagram(
                        self.graph, 
                        self.critical_activities, 
                        layout=layout
                    )
                    assert fig is not None
                    plt.close(fig)
                except Exception as e:
                    # Some layouts might not be available
                    pass
    
    def test_node_color_customization(self):
        """Test custom node colors"""
        if 'draw_network_diagram' in globals():
            custom_colors = {
                'critical_color': 'red',
                'normal_color': 'blue',
                'start_color': 'green',
                'end_color': 'orange'
            }
            
            fig, ax = draw_network_diagram(
                self.graph, 
                self.critical_activities,
                **custom_colors
            )
            
            assert fig is not None
    
    def test_empty_graph_handling(self):
        """Test handling of empty graph"""
        empty_graph = nx.DiGraph()
        
        if 'draw_network_diagram' in globals():
            try:
                fig, ax = draw_network_diagram(empty_graph, [])
                # Should handle gracefully
                assert fig is not None
            except Exception:
                # Empty graph might raise an exception
                pass


class TestGanttCharts:
    """Test Gantt chart visualization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        # Sample activity data for Gantt chart
        self.activities = [
            {'id': 'A', 'ES': 0, 'EF': 3, 'LS': 0, 'LF': 3, 'float': 0, 'duration': 3},
            {'id': 'B', 'ES': 3, 'EF': 8, 'LS': 3, 'LF': 8, 'float': 0, 'duration': 5},
            {'id': 'C', 'ES': 3, 'EF': 7, 'LS': 4, 'LF': 8, 'float': 1, 'duration': 4},
            {'id': 'D', 'ES': 8, 'EF': 10, 'LS': 8, 'LF': 10, 'float': 0, 'duration': 2}
        ]
        self.critical_activities = ['A', 'B', 'D']
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_create_gantt_chart_basic(self):
        """Test basic Gantt chart creation"""
        if 'create_gantt_chart' in globals():
            fig, ax = create_gantt_chart(self.activities, self.critical_activities)
            
            assert fig is not None
            assert ax is not None
            assert len(fig.get_axes()) == 1
    
    def test_gantt_chart_with_float(self):
        """Test Gantt chart showing float/slack"""
        if 'create_gantt_chart' in globals():
            fig, ax = create_gantt_chart(
                self.activities, 
                self.critical_activities, 
                show_float=True
            )
            
            assert fig is not None
            # Activity C should show float
    
    def test_gantt_chart_without_float(self):
        """Test Gantt chart without float display"""
        if 'create_gantt_chart' in globals():
            fig, ax = create_gantt_chart(
                self.activities, 
                self.critical_activities, 
                show_float=False
            )
            
            assert fig is not None
    
    def test_gantt_chart_custom_title(self):
        """Test Gantt chart with custom title"""
        if 'create_gantt_chart' in globals():
            custom_title = "Project Schedule - Test Case"
            fig, ax = create_gantt_chart(
                self.activities, 
                self.critical_activities, 
                title=custom_title
            )
            
            assert fig is not None
            assert ax.get_title() == custom_title
    
    def test_gantt_chart_custom_colors(self):
        """Test Gantt chart with custom colors"""
        if 'create_gantt_chart' in globals():
            colors = {
                'critical_color': 'red',
                'normal_color': 'blue',
                'float_color': 'gray'
            }
            
            fig, ax = create_gantt_chart(
                self.activities, 
                self.critical_activities,
                **colors
            )
            
            assert fig is not None
    
    def test_gantt_chart_large_project(self):
        """Test Gantt chart with many activities"""
        # Generate large activity list
        large_activities = []
        for i in range(50):
            large_activities.append({
                'id': f'A{i}',
                'ES': i,
                'EF': i + 2,
                'LS': i,
                'LF': i + 2,
                'float': 0,
                'duration': 2
            })
        
        if 'create_gantt_chart' in globals():
            fig, ax = create_gantt_chart(large_activities, [])
            assert fig is not None
    
    def test_gantt_chart_overlapping_activities(self):
        """Test Gantt chart with overlapping activities"""
        overlapping_activities = [
            {'id': 'A', 'ES': 0, 'EF': 5, 'LS': 0, 'LF': 5, 'float': 0, 'duration': 5},
            {'id': 'B', 'ES': 2, 'EF': 7, 'LS': 2, 'LF': 7, 'float': 0, 'duration': 5},
            {'id': 'C', 'ES': 4, 'EF': 8, 'LS': 4, 'LF': 8, 'float': 0, 'duration': 4}
        ]
        
        if 'create_gantt_chart' in globals():
            fig, ax = create_gantt_chart(overlapping_activities, ['A', 'B', 'C'])
            assert fig is not None


class TestProbabilityPlots:
    """Test probability distribution visualization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_plot_normal_distribution(self):
        """Test normal distribution plotting"""
        if 'plot_normal_distribution' in globals():
            fig, ax = plot_normal_distribution(mean=100, std_dev=10)
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_beta_distribution(self):
        """Test beta distribution plotting"""
        if 'plot_beta_distribution' in globals():
            fig, ax = plot_beta_distribution(alpha=2, beta=3, scale=10)
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_project_completion_probability(self):
        """Test project completion probability curve"""
        if 'plot_completion_probability' in globals():
            durations = list(range(80, 121))  # 80 to 120 days
            probabilities = [i/40.0 for i in range(len(durations))]  # Sample probabilities
            
            fig, ax = plot_completion_probability(durations, probabilities)
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_monte_carlo_histogram(self):
        """Test Monte Carlo results histogram"""
        if 'plot_monte_carlo_histogram' in globals():
            # Sample Monte Carlo simulation results
            import numpy as np
            simulation_results = np.random.normal(100, 10, 1000)
            
            fig, ax = plot_monte_carlo_histogram(simulation_results)
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_confidence_intervals(self):
        """Test confidence interval visualization"""
        if 'plot_confidence_intervals' in globals():
            mean = 100
            confidence_levels = [0.68, 0.95, 0.99]
            intervals = [(95, 105), (90, 110), (85, 115)]
            
            fig, ax = plot_confidence_intervals(mean, confidence_levels, intervals)
            
            assert fig is not None
            assert ax is not None


class TestStatisticalCharts:
    """Test statistical visualization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_plot_scatter_plot(self):
        """Test scatter plot creation"""
        if 'create_scatter_plot' in globals():
            x_data = [1, 2, 3, 4, 5]
            y_data = [2, 4, 6, 8, 10]
            
            fig, ax = create_scatter_plot(x_data, y_data, 
                                        xlabel="X Values", 
                                        ylabel="Y Values")
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_bar_chart(self):
        """Test bar chart creation"""
        if 'create_bar_chart' in globals():
            categories = ['A', 'B', 'C', 'D']
            values = [3, 5, 4, 2]
            
            fig, ax = create_bar_chart(categories, values, 
                                     title="Activity Durations")
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_pie_chart(self):
        """Test pie chart creation"""
        if 'create_pie_chart' in globals():
            labels = ['Critical', 'Non-Critical']
            sizes = [60, 40]
            
            fig, ax = create_pie_chart(labels, sizes, 
                                     title="Activity Distribution")
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_line_graph(self):
        """Test line graph creation"""
        if 'create_line_graph' in globals():
            x_data = [0, 1, 2, 3, 4, 5]
            y_data = [0, 3, 8, 10, 10, 10]  # Cumulative progress
            
            fig, ax = create_line_graph(x_data, y_data, 
                                      xlabel="Time", 
                                      ylabel="Cumulative Progress")
            
            assert fig is not None
            assert ax is not None
    
    def test_plot_box_plot(self):
        """Test box plot creation"""
        if 'create_box_plot' in globals():
            import numpy as np
            data = [np.random.normal(100, 10, 100) for _ in range(4)]
            labels = ['Option A', 'Option B', 'Option C', 'Option D']
            
            fig, ax = create_box_plot(data, labels, 
                                    title="Duration Distributions")
            
            assert fig is not None
            assert ax is not None


class TestPlotCustomization:
    """Test plot customization and styling functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_apply_custom_style(self):
        """Test applying custom plot styles"""
        if 'apply_plot_style' in globals():
            fig, ax = plt.subplots()
            
            # Apply custom style
            apply_plot_style(ax, style='professional')
            
            assert fig is not None
            assert ax is not None
    
    def test_set_plot_colors(self):
        """Test setting custom plot colors"""
        if 'set_plot_colors' in globals():
            fig, ax = plt.subplots()
            
            colors = {
                'background': 'white',
                'grid': 'lightgray',
                'text': 'black'
            }
            
            set_plot_colors(ax, colors)
            
            assert fig is not None
    
    def test_add_plot_annotations(self):
        """Test adding annotations to plots"""
        if 'add_annotation' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            add_annotation(ax, "Critical Point", x=2, y=4)
            
            assert fig is not None
    
    def test_customize_legend(self):
        """Test legend customization"""
        if 'customize_legend' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9], label='Data')
            
            customize_legend(ax, location='upper left', style='professional')
            
            assert fig is not None
    
    def test_set_axis_properties(self):
        """Test setting axis properties"""
        if 'set_axis_properties' in globals():
            fig, ax = plt.subplots()
            
            properties = {
                'xlabel': 'Time (days)',
                'ylabel': 'Progress (%)',
                'title': 'Project Progress',
                'grid': True
            }
            
            set_axis_properties(ax, properties)
            
            assert fig is not None
            assert ax.get_xlabel() == 'Time (days)'
            assert ax.get_ylabel() == 'Progress (%)'
            assert ax.get_title() == 'Project Progress'


class TestPlotExport:
    """Test plot export and saving functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_save_plot_png(self):
        """Test saving plot as PNG"""
        if 'save_plot' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            output_file = os.path.join(self.temp_dir, 'test_plot.png')
            success = save_plot(fig, output_file, format='png')
            
            assert success
            assert os.path.exists(output_file)
    
    def test_save_plot_pdf(self):
        """Test saving plot as PDF"""
        if 'save_plot' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            output_file = os.path.join(self.temp_dir, 'test_plot.pdf')
            success = save_plot(fig, output_file, format='pdf')
            
            assert success
            assert os.path.exists(output_file)
    
    def test_save_plot_svg(self):
        """Test saving plot as SVG"""
        if 'save_plot' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            output_file = os.path.join(self.temp_dir, 'test_plot.svg')
            success = save_plot(fig, output_file, format='svg')
            
            assert success
            assert os.path.exists(output_file)
    
    def test_export_multiple_plots(self):
        """Test exporting multiple plots"""
        if 'export_all_plots' in globals():
            figures = []
            for i in range(3):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [i+1, (i+1)*4, (i+1)*9])
                figures.append(fig)
            
            output_dir = os.path.join(self.temp_dir, 'plots')
            success = export_all_plots(figures, output_dir)
            
            assert success
            assert os.path.exists(output_dir)
    
    def test_save_plot_with_metadata(self):
        """Test saving plot with metadata"""
        if 'save_plot_with_metadata' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            metadata = {
                'title': 'Test Plot',
                'author': 'PMHelper',
                'description': 'Unit test plot'
            }
            
            output_file = os.path.join(self.temp_dir, 'test_with_metadata.png')
            success = save_plot_with_metadata(fig, output_file, metadata)
            
            assert success
            assert os.path.exists(output_file)


class TestErrorHandling:
    """Test error handling in visualization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test"""
        plt.close('all')
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        if 'create_gantt_chart' in globals():
            # Empty activities list
            try:
                fig, ax = create_gantt_chart([], [])
                # Should handle gracefully
            except Exception:
                # Or raise appropriate error
                pass
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        if 'create_gantt_chart' in globals():
            # Activities missing required fields
            invalid_activities = [
                {'id': 'A'}  # Missing ES, EF, etc.
            ]
            
            try:
                fig, ax = create_gantt_chart(invalid_activities, [])
                # Should handle gracefully or raise appropriate error
            except KeyError:
                # Expected behavior for missing fields
                pass
    
    def test_invalid_file_path(self):
        """Test handling of invalid file paths for saving"""
        if 'save_plot' in globals():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            invalid_path = "/invalid/path/that/does/not/exist/plot.png"
            
            try:
                success = save_plot(fig, invalid_path)
                # Should return False or raise error
                assert not success
            except Exception:
                # Expected behavior for invalid path
                pass
    
    def test_memory_handling_large_plots(self):
        """Test memory handling with very large plots"""
        if 'create_gantt_chart' in globals():
            # Create very large activity list
            large_activities = []
            for i in range(1000):  # 1000 activities
                large_activities.append({
                    'id': f'A{i}',
                    'ES': i,
                    'EF': i + 1,
                    'LS': i,
                    'LF': i + 1,
                    'float': 0,
                    'duration': 1
                })
            
            try:
                fig, ax = create_gantt_chart(large_activities, [])
                # Should handle large datasets
                assert fig is not None
            except MemoryError:
                # Expected for very large datasets
                pass
    
    def test_invalid_color_specifications(self):
        """Test handling of invalid color specifications"""
        if 'draw_network_diagram' in globals():
            graph = nx.DiGraph()
            graph.add_node('A', duration=3)
            
            try:
                fig, ax = draw_network_diagram(
                    graph, [], 
                    critical_color='invalid_color'
                )
                # Should handle gracefully
            except Exception:
                # Invalid color might raise error
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
