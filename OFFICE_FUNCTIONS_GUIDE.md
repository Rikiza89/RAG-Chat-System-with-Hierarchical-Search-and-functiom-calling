# Office Document Functions Guide

## Installation

```bash
pip install pandas openpyxl xlsxwriter beautifulsoup4 lxml python-pptx
```

## Excel Functions (`functions/excel/process.py`)

### Basic Usage

**Analyze Excel file:**
```
Question: Analyze the sales data
<run:excel/process filepath="general/sales.xlsx" output_format="summary">
```

**Read specific sheet:**
```
<run:excel/read_sheet filepath="general/data.xlsx" sheet_name="Q1 Results" rows=5>
```

### Available Functions

| Function | Parameters | Description |
|----------|-----------|-------------|
| `run()` | filepath, output_format | Analyze Excel: summary/json/csv |
| `get_sheet_names()` | filepath | List all sheets |
| `read_sheet()` | filepath, sheet_name, rows | Read specific sheet |
| `analyze_column()` | filepath, column_name | Column statistics |
| `filter_rows()` | filepath, column, value, operator | Filter data |
| `create_pivot()` | filepath, index_col, values_col, aggfunc | Pivot summary |

### Examples

**Column analysis:**
```
What are the statistics for the Revenue column?
<run:excel/analyze_column filepath="sales.xlsx" column_name="Revenue">
```

**Filter data:**
```
Show all rows where Status equals "Active"
<run:excel/filter_rows filepath="customers.xlsx" column="Status" value="Active" operator="equals">
```

**Pivot table:**
```
Summarize sales by region
<run:excel/create_pivot filepath="sales.xlsx" index_col="Region" values_col="Amount" aggfunc="sum">
```

## HTML Functions (`functions/html/process.py`)

### Basic Usage

**Extract text:**
```
<run:html/process filepath="general/page.html" extract="text">
```

**Get all links:**
```
<run:html/process filepath="general/index.html" extract="links">
```

### Available Functions

| Function | Parameters | Description |
|----------|-----------|-------------|
| `run()` | filepath, extract | Extract: text/links/images/tables/metadata |
| `extract_forms()` | filepath | Get all forms and inputs |
| `create_html_report()` | data, title, output_path | Generate HTML report |
| `sanitize_html()` | html_string | Remove dangerous elements |
| `html_to_markdown()` | filepath | Convert HTML to Markdown |

### Examples

**Extract tables:**
```
Get all tables from the report
<run:html/process filepath="report.html" extract="tables">
```

**Create report:**
```
<run:html/create_html_report data='{"sales": 10000, "profit": 2500}' title="Q1 Report" output_path="reports/q1.html">
```

**Convert to Markdown:**
```
<run:html/html_to_markdown filepath="general/document.html">
```

## PowerPoint Functions (`functions/powerpoint/process.py`)

### Basic Usage

**Analyze presentation:**
```
<run:powerpoint/process filepath="general/presentation.pptx" extract="summary">
```

**Extract all text:**
```
<run:powerpoint/extract_all_text filepath="general/slides.pptx">
```

### Available Functions

| Function | Parameters | Description |
|----------|-----------|-------------|
| `run()` | filepath, extract | Extract: summary/text/notes/images |
| `get_slide_text()` | filepath, slide_num | Text from specific slide |
| `create_presentation()` | title, slides_data, output_path | Generate PPTX |
| `extract_all_text()` | filepath | All text content |
| `count_slides()` | filepath | Total slides |
| `search_in_presentation()` | filepath, search_term | Find text |
| `pptx_to_pdf()` | filepath, output_path | Convert to PDF (requires LibreOffice) |

### Examples

**Get speaker notes:**
```
Show speaker notes from presentation
<run:powerpoint/process filepath="presentation.pptx" extract="notes">
```

**Search content:**
```
<run:powerpoint/search_in_presentation filepath="slides.pptx" search_term="revenue">
```

**Create presentation:**
```python
slides = [
    {"title": "Q1 Results", "content": ["Revenue: $10M", "Growth: 25%"]},
    {"title": "Next Steps", "content": ["Expand team", "Launch product"]}
]
<run:powerpoint/create_presentation title="Quarterly Review" slides_data=slides output_path="reports/review.pptx">
```

## Integration Examples

### Excel → HTML Report

```
Question: Create an HTML report from sales.xlsx

Step 1: <run:excel/process filepath="sales.xlsx" output_format="summary">
Step 2: <run:html/create_html_report data=result title="Sales Report">
```

### PowerPoint → Text Extraction

```
Extract all text from presentation.pptx
<run:powerpoint/extract_all_text filepath="presentation.pptx">
```

### Excel Data Analysis

```
Analyze the Revenue column in Q1_data.xlsx and show statistics
<run:excel/analyze_column filepath="Q1_data.xlsx" column_name="Revenue">
```

## Auto-Detection Patterns

The system can auto-detect these requests:

**Excel:**
- "analyze sales.xlsx" → runs excel/process
- "show columns in data.xlsx" → gets sheet info
- "filter customers where status is active" → filter_rows

**HTML:**
- "extract text from page.html" → html/process with extract="text"
- "get links from index.html" → html/process with extract="links"

**PowerPoint:**
- "how many slides in presentation.pptx" → count_slides
- "search for revenue in slides.pptx" → search_in_presentation

## Error Handling

All functions return descriptive error messages:

```python
# File not found
"File not found: sales.xlsx"

# Missing dependency
"Error: pandas not installed. Run: pip install pandas openpyxl"

# Invalid parameter
"Column 'Revenue' not found. Available: ['Name', 'Amount', 'Date']"
```

## Common Use Cases

### 1. Data Analysis Pipeline

```bash
# Upload Excel file
curl -X POST -F "file=@sales.xlsx" -F "folder=data" http://localhost:5000/

# Analyze via function
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{"name": "excel/analyze_column", "kwargs": {"filepath": "data/sales.xlsx", "column_name": "Revenue"}}'
```

### 2. Report Generation

```python
# Create HTML report from Excel data
Question: Generate a report from Q1_results.xlsx
<run:excel/process filepath="Q1_results.xlsx" output_format="json">
<run:html/create_html_report data=result title="Q1 Results">
```

### 3. Presentation Analysis

```python
# Extract and summarize presentation
<run:powerpoint/extract_all_text filepath="meeting.pptx">
<run:text/summarize text=result max_length=200>
```

## File Path Guidelines

**Absolute paths:**
```python
filepath="/full/path/to/file.xlsx"
```

**Relative to documents/ folder:**
```python
filepath="general/sales.xlsx"  # Looks in documents/general/
filepath="data/report.html"    # Looks in documents/data/
```

**After upload:**
```python
# File uploaded to "reports" category
filepath="uploaded_docs_reports/file.xlsx"
```

## Performance Tips

1. **Large Excel files:** Use `rows` parameter to limit data:
   ```python
   read_sheet(filepath="big.xlsx", sheet_name="Data", rows=100)
   ```

2. **HTML parsing:** Extract specific elements instead of full text
   ```python
   extract="links"  # Faster than "text"
   ```

3. **PowerPoint:** Count slides before extracting all text
   ```python
   count_slides(filepath)  # Quick check
   ```

## Security Notes

- HTML sanitization removes `<script>`, `<iframe>`, event handlers
- Excel formulas not evaluated, only values extracted
- File paths validated to prevent directory traversal
- Max file size: 50MB (configurable)

## Troubleshooting

**"Module not found" errors:**
```bash
pip install pandas openpyxl beautifulsoup4 lxml python-pptx
```

**Excel encoding issues:**
```python
# Try reading with specific encoding
df = pd.read_excel(filepath, encoding='utf-8')
```

**PowerPoint images not extracting:**
- Images embedded as shapes (type 13)
- Use `extract="images"` for metadata only
- Actual image data requires additional processing

**HTML table parsing:**
- Complex tables may need manual processing
- Use `extract="tables"` for structure
- BeautifulSoup handles most standard HTML

## Advanced Examples

### Conditional Excel Processing

```python
# Filter and analyze
<run:excel/filter_rows filepath="sales.xlsx" column="Region" value="North" operator="equals">
# Then analyze filtered results
<run:excel/analyze_column filepath="sales.xlsx" column_name="Amount">
```

### Multi-slide PowerPoint Analysis

```python
# Get summary first
<run:powerpoint/process filepath="deck.pptx" extract="summary">
# Then extract specific slide
<run:powerpoint/get_slide_text filepath="deck.pptx" slide_num=3>
```

### HTML Form Extraction

```python
# Extract forms for documentation
<run:html/extract_forms filepath="application.html">
# Returns all form fields and actions
```

## Function Chaining

Chain multiple functions for complex workflows:

```
Question: Analyze sales.xlsx, create HTML report, and summarize it

1. <run:excel/process filepath="sales.xlsx">
2. <run:html/create_html_report data=result title="Sales Analysis">
3. <run:text/summarize text="Report created with X rows">
```

## CLI Testing

```bash
# Test Excel function
python manage_functions.py run excel/process filepath="sales.xlsx" output_format="summary"

# Test HTML function
python manage_functions.py run html/process filepath="page.html" extract="links"

# Test PowerPoint function
python manage_functions.py run powerpoint/count_slides filepath="presentation.pptx"
```
