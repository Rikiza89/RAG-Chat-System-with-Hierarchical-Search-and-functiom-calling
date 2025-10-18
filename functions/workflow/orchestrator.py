"""
Complex workflow orchestration and nested problem solving
Creates detailed execution plans with visualization
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

def run(workflow_definition, execute=False):
    """
    Orchestrate complex multi-step workflow
    
    Args:
        workflow_definition: Dict defining workflow steps
        execute: If True, actually execute steps (default: plan only)
    
    Example:
    {
        "name": "Data Processing Pipeline",
        "steps": [
            {"id": "extract", "type": "data_extraction", "depends_on": []},
            {"id": "transform", "type": "data_transform", "depends_on": ["extract"]},
            {"id": "analyze", "type": "analysis", "depends_on": ["transform"]},
            {"id": "report", "type": "generate_report", "depends_on": ["analyze"]}
        ]
    }
    """
    workflow_name = workflow_definition.get('name', 'Unnamed Workflow')
    steps = workflow_definition.get('steps', [])
    
    # Build dependency graph
    graph = build_dependency_graph(steps)
    
    # Detect cycles
    if has_cycle(graph):
        return {
            "status": "error",
            "message": "Circular dependency detected in workflow",
            "graph": graph
        }
    
    # Determine execution order
    execution_order = topological_sort(graph, steps)
    
    # Calculate execution levels (for parallelization)
    levels = calculate_execution_levels(steps, execution_order)
    
    # Estimate time and resources
    estimates = estimate_execution(steps, levels)
    
    # Generate execution plan
    plan = {
        "workflow_name": workflow_name,
        "total_steps": len(steps),
        "execution_order": execution_order,
        "parallel_levels": levels,
        "estimates": estimates,
        "visualization": generate_workflow_diagram(steps, execution_order),
        "critical_path": identify_critical_path(steps, execution_order),
        "optimizations": suggest_optimizations(steps, levels)
    }
    
    # Execute if requested
    if execute:
        execution_results = execute_workflow(steps, execution_order)
        plan['execution_results'] = execution_results
    
    # Save plan
    filepath = save_workflow_plan(workflow_name, plan)
    plan['saved_to'] = filepath
    
    return plan


def build_dependency_graph(steps):
    """Build dependency graph from steps"""
    graph = {}
    for step in steps:
        graph[step['id']] = step.get('depends_on', [])
    return graph


def has_cycle(graph):
    """Detect cycles using DFS"""
    def dfs(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    visited = set()
    for node in graph:
        if node not in visited:
            if dfs(node, visited, set()):
                return True
    return False


def topological_sort(graph, steps):
    """Topological sort for execution order"""
    in_degree = {step['id']: 0 for step in steps}
    
    for node in graph:
        for dep in graph[node]:
            in_degree[node] += 1
    
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for other_node in graph:
            if node in graph[other_node]:
                in_degree[other_node] -= 1
                if in_degree[other_node] == 0:
                    queue.append(other_node)
    
    return result


def calculate_execution_levels(steps, execution_order):
    """Calculate which steps can run in parallel"""
    step_dict = {s['id']: s for s in steps}
    levels = {}
    level_num = 0
    
    processed = set()
    remaining = set(execution_order)
    
    while remaining:
        # Find steps with all dependencies processed
        current_level = []
        for step_id in remaining:
            deps = step_dict[step_id].get('depends_on', [])
            if all(d in processed for d in deps):
                current_level.append(step_id)
        
        if not current_level:
            break
        
        levels[f"Level_{level_num}"] = current_level
        processed.update(current_level)
        remaining -= set(current_level)
        level_num += 1
    
    return levels


def estimate_execution(steps, levels):
    """Estimate total execution time and resources"""
    step_dict = {s['id']: s for s in steps}
    
    # Default durations if not specified
    default_durations = {
        'data_extraction': 10,
        'data_transform': 15,
        'analysis': 20,
        'generate_report': 5,
        'default': 10
    }
    
    total_sequential_time = 0
    total_parallel_time = 0
    
    for level_name, step_ids in levels.items():
        # Get max duration in this level (parallel execution)
        level_durations = []
        for step_id in step_ids:
            step = step_dict[step_id]
            duration = step.get('duration', 
                               default_durations.get(step.get('type', ''), 
                                                    default_durations['default']))
            level_durations.append(duration)
            total_sequential_time += duration
        
        total_parallel_time += max(level_durations) if level_durations else 0
    
    return {
        "sequential_execution_time": total_sequential_time,
        "parallel_execution_time": total_parallel_time,
        "time_saved": total_sequential_time - total_parallel_time,
        "speedup_factor": round(total_sequential_time / total_parallel_time, 2) if total_parallel_time > 0 else 1,
        "estimated_completion": (datetime.now() + timedelta(minutes=total_parallel_time)).strftime('%Y-%m-%d %H:%M:%S')
    }


def identify_critical_path(steps, execution_order):
    """Identify critical path through workflow"""
    step_dict = {s['id']: s for s in steps}
    
    # Simple heuristic: longest dependency chain
    def get_depth(step_id, memo={}):
        if step_id in memo:
            return memo[step_id]
        
        step = step_dict[step_id]
        deps = step.get('depends_on', [])
        
        if not deps:
            depth = 0
        else:
            depth = 1 + max(get_depth(d) for d in deps)
        
        memo[step_id] = depth
        return depth
    
    depths = {step_id: get_depth(step_id) for step_id in execution_order}
    max_depth = max(depths.values()) if depths else 0
    
    critical = [step_id for step_id, depth in depths.items() if depth == max_depth]
    
    return {
        "path": critical,
        "length": max_depth + 1,
        "recommendation": f"Focus optimization efforts on these {len(critical)} critical steps"
    }


def suggest_optimizations(steps, levels):
    """Suggest workflow optimizations"""
    suggestions = []
    
    # Check for bottlenecks
    for level_name, step_ids in levels.items():
        if len(step_ids) == 1:
            suggestions.append({
                "type": "bottleneck",
                "level": level_name,
                "step": step_ids[0],
                "suggestion": f"Step '{step_ids[0]}' blocks parallel execution. Consider splitting it."
            })
    
    # Check for under-utilized parallelism
    level_sizes = [len(step_ids) for step_ids in levels.values()]
    avg_parallelism = sum(level_sizes) / len(level_sizes) if level_sizes else 0
    
    if avg_parallelism < 2:
        suggestions.append({
            "type": "low_parallelism",
            "average": round(avg_parallelism, 2),
            "suggestion": "Low parallelism detected. Review dependencies to enable more concurrent execution."
        })
    
    # Check for long dependency chains
    if len(levels) > 5:
        suggestions.append({
            "type": "long_chain",
            "levels": len(levels),
            "suggestion": f"Workflow has {len(levels)} sequential levels. Consider consolidating steps."
        })
    
    return suggestions


def generate_workflow_diagram(steps, execution_order):
    """Generate ASCII workflow diagram"""
    diagram = []
    diagram.append("Workflow Execution Flow:")
    diagram.append("=" * 50)
    
    step_dict = {s['id']: s for s in steps}
    
    for i, step_id in enumerate(execution_order, 1):
        step = step_dict[step_id]
        deps = step.get('depends_on', [])
        
        # Show step
        diagram.append(f"\n{i}. [{step_id}] - {step.get('type', 'unknown')}")
        
        # Show dependencies
        if deps:
            diagram.append(f"   Depends on: {', '.join(deps)}")
        else:
            diagram.append("   (No dependencies - can start immediately)")
    
    return "\n".join(diagram)


def execute_workflow(steps, execution_order):
    """Execute workflow steps (simulation)"""
    results = []
    step_dict = {s['id']: s for s in steps}
    
    for step_id in execution_order:
        step = step_dict[step_id]
        
        # Simulate execution
        result = {
            "step_id": step_id,
            "type": step.get('type'),
            "status": "completed",
            "start_time": datetime.now().isoformat(),
            "duration": step.get('duration', 10),
            "output": f"Executed {step_id} successfully"
        }
        
        results.append(result)
    
    return {
        "total_executed": len(results),
        "total_time": sum(r['duration'] for r in results),
        "steps": results
    }


def save_workflow_plan(workflow_name, plan):
    """Save workflow plan to file"""
    os.makedirs('workflows', exist_ok=True)
    
    safe_name = workflow_name.replace(' ', '_').lower()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save as JSON
    filepath_json = f"workflows/{safe_name}_{timestamp}.json"
    with open(filepath_json, 'w') as f:
        json.dump(plan, f, indent=2)
    
    # Save as Markdown report
    filepath_md = f"workflows/{safe_name}_{timestamp}.md"
    with open(filepath_md, 'w') as f:
        f.write(format_workflow_markdown(workflow_name, plan))
    
    return filepath_json


def format_workflow_markdown(workflow_name, plan):
    """Format workflow plan as Markdown report"""
    md = f"# {workflow_name}\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    md += "## Execution Summary\n\n"
    md += f"- **Total Steps:** {plan['total_steps']}\n"
    md += f"- **Sequential Time:** {plan['estimates']['sequential_execution_time']} min\n"
    md += f"- **Parallel Time:** {plan['estimates']['parallel_execution_time']} min\n"
    md += f"- **Time Saved:** {plan['estimates']['time_saved']} min\n"
    md += f"- **Speedup:** {plan['estimates']['speedup_factor']}x\n\n"
    
    md += "## Execution Order\n\n"
    for i, step_id in enumerate(plan['execution_order'], 1):
        md += f"{i}. `{step_id}`\n"
    
    md += "\n## Parallel Execution Levels\n\n"
    for level, steps in plan['parallel_levels'].items():
        md += f"**{level}:** {', '.join(steps)}\n"
    
    md += "\n## Critical Path\n\n"
    md += f"**Path:** {' → '.join(plan['critical_path']['path'])}\n"
    md += f"**Length:** {plan['critical_path']['length']} steps\n\n"
    
    if plan.get('optimizations'):
        md += "## Optimization Suggestions\n\n"
        for opt in plan['optimizations']:
            md += f"- **{opt['type']}:** {opt['suggestion']}\n"
    
    md += "\n## Visualization\n\n```\n"
    md += plan['visualization']
    md += "\n```\n"
    
    return md


def analyze_workflow_complexity(workflow_definition):
    """Analyze workflow complexity metrics"""
    steps = workflow_definition.get('steps', [])
    graph = build_dependency_graph(steps)
    
    # Calculate metrics
    metrics = {
        "total_nodes": len(steps),
        "total_edges": sum(len(deps) for deps in graph.values()),
        "avg_dependencies": sum(len(deps) for deps in graph.values()) / len(steps) if steps else 0,
        "max_dependencies": max((len(deps) for deps in graph.values()), default=0),
        "independent_nodes": sum(1 for deps in graph.values() if len(deps) == 0),
        "has_cycles": has_cycle(graph),
        "complexity_score": calculate_complexity_score(graph)
    }
    
    return metrics


def calculate_complexity_score(graph):
    """Calculate workflow complexity score (0-100)"""
    if not graph:
        return 0
    
    # Factors: number of nodes, edges, max dependencies, depth
    n_nodes = len(graph)
    n_edges = sum(len(deps) for deps in graph.values())
    max_deps = max((len(deps) for deps in graph.values()), default=0)
    
    # Weighted score
    node_score = min(n_nodes * 2, 30)  # Max 30 points
    edge_score = min(n_edges * 3, 40)  # Max 40 points
    depth_score = min(max_deps * 10, 30)  # Max 30 points
    
    return min(node_score + edge_score + depth_score, 100)


def create_nested_workflow(base_workflow, sub_workflows):
    """
    Create complex nested workflow from sub-workflows
    
    Args:
        base_workflow: Main workflow definition
        sub_workflows: Dict of step_id -> sub_workflow_definition
    
    Returns:
        Expanded workflow with nested steps
    """
    expanded_steps = []
    
    for step in base_workflow.get('steps', []):
        step_id = step['id']
        
        if step_id in sub_workflows:
            # Expand this step into sub-workflow
            sub_workflow = sub_workflows[step_id]
            for sub_step in sub_workflow.get('steps', []):
                # Prefix sub-step IDs
                expanded_step = sub_step.copy()
                expanded_step['id'] = f"{step_id}_{sub_step['id']}"
                
                # Update dependencies
                if 'depends_on' in expanded_step:
                    expanded_step['depends_on'] = [
                        f"{step_id}_{dep}" for dep in expanded_step['depends_on']
                    ]
                
                expanded_steps.append(expanded_step)
        else:
            expanded_steps.append(step)
    
    return {
        "name": f"{base_workflow.get('name', 'Workflow')} (Expanded)",
        "steps": expanded_steps
      }
