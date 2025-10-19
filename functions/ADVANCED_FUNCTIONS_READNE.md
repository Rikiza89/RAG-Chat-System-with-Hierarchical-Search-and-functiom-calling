# 🧠 Advanced Problem-Solving Functions

Powerful functions for solving complex, nested problems with automated file generation and visualization.

## 🎯 What's Included

### 1. **Solver** (`functions/solver/advanced.py`)
Solve optimization, dependency, scheduling, and resource allocation problems.

### 2. **Workflow Orchestrator** (`functions/workflow/orchestrator.py`)
Plan and visualize complex workflows with dependency management.

### 3. **Decision Builder** (`functions/decision/builder.py`)
Multi-criteria decision analysis with sensitivity testing.

## 🚀 Quick Start

### Installation
```bash
pip install scipy numpy

# Copy function files
cp functions/solver/advanced.py functions/solver/
cp functions/workflow/orchestrator.py functions/workflow/
cp functions/decision/builder.py functions/decision/

# Restart app
python app.py
```

### Test Functions
```bash
# Interactive demo
python test_advanced_functions.py

# Create sample data
python test_advanced_functions.py create-samples

# Verify loaded
python manage_functions.py list | grep -E "(solver|workflow|decision)"
```

## 📊 Usage Examples

### Example 1: Plan Project Timeline
```
Question: Plan deployment of 5 microservices with dependencies

<run:solver/advanced problem_type="dependency" data='{"tasks": {...}}' output_format="html">

Output:
- Optimal deployment order
- Critical path: 45 minutes
- Parallel execution saves 15 minutes
- HTML report saved
```

### Example 2: Allocate Budget
```
Question: Allocate $500K across 4 competing projects

<run:solver/advanced problem_type="resource_allocation" data='{"resources": {...}, "projects": [...]}'>

Output:
- Selected projects by ROI
- Expected value: $950K
- ROI: 2.1x
- Remaining resources tracked
```

### Example 3: Choose Technology
```
Question: Should we use React, Vue, or Angular?

<run:decision/builder problem_description="Framework selection" criteria='[...]' options='[...]'>

Output:
- Winner: React (score: 8.5/10)
- Confidence: 75/100
- Sensitivity: Stable
- Detailed HTML report
```

### Example 4: Plan Complex Workflow
```
Question: Optimize our data pipeline workflow

<run:workflow/orchestrator workflow_definition='{"name": "Pipeline", "steps": [...]}'>

Output:
- Execution plan with 4 parallel levels
- Sequential: 60min → Parallel: 40min
- 33% time savings
- Critical path identified
- ASCII diagram + reports
```

## 📁 Output Files

All functions create organized outputs:

```
solutions/              # Solver outputs
├── optimization_20250118_143022.json
├── dependency_20250118_143045.html
└── scheduling_20250118_143108.md

workflows/              # Workflow plans
├── data_pipeline_20250118_143200.json
└── data_pipeline_20250118_143200.md

decisions/             # Decision reports
├── framework_selection_20250118_143300.html
└── database_choice_20250118_143330.json
```

## 🎨 Output Formats

### JSON
Machine-readable, API-friendly
```json
{
  "status": "solved",
  "solution": {...},
  "file": "solutions/problem.json"
}
```

### HTML
Beautiful reports for stakeholders
- Styled tables
- Color-coded results
- Recommendations
- Downloadable

### Markdown
Version-control friendly documentation
- Plaintext
- GitHub-compatible
- Easy to diff

## 🔗 Chaining Functions

Combine functions for powerful workflows:

```
Step 1: Extract data from Excel
<run:excel/process filepath="projects.xlsx">

Step 2: Plan workflow
<run:workflow/orchestrator workflow_definition=extracted_data>

Step 3: Allocate resources
<run:solver/advanced problem_type="resource_allocation" data=workflow_results>

Step 4: Generate HTML report
<run:html/create_html_report data=final_results title="Project Plan">
```

## 💡 Real-World Use Cases

| Use Case | Function | Output |
|----------|----------|--------|
| Sprint planning | `workflow/orchestrator` | Task order, timeline |
| Budget allocation | `solver/advanced` (resource_allocation) | Project selection, ROI |
| Tech stack decision | `decision/builder` | Scored options, recommendations |
| Microservices deployment | `solver/advanced` (dependency) | Deployment order, critical path |
| Feature prioritization | `decision/builder` | Ranked features, confidence |
| Resource scheduling | `solver/advanced` (scheduling) | Timeline, utilization |

## 🎓 Learning Path

1. **Start Simple:**
   ```bash
   python test_advanced_functions.py
   # Try test #1: Dependency Resolution
   ```

2. **Use Sample Data:**
   ```bash
   python test_advanced_functions.py create-samples
   # Load test_data/sample_workflow.json
   ```

3. **Web Interface:**
   - Upload sample JSON to documents/
   - Ask: "Analyze the workflow in sample_workflow.json"
   - Add: `<run:workflow/orchestrator ...>`

4. **CLI Testing:**
   ```bash
   python manage_functions.py run solver/advanced \
     problem_type="dependency" \
     data='{"tasks": {...}}'
   ```

5. **Integration:**
   - Combine with Excel functions
   - Chain with HTML report generation
   - Use in RAG queries

## 📚 Documentation

- **Full Guide:** `ADVANCED_FUNCTIONS_GUIDE.md`
- **Office Functions:** `OFFICE_FUNCTIONS_GUIDE.md`
- **Examples:** `OFFICE_FUNCTIONS_EXAMPLES.md`

## 🔧 Troubleshooting

**Functions not loading:**
```bash
# Check they exist
ls -la functions/solver/advanced.py
ls -la functions/workflow/orchestrator.py
ls -la functions/decision/builder.py

# Restart app
python app.py

# Verify
python manage_functions.py list
```

**scipy/numpy errors:**
```bash
pip install --upgrade scipy numpy
```

**Circular dependency detected:**
- Check your workflow definition
- Ensure no task depends on itself (directly or indirectly)
- Use `has_cycle()` to validate before running

**File output errors:**
```bash
# Create output directories
mkdir -p solutions workflows decisions reports

# Check permissions
chmod 755 solutions workflows decisions
```

## 🎯 Best Practices

### 1. Start with Small Problems
Test with 3-5 items before scaling to 50+

### 2. Validate Input Data
```python
# Bad
data = {"tasks": {...}}  # Missing required fields

# Good
data = {
    "tasks": {
        "A": {"duration": 5, "depends_on": []}
    }
}
```

### 3. Review Generated Reports
Always check HTML/Markdown outputs for insights

### 4. Save Important Results
Move critical reports from `solutions/` to permanent storage

### 5. Iterate and Refine
Use recommendations to improve your inputs

## 🔥 Advanced Patterns

### Pattern 1: What-If Analysis
```python
# Run base case
base = <run:decision/builder ...>

# Modify criteria weights
modified_criteria = adjust_weights(base.criteria, "Performance", +0.1)

# Re-run
alternative = <run:decision/builder criteria=modified_criteria ...>

# Compare results
```

### Pattern 2: Multi-Stage Planning
```python
# Stage 1: High-level workflow
high_level = <run:workflow/orchestrator workflow=main_workflow>

# Stage 2: Expand critical path steps
for step in high_level.critical_path:
    detailed = <run:workflow/orchestrator workflow=sub_workflows[step]>

# Stage 3: Resource allocation
allocation = <run:solver/advanced problem_type="resource_allocation" data=combined_plan>
```

### Pattern 3: Decision Validation
```python
# Make decision
decision = <run:decision/builder ...>

# If confidence < 70, run sensitivity analysis
if decision.confidence_score < 70:
    # Test extreme scenarios
    scenarios = create_extreme_scenarios(decision.options)
    comparison = <run:decision/compare_scenarios scenarios=scenarios>
```

## 📊 Performance Guidelines

| Problem Size | Response Time | Recommendation |
|--------------|---------------|----------------|
| 1-10 items | < 1s | All formats OK |
| 10-50 items | 1-5s | Use JSON for speed |
| 50-100 items | 5-15s | Consider batching |
| 100+ items | 15s+ | Break into sub-problems |

## 🛡️ Limitations

**Optimization Solver:**
- Linear problems only (current implementation)
- For complex non-linear problems, use specialized tools
- Constraint parsing is simplified

**Workflow Orchestrator:**
- Assumes deterministic durations
- No resource constraints (use scheduling for that)
- No probabilistic modeling

**Decision Builder:**
- Assumes independent criteria
- No fuzzy logic
- Weights must sum to 1.0

## 🚀 Extending Functions

### Add Custom Solver Type

```python
# In solver/advanced.py

def solve_custom_problem(data):
    """Your custom solver logic"""
    # Process data
    # Calculate solution
    return solution

# Register in run()
solvers = {
    'optimization': solve_optimization,
    'custom': solve_custom_problem  # Add this
}
```

### Add Custom Decision Criteria

```python
# In decision/builder.py

def custom_scoring(options, criteria):
    """Custom scoring algorithm"""
    # Your logic
    return scored_options

# Use in evaluate_options()
```

## 💼 Enterprise Features

### Audit Trail
All functions log:
- Timestamp
- Input parameters
- Output results
- File locations

Check `function_calls.log` for history.

### Version Control
Save generated reports to git:
```bash
git add solutions/ workflows/ decisions/
git commit -m "Project planning results $(date)"
```

### Team Collaboration
Share output files:
- HTML reports: Email to stakeholders
- JSON files: API integration
- Markdown: Documentation

## 🔗 API Integration

### REST API
```bash
# Run solver via API
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{
    "name": "solver/advanced",
    "kwargs": {
      "problem_type": "dependency",
      "data": {...}
    }
  }'
```

### Python Script
```python
import requests

result = requests.post('http://localhost:5000/run_function', json={
    'name': 'workflow/orchestrator',
    'kwargs': {
        'workflow_definition': workflow_data,
        'execute': False
    }
}).json()

print(f"Saved to: {result['saved_to']}")
```

## 📈 Metrics & Analytics

Track function usage:
```bash
# Count executions
grep "solver/advanced" function_calls.log | wc -l

# Find popular problem types
grep "problem_type" function_calls.log | cut -d'"' -f4 | sort | uniq -c

# Average execution time
grep "solver/advanced" function_calls.log | \
  jq -r '.result' | grep -o '[0-9.]*' | \
  awk '{sum+=$1} END {print sum/NR}'
```

## 🎓 Learning Resources

### Example Problems

**Beginner:**
1. 3-task dependency chain
2. 2-option decision with 3 criteria
3. 5-step linear workflow

**Intermediate:**
1. 10-task project with parallelization
2. 5-option decision with sensitivity
3. Resource allocation across 4 projects

**Advanced:**
1. 50+ task nested workflow
2. Multi-stage decision with scenarios
3. Combined optimization + scheduling

### Templates

Located in `test_data/`:
- `sample_workflow.json`
- `sample_decision.json`
- `sample_allocation.json`

Copy and modify for your needs.

## 🤝 Contributing

Add your own solvers:
1. Create new function in appropriate directory
2. Follow existing patterns
3. Add docstrings
4. Test with `manage_functions.py`
5. Document in guide

## 📞 Support

**Issues with functions:**
1. Check logs: `tail -f function_calls.log`
2. Validate input data structure
3. Try with sample data first
4. Review generated error messages

**Need help:**
1. Read `ADVANCED_FUNCTIONS_GUIDE.md`
2. Run `python test_advanced_functions.py`
3. Check function docstrings
4. Review output files for insights

## ✅ Success Checklist

Before using in production:

- [ ] Functions load correctly (`manage_functions.py list`)
- [ ] Tested with sample data
- [ ] Output directories created and writable
- [ ] scipy/numpy installed
- [ ] Reviewed generated reports
- [ ] Understood confidence scores
- [ ] Know where files are saved
- [ ] Can chain functions together

## 🎉 Summary

You now have enterprise-grade problem-solving capabilities:

✅ **Optimization** - Maximize/minimize with constraints
✅ **Dependencies** - Critical path, parallel execution  
✅ **Scheduling** - Resource-aware task planning
✅ **Allocation** - ROI-based project selection
✅ **Workflows** - Complex orchestration with visualization
✅ **Decisions** - Multi-criteria analysis with confidence
✅ **Reports** - Professional HTML/Markdown/JSON outputs
✅ **Integration** - Works with your RAG system

Start solving complex problems today! 🚀
