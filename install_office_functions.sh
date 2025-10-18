#!/bin/bash
# Install Office Document Processing Functions

echo "========================================"
echo "Installing Office Document Functions"
echo "========================================"

# Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
pip install pandas openpyxl xlsxwriter beautifulsoup4 lxml html5lib python-pptx

# Create function directories
echo ""
echo "📁 Creating function directories..."
mkdir -p functions/excel
mkdir -p functions/html
mkdir -p functions/powerpoint
mkdir -p reports

# Create example files
echo ""
echo "📝 Creating example functions..."

# Excel function
cat > functions/excel/process.py << 'EOF'
"""Excel data processing functions"""
import os
import pandas as pd

def run(filepath, output_format="summary"):
    """Process Excel file and return analysis"""
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(full_path):
        return f"File not found: {filepath}"
    
    try:
        df = pd.read_excel(full_path, sheet_name=0)
        
        if output_format == "summary":
            return {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            }
    except Exception as e:
        return f"Error: {str(e)}"
EOF

# HTML function
cat > functions/html/process.py << 'EOF'
"""HTML processing functions"""
import os
from bs4 import BeautifulSoup

def run(filepath, extract="text"):
    """Process HTML file"""
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(full_path):
        return f"File not found: {filepath}"
    
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        if extract == "text":
            return soup.get_text()[:500]
        elif extract == "links":
            return [a.get('href') for a in soup.find_all('a', href=True)][:10]
    except Exception as e:
        return f"Error: {str(e)}"
EOF

# PowerPoint function
cat > functions/powerpoint/process.py << 'EOF'
"""PowerPoint processing functions"""
import os
from pptx import Presentation

def run(filepath, extract="summary"):
    """Process PowerPoint file"""
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(full_path):
        return f"File not found: {filepath}"
    
    try:
        prs = Presentation(full_path)
        
        if extract == "summary":
            return {
                "total_slides": len(prs.slides),
                "slides": [{"num": i+1, "shapes": len(s.shapes)} for i, s in enumerate(prs.slides[:5])]
            }
    except Exception as e:
        return f"Error: {str(e)}"
EOF

# Test functions
echo ""
echo "🧪 Testing functions..."
python manage_functions.py list

echo ""
echo "========================================"
echo "✅ Installation complete!"
echo "========================================"
echo ""
echo "Available functions:"
echo "  • excel/process - Process Excel files"
echo "  • html/process - Process HTML files"
echo "  • powerpoint/process - Process PowerPoint files"
echo ""
echo "Usage examples:"
echo "  <run:excel/process filepath=\"data.xlsx\" output_format=\"summary\">"
echo "  <run:html/process filepath=\"page.html\" extract=\"links\">"
echo "  <run:powerpoint/process filepath=\"slides.pptx\">"
echo ""
echo "For full function code, see the artifacts above."
