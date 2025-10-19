# Advanced Problem-Solving Functions Guide

## Overview

Three powerful function modules for solving complex, nested problems with automated report generation:

1. **`solver/advanced.py`** - Optimization, dependencies, scheduling, resource allocation
2. **`workflow/orchestrator.py`** - Complex workflow orchestration and visualization
3. **`decision/builder.py`** - Decision trees, scenario analysis, multi-criteria evaluation

## Installation

```bash
pip install scipy numpy
```

---

## 1. Advanced Solver (`solver/advanced.py`)

### Problem Types

#### Optimization Problems
```python
data = {
    "objective": "maximize",
    "target": "profit",
    "variables": {
        "x": {"min": 0, "max": 100},
        "y": {"min": 0, "max": 50}
    },
    "constraints": [
        {"expr": "2*x + y <= 100", "name": "budget"},
        {"expr": "x + 3*y <= 120", "name": "time"}
    ],
    "objective_function": "50*x + 40*y"
}
```

**Usage:**
```
<run:solver/advanced problem_type="optimization" data=data output_format="html">
```

**Output:**
- Optimal solution values
- Objective function value
- Constraints satisfaction
- Recommendations
- Saved to `solutions/optimization_TIMESTAMP.html`

#### Dependency Resolution
```python
data = {
    "tasks": {
        "A": {"duration": 2, "depends_on": []},
        "B": {"duration": 3, "depends_on": ["A"]},
        "C": {"duration": 1, "depends_on": ["A"]},
        "D": {"duration": 4, "depends_on": ["B", "C"]}
    }
}
```

**Usage:**
```
Analyze task dependencies: <run:solver/advanced problem_type="dependency" data=data>
```

**Output:**
- Execution order (topological sort)
- Critical path analysis
- Parallel execution opportunities
- Total duration estimate
- Optimization recommendations

#### Scheduling Problems
```python
data = {
    "tasks": [
        {"id": "T1", "duration": 2, "resources": ["R1"], "priority": 1},
        {"id": "T2", "duration": 3, "resources": ["R1", "R2"], "priority": 2}
    ],
    "resources": {"R1": 1, "R2": 1},
    "deadline": 10
}
```

**Features:**
- Resource-constrained scheduling
- Priority-based allocation
- Gantt chart data generation
- Resource utilization metrics

#### Resource Allocation
```python
data = {
    "resources": {"budget": 100000, "people": 10, "time": 6},
    "projects": [
        {"name": "P1", "required": {"budget": 30000, "people": 3, "time": 4}, "value": 50000},
        {"name": "P2", "required": {"budget": 50000, "people": 5, "time": 6}, "value": 80000}
    ]
}
```

**Features:**
- ROI-based project selection
- Greedy allocation algorithm
- Remaining resource tracking
- Investment recommendations

---

## 2. Workflow Orchestrator (`workflow/orchestrator.py`)

### Basic Workflow

```python
workflow = {
    "name": "Data Processing Pipeline",
    "steps": [
        {"id": "extract", "type": "data_extraction", "depends_on": [], "duration": 10},
        {"id": "transform", "type": "data_transform", "depends_on": ["extract"], "duration": 15},
        {"id": "analyze", "type": "analysis", "depends_on": ["transform"], "duration": 20},
        {"id": "report", "type": "generate_report", "depends_on": ["analyze"], "duration": 5}
    ]
}
```

**Usage:**
```
<run:workflow/orchestrator workflow_definition=workflow execute=false>
```

**Output:**
```json
{
  "workflow_name": "Data Processing Pipeline",
  "execution_order": ["extract", "transform", "analyze", "report"],
  "parallel_levels": {
    "Level_0": ["extract"],
    "Level_1": ["transform"],
    "Level_2": ["analyze"],
    "Level_3": ["report"]
  },
  "estimates": {
    "sequential_execution_time": 50,
    "parallel_execution_time": 50,
    "time_saved": 0,
    "speedup_factor": 1.0
  },
  "critical_path": {
    "path": ["report"],
    "length": 4
  },
  "saved_to": "workflows/data_processing_pipeline_TIMESTAMP.json"
}
```

### Parallel Workflow Example

```python
workflow = {
    "name": "Multi-Branch Pipeline",
    "steps": [
        {"id": "init", "depends_on": []},
        {"id": "branch_a", "depends_on": ["init"]},
        {"id": "branch_b", "depends_on": ["init"]},
        {"id": "branch_c", "depends_on": ["init"]},
        {"id": "merge", "depends_on": ["branch_a", "branch_b", "branch_c"]}
    ]
}
```

**Features:**
- Parallel execution detection
- Critical path identification
- Bottleneck analysis
- Optimization suggestions
- Visual ASCII diagram

### Nested Workflows

```python
base_workflow = {
    "name": "Main Process",
    "steps": [
        {"id": "prepare", "depends_on": []},
        {"id": "process", "depends_on": ["prepare"]},
        {"id": "finalize", "depends_on": ["process"]}
    ]
}

sub_workflows = {
    "process": {
        "steps": [
            {"id": "validate", "depends_on": []},
            {"id": "transform", "depends_on": ["validate"]},
            {"id": "verify", "depends_on": ["transform"]}
        ]
    }
}
```

**Usage:**
```python
from workflow.orchestrator import create_nested_workflow

expanded = create_nested_workflow(base_workflow, sub_workflows)
# Result: prepare -> process_validate -> process_transform -> process_verify -> finalize
```

---

## 3. Decision Builder (`decision/builder.py`)

### Multi-Criteria Decision Analysis

```python
problem = {
    "problem": "Choose development framework",
    "criteria": [
        {"name": "Performance", "weight": 0.3},
        {"name": "Learning Curve", "weight": 0.2},
        {"name": "Community Support", "weight": 0.25},
        {"name": "Cost", "weight": 0.25}
    ],
    "options": [
        {"name": "React", "scores": {"Performance": 8, "Learning Curve": 7, "Community Support": 9, "Cost": 10}},
        {"name": "Vue", "scores": {"Performance": 7, "Learning Curve": 9, "Community Support": 7, "Cost": 10}},
        {"name": "Angular", "scores": {"Performance": 9, "Learning Curve": 5, "Community Support": 8, "Cost": 10}}
    ]
}
```

**Usage:**
```
<run:decision/builder problem_description="Choose development framework" criteria=problem.criteria options=problem.options>
```

**Output:**
```json
{
  "best_option": "React",
  "confidence_score": 75.3,
  "evaluation": [
    {
      "name": "React",
      "total_score": 8.55,
      "score_breakdown": {
        "Performance": {"raw_score": 8, "weight": 0.3, "weighted_score": 2.4},
        "Learning Curve": {"raw_score": 7, "weight": 0.2, "weighted_score": 1.4}
      }
    }
  ],
  "sensitivity_analysis": {
    "overall_stability": "stable",
    "criterion_sensitivity": {
      "Performance": {"average_ranking_changes": 0.5, "stability": "stable"}
    }
  },
  "recommendations": [
    {
      "type": "primary",
      "recommendation": "Choose 'React' with total score of 8.55",
      "confidence": "high"
    }
  ]
}
```

### Scenario Comparison

```python
scenarios = [
    {"name": "Optimistic", "revenue": 100000, "cost": 50000, "risk": "low", "probability": 0.2},
    {"name": "Realistic", "revenue": 75000, "cost": 50000, "risk": "medium", "probability": 0.6},
    {"name": "Pessimistic", "revenue": 50000, "cost": 50000, "risk": "high", "probability": 0.2}
]
```

**Usage:**
```python
from decision.builder import compare_scenarios

comparison = compare_scenarios(scenarios)
```

**Output:**
- Best/worst case analysis
- Expected value calculation
- Risk-adjusted outcomes
- Probability-weighted results

---

## Real-World Examples

### Example 1: Project Planning

**Problem:** Plan software development project with dependencies

```python
workflow = {
    "name": "Software Release v2.0",
    "steps": [
        {"id": "requirements", "duration": 5, "depends_on": []},
        {"id": "design", "duration": 10, "depends_on": ["requirements"]},
        {"id": "backend_dev", "duration": 20, "depends_on": ["design"]},
        {"id": "frontend_dev", "duration": 15, "depends_on": ["design"]},
        {"id": "testing", "duration": 10, "depends_on": ["backend_dev", "frontend_dev"]},
        {"id": "deployment", "duration": 2, "depends_on": ["testing"]}
    ]
}
```

**Question:**
```
Plan the Software Release v2.0 project
<run:workflow/orchestrator workflow_definition=workflow>
```

**Results:**
- Total sequential time: 62 days
- Parallel execution time: 47 days (backend/frontend run concurrently)
- Time saved: 15 days (24% faster)
- Critical path: requirements → design → backend_dev → testing → deployment
- Report saved with Gantt chart data

### Example 2: Resource Allocation

**Problem:** Allocate limited budget across competing projects

```python
allocation_data = {
    "resources": {
        "budget": 500000,
        "engineers": 15,
        "months": 12
    },
    "projects": [
        {
            "name": "Mobile App",
            "required": {"budget": 200000, "engineers": 5, "months": 6},
            "value": 400000
        },
        {
            "name": "API Redesign",
            "required": {"budget": 150000, "engineers": 4, "months": 8},
            "value": 300000
        },
        {
            "name": "Analytics Dashboard",
            "required": {"budget": 100000, "engineers": 3, "months": 4},
            "value": 250000
        },
        {
            "name": "DevOps Automation",
            "required": {"budget": 180000, "engineers": 6, "months": 10},
            "value": 280000
        }
    ]
}
```

**Question:**
```
How should I allocate resources across these projects?
<run:solver/advanced problem_type="resource_allocation" data=allocation_data output_format="html">
```

**Output:**
- Allocated: Mobile App, Analytics Dashboard, API Redesign
- Total expected value: $950,000
- ROI: 2.11x
- Unallocated: DevOps Automation (insufficient remaining resources)
- HTML report with recommendations

### Example 3: Technology Decision

**Problem:** Choose database for new application

```python
decision_data = {
    "problem": "Select database technology",
    "criteria": [
        {"name": "Scalability", "weight": 0.35},
        {"name": "Query Performance", "weight": 0.25},
        {"name": "Operational Complexity", "weight": 0.15},
        {"name": "Cost", "weight": 0.15},
        {"name": "Team Expertise", "weight": 0.10}
    ],
    "options": [
        {
            "name": "PostgreSQL",
            "scores": {
                "Scalability": 7,
                "Query Performance": 8,
                "Operational Complexity": 6,
                "Cost": 10,
                "Team Expertise": 9
            }
        },
        {
            "name": "MongoDB",
            "scores": {
                "Scalability": 9,
                "Query Performance": 7,
                "Operational Complexity": 7,
                "Cost": 9,
                "Team Expertise": 6
            }
        },
        {
            "name": "DynamoDB",
            "scores": {
                "Scalability": 10,
                "Query Performance": 6,
                "Operational Complexity": 8,
                "Cost": 7,
                "Team Expertise": 4
            }
        }
    ]
}
```

**Question:**
```
Help me choose a database
<run:decision/builder problem_description="Select database technology" criteria=decision_data.criteria options=decision_data.options output_format="html">
```

**Output:**
1. **Winner:** MongoDB (score: 7.95)
2. **Close second:** PostgreSQL (score: 7.75)
3. **Confidence:** 72/100 (moderate - scores are close)
4. **Sensitivity:** Stable overall, but sensitive to "Scalability" weight
5. **Recommendation:** Choose MongoDB if scalability is priority, PostgreSQL for team familiarity

### Example 4: Complex Dependency Resolution

**Problem:** Microservices deployment order

```python
services_data = {
    "tasks": {
        "database": {"duration": 5, "depends_on": []},
        "cache": {"duration": 3, "depends_on": []},
        "auth_service": {"duration": 8, "depends_on": ["database"]},
        "user_service": {"duration": 10, "depends_on": ["database", "auth_service"]},
        "product_service": {"duration": 12, "depends_on": ["database"]},
        "order_service": {"duration": 15, "depends_on": ["user_service", "product_service"]},
        "api_gateway": {"duration": 6, "depends_on": ["auth_service", "user_service", "product_service", "order_service"]},
        "frontend": {"duration": 7, "depends_on": ["api_gateway"]}
    }
}
```

**Question:**
```
What's the optimal deployment order for these microservices?
<run:solver/advanced problem_type="dependency" data=services_data output_format="markdown">
```

**Output:**
- **Execution order:** database, cache, auth_service, product_service, user_service, order_service, api_gateway, frontend
- **Critical path:** database → auth_service → user_service → order_service → api_gateway → frontend (58 units)
- **Parallel opportunities:**
  - Level 0: database, cache (can deploy simultaneously)
  - Level 2: product_service, user_service (parallel after auth_service)
- **Total duration:** 58 time units (sequential), 48 with parallelization
- **Recommendation:** Deploy database and cache first, then parallelize service deployments

---

## Advanced Patterns

### Pattern 1: Chained Problem Solving

```
Question: Plan project, allocate resources, then create decision tree

Step 1: Plan workflow
<run:workflow/orchestrator workflow_definition=project_plan>

Step 2: Allocate resources based on critical path
<run:solver/advanced problem_type="resource_allocation" data=resource_data>

Step 3: Make go/no-go decision
<run:decision/builder problem_description="Project approval" criteria=approval_criteria options=scenarios>
```

### Pattern 2: Nested Workflow Expansion

```python
# Main workflow
main = {
    "name": "Product Launch",
    "steps": [
        {"id": "development", "depends_on": []},
        {"id": "marketing", "depends_on": ["development"]},
        {"id": "launch", "depends_on": ["development", "marketing"]}
    ]
}

# Sub-workflows
subs = {
    "development": {
        "steps": [
            {"id": "design", "depends_on": []},
            {"id": "implement", "depends_on": ["design"]},
            {"id": "test", "depends_on": ["implement"]}
        ]
    },
    "marketing": {
        "steps": [
            {"id": "content", "depends_on": []},
            {"id": "ads", "depends_on": ["content"]},
            {"id": "pr", "depends_on": ["content"]}
        ]
    }
}

# Expand and analyze
expanded = create_nested_workflow(main, subs)
<run:workflow/orchestrator workflow_definition=expanded>
```

### Pattern 3: Sensitivity-Aware Decisions

```python
# Run decision analysis
decision_result = <run:decision/builder ...>

# Check confidence
if decision_result['confidence_score'] < 60:
    # Low confidence - run scenario comparison
    scenarios = generate_scenarios_from_top_options(decision_result['evaluation'])
    <run:decision/compare_scenarios scenarios=scenarios>
```

---

## Output Formats

### JSON Format
```json
{
  "status": "solved",
  "solution": { ... },
  "file": "solutions/problem_20250118_143022.json",
  "timestamp": "2025-01-18T14:30:22"
}
```

**Use for:** API integration, further processing

### HTML Format
```html
<!DOCTYPE html>
<html>
  <!-- Styled report with tables, charts, recommendations -->
</html>
```

**Use for:** Presentation, stakeholder reports, archiving

### Markdown Format
```markdown
# Problem Solution

## Summary
- Total steps: 10
- Duration: 45 minutes

## Recommendations
1. Focus on critical path
2. Parallelize steps A and B
```

**Use for:** Documentation, GitHub, version control

---

## CLI Testing

```bash
# Test optimization solver
python manage_functions.py run solver/advanced \
  problem_type="optimization" \
  data='{"objective":"maximize","variables":{"x":{"min":0,"max":100}}}'

# Test workflow orchestrator
python manage_functions.py run workflow/orchestrator \
  workflow_definition='{"name":"Test","steps":[{"id":"A","depends_on":[]}]}'

# Test decision builder
python manage_functions.py run decision/builder \
  problem_description="Test" \
  criteria='[{"name":"Cost","weight":0.5}]' \
  options='[{"name":"A","scores":{"Cost":8}}]'
```

---

## File Output Locations

All functions save results to organized directories:

```
project_root/
├── solutions/           # Solver outputs
│   ├── optimization_*.json
│   ├── dependency_*.html
│   └── scheduling_*.md
├── workflows/           # Workflow plans
│   ├── pipeline_*.json
│   └── pipeline_*.md
└── decisions/          # Decision reports
    ├── framework_*.html
    └── database_*.json
```

---

## Performance Tips

### Large Workflows (100+ steps)
- Use `execute=False` for planning only
- Break into sub-workflows
- Focus on critical path analysis

### Complex Optimization
- Simplify constraints when possible
- Use approximation for initial analysis
- Refine with detailed models

### Sensitivity Analysis
- Test ±10-20% weight variations
- Focus on top criteria
- Run for top 3-5 options only

---

## Integration with RAG System

### In Questions
```
I have a project with these tasks [data]. Help me plan the execution order.
<run:workflow/orchestrator workflow_definition=data>
```

### In Documents
Upload project plans, resource sheets, decision matrices to `documents/` and reference them:

```
Analyze the project plan in documents/projects/launch_plan.json
<run:workflow/orchestrator workflow_definition=@launch_plan.json>
```

### Chained with Other Functions
```
1. Extract data from Excel
   <run:excel/process filepath="projects.xlsx">

2. Build workflow from extracted data
   <run:workflow/orchestrator workflow_definition=extracted_data>

3. Generate HTML report
   <run:html/create_html_report data=workflow_result title="Project Plan">
```

---

## Error Handling

All functions return structured errors:

```json
{
  "error": "Circular dependency detected in workflow",
  "status": "unsolvable",
  "details": {
    "cycle": ["A", "B", "C", "A"]
  }
}
```

Common errors:
- Circular dependencies → Check task dependencies
- Invalid weights → Must sum to 1.0
- Missing data → Verify all required fields
- Infeasible constraints → Relax constraints or adjust bounds

---

## Best Practices

1. **Start Simple:** Test with small problems first
2. **Validate Input:** Check data structure before running
3. **Review Reports:** Read generated HTML/Markdown reports
4. **Iterate:** Use recommendations to refine approach
5. **Document:** Save all reports with meaningful names
6. **Combine Functions:** Chain multiple solvers for complex problems

---

## Summary

These advanced functions transform complex decision-making and planning challenges into structured, analyzable problems with:

- ✅ Automated report generation (HTML, JSON, Markdown)
- ✅ Visual workflow diagrams
- ✅ Sensitivity analysis
- ✅ Optimization recommendations
- ✅ Critical path identification
- ✅ Parallel execution detection
- ✅ Confidence scoring
- ✅ File-based outputs for archiving

Perfect for project planning, resource allocation, technology selection, and any complex decision involving multiple criteria and constraints.
