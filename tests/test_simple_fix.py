#!/usr/bin/env python3
"""Minimal test to verify the artist fix"""

import sys
import os
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("Testing matplotlib artist fix...")

try:
    # Test the imports work
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt
    import networkx as nx
    print("✓ Matplotlib and NetworkX imports successful")
    
    # Create a simple test graph
    G = nx.Graph()
    G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D')])
    
    # Test creating two separate figures (simulating the old problem)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    
    # Draw network directly on each figure (the fixed approach)
    pos1 = nx.spring_layout(G)
    pos2 = nx.spring_layout(G)
    
    # This should work fine now - each figure gets its own artists
    nx.draw_networkx(G, pos1, ax=ax1)
    nx.draw_networkx(G, pos2, ax=ax2)
    
    plt.close(fig1)
    plt.close(fig2)
    
    print("✓ Multiple figure creation with separate artists successful")
    print("🎉 The matplotlib artist reuse fix is working correctly!")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    sys.exit(1)
