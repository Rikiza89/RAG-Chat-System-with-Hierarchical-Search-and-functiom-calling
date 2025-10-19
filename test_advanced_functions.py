#!/usr/bin/env python3
"""
Test suite for advanced problem-solving functions
"""

import sys
import json

def test_dependency_solver():
    """Test dependency resolution"""
    print("\n" + "="*60)
    print("TEST 1: Dependency Resolution")
    print("="*60)
    
    data = {
        "tasks": {
            "setup_db": {"duration": 5, "depends_on": []},
            "setup_cache": {"duration": 3, "depends_on": []},
            "deploy_auth": {"duration": 8, "depends_on": ["setup_db"]},
            "deploy_api": {"duration": 10, "depends_on": ["setup_db", "deploy_auth"]},
            "deploy_frontend": {"duration": 7, "depends_on": ["deploy_api"]}
        }
    }
    
    print("\nProblem: Microservices Deployment Order")
    print(json.dumps(data, indent=2))
    
    print("\nCommand:")
    print('python manage_functions.py run solver/advanced problem_type="dependency" data=\'...\' output_format="json"')
    
    print("\nExpected Output:")
    print("- Execution order: setup_db, setup_cache, deploy_auth, deploy_api, deploy_frontend")
    print("- Critical path identified")
    print("- Parallel opportunities: setup_db and setup_cache")
    print("- Total duration: 33 time units")


def test_resource_allocation():
    """Test resource allocation"""
    print("\n" + "="*60)
    print("TEST 2: Resource Allocation")
    print("="*60)
    
    data = {
        "resources": {"budget": 100000, "people": 10, "time": 6},
        "projects": [
            {
                "name": "Website Redesign",
                "required": {"budget": 30000, "people": 3, "time": 4},
                "value": 60000
            },
            {
                "name": "Mobile App",
                "required": {"budget": 50000, "people": 5, "time": 6},
                "value": 100000
            },
            {
                "name": "Marketing Campaign",
                "required": {"budget": 25000, "people": 2, "time": 3},
                "value": 40000
            }
        ]
    }
    
    print("\nProblem: Project Portfolio Selection")
    print(f"Available: ${data['resources']['budget']}, {data['resources']['people']} people, {data['resources']['time']} months")
    
    print("\nExpected Output:")
    print("- Allocate by ROI: Mobile App (2.0x), Website (2.0x), Marketing (1.6x)")
    print("- Total value: ~$200,000")
    print("- Remaining resources shown")
    print("- HTML report with recommendations")


def test_workflow_orchestration():
    """Test workflow orchestration"""
    print("\n" + "="*60)
    print("TEST 3: Workflow Orchestration")
    print("="*60)
    
    workflow = {
        "name": "Data Pipeline",
        "steps": [
            {"id": "extract", "type": "extraction", "depends_on": [], "duration": 10},
            {"id": "clean", "type": "cleaning", "depends_on": ["extract"], "duration": 15},
            {"id": "analyze", "type": "analysis", "depends_on": ["clean"], "duration": 20},
            {"id": "visualize", "type": "visualization", "depends_on": ["analyze"], "duration": 8},
            {"id": "report", "type": "reporting", "depends_on": ["visualize"], "duration": 5}
        ]
    }
    
    print("\nProblem: Data Processing Pipeline")
    print(f"Steps: {len(workflow['steps'])}")
    
    print("\nExpected Output:")
    print("- Execution order determined")
    print("- Sequential time: 58 min")
    print("- Parallel time: 58 min (no parallelization in this linear workflow)")
    print("- Critical path: extract → clean → analyze → visualize → report")
    print("- ASCII diagram generated")
    print("- Files saved: workflows/data_pipeline_*.json and *.md")


def test_decision_analysis():
    """Test multi-criteria decision analysis"""
    print("\n" + "="*60)
    print("TEST 4: Decision Analysis")
    print("="*60)
    
    data = {
        "problem": "Cloud Provider Selection",
        "criteria": [
            {"name": "Cost", "weight": 0.30},
            {"name": "Performance", "weight": 0.25},
            {"name": "Reliability", "weight": 0.25},
            {"name": "Support", "weight": 0.20}
        ],
        "options": [
            {
                "name": "AWS",
                "scores": {"Cost": 6, "Performance": 9, "Reliability": 9, "Support": 8}
            },
            {
                "name": "Azure",
                "scores": {"Cost": 7, "Performance": 8, "Reliability": 8, "Support": 9}
            },
            {
                "name": "GCP",
                "scores": {"Cost": 8, "Performance": 8, "Reliability": 7, "Support": 7}
            }
        ]
    }
    
    print("\nProblem: Choose Cloud Provider")
    print(f"Criteria: {[c['name'] for c in data['criteria']]}")
    print(f"Options: {[o['name'] for o in data['options']]}")
    
    print("\nExpected Output:")
    print("- Best option: AWS or Azure (scores close)")
    print("- Confidence score: ~70/100")
    print("- Sensitivity analysis: stable")
    print("- Recommendations with reasoning")
    print("- HTML report with visualization")


def test_scheduling():
    """Test resource-constrained scheduling"""
    print("\n" + "="*60)
    print("TEST 5: Task Scheduling")
    print("="*60)
    
    data = {
        "tasks": [
            {"id": "T1", "duration": 3, "resources": ["R1"], "priority": 2},
            {"id": "T2", "duration": 2, "resources": ["R1"], "priority": 1},
            {"id": "T3", "duration": 4, "resources": ["R2"], "priority": 3},
            {"id": "T4", "duration": 2, "resources": ["R1", "R2"], "priority": 1}
        ],
        "resources": {"R1": 1, "R2": 1},
        "deadline": 15
    }
    
    print("\nProblem: Schedule tasks with limited resources")
    print(f"Tasks: {len(data['tasks'])}")
    print(f"Resources: {data['resources']}")
    print(f"Deadline: {data['deadline']} time units")
    
    print("\nExpected Output:")
    print("- Optimal schedule respecting resource constraints")
    print("- Deadline met: Yes/No")
    print("- Resource utilization percentages")
    print("- Gantt chart data for visualization")


def run_interactive_demo():
    """Run interactive demo"""
    print("\n" + "="*60)
    print("Advanced Functions Interactive Demo")
    print("="*60)
    
    print("\nAvailable tests:")
    print("1. Dependency Resolution (microservices deployment)")
    print("2. Resource Allocation (project portfolio)")
    print("3. Workflow Orchestration (data pipeline)")
    print("4. Decision Analysis (cloud provider)")
    print("5. Task Scheduling (resource constraints)")
    print("6. Run all tests")
    
    try:
        choice = input("\nSelect test (1-6): ").strip()
        
        if choice == '1':
            test_dependency_solver()
        elif choice == '2':
            test_resource_allocation()
        elif choice == '3':
            test_workflow_orchestration()
        elif choice == '4':
            test_decision_analysis()
        elif choice == '5':
            test_scheduling()
        elif choice == '6':
            test_dependency_solver()
            test_resource_allocation()
            test_workflow_orchestration()
            test_decision_analysis()
            test_scheduling()
        else:
            print("Invalid choice")
            return
        
        print("\n" + "="*60)
        print("To actually run these functions:")
        print("="*60)
        print("\n1. Ensure functions are in functions/ directory")
        print("2. Restart app.py to load new functions")
        print("3. Use via web interface or CLI:")
        print("   python manage_functions.py run solver/advanced ...")
        print("\n4. Or in RAG queries:")
        print('   "Solve this dependency problem: <run:solver/advanced ...>"')
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled.")


def create_sample_data_files():
    """Create sample JSON files for testing"""
    import os
    
    os.makedirs('test_data', exist_ok=True)
    
    # Sample workflow
    workflow = {
        "name": "E-commerce Launch",
        "steps": [
            {"id": "setup_infra", "depends_on": [], "duration": 5},
            {"id": "backend_api", "depends_on": ["setup_infra"], "duration": 15},
            {"id": "frontend_app", "depends_on": ["setup_infra"], "duration": 12},
            {"id": "payment_integration", "depends_on": ["backend_api"], "duration": 8},
            {"id": "testing", "depends_on": ["backend_api", "frontend_app", "payment_integration"], "duration": 10},
            {"id": "deployment", "depends_on": ["testing"], "duration": 3}
        ]
    }
    
    with open('test_data/sample_workflow.json', 'w') as f:
        json.dump(workflow, f, indent=2)
    
    print("✅ Created test_data/sample_workflow.json")
    
    # Sample decision problem
    decision = {
        "problem": "CRM Software Selection",
        "criteria": [
            {"name": "Features", "weight": 0.35},
            {"name": "Ease of Use", "weight": 0.25},
            {"name": "Integration", "weight": 0.20},
            {"name": "Price", "weight": 0.20}
        ],
        "options": [
            {"name": "Salesforce", "scores": {"Features": 9, "Ease of Use": 7, "Integration": 9, "Price": 5}},
            {"name": "HubSpot", "scores": {"Features": 8, "Ease of Use": 9, "Integration": 8, "Price": 7}},
            {"name": "Zoho", "scores": {"Features": 7, "Ease of Use": 8, "Integration": 6, "Price": 9}}
        ]
    }
    
    with open('test_data/sample_decision.json', 'w') as f:
        json.dump(decision, f, indent=2)
    
    print("✅ Created test_data/sample_decision.json")
    
    # Sample resource allocation
    allocation = {
        "resources": {"budget": 250000, "engineers": 20, "months": 12},
        "projects": [
            {"name": "Cloud Migration", "required": {"budget": 100000, "engineers": 8, "months": 10}, "value": 200000},
            {"name": "Security Audit", "required": {"budget": 50000, "engineers": 3, "months": 6}, "value": 120000},
            {"name": "Mobile App v2", "required": {"budget": 80000, "engineers": 6, "months": 8}, "value": 180000},
            {"name": "AI Features", "required": {"budget": 120000, "engineers": 10, "months": 12}, "value": 250000}
        ]
    }
    
    with open('test_data/sample_allocation.json', 'w') as f:
        json.dump(allocation, f, indent=2)
    
    print("✅ Created test_data/sample_allocation.json")
    
    print("\n📁 Sample data files created in test_data/")
    print("Use these for testing the functions!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-samples":
        create_sample_data_files()
    else:
        run_interactive_demo()
