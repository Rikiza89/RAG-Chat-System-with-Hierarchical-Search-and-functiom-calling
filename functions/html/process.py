"""
HTML file processing and generation functions
Requires: pip install beautifulsoup4 lxml html5lib
"""

import os
import re
from pathlib import Path

def run(filepath, extract="text"):
    """
    Process HTML file
    
    Args:
        filepath: Path to HTML file
        extract: 'text', 'links', 'images', 'tables', 'metadata'
    
    Returns:
        Extracted content
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return "Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4 lxml"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(full_path):
        return f"File not found: {filepath}"
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if extract == "text":
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:1000] + "..." if len(text) > 1000 else text
        
        elif extract == "links":
            links = []
            for a in soup.find_all('a', href=True):
                links.append({
                    "text": a.get_text(strip=True),
                    "href": a['href']
                })
            return links[:20]  # First 20 links
        
        elif extract == "images":
            images = []
            for img in soup.find_all('img'):
                images.append({
                    "src": img.get('src', ''),
                    "alt": img.get('alt', ''),
                    "title": img.get('title', '')
                })
            return images[:20]
        
        elif extract == "tables":
            tables = []
            for i, table in enumerate(soup.find_all('table')):
                rows = []
                for tr in table.find_all('tr')[:5]:  # First 5 rows
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    rows.append(cells)
                tables.append({"table_num": i+1, "rows": rows})
            return tables
        
        elif extract == "metadata":
            meta = {
                "title": soup.title.string if soup.title else None,
                "meta_tags": {}
            }
            for tag in soup.find_all('meta'):
                name = tag.get('name') or tag.get('property')
                content = tag.get('content')
                if name and content:
                    meta['meta_tags'][name] = content
            return meta
    
    except Exception as e:
        return f"Error processing HTML: {str(e)}"


def extract_forms(filepath):
    """Extract all forms from HTML"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return "Error: beautifulsoup4 not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        forms = []
        for form in soup.find_all('form'):
            inputs = []
            for inp in form.find_all(['input', 'textarea', 'select']):
                inputs.append({
                    "type": inp.get('type', inp.name),
                    "name": inp.get('name', ''),
                    "id": inp.get('id', '')
                })
            
            forms.append({
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "inputs": inputs
            })
        
        return forms
    
    except Exception as e:
        return f"Error: {str(e)}"


def create_html_report(data, title="Report", output_path="reports/report.html"):
    """
    Create HTML report from data
    
    Args:
        data: Dict or list of data
        title: Report title
        output_path: Where to save (relative to project root)
    """
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .summary {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="summary">
            <strong>Generated:</strong> {{% import datetime %}}{{{{ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}}}
        </div>
        
        {{% if data is mapping %}}
        <h2>Summary</h2>
        <table>
            <tr><th>Key</th><th>Value</th></tr>
            {{% for key, value in data.items() %}}
            <tr><td>{{{{ key }}}}</td><td>{{{{ value }}}}</td></tr>
            {{% endfor %}}
        </table>
        {{% elif data is sequence %}}
        <h2>Data</h2>
        <table>
            <tr>
            {{% for key in data[0].keys() %}}
                <th>{{{{ key }}}}</th>
            {{% endfor %}}
            </tr>
            {{% for row in data %}}
            <tr>
                {{% for value in row.values() %}}
                <td>{{{{ value }}}}</td>
                {{% endfor %}}
            </tr>
            {{% endfor %}}
        </table>
        {{% endif %}}
    </div>
</body>
</html>
"""
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Simple template rendering
        import json
        from datetime import datetime
        
        content = html_template
        content = content.replace('{title}', title)
        content = content.replace('{{{{ datetime.datetime.now().strftime(', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Basic data rendering
        if isinstance(data, dict):
            table_rows = ""
            for key, value in data.items():
                table_rows += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
            content = content.replace('{{% if data is mapping %}}', '').replace('{{% elif', '<!--').replace('{{% endif %}}', '')
            content = content.replace('{{% for key, value in data.items() %}}', '').replace('{{% endfor %}}', '')
            content = re.sub(r'<tr><th>Key</th><th>Value</th></tr>.*?</table>', 
                           f'<tr><th>Key</th><th>Value</th></tr>{table_rows}</table>', content, flags=re.DOTALL)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"HTML report created: {output_path}"
    
    except Exception as e:
        return f"Error creating HTML: {str(e)}"


def sanitize_html(html_string):
    """Remove potentially dangerous HTML elements"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return "Error: beautifulsoup4 not installed"
    
    try:
        soup = BeautifulSoup(html_string, 'html.parser')
        
        # Remove dangerous tags
        for tag in soup(['script', 'style', 'iframe', 'object', 'embed']):
            tag.decompose()
        
        # Remove event handlers
        for tag in soup.find_all():
            for attr in list(tag.attrs):
                if attr.startswith('on'):
                    del tag[attr]
        
        return str(soup)
    
    except Exception as e:
        return f"Error: {str(e)}"


def html_to_markdown(filepath):
    """Convert HTML to Markdown"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return "Error: beautifulsoup4 not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Basic conversion
        markdown = ""
        
        # Title
        if soup.title:
            markdown += f"# {soup.title.string}\n\n"
        
        # Process body content
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'a', 'ul', 'ol']):
            if element.name == 'h1':
                markdown += f"# {element.get_text(strip=True)}\n\n"
            elif element.name == 'h2':
                markdown += f"## {element.get_text(strip=True)}\n\n"
            elif element.name == 'h3':
                markdown += f"### {element.get_text(strip=True)}\n\n"
            elif element.name == 'p':
                markdown += f"{element.get_text(strip=True)}\n\n"
            elif element.name == 'a':
                text = element.get_text(strip=True)
                href = element.get('href', '')
                markdown += f"[{text}]({href}) "
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    markdown += f"- {li.get_text(strip=True)}\n"
                markdown += "\n"
        
        return markdown
    
    except Exception as e:
        return f"Error: {str(e)}"
