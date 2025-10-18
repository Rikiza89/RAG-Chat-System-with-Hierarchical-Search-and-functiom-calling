# Office Functions - Practical Examples

## Quick Setup

```bash
# Install dependencies
pip install pandas openpyxl xlsxwriter beautifulsoup4 lxml python-pptx

# Create test files
python create_test_files.py

# Verify functions loaded
python manage_functions.py list | grep -E "(excel|html|powerpoint)"
```

## Excel Examples

### Example 1: Analyze Sales Data
```
Question: Analyze the sales data in test/sales_data.xlsx

Answer with: <run:excel/process filepath="test/sales_data.xlsx" output_format="summary">

Expected output:
{
  "rows": 5,
  "columns": 4,
  "column_names": ["Product", "Sales", "Revenue", "Region"]
}
```

### Example 2: Get Revenue Statistics
```
<run:excel/analyze_column filepath="test/sales_data.xlsx" column_name="Revenue">

Output:
{
  "type": "numeric",
  "mean": 18620.0,
  "median": 9600.0,
  "min": 3000.0,
  "max": 50000.0
}
```

### Example 3: Filter by Region
```
<run:excel/filter_rows filepath="test/sales_data.xlsx" column="Region" value="North" operator="equals">

Output:
{
  "matched_rows": 2,
  "data": [
    {"Product": "Laptop", "Sales": 50, "Revenue": 50000, "Region": "North"},
    {"Product": "Keyboard", "Sales": 100, "Revenue": 8000, "Region": "North"}
  ]
}
```

## HTML Examples

### Example 1: Extract Text Content
```
<run:html/process filepath="test/report.html" extract="text">

Output: "Q1 Sales Report This is a sample sales report..."
```

### Example 2: Get All Links
```
<run:html/process filepath="test/report.html" extract="links">

Output: [
  {"text": "Full Report", "href": "https://example.com/report"},
  {"text": "Data Source", "href": "https://example.com/data"}
]
```

### Example 3: Extract Tables
```
<run:html/process filepath="test/report.html" extract="tables">

Output: [
  {
    "table_num": 1,
    "rows": [
      ["Region", "Sales"],
      ["North", "$58,000"],
      ["South", "$3,000"]
    ]
  }
]
```

### Example 4: Create HTML Report
```python
data = {"Q1_Sales": 93100, "Units": 495, "Growth": "15%"}
<run:html/create_html_report data=data title="Q1 Report" output_path="reports/q1_summary.html">

Output: "HTML report created: reports/q1_summary.html"
```

## PowerPoint Examples

### Example 1: Get Presentation Summary
```
<run:powerpoint/process filepath="test/presentation.pptx" extract="summary">

Output:
{
  "total_slides": 3,
  "slides": [
    {"slide_num": 1, "shapes": 2, "title": "Q1 Business Review"},
    {"slide_num": 2, "shapes": 2, "title": "Key Achievements"},
    {"slide_num": 3, "shapes": 2, "title": "Next Steps"}
  ]
}
```

### Example 2: Extract All Text
```
<run:powerpoint/extract_all_text filepath="test/presentation.pptx">

Output: "Q1 Business Review\nJanuary - March 2025\nKey Achievements\nRevenue Growth..."
```

### Example 3: Search Content
```
<run:powerpoint/search_in_presentation filepath="test/presentation.pptx" search_term="revenue">

Output: [
  {
    "slide_num": 2,
    "matches": ["Revenue Growth"]
  }
]
```

### Example 4: Create Presentation
```python
slides = [
    {
        "title": "Overview",
        "content": ["Total Sales: $93K", "Units Sold: 495"]
    },
    {
        "title": "Goals",
        "content": ["Increase revenue by 20%", "Expand to 3 new markets"]
    }
]

<run:powerpoint/create_presentation title="Sales Summary" slides_data=slides output_path="reports/summary.pptx">

Output: "Presentation created: reports/summary.pptx (3 slides)"
```

## Combined Workflows

### Workflow 1: Excel → HTML Report

```
Step 1: Extract data
<run:excel/process filepath="test/sales_data.xlsx" output_format="json">

Step 2: Create HTML report
<run:html/create_html_report data=result title="Sales Analysis" output_path="reports/sales.html">
```

### Workflow 2: PowerPoint → Summary

```
Step 1: Extract text
<run:powerpoint/extract_all_text filepath="test/presentation.pptx">

Step 2: Summarize
<run:text/summarize text=result max_length=200>
```

### Workflow 3: Excel Analysis Pipeline

```
1. Get overview:
   <run:excel/process filepath="sales.xlsx">

2. Analyze key column:
   <run:excel/analyze_column filepath="sales.xlsx" column_name="Revenue">

3. Create pivot:
   <run:excel/create_pivot filepath="sales.xlsx" index_col="Region" values_col="Revenue">
```

## Real-World Scenarios

### Scenario 1: Monthly Sales Report

**Question:** "Generate a monthly sales report from January_sales.xlsx"

**Response with functions:**
```
<run:excel/process filepath="January_sales.xlsx" output_format="summary">
<run:excel/analyze_column filepath="January_sales.xlsx" column_name="Revenue">
<run:excel/create_pivot filepath="January_sales.xlsx" index_col="Product" values_col="Revenue" aggfunc="sum">
```

### Scenario 2: Website Content Analysis

**Question:** "Extract and analyze content from our homepage"

**Response:**
```
<run:html/process filepath="homepage.html" extract="text">
<run:html/process filepath="homepage.html" extract="links">
<run:text/word_count text=extracted_text>
```

### Scenario 3: Presentation Review

**Question:** "How many slides discuss revenue in our Q1 deck?"

**Response:**
```
<run:powerpoint/count_slides filepath="Q1_deck.pptx">
<run:powerpoint/search_in_presentation filepath="Q1_deck.pptx" search_term="revenue">
```

## API Usage

### Via REST API

**Analyze Excel:**
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{
    "name": "excel/process",
    "kwargs": {
      "filepath": "test/sales_data.xlsx",
      "output_format": "summary"
    }
  }'
```

**Extract HTML links:**
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{
    "name": "html/process",
    "kwargs": {
      "filepath": "test/report.html",
      "extract": "links"
    }
  }'
```

**PowerPoint summary:**
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{
    "name": "powerpoint/process",
    "kwargs": {
      "filepath": "test/presentation.pptx",
      "extract": "summary"
    }
  }'
```

## Error Handling Examples

**File not found:**
```
<run:excel/process filepath="nonexistent.xlsx">
→ "File not found: nonexistent.xlsx"
```

**Invalid column:**
```
<run:excel/analyze_column filepath="sales.xlsx" column_name="InvalidColumn">
→ "Column 'InvalidColumn' not found. Available: ['Product', 'Sales', 'Revenue']"
```

**Missing dependency:**
```
<run:powerpoint/process filepath="slides.pptx">
→ "Error: python-pptx not installed. Run: pip install python-pptx"
```

## Performance Tips

**Large Excel files:**
- Use `rows` parameter: `read_sheet(..., rows=100)`
- Filter before analyzing: `filter_rows()` then `analyze_column()`

**Complex HTML:**
- Extract specific elements: `extract="links"` vs `extract="text"`
- Sanitize untrusted HTML: `sanitize_html()`

**Big presentations:**
- Check slide count first: `count_slides()`
- Extract specific slides: `get_slide_text(..., slide_num=5)`

## Troubleshooting

**pandas errors:**
```bash
pip install --upgrade pandas openpyxl
```

**BeautifulSoup parser warnings:**
```bash
pip install lxml html5lib
```

**PowerPoint shape errors:**
- Some shapes don't have text attributes
- Check `hasattr(shape, 'text')` in custom functions

## Next Steps

1. Upload your office files to `documents/` folder
2. Test functions using `manage_functions.py`
3. Use in RAG queries with `<run:function>` syntax
4. Create custom functions for specific needs
5. Chain functions for complex workflows
