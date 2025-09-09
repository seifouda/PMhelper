#!/usr/bin/env python3
"""Test script to verify the network diagram fix"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

from pmhelper.core.cpm_analyzer import CPMAnalyzer
import pandas as pd

def test_network_creation():
    """Test network diagram creation with the fixed code"""
    print("Testing network diagram creation...")
    
    # Test with sample data
    data = [
        {'id': 'A', 'duration': 3, 'predecessors': ''},
        {'id': 'B', 'duration': 4, 'predecessors': 'A'},
        {'id': 'C', 'duration': 2, 'predecessors': 'A'},
        {'id': 'D', 'duration': 5, 'predecessors': 'B,C'}
    ]

    analyzer = CPMAnalyzer()
    results = analyzer.analyze_from_data(data)
    
    print('CPM Analysis completed successfully')
    print(f'Project Duration: {results["project_duration"]}')
    print(f'Critical Activities: {results["critical_activities"]}')
    
    # Check if graph was created
    graph = results.get('graph')
    if graph:
        print(f'Graph nodes: {len(graph.nodes())}')
        print(f'Graph edges: {len(graph.edges())}')
        print('Graph creation successful!')
    else:
        print('No graph created')
    
    return results

if __name__ == "__main__":
    test_network_creation()
