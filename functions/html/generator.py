"""
HTML File Generator - Create custom HTML files from user requests
Supports various templates and customization options
"""

import os
import json
from datetime import datetime
from pathlib import Path

def run(content, title="Generated Page", template="basic", output_path=None, **kwargs):
    """
    Generate HTML file based on user request
    
    Args:
        content: Main content (text, list, dict, or HTML string)
        title: Page title
        template: Template type ('basic', 'report', 'dashboard', 'blog', 'portfolio', 'landing')
        output_path: Where to save (default: reports/generated_TIMESTAMP.html)
        **kwargs: Additional customization options
            - theme: 'light' or 'dark' (default: 'light')
            - color: Primary color (default: '#667eea')
            - include_css: Custom CSS string
            - include_js: Custom JavaScript string
            - sections: List of sections for multi-section pages
    
    Returns:
        Path to generated HTML file
    
    Examples:
        # Simple text page
        <run:html/generator content="Hello World" title="My Page">
        
        # Report with data
        <run:html/generator content='{"sales": 10000, "profit": 2500}' 
                           title="Q1 Report" 
                           template="report">
        
        # Dashboard with sections
        <run:html/generator sections='[{"title": "Overview", "content": "..."}]'
                           title="Analytics Dashboard"
                           template="dashboard">
    """
    
    # Set default output path
    if output_path is None:
        os.makedirs('reports', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'reports/{title.lower().replace(" ", "_")}_{timestamp}.html'
    else:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # Get template
    templates = {
        'basic': generate_basic_template,
        'report': generate_report_template,
        'dashboard': generate_dashboard_template,
        'blog': generate_blog_template,
        'portfolio': generate_portfolio_template,
        'landing': generate_landing_template
    }
    
    generator = templates.get(template, generate_basic_template)
    
    # Generate HTML
    html_content = generator(content, title, **kwargs)
    
    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return f"✅ HTML file created: {output_path}"


def generate_basic_template(content, title, theme='light', color='#667eea', 
                            include_css='', include_js='', **kwargs):
    """Generate basic HTML template"""
    
    bg_color = '#ffffff' if theme == 'light' else '#1a1a1a'
    text_color = '#333333' if theme == 'light' else '#e0e0e0'
    
    # Process content
    if isinstance(content, dict):
        content_html = dict_to_html_table(content)
    elif isinstance(content, list):
        content_html = list_to_html_list(content)
    else:
        content_html = f"<p>{content}</p>"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {bg_color};
            color: {text_color};
            line-height: 1.6;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: {bg_color};
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: {color};
            margin-bottom: 30px;
            font-size: 2.5em;
            border-bottom: 3px solid {color};
            padding-bottom: 10px;
        }}
        
        .content {{
            margin-top: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: {color};
            color: white;
            font-weight: bold;
        }}
        
        tr:hover {{
            background: rgba(102, 126, 234, 0.1);
        }}
        
        ul, ol {{
            margin: 20px 0;
            padding-left: 40px;
        }}
        
        li {{
            margin: 10px 0;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}
        
        {include_css}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            {content_html}
        </div>
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        {include_js}
    </script>
</body>
</html>"""
    
    return html


def generate_report_template(content, title, theme='light', color='#667eea', **kwargs):
    """Generate professional report template"""
    
    # Parse content
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except:
            pass
    
    # Build sections
    sections_html = ""
    if isinstance(content, dict):
        for key, value in content.items():
            sections_html += f"""
            <div class="report-section">
                <h3>{key.replace('_', ' ').title()}</h3>
                <div class="report-value">{format_value(value)}</div>
            </div>
            """
    else:
        sections_html = f"<div class='report-section'>{content}</div>"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        
        .report-container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 60px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .report-header {{
            text-align: center;
            margin-bottom: 50px;
            border-bottom: 3px solid {color};
            padding-bottom: 30px;
        }}
        
        .report-header h1 {{
            color: {color};
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .report-date {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .report-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid {color};
            border-radius: 5px;
        }}
        
        .report-section h3 {{
            color: {color};
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        
        .report-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .report-footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #999;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .report-container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1>{title}</h1>
            <div class="report-date">{datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        
        {sections_html}
        
        <div class="report-footer">
            <p>Generated by RAG System</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html


def generate_dashboard_template(content, title, sections=None, **kwargs):
    """Generate interactive dashboard template"""
    
    if sections is None:
        sections = [{"title": "Overview", "content": str(content)}]
    elif isinstance(sections, str):
        try:
            sections = json.loads(sections)
        except:
            sections = [{"title": "Data", "content": sections}]
    
    cards_html = ""
    for i, section in enumerate(sections):
        cards_html += f"""
        <div class="dashboard-card">
            <h3>{section.get('title', f'Section {i+1}')}</h3>
            <div class="card-content">
                {format_value(section.get('content', ''))}
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard-header {{
            text-align: center;
            color: white;
            padding: 30px;
            margin-bottom: 30px;
        }}
        
        .dashboard-header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .dashboard-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .dashboard-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
        
        .dashboard-card h3 {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .card-content {{
            font-size: 1.1em;
            color: #333;
        }}
        
        .metric {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>📊 {title}</h1>
        <p>{datetime.now().strftime('%B %d, %Y - %H:%M')}</p>
    </div>
    
    <div class="dashboard-grid">
        {cards_html}
    </div>
</body>
</html>"""
    
    return html


def generate_blog_template(content, title, author="RAG System", **kwargs):
    """Generate blog post template"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            background: #fafafa;
            color: #333;
            line-height: 1.8;
        }}
        
        .blog-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 60px 20px;
        }}
        
        article {{
            background: white;
            padding: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .blog-header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        
        h1 {{
            font-size: 3em;
            color: #222;
            margin-bottom: 20px;
            line-height: 1.2;
        }}
        
        .meta {{
            color: #999;
            font-size: 1em;
            font-style: italic;
        }}
        
        .content {{
            font-size: 1.2em;
            color: #444;
        }}
        
        .content p {{
            margin: 20px 0;
        }}
        
        .share {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid #ddd;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="blog-container">
        <article>
            <div class="blog-header">
                <h1>{title}</h1>
                <div class="meta">
                    By {author} | {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
            
            <div class="content">
                {format_value(content)}
            </div>
            
            <div class="share">
                <p>Thanks for reading!</p>
            </div>
        </article>
    </div>
</body>
</html>"""
    
    return html


def generate_landing_template(content, title, subtitle="", cta_text="Get Started", **kwargs):
    """Generate landing page template"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}
        
        .hero {{
            text-align: center;
            padding: 60px 20px;
            max-width: 900px;
        }}
        
        h1 {{
            font-size: 4em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{
            font-size: 1.5em;
            margin-bottom: 40px;
            opacity: 0.9;
        }}
        
        .cta-button {{
            display: inline-block;
            padding: 20px 50px;
            background: white;
            color: #667eea;
            font-size: 1.3em;
            font-weight: bold;
            text-decoration: none;
            border-radius: 50px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }}
        
        .cta-button:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}
        
        .features {{
            margin-top: 60px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
        }}
        
        .feature {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .feature h3 {{
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle or format_value(content)}</p>
        <a href="#" class="cta-button">{cta_text}</a>
    </div>
</body>
</html>"""
    
    return html


def generate_portfolio_template(content, title, **kwargs):
    """Generate portfolio/showcase template"""
    
    # Parse projects
    projects = []
    if isinstance(content, list):
        projects = content
    elif isinstance(content, dict):
        projects = [{"title": k, "description": v} for k, v in content.items()]
    else:
        projects = [{"title": "Project", "description": str(content)}]
    
    projects_html = ""
    for project in projects:
        projects_html += f"""
        <div class="project-card">
            <h3>{project.get('title', 'Project')}</h3>
            <p>{project.get('description', '')}</p>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        
        .portfolio-header {{
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .portfolio-header h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        
        .projects-grid {{
            max-width: 1200px;
            margin: 60px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }}
        
        .project-card {{
            background: #2a2a2a;
            padding: 40px;
            border-radius: 10px;
            transition: transform 0.3s;
        }}
        
        .project-card:hover {{
            transform: translateY(-10px);
        }}
        
        .project-card h3 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        
        .project-card p {{
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="portfolio-header">
        <h1>{title}</h1>
        <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <div class="projects-grid">
        {projects_html}
    </div>
</body>
</html>"""
    
    return html


# Helper functions

def dict_to_html_table(data):
    """Convert dictionary to HTML table"""
    html = "<table><tr><th>Key</th><th>Value</th></tr>"
    for key, value in data.items():
        html += f"<tr><td>{key}</td><td>{format_value(value)}</td></tr>"
    html += "</table>"
    return html


def list_to_html_list(data):
    """Convert list to HTML list"""
    html = "<ul>"
    for item in data:
        html += f"<li>{format_value(item)}</li>"
    html += "</ul>"
    return html


def format_value(value):
    """Format value for HTML display"""
    if isinstance(value, dict):
        return dict_to_html_table(value)
    elif isinstance(value, list):
        return list_to_html_list(value)
    elif isinstance(value, (int, float)):
        return f'<span class="metric">{value:,}</span>'
    else:
        return str(value)
