# Universal Auto-Detection System

## 🎯 What is Auto-Detection?

**Current System:** You must explicitly write `<run:math/add a=5 b=3>`

**With Universal Auto-Detection:** Just ask "What is 5 plus 3?" and it automatically executes!

## ✨ How It Works

### Automatic Discovery (Already Working!)

```
You add: functions/mycat/myfunction.py
         ↓
System scans within 2 seconds
         ↓
Function appears in registry
         ↓
Auto-detection rules generated
         ↓
Ready to use!
```

**No configuration needed!** The system:
1. Reads function name
2. Reads docstring
3. Reads parameters
4. Generates detection patterns automatically

### Detection Strategies

**1. Keyword Matching**
```python
# Function: excel/process
# Auto-detects: "analyze spreadsheet", "open excel", ".xlsx"

Question: "Analyze the sales.xlsx file"
→ Detects: excel/process (confidence: 75%)
```

**2. Pattern Matching**
```python
# Function: math/add
# Pattern: \d+ (plus|+) \d+

Question: "What is 15 plus 27?"
→ Detects: math/add a=15 b=27 (confidence: 90%)
```

**3. File Extension**
```python
# Any mention of .xlsx, .pptx, .html
→ Routes to appropriate function
```

**4. Semantic Analysis**
```python
# "summarize" → text/summarize
# "translate" → text/translate  
# "plan workflow" → workflow/orchestrator
```

## 🚀 Installation

### Step 1: Add Auto-Detector

```bash
# Copy the auto_detector.py file
cp auto_detector.py functions/

# It will be loaded automatically!
```

### Step 2: Update app.py

Replace your `process_answer_with_functions` with enhanced version:

```python
# Add import at top
from functions.auto_detector import enhanced_process_answer_with_functions

# In /ask route, replace this line:
answer, function_outputs = process_answer_with_functions(answer, question)

# With this:
answer, function_outputs = enhanced_process_answer_with_functions(answer, question, function_manager)
```

### Step 3: Restart

```bash
python app.py
```

**That's it!** Now ALL functions have auto-detection.

## 📊 Examples

### Before (Manual)
```
Q: What is 15 plus 27?
A: The answer is 42.

You must add: <run:math/add a=15 b=27>
```

### After (Automatic)
```
Q: What is 15 plus 27?
A: The answer is 42.

---
🤖 Auto-Detected Functions:
`math/add(a=15, b=27)` = **42** ✅ (confidence: 90%)
```

### Excel Auto-Detection
```
Q: Show me statistics for the Revenue column in sales.xlsx
A: Here's the analysis...

---
🤖 Auto-Detected Functions:
`excel/analyze_column(filepath=sales.xlsx, column_name=Revenue)` = **{mean: 18620, ...}** ✅
```

### Workflow Auto-Detection
```
Q: Help me plan this project workflow
A: Here's the execution plan...

---
🤖 Auto-Detected Functions:
`workflow/orchestrator(workflow_definition=...)` = **{critical_path: [...]}** ✅
```

## 🎓 How to Add Detection for YOUR Functions

### Automatic (Recommended)

Just write good docstrings and function names!

```python
# functions/finance/calculate_roi.py

def run(investment, returns):
    """Calculate Return on Investment (ROI) percentage"""
    return ((returns - investment) / investment) * 100
```

**Auto-generates detection for:**
- Keywords: "roi", "return", "investment", "calculate"
- Triggers: "calculate roi", "what's the roi", "investment returns"

### Manual (Advanced)

For complex patterns, customize triggers in `auto_detector.py`:

```python
# In _generate_triggers() method

if 'calculate_roi' in func_name:
    triggers.append({
        'pattern': r'(?:calculate|compute|find).*?roi',
        'type': 'keyword'
    })
```

## 🔧 Confidence Tuning

### Default Thresholds

```python
# In auto_detector.py

def auto_execute(self, question, threshold=20):
    # threshold: minimum confidence (0-100)
    # 20 = execute anything with >20% confidence
```

### Adjust for Your Needs

**Conservative (fewer false positives):**
```python
threshold=50  # Only execute if >50% confident
```

**Aggressive (catch more patterns):**
```python
threshold=10  # Execute if >10% confident
```

### Per-Function Threshold

```python
# Only auto-execute expensive functions if very confident
if func_name.startswith('solver/') and confidence < 60:
    skip_execution()
```

## 📈 Monitoring Detection

### View Suggestions (Without Executing)

```python
from functions.auto_detector import get_function_suggestions

question = "Analyze the sales spreadsheet"
suggestions = get_function_suggestions(question, function_manager)

for s in suggestions:
    print(f"{s['function']} - {s['confidence']}%")
    print(f"  Usage: {s['suggested_use']}")
```

Output:
```
excel/process - 85%
  Usage: <run:excel/process filepath=sales.xlsx>

excel/analyze_column - 45%
  Usage: <run:excel/analyze_column ...>
```

### Check Logs

```bash
# See what was auto-detected
grep "auto_detected" function_calls.log

# See confidence scores
grep "confidence" function_calls.log | jq -r '.confidence'
```

## 🎯 Detection Rules

### Built-In Patterns

| Pattern Type | Example | Function |
|--------------|---------|----------|
| Math operations | "5 + 3", "10 times 2" | math/* |
| File extensions | ".xlsx", ".pptx" | excel/*, powerpoint/* |
| Action verbs | "summarize", "translate" | text/* |
| Domain keywords | "workflow", "schedule" | workflow/* |
| Comparison words | "choose", "decide", "compare" | decision/* |

### Custom Patterns

Add to your function docstrings:

```python
def run(data):
    """
    Process financial data
    
    Triggers: finance, budget, accounting, fiscal
    Patterns: calculate profit, analyze expenses
    """
    pass
```

The system extracts these automatically!

## 🧪 Testing Auto-Detection

### Test Single Question

```python
from functions.auto_detector import UniversalAutoDetector

detector = UniversalAutoDetector(function_manager)

question = "What is 100 minus 30?"
candidates = detector.detect(question)

for c in candidates:
    print(f"{c['function']}: {c['confidence']}%")
```

### Test All Questions

```bash
# Create test_auto_detection.py

questions = [
    "What is 15 plus 27?",
    "Analyze sales.xlsx",
    "Summarize this text: ...",
    "Plan project workflow"
]

for q in questions:
    results = detector.auto_execute(q)
    print(f"\nQ: {q}")
    print(f"Detected: {[r['function'] for r in results]}")
```

## ⚡ Performance

### Fast Detection
- Pattern matching: <1ms
- Keyword matching: <5ms
- Total per question: <10ms

### Caching
```python
# Detection rules built once at startup
# Reused for all questions
```

### Lazy Loading
```python
# Only loads detector when needed
# No overhead if not used
```

## 🛡️ Safety Features

### Confidence Threshold
Only executes if confidence > threshold

### Execution Logging
All auto-executions logged with confidence scores

### Manual Override
Explicit `<run:function>` always takes precedence

### Dry-Run Mode
```python
# Get suggestions without executing
suggestions = detector.suggest_functions(question)
# Show to user, let them choose
```

## 🎨 UI Integration

### Show Suggestions

```html
<!-- In your template -->
{% if function_suggestions %}
<div class="suggestions">
    <h3>💡 Suggested Functions:</h3>
    {% for suggestion in function_suggestions %}
    <button onclick="addFunction('{{ suggestion.suggested_use }}')">
        {{ suggestion.function }} ({{ suggestion.confidence }}%)
    </button>
    {% endfor %}
</div>
{% endif %}
```

### Auto-Complete

```javascript
// As user types question
onQuestionInput(question) {
    fetch('/suggest_functions', {
        method: 'POST',
        body: JSON.stringify({question: question})
    })
    .then(r => r.json())
    .then(suggestions => {
        showSuggestions(suggestions);
    });
}
```

## 🔄 Future Functions

**The beauty:** When you add ANY new function, auto-detection works immediately!

```python
# You add this tomorrow:
# functions/crypto/hash.py

def run(text, algorithm="sha256"):
    """Generate cryptographic hash"""
    import hashlib
    return hashlib.new(algorithm, text.encode()).hexdigest()

# System automatically detects:
# - Keywords: "hash", "crypto", "checksum"
# - Patterns: "hash this", "generate hash"
# - NO CODE CHANGES NEEDED!
```

## 📚 Summary

### What's Automatic ✅

1. Function discovery (scanning)
2. Function loading
3. Registry updates
4. Detection rule generation
5. Keyword extraction
6. Pattern matching
7. Confidence scoring

### What You Control 🎛️

1. Confidence threshold
2. Custom patterns (optional)
3. Enable/disable per function
4. Execution vs. suggestion mode

### Zero Configuration 🎉

- Add function → Works immediately
- Good naming → Better detection
- Good docstrings → Best detection
- No manual setup required!

---

**Result:** Your RAG system becomes truly intelligent - it knows which functions to call based on natural language questions!
