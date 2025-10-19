# Functions Quick Reference Card

## 📦 Office Documents

### Excel
```
<run:excel/process filepath="data.xlsx" output_format="summary">
<run:excel/analyze_column filepath="sales.xlsx" column_name="Revenue">
<run:excel/filter_rows filepath="data.xlsx" column="Status" value="Active" operator="equals">
<run:excel/create_pivot filepath="sales.xlsx" index_col="Region" values_col="Amount">
```

### HTML
```
<run:html/process filepath="page.html" extract="text">
<run:html/process filepath="page.html" extract="links">
<run:html/create_html_report data='{"key": "value"}' title="Report">
<run:html/html_to_markdown filepath="page.html">
```

### PowerPoint
```
<run:powerpoint/process filepath="deck.pptx" extract="summary">
<run:powerpoint/extract_all_text filepath="slides.pptx">
<run:powerpoint/search_in_presentation filepath="deck.pptx" search_term="revenue">
<run:powerpoint/count_slides filepath="presentation.pptx">
```

## 🧠 Problem Solving

### Optimization
```
<run:solver/advanced problem_type="optimization" data='{"objective": "maximize", ...}' output_format="html">
```

### Dependencies
```
<run:solver/advanced problem_type="dependency" data='{"tasks": {...}}' output_format="json">
```

### Scheduling
```
<run:solver/advanced problem_type="scheduling" data='{"tasks": [...], "resources": {...}}'>
```

### Resource Allocation
```
<run:solver/advanced problem_type="resource_allocation" data='{"resources": {...}, "projects": [...}}'>
```

## 🔄 Workflows

### Plan Workflow
```
<run:workflow/orchestrator workflow_definition='{"name": "Pipeline", "steps": [...]}' execute=false>
```

### Execute Workflow
```
<run:workflow/orchestrator workflow_definition=data execute=true>
```

## 🎯 Decisions

### Multi-Criteria Analysis
```
<run:decision/builder problem_description="Choose framework" criteria='[...]' options='[...]' output_format="html">
```

## 🔢 Math & Text

### Basic Math
```
<run:math/add a=15 b=27>
<run:math/multiply a=4 b=8>
<run:math/add/add_three a=1 b=2 c=3>
```

### Text Processing
```
<run:text/summarize text="Long text here" max_length=100>
<run:text/word_count text="Count these words">
<run:text/translate text="Hello" target_lang="es">
```

## 📂 Output Locations

```
solutions/          # Solver outputs
workflows/          # Workflow plans  
decisions/          # Decision reports
reports/            # HTML reports
function_calls.log  # Execution log
```

## 🔥 Common Patterns

### Auto-Detection
```
Question: What is 15 plus 27?
→ Automatically executes math/add

Question: Analyze sales.xlsx
→ Automatically runs excel/process
```

### Chaining
```
Step 1: <run:excel/process filepath="data.xlsx">
Step 2: <run:solver/advanced problem_type="resource_allocation" data=result>
Step 3: <run:html/create_html_report data=allocation_result>
```

### File Processing
```
# From uploaded file
<run:excel/process filepath="uploaded_docs_reports/data.xlsx">

# From documents folder  
<run:excel/process filepath="general/sales.xlsx">

# Absolute path
<run:excel/process filepath="/full/path/to/file.xlsx">
```

## ⚡ CLI Quick Tests

```bash
# List functions
python manage_functions.py list

# Test function
python manage_functions.py run math/add a=5 b=3

# Get info
python manage_functions.py info excel/process

# Test all
python manage_functions.py test
```

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| Function not found | Restart app.py |
| File not found | Check filepath relative to documents/ |
| Import error | pip install missing package |
| Invalid syntax | Use / not . in function names |
| Circular dependency | Check workflow task dependencies |

## 💡 Tips

1. **Use correct separator:** `math/add` not `math.add`
2. **Check logs:** `tail -f function_calls.log`
3. **Start simple:** Test with small data first
4. **Save reports:** Move important files from output folders
5. **Auto-detection:** For math, just ask "What is X + Y?"

## 📊 Function Categories

| Category | Count | Examples |
|----------|-------|----------|
| Math | 4+ | add, multiply, subtract |
| Text | 5+ | summarize, translate, word_count |
| Excel | 6+ | process, analyze_column, filter |
| HTML | 6+ | process, extract_forms, create_report |
| PowerPoint | 7+ | process, search, count_slides |
| Solver | 4 | optimization, dependency, scheduling |
| Workflow | 3+ | orchestrator, nested, analyze |
| Decision | 3+ | builder, scenarios, matrix |

## 🎯 Use Case Lookup

| Need | Function |
|------|----------|
| Calculate sum | `math/add` |
| Analyze spreadsheet | `excel/process` |
| Plan project | `workflow/orchestrator` |
| Choose option | `decision/builder` |
| Extract web content | `html/process` |
| Summarize presentation | `powerpoint/extract_all_text` |
| Optimize resources | `solver/advanced` (resource_allocation) |
| Find critical path | `solver/advanced` (dependency) |

## 🔗 Integration

### With Documents
```
Upload file → Ask question → Add <run:function> tag
```

### With API
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{"name": "math/add", "kwargs": {"a": 5, "b": 3}}'
```

### With Python
```python
from functions_manager import get_function_manager

manager = get_function_manager()
result = manager.execute_function('math/add', kwargs={'a': 5, 'b': 3})
print(result['result'])  # 8
```

## 📚 Documentation Files

- `OFFICE_FUNCTIONS_GUIDE.md` - Office docs functions
- `ADVANCED_FUNCTIONS_GUIDE.md` - Problem solvers
- `ADVANCED_FUNCTIONS_README.md` - Quick start
- `FUNCTIONS_QUICK_REFERENCE.md` - This file

## ✅ Quick Start Checklist

```bash
# 1. Install dependencies
pip install pandas openpyxl beautifulsoup4 python-pptx scipy

# 2. Create directories  
mkdir -p functions/{math,text,excel,html,powerpoint,solver,workflow,decision}

# 3. Add function files (from artifacts)

# 4. Restart app
python app.py

# 5. Test
python manage_functions.py list

# 6. Try in browser
http://localhost:5000
```

---

**🎉 You're ready! Start using functions in your RAG queries.**
