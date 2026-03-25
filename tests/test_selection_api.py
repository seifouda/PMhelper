"""
Test script for Selection API endpoints

Tests all four selection methods: AHP, Linear Scoring, B/C Analysis, and Portfolio.
"""

import requests
import json
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8000/api/selection"


def test_ahp():
    """Test AHP analysis endpoint."""
    print("\n" + "="*60)
    print("Testing AHP Analysis")
    print("="*60)
    
    data = {
        "criteria": ["Cost", "Quality", "Speed", "Support"],
        "comparisons": {
            "Cost": {"Quality": 0.333, "Speed": 0.5, "Support": 0.25},
            "Quality": {"Speed": 2.0, "Support": 0.5},
            "Speed": {"Support": 0.333}
        },
        "alternatives": [
            {
                "name": "Software A",
                "scores": {"Cost": 8.5, "Quality": 7.2, "Speed": 8.0, "Support": 6.5}
            },
            {
                "name": "Software B",
                "scores": {"Cost": 7.0, "Quality": 8.5, "Speed": 6.0, "Support": 8.0}
            },
            {
                "name": "Software C",
                "scores": {"Cost": 6.5, "Quality": 6.0, "Speed": 9.0, "Support": 7.0}
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/ahp", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ AHP Analysis successful!")
        print(f"Consistency Ratio: {result['consistency_ratio']:.4f}")
        print(f"Is Consistent: {result['is_consistent']}")
        print("\nCriterion Weights:")
        for criterion, weight in result['weights'].items():
            print(f"  {criterion:20s} {weight:.4f}")
        
        if result.get('ranked_alternatives'):
            print("\nRanked Alternatives:")
            for i, alt in enumerate(result['ranked_alternatives'], 1):
                print(f"  {i}. {alt['Alternative']:20s} Score: {alt['Total Score']:.4f}")
    else:
        print(f"\n✗ AHP Analysis failed: {response.status_code}")
        print(response.text)


def test_linear_scoring():
    """Test Linear Scoring endpoint."""
    print("\n" + "="*60)
    print("Testing Linear Scoring Analysis")
    print("="*60)
    
    data = {
        "criteria": [
            {"name": "Performance", "weight": 0.35, "direction": "maximize"},
            {"name": "Cost", "weight": 0.25, "direction": "minimize"},
            {"name": "Reliability", "weight": 0.25, "direction": "maximize"},
            {"name": "Ease_of_Use", "weight": 0.15, "direction": "maximize"}
        ],
        "alternatives": [
            {
                "name": "Product A",
                "scores": {"Performance": 85, "Cost": 7500, "Reliability": 92, "Ease_of_Use": 78}
            },
            {
                "name": "Product B",
                "scores": {"Performance": 78, "Cost": 6200, "Reliability": 88, "Ease_of_Use": 85}
            },
            {
                "name": "Product C",
                "scores": {"Performance": 92, "Cost": 8900, "Reliability": 85, "Ease_of_Use": 72}
            },
            {
                "name": "Product D",
                "scores": {"Performance": 80, "Cost": 7100, "Reliability": 95, "Ease_of_Use": 90}
            }
        ],
        "sensitivity_analysis": True
    }
    
    response = requests.post(f"{BASE_URL}/linear-scoring", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Linear Scoring Analysis successful!")
        print("\nRanked Alternatives:")
        for i, alt in enumerate(result['ranked_alternatives'], 1):
            print(f"  {i}. {alt['name']:20s} Score: {alt['Total Score']:.4f}")
        
        if result.get('sensitivity_results'):
            print("\n✓ Sensitivity analysis completed")
            for criterion, data in result['sensitivity_results']['variations'].items():
                rank_changes = sum(1 for v in data if v['rank_changed'])
                print(f"  {criterion}: {rank_changes}/{len(data)} variations caused rank changes")
    else:
        print(f"\n✗ Linear Scoring Analysis failed: {response.status_code}")
        print(response.text)


def test_benefit_cost():
    """Test B/C Analysis endpoint."""
    print("\n" + "="*60)
    print("Testing B/C Analysis")
    print("="*60)
    
    data = {
        "projects": [
            {
                "name": "Project A",
                "cost": 100000,
                "benefit": 25000,
                "life": 10,
                "initial_cost": 100000,
                "annual_om": 3000,
                "salvage": 10000
            },
            {
                "name": "Project B",
                "cost": 150000,
                "benefit": 35000,
                "life": 10,
                "initial_cost": 150000,
                "annual_om": 5000,
                "salvage": 15000
            },
            {
                "name": "Project C",
                "cost": 200000,
                "benefit": 48000,
                "life": 10,
                "initial_cost": 200000,
                "annual_om": 8000,
                "salvage": 20000
            }
        ],
        "marr": 0.12,
        "analysis_type": "mutually_exclusive"
    }
    
    response = requests.post(f"{BASE_URL}/benefit-cost", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ B/C Analysis successful!")
        print(f"Analysis Type: {result['analysis_type']}")
        print(f"MARR: {result['marr']*100:.1f}%")
        
        if result.get('optimal_project'):
            opt = result['optimal_project']
            print(f"\nOptimal Project: {opt['name']}")
            print(f"  B/C Ratio: {opt['BC_Ratio']:.3f}")
            print(f"  Initial Cost: ${opt['initial_cost']:,.2f}")
            print(f"  Annual Benefits: ${opt['annual_benefits']:,.2f}")
        
        if result.get('comparisons'):
            print("\nIncremental Analysis:")
            for comp in result['comparisons']:
                print(f"  {comp['current']} vs {comp['challenger']}")
                print(f"    Incremental B/C: {comp['incremental_bc']:.3f}")
                print(f"    Decision: {comp['decision']}")
    else:
        print(f"\n✗ B/C Analysis failed: {response.status_code}")
        print(response.text)


def test_portfolio():
    """Test Portfolio Optimization endpoint."""
    print("\n" + "="*60)
    print("Testing Portfolio Optimization")
    print("="*60)
    
    data = {
        "projects": [
            {"name": "AI Research", "cost": 1200000, "benefit": 450000},
            {"name": "Cloud Migration", "cost": 800000, "benefit": 320000},
            {"name": "Mobile App", "cost": 500000, "benefit": 180000},
            {"name": "Data Analytics", "cost": 900000, "benefit": 350000},
            {"name": "Security Upgrade", "cost": 400000, "benefit": 140000},
            {"name": "IoT Platform", "cost": 1100000, "benefit": 410000},
            {"name": "Blockchain POC", "cost": 600000, "benefit": 200000}
        ],
        "budget": 3000000,
        "constraints": [
            {
                "type": "require",
                "projects": ["Security Upgrade"],
                "description": "Security Upgrade is mandatory"
            },
            {
                "type": "exclude",
                "projects": ["AI Research", "Blockchain POC"],
                "description": "AI Research and Blockchain POC cannot both be selected"
            },
            {
                "type": "dependency",
                "projects": ["Cloud Migration", "Mobile App"],
                "description": "Mobile App requires Cloud Migration"
            }
        ],
        "time_limit": 60,
        "sensitivity_analysis": True
    }
    
    response = requests.post(f"{BASE_URL}/portfolio", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Portfolio Optimization successful!")
        print(f"Status: {result['status']}")
        print(f"\nSelected Projects: {len(result['selected_projects'])}")
        for proj in result['selected_projects']:
            print(f"  • {proj}")
        
        print(f"\nTotal Cost: ${result['total_cost']:,.2f}")
        print(f"Total Annual Benefit: ${result['total_benefit']:,.2f}")
        print(f"Budget Utilization: {result['budget_utilization']:.1f}%")
        print(f"Objective Value: ${result['objective_value']:,.2f}")
        
        if result.get('shadow_price_budget'):
            print(f"\nMarginal Value of $1 additional budget: ${result['shadow_price_budget']:.2f}")
        
        if result.get('sensitivity_results'):
            print("\n✓ Budget sensitivity analysis completed")
            print(f"  Analyzed {len(result['sensitivity_results'])} budget points")
    else:
        print(f"\n✗ Portfolio Optimization failed: {response.status_code}")
        print(response.text)


def test_methods():
    """Test methods listing endpoint."""
    print("\n" + "="*60)
    print("Testing Methods Listing")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/methods")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Methods listing successful!")
        print(f"\nAvailable Methods: {result['total_methods']}")
        for method in result['methods']:
            print(f"\n{method['name']} ({method['id']})")
            print(f"  Description: {method['description']}")
            print(f"  Best for: {method['best_for']}")
    else:
        print(f"\n✗ Methods listing failed: {response.status_code}")
        print(response.text)


def test_health():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("Testing Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Health check successful!")
        print(f"Status: {result['status']}")
        print(f"Module: {result['module']}")
        print(f"Version: {result['version']}")
        print(f"Solver Available: {result['solver_available']}")
    else:
        print(f"\n✗ Health check failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PMHelper Selection API Test Suite")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    
    try:
        # Test each endpoint
        test_health()
        test_methods()
        test_ahp()
        test_linear_scoring()
        test_benefit_cost()
        test_portfolio()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {e}")
