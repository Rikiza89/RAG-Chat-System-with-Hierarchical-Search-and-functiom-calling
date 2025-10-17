# 🚀 RAG System with Dynamic Functions - Setup Guide

## 📋 Overview

This enhanced RAG system now includes:
- ✅ Document Q&A using FAISS + Ollama
- ✅ Dynamic function loading from `functions/` directory
- ✅ Automatic function execution from LLM responses
- ✅ Real-time file watching for both documents and functions
- ✅ RESTful API for function management
- ✅ Web UI with function monitoring

---

## 🏗️ Project Structure

```
rag_system/
├── app.py                      # Main Flask application
├── functions_manager.py        # Function loading & execution
├── functions_watcher.py        # File watcher for functions
├── manage_functions.py         # CLI tool
├── functions/                  # Dynamic functions directory
│   ├── math/
│   │   ├── add.py
│   │   └── multiply.py
│   ├── text/
│   │   ├── summarize.py
│   │   └── translate.py
│   └── utils/
│       └── format.py
├── documents/                  # Default documents
│   ├── general/
│   ├── technical/
│   └── research/
├── uploaded_docs/              # User uploads
├── templates/
│   └── index.html             # Web interface
├── functions_list.json        # Auto-generated function registry
└── function_calls.log         # Execution log
```

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install flask sentence-transformers faiss-cpu PyMuPDF python-docx watchdog werkzeug
```

### 2. Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.2:3b
```

### 3. Create Project Structure

```bash
mkdir -p functions/math functions/text functions/utils
mkdir -p documents/general documents/technical documents/research
mkdir -p uploaded_docs templates
```

### 4. Add Example Functions

Create `functions/math/add.py`:
```python
def run(a, b):
    """Add two numbers together"""
    return a + b
```

Create `functions/text/summarize.py`:
```python
def run(text, max_length=100):
    """Summarize text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3].rsplit(' ', 1)[0] + '...'
```

### 5. Copy Files

Place all the provided files in your project directory:
- `app.py` (updated with function integration)
- `functions_manager.py`
- `functions_watcher.py`
- `manage_functions.py`
- `templates/index.html`

---

## 🎯 Quick Start

### 1. Start the Application

```bash
python app.py
```

You should see:
```
INFO - Function manager initialized with 8 functions
INFO - Initial index built successfully
INFO - Document watcher started
INFO - Functions watcher started
INFO - Starting Flask server on http://0.0.0.0:5000
```

### 2. Access the Web Interface

Open your browser to: `http://localhost:5000`

### 3. Upload Documents

- Go to "Upload Documents" tab
- Select a file (TXT, PDF, or DOCX)
- Choose a category/folder
- Click "Upload Document"

### 4. Ask Questions with Function Calls

Example question:
```
What is 15 plus 27? <run:math/add a=15 b=27>
```

The system will:
1. Process your question
2. Detect the function call syntax
3. Execute `math/add(15, 27)`
4. Display the result inline

---

## ⚡ Function System Usage

### Creating New Functions

#### Basic Function

Create `functions/your_category/your_function.py`:

```python
def run(arg1, arg2):
    """Your function description"""
    # Your logic here
    return result
```

#### Multiple Functions in One File

```python
def run(text):
    """Default function"""
    return text.upper()

def another_function(x, y):
    """Another function"""
    return x * y
```

Access as:
- `your_category/your_function` → calls `run()`
- `your_category/your_function/another_function` → calls `another_function()`

### Function Naming Convention

| File Path | Function Name | Access As |
|-----------|---------------|-----------|
| `functions/math/add.py` (with `run()`) | `math/add` |
| `functions/math/add.py` (with `add_three()`) | `math/add/add_three` |
| `functions/text/process.py` (with `run()`) | `text/process` |

### Automatic Reload

The system watches the `functions/` directory. When you:
- **Add** a new `.py` file → Automatically loaded
- **Modify** an existing file → Reloaded
- **Delete** a file → Removed from registry

Changes are reflected within 2 seconds (configurable debounce).

---

## 🔧 CLI Tool Usage

### List All Functions

```bash
python manage_functions.py list
```

Output:
```
====================================
Available Functions (8)
Last Updated: 2025-10-18T10:30:45
====================================

📦 math/add
   Params: a, b
   Doc: Add two numbers together
   Path: functions/math/add.py

📦 text/summarize
   Params: text, max_length
   Doc: Summarize text to maximum length
   Path: functions/text/summarize.py
```

### Get Function Info

```bash
python manage_functions.py info math/add
```

### Execute Function from CLI

```bash
python manage_functions.py run math/add a=5 b=3
```

Output:
```
🚀 Running function: math/add
Arguments: ['a=5', 'b=3']

====================================
✅ Success!
Result: 8
====================================
```

### Test All Functions

```bash
python manage_functions.py test
```

### Reload Functions

```bash
python manage_functions.py reload
```

---

## 🌐 API Endpoints

### GET /functions

Get list of all available functions.

**Response:**
```json
{
  "last_updated": "2025-10-18T10:30:45",
  "total_functions": 8,
  "functions": [
    {
      "name": "math/add",
      "params": ["a", "b"],
      "signature": "(a, b)",
      "doc": "Add two numbers together",
      "path": "functions/math/add.py"
    }
  ]
}
```

### POST /run_function

Execute a function with arguments.

**Request:**
```json
{
  "name": "math/add",
  "kwargs": {
    "a": 5,
    "b": 3
  }
}
```

**Response (Success):**
```json
{
  "status": "success",
  "result": 8,
  "function": "math/add"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Invalid arguments for math/add: ...",
  "signature": "(a, b)"
}
```

### GET /function/<func_name>

Get detailed information about a specific function.

**Example:**
```bash
curl http://localhost:5000/function/math/add
```

### POST /reload_functions

Manually trigger function registry reload.

**Response:**
```json
{
  "status": "success",
  "message": "Reloaded 8 functions",
  "total": 8
}
```

### GET /health

System health check including function manager status.

**Response:**
```json
{
  "status": "healthy",
  "ollama_available": true,
  "model_available": true,
  "index_built": true,
  "total_chunks": 150,
  "total_folders": 3,
  "functions": {
    "enabled": true,
    "total": 8,
    "last_update": "2025-10-18T10:30:45"
  }
}
```

---

## 📝 Function Call Syntax in LLM Answers

The system detects and executes function calls in the format:

```
<run:function_name arg1=value1 arg2=value2>
```

### Examples

**Simple calculation:**
```
The sum is: <run:math/add a=10 b=20>
```

**Text processing:**
```
Summary: <run:text/summarize text="This is a long text..." max_length=50>
```

**Multiple functions:**
```
First: <run:math/add a=5 b=3>
Then multiply: <run:math/multiply a=8 b=2>
```

### Supported Value Types

- **Integers:** `a=5`
- **Floats:** `a=3.14`
- **Booleans:** `flag=true` or `flag=false`
- **Strings:** `text=hello` or `text="hello world"`

---

## 🎨 Advanced Examples

### Example 1: Calculator Function

`functions/calc/advanced.py`:
```python
import math

def run(expression):
    """Evaluate a mathematical expression safely"""
    try:
        # Only allow math operations
        allowed = {
            'sin': math.sin,
            'cos': math.cos,
            'sqrt': math.sqrt,
            'pi': math.pi,
            'e': math.e
        }
        result = eval(expression, {"__builtins__": {}}, allowed)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def factorial(n):
    """Calculate factorial of n"""
    return math.factorial(int(n))
```

**Usage:**
```
Calculate: <run:calc/advanced expression="sqrt(16) + 5">
Factorial: <run:calc/advanced/factorial n=5>
```

### Example 2: Data Processing

`functions/data/analyze.py`:
```python
def run(numbers):
    """Analyze a list of numbers"""
    nums = [float(x) for x in numbers.split(',')]
    return {
        'mean': sum(nums) / len(nums),
        'min': min(nums),
        'max': max(nums),
        'count': len(nums)
    }

def median(numbers):
    """Calculate median"""
    nums = sorted([float(x) for x in numbers.split(',')])
    n = len(nums)
    mid = n // 2
    if n % 2 == 0:
        return (nums[mid-1] + nums[mid]) / 2
    return nums[mid]
```

**Usage:**
```
Statistics: <run:data/analyze numbers="10,20,30,40,50">
Median: <run:data/analyze/median numbers="5,2,8,1,9">
```

### Example 3: File Operations

`functions/files/reader.py`:
```python
import os

def run(filename):
    """Read a file from the documents folder"""
    filepath = os.path.join('documents', 'general', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Read {len(content)} characters from {filename}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(folder='general'):
    """List files in a folder"""
    folder_path = os.path.join('documents', folder)
    try:
        files = os.listdir(folder_path)
        return ', '.join(files)
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## 🔒 Security Considerations

### Safe Practices

1. **No `eval()` or `exec()`** on user input (only on controlled expressions)
2. **Import isolation** - Each function is loaded in its own namespace
3. **Argument validation** - Type checking and sanitization
4. **File system restrictions** - Limit file operations to specific directories
5. **Timeout protection** - Add timeouts for long-running functions

### Example: Secure Function

```python
def run(user_input, max_length=100):
    """Process user input safely"""
    # Validate input
    if not isinstance(user_input, str):
        raise ValueError("Input must be string")
    
    if len(user_input) > max_length:
        raise ValueError(f"Input too long (max {max_length})")
    
    # Sanitize
    clean_input = user_input.strip()
    
    # Process
    return clean_input.upper()
```

### Recommended Restrictions

```python
# In functions_manager.py, add to execute_function():

# Timeout wrapper
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout

try:
    result = func(*args, **kwargs)
finally:
    signal.alarm(0)  # Cancel alarm
```

---

## 📊 Monitoring & Logging

### Function Call Logs

All function executions are logged to `function_calls.log`:

```json
{"timestamp": "2025-10-18T10:30:45", "function": "math/add", "args": "[]", "kwargs": "{'a': 5, 'b': 3}", "result": "8", "error": null, "status": "success"}
{"timestamp": "2025-10-18T10:31:12", "function": "text/summarize", "args": "[]", "kwargs": "{'text': 'Long text...', 'max_length': 50}", "result": "Summary...", "error": null, "status": "success"}
```

### Parse Logs with Python

```python
import json

with open('function_calls.log', 'r') as f:
    for line in f:
        log = json.loads(line)
        print(f"{log['timestamp']}: {log['function']} -> {log['result']}")
```

### Real-time Monitoring

```bash
# Watch logs in real-time
tail -f function_calls.log

# Count function calls
wc -l function_calls.log

# Find errors
grep '"status": "error"' function_calls.log
```

---

## 🐛 Troubleshooting

### Functions Not Loading

**Check:**
```bash
python manage_functions.py list
```

**Common issues:**
- Syntax errors in `.py` files
- Files starting with `_` are ignored
- Functions must be callable (not classes)

**Solution:**
```bash
# Test individual function
python -c "from functions.math.add import run; print(run(5, 3))"
```

### Function Not Executing from LLM

**Check syntax:**
- ✅ Correct: `<run:math/add a=5 b=3>`
- ❌ Wrong: `<run:math/add(5, 3)>` (no parentheses)
- ❌ Wrong: `<run:math/add 5 3>` (need key=value)

**Verify function exists:**
```bash
curl http://localhost:5000/functions | jq '.functions[].name'
```

### Import Errors

**Issue:** Module not found

**Solution:**
```python
# In your function file, use absolute imports
import os  # ✅ Good
from pathlib import Path  # ✅ Good

# Avoid relative imports in dynamic functions
from ..utils import helper  # ❌ May fail
```

### Watchdog Not Detecting Changes

**Restart watchers:**
```bash
# Stop the app (Ctrl+C)
# Start again
python app.py
```

**Manual reload:**
```bash
curl -X POST http://localhost:5000/reload_functions
```

---

## 🚀 Production Deployment

### Environment Variables

```bash
export SECRET_KEY="your-secret-key-here"
export LLM_MODEL="llama3.2:3b"
export FUNCTIONS_DIR="/var/www/rag/functions"
export MAX_FILE_SIZE=104857600  # 100MB
```

### Using Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

`Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t rag-functions .
docker run -p 5000:5000 -v $(pwd)/functions:/app/functions rag-functions
```

---

## 📚 Additional Resources

### Example Function Templates

**Weather function** (mock):
```python
def run(city):
    """Get weather for a city (mock)"""
    return f"The weather in {city} is sunny, 25°C"
```

**Time function**:
```python
from datetime import datetime

def run(timezone='UTC'):
    """Get current time"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

**JSON formatter**:
```python
import json

def run(data):
    """Pretty print JSON"""
    if isinstance(data, str):
        data = json.loads(data)
    return json.dumps(data, indent=2)
```

### Integration with External APIs

```python
# functions/api/weather.py
import requests

def run(city, api_key):
    """Fetch real weather data"""
    url = f"http://api.weatherapi.com/v1/current.json"
    params = {'key': api_key, 'q': city}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        return f"{data['current']['temp_c']}°C, {data['current']['condition']['text']}"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## ✅ Summary

You now have a fully functional RAG system with:

- ✅ Dynamic function loading
- ✅ Automatic function execution in LLM answers
- ✅ Real-time file watching
- ✅ RESTful API
- ✅ CLI management tools
- ✅ Web interface
- ✅ Comprehensive logging

**Next steps:**
1. Add your own custom functions
2. Upload domain-specific documents
3. Configure prompt strategies
4. Monitor function execution logs
5. Deploy to production

Happy coding! 🎉