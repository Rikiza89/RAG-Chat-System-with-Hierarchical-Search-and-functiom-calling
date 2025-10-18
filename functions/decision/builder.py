"""
Decision tree and scenario analysis builder
Creates decision trees, evaluates scenarios, generates reports
"""

import os
import json
from datetime import datetime
from collections import defaultdict

def run(problem_description, criteria, options, output_format="html"):
    """
    Build decision tree and evaluate options
    
    Args:
        problem_description: Description of decision problem
        criteria: List of evaluation criteria with weights
        options: List of options to evaluate
        output_format: 'html', 'json', 'markdown'
    
    Example:
    {
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
    """
    # Validate inputs
    if not criteria or not options:
        return {"error": "Both criteria and options required"}
    
    # Calculate weighted scores
    evaluation = evaluate_options(criteria, options)
    
    # Generate decision tree
    tree = build_decision_tree(criteria, evaluation)
    
    # Perform sensitivity analysis
    sensitivity = sensitivity_analysis(criteria, options)
    
    # Generate recommendations
    recommendations = generate_recommendations(evaluation, sensitivity)
    
    # Create comprehensive report
    report = {
        "problem": problem_description,
        "timestamp": datetime.now().isoformat(),
        "criteria": criteria,
        "evaluation": evaluation,
        "decision_tree": tree,
        "sensitivity_analysis": sensitivity,
        "recommendations": recommendations,
        "best_option": evaluation[0]['name'] if evaluation else None,
        "confidence_score": calculate_confidence(evaluation, sensitivity)
    }
    
    # Save report
    filepath = save_decision_report(problem_description, report, output_format)
    report['saved_to'] = filepath
    
    return report


def evaluate_options(criteria, options):
    """Calculate weighted scores for all options"""
    results = []
    
    for option in options:
        weighted_sum = 0
        score_breakdown = {}
        
        for criterion in criteria:
            name = criterion['name']
            weight = criterion['weight']
            score = option['scores'].get(name, 0)
            
            weighted_score = score * weight
            weighted_sum += weighted_score
            
            score_breakdown[name] = {
                "raw_score": score,
                "weight": weight,
                "weighted_score": round(weighted_score, 2)
            }
        
        results.append({
            "name": option['name'],
            "total_score": round(weighted_sum, 2),
            "score_breakdown": score_breakdown,
            "metadata": option.get('metadata', {})
        })
    
    # Sort by total score (descending)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def build_decision_tree(criteria, evaluation):
    """Build decision tree structure"""
    tree = {
        "root": {
            "question": "What are your priorities?",
            "branches": []
        }
    }
    
    # Create branches based on dominant criteria
    for criterion in criteria:
        branch = {
            "criterion": criterion['name'],
            "weight": criterion['weight'],
            "top_options": []
        }
        
        # Find top options for this criterion
        for option in evaluation:
            criterion_score = option['score_breakdown'][criterion['name']]
            branch['top_options'].append({
                "name": option['name'],
                "score": criterion_score['raw_score'],
                "weighted_contribution": criterion_score['weighted_score']
            })
        
        # Sort by raw score for this criterion
        branch['top_options'].sort(key=lambda x: x['score'], reverse=True)
        branch['top_options'] = branch['top_options'][:3]  # Top 3
        
        tree['root']['branches'].append(branch)
    
    return tree


def sensitivity_analysis(criteria, options):
    """Analyze how sensitive rankings are to weight changes"""
    analysis = {
        "overall_stability": 0,
        "criterion_sensitivity": {}
    }
    
    base_evaluation = evaluate_options(criteria, options)
    base_ranking = [opt['name'] for opt in base_evaluation]
    
    # Test weight variations
    for i, criterion in enumerate(criteria):
        variations = []
        
        # Test +/- 20% weight change
        for delta in [-0.2, -0.1, 0.1, 0.2]:
            modified_criteria = criteria.copy()
            modified_criteria[i] = criterion.copy()
            modified_criteria[i]['weight'] += delta
            
            # Normalize weights
            total_weight = sum(c['weight'] for c in modified_criteria)
            for c in modified_criteria:
                c['weight'] /= total_weight
            
            new_evaluation = evaluate_options(modified_criteria, options)
            new_ranking = [opt['name'] for opt in new_evaluation]
            
            # Calculate ranking change
            changes = sum(1 for j in range(len(base_ranking)) 
                         if base_ranking[j] != new_ranking[j])
            
            variations.append({
                "weight_delta": delta,
                "ranking_changes": changes,
                "new_winner": new_ranking[0]
            })
        
        # Average sensitivity for this criterion
        avg_changes = sum(v['ranking_changes'] for v in variations) / len(variations)
        
        analysis['criterion_sensitivity'][criterion['name']] = {
            "average_ranking_changes": round(avg_changes, 2),
            "stability": "stable" if avg_changes < 1 else "sensitive",
            "variations": variations
        }
    
    # Overall stability
    total_changes = sum(
        sens['average_ranking_changes'] 
        for sens in analysis['criterion_sensitivity'].values()
    )
    analysis['overall_stability'] = "stable" if total_changes < len(criteria) else "sensitive"
    
    return analysis


def generate_recommendations(evaluation, sensitivity):
    """Generate decision recommendations"""
    recommendations = []
    
    # Top recommendation
    if evaluation:
        best = evaluation[0]
        recommendations.append({
            "type": "primary",
            "recommendation": f"Choose '{best['name']}' with total score of {best['total_score']}",
            "confidence": "high" if sensitivity['overall_stability'] == "stable" else "moderate",
            "reasoning": f"Scores highest across weighted criteria"
        })
    
    # Close alternatives
    if len(evaluation) > 1:
        best_score = evaluation[0]['total_score']
        close_alternatives = [
            opt for opt in evaluation[1:] 
            if abs(opt['total_score'] - best_score) < 1.0
        ]
        
        if close_alternatives:
            alt_names = ', '.join(opt['name'] for opt in close_alternatives)
            recommendations.append({
                "type": "alternative",
                "recommendation": f"Consider {alt_names} as close alternatives",
                "confidence": "moderate",
                "reasoning": "Scores are within 1 point of best option"
            })
    
    # Sensitivity warnings
    sensitive_criteria = [
        name for name, data in sensitivity['criterion_sensitivity'].items()
        if data['stability'] == 'sensitive'
    ]
    
    if sensitive_criteria:
        recommendations.append({
            "type": "caution",
            "recommendation": f"Rankings sensitive to: {', '.join(sensitive_criteria)}",
            "confidence": "low",
            "reasoning": "Small weight changes could alter rankings"
        })
    
    return recommendations


def calculate_confidence(evaluation, sensitivity):
    """Calculate confidence score for recommendation"""
    if not evaluation:
        return 0
    
    # Factor 1: Score separation (0-50 points)
    if len(evaluation) > 1:
        score_diff = evaluation[0]['total_score'] - evaluation[1]['total_score']
        separation_score = min(score_diff * 10, 50)
    else:
        separation_score = 50
    
    # Factor 2: Overall stability (0-50 points)
    stability_score = 50 if sensitivity['overall_stability'] == 'stable' else 25
    
    total = separation_score + stability_score
    return round(total, 1)


def compare_scenarios(scenarios):
    """
    Compare multiple scenarios side-by-side
    
    Args:
        scenarios: List of scenario dicts with outcomes
    
    Example:
    [
        {"name": "Optimistic", "revenue": 100000, "cost": 50000, "risk": "low"},
        {"name": "Realistic", "revenue": 75000, "cost": 50000, "risk": "medium"},
        {"name": "Pessimistic", "revenue": 50000, "cost": 50000, "risk": "high"}
    ]
    """
    comparison = {
        "scenarios": [],
        "best_case": None,
        "worst_case": None,
        "expected_value": 0
    }
    
    for scenario in scenarios:
        # Calculate net outcome
        revenue = scenario.get('revenue', 0)
        cost = scenario.get('cost', 0)
        net = revenue - cost
        
        scenario_result = {
            "name": scenario['name'],
            "revenue": revenue,
            "cost": cost,
            "net_outcome": net,
            "risk_level": scenario.get('risk', 'unknown'),
            "probability": scenario.get('probability', 1.0 / len(scenarios))
        }
        
        comparison['scenarios'].append(scenario_result)
    
    # Sort by net outcome
    sorted_scenarios = sorted(comparison['scenarios'], 
                             key=lambda x: x['net_outcome'], 
                             reverse=True)
    
    comparison['best_case'] = sorted_scenarios[0]
    comparison['worst_case'] = sorted_scenarios[-1]
    
    # Calculate expected value
    comparison['expected_value'] = sum(
        s['net_outcome'] * s['probability'] 
        for s in comparison['scenarios']
    )
    
    return comparison


def create_decision_matrix(options, criteria_scores):
    """
    Create visual decision matrix
    
    Args:
        options: List of option names
        criteria_scores: Dict of option -> criteria -> score
    
    Returns:
        ASCII matrix visualization
    """
    if not options or not criteria_scores:
        return "No data for matrix"
    
    # Get all criteria
    first_option = list(criteria_scores.keys())[0]
    criteria = list(criteria_scores[first_option].keys())
    
    # Build matrix
    matrix = []
    
    # Header
    header = "Option".ljust(20) + " | " + " | ".join(c.ljust(15) for c in criteria)
    matrix.append(header)
    matrix.append("-" * len(header))
    
    # Rows
    for option in options:
        row = option.ljust(20) + " | "
        scores = criteria_scores.get(option, {})
        row += " | ".join(
            str(scores.get(c, 0)).ljust(15) 
            for c in criteria
        )
        matrix.append(row)
    
    return "\n".join(matrix)


def save_decision_report(problem_description, report, output_format):
    """Save decision report to file"""
    os.makedirs('decisions', exist_ok=True)
    
    safe_name = problem_description.replace(' ', '_').lower()[:30]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'json':
        filepath = f"decisions/{safe_name}_{timestamp}.json"
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
    
    elif output_format == 'markdown':
        filepath = f"decisions/{safe_name}_{timestamp}.md"
        with open(filepath, 'w') as f:
            f.write(format_decision_markdown(report))
    
    elif output_format == 'html':
        filepath = f"decisions/{safe_name}_{timestamp}.html"
        with open(filepath, 'w') as f:
            f.write(format_decision_html(report))
    
    return filepath


def format_decision_markdown(report):
    """Format decision report as Markdown"""
    md = f"# Decision Analysis: {report['problem']}\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    md += "## Evaluation Results\n\n"
    md += "| Rank | Option | Total Score |\n"
    md += "|------|--------|-------------|\n"
    
    for i, option in enumerate(report['evaluation'], 1):
        md += f"| {i} | {option['name']} | {option['total_score']} |\n"
    
    md += "\n## Recommendations\n\n"
    for rec in report['recommendations']:
        md += f"### {rec['type'].upper()}\n"
        md += f"**{rec['recommendation']}**\n\n"
        md += f"*Confidence: {rec['confidence']}*\n\n"
        md += f"Reasoning: {rec['reasoning']}\n\n"
    
    md += f"\n## Confidence Score: {report['confidence_score']}/100\n\n"
    
    md += "## Sensitivity Analysis\n\n"
    md += f"**Overall Stability:** {report['sensitivity_analysis']['overall_stability']}\n\n"
    
    for criterion, data in report['sensitivity_analysis']['criterion_sensitivity'].items():
        md += f"- **{criterion}:** {data['stability']} "
        md += f"(avg changes: {data['average_ranking_changes']})\n"
    
    return md


def format_decision_html(report):
    """Format decision report as HTML"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Decision Analysis: {report['problem']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #4caf50; }}
        .caution {{ background: #fff3e0; border-left-color: #ff9800; }}
        .confidence {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        .stable {{ background: #4caf50; color: white; }}
        .sensitive {{ background: #ff9800; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Decision Analysis: {report['problem']}</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Evaluation Results</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Option</th>
                <th>Total Score</th>
            </tr>
"""
    
    for i, option in enumerate(report['evaluation'], 1):
        html += f"""
            <tr>
                <td>{i}</td>
                <td><strong>{option['name']}</strong></td>
                <td>{option['total_score']}</td>
            </tr>
"""
    
    html += """
        </table>
        
        <h2>Recommendations</h2>
"""
    
    for rec in report['recommendations']:
        css_class = "caution" if rec['type'] == "caution" else "recommendation"
        html += f"""
        <div class="{css_class}">
            <h3>{rec['type'].upper()}</h3>
            <p><strong>{rec['recommendation']}</strong></p>
            <p><em>Confidence: {rec['confidence']}</em></p>
            <p>{rec['reasoning']}</p>
        </div>
"""
    
    html += f"""
        <h2>Confidence Score</h2>
        <p class="confidence">{report['confidence_score']}/100</p>
        
        <h2>Sensitivity Analysis</h2>
        <p><strong>Overall Stability:</strong> 
        <span class="badge {report['sensitivity_analysis']['overall_stability']}">
            {report['sensitivity_analysis']['overall_stability']}
        </span></p>
    </div>
</body>
</html>
"""
    
    return html
