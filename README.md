# RAG Chat System with Hierarchical Search & Dynamic Functions

A robust Retrieval-Augmented Generation (RAG) system with intelligent folder-based document organization, local LLM integration via Ollama, and dynamic Python function execution.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### Core RAG Features
- 🗂️ **Hierarchical Document Organization** - Organize documents by category/topic for intelligent search
- 🔍 **Two-Stage Retrieval** - Searches relevant folders first, then finds best matching content
- 🤖 **Local LLM Integration** - Uses Ollama for privacy-focused, offline AI responses
- 🧠 **8 Prompt Strategies** - Direct, Detailed, Chain-of-Thought, Reasoning, Analytical, Comparative, Extractive, ELI5
- 🌍 **Multilingual Support** - Handles English, Japanese, and other languages

### Dynamic Function System
- ⚡ **Auto-Loading Functions** - Automatically discovers and loads Python functions from `functions/` directory
- 🔄 **Hot Reload** - File watcher detects changes and reloads functions in real-time
- 🎯 **Auto-Execution** - Detects calculations in questions and executes automatically
- 🔧 **Flexible Syntax** - Supports both explicit tags `<run:math/add a=5 b=3>` and auto-detection
- 📝 **Function Logging** - All executions logged to `function_calls.log`
- 🌐 **REST API** - Endpoints for listing and executing functions
- 💻 **CLI Tool** - Test and manage functions from command line

### Additional Features
- 🤔 **Smart Reasoning Detection** - Auto-detects thinking process for Qwen/DeepSeek/R1 models
- 📊 **Real-time Monitoring** - Index statistics and health check endpoints
- 🔄 **Auto-indexing** - Watches folders and automatically updates index on file changes
- 💪 **Robust Error Handling** - Graceful degradation with comprehensive logging
- 🎨 **Modern UI** - Functions tab, drag-and-drop uploads, collapsible folders

## Architecture

```
┌─────────────┐         ┌─────────────────┐
│   Upload    │         │    Functions    │
│  Documents  │         │    Directory    │
└──────┬──────┘         └────────┬────────┘
       │                         │
       ▼                         ▼
┌─────────────────────┐   ┌──────────────────┐
│ Hierarchical Storage│   │ Function Manager │
│ documents/{cat}/    │   │ Auto-Discovery   │
└──────────┬──────────┘   └────────┬─────────┘
           │                       │
           ▼                       │
┌──────────────────────┐          │
│ Sentence Transformers│          │
│ Embeddings + FAISS   │          │
└──────────┬───────────┘          │
           │                      │
     ┌─────▼──────┐               │
     │   Query    │               │
     └─────┬──────┘               │
           │                      │
           ▼                      │
┌──────────────────────┐          │
│ Stage 1: Find Top    │          │
│ Relevant Folders     │          │
└──────────┬───────────┘          │
           │                      │
           ▼                      │
┌──────────────────────┐          │
│ Stage 2: Retrieve    │          │
│ Best Chunks          │          │
└──────────┬───────────┘          │
           │                      │
           ▼                      │
┌──────────────────────┐          │
│   Ollama LLM         │          │
│   (llama3.2:3b)      │          │
└──────────┬───────────┘          │
           │                      │
           ▼                      │
      ┌────────┐                  │
      │ Answer │◄─────────────────┘
      └────┬───┘      Parse & Execute
           │          Functions
           ▼
    ┌─────────────┐
    │Final Output │
    └─────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- Ollama

### 1. Clone Repository

```bash
git clone https://github.com/Rikiza89/RAG-Chat-System-with-Hierarchical-Search.git
cd RAG-Chat-System-with-Hierarchical-Search
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Create `requirements.txt`:
```txt
flask>=2.0.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
PyMuPDF>=1.23.0
python-docx>=0.8.11
watchdog>=3.0.0
werkzeug>=2.0.0
numpy>=1.21.0
```

### 3. Install Ollama

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com)

### 4. Download LLM Model

```bash
ollama pull llama3.2:3b
```

Alternative models:
- `phi3:mini` - Faster, smaller
- `tinyllama` - Ultra-fast, basic
- `qwen3:4b` - Multilingual
- `deepseek-r1:8b` - Advanced reasoning

### 5. Set Up Functions (Optional)

```bash
# Create function directories
mkdir -p functions/math
mkdir -p functions/text
mkdir -p functions/utils

# Add example functions (see Function System section)
```

## Quick Start

### 1. Start Ollama

```bash
ollama serve
```

### 2. Run Application

```bash
python app.py
```

Output:
```
INFO - Function manager initialized with 8 functions
INFO - Initial index built successfully
INFO - Document watcher started
INFO - Functions watcher started
INFO - Starting Flask server on http://0.0.0.0:5000
```

### 3. Access Web Interface

Open browser to `http://localhost:5000`

### 4. Add Documents

**Option A: Web Upload**
1. Click "Upload Documents" tab
2. Enter category name (e.g., "technical", "research")
3. Drag-and-drop or select file
4. System auto-indexes

**Option B: Manual**
```bash
mkdir -p documents/technical
cp manual.pdf documents/technical/
# System auto-detects and indexes
```

### 5. Ask Questions

**Regular question:**
```
What is machine learning?
```

**With explicit function call:**
```
What is 15 plus 27? <run:math/add a=15 b=27>
```

**Auto-detected (no tag needed):**
```
What is 15 plus 27?
```
System automatically detects and executes `math/add`.

## Function System

### Overview

The system dynamically loads Python functions from the `functions/` directory and can execute them:
1. **Explicitly** via `<run:function_name arg=value>` syntax in questions
2. **Automatically** by detecting calculations in questions
3. **Via API** using REST endpoints

### Directory Structure

```
functions/
├── math/
│   ├── add.py
│   ├── multiply.py
│   └── subtract.py
├── text/
│   ├── summarize.py
│   ├── translate.py
│   └── word_count.py
└── utils/
    ├── format.py
    └── json_prettify.py
```

### Creating Functions

**Basic function (`functions/math/add.py`):**
```python
def run(a, b):
    """Add two numbers together"""
    return a + b

def add_three(a, b, c):
    """Add three numbers"""
    return a + b + c
```

**Accessing:**
- `math/add` → calls `run(a, b)`
- `math/add/add_three` → calls `add_three(a, b, c)`

**Text processing (`functions/text/summarize.py`):**
```python
def run(text, max_length=100):
    """Summarize text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3].rsplit(' ', 1)[0] + '...'
```

### Function Syntax

**Explicit execution:**
```
Calculate this: <run:math/add a=15 b=27>
Summarize: <run:text/summarize text="Long text here" max_length=50>
```

**Auto-detection patterns:**
- `What is 15 plus 27?` → auto-executes `math/add`
- `Calculate 4 times 8` → auto-executes `math/multiply`
- `What is 100 minus 42?` → auto-executes `math/subtract`

### CLI Tool

**List functions:**
```bash
python manage_functions.py list
```

**Test function:**
```bash
python manage_functions.py run math/add a=5 b=3
# Output: ✅ Success! Result: 8
```

**Get function info:**
```bash
python manage_functions.py info math/add
```

**Test all functions:**
```bash
python manage_functions.py test
```

### Hot Reload

Functions are automatically reloaded when:
- New `.py` file added to `functions/`
- Existing function file modified
- Function file deleted

Changes detected within 2 seconds (configurable).

### Function API Endpoints

**List all functions:**
```bash
curl http://localhost:5000/functions
```

Response:
```json
{
  "total_functions": 8,
  "last_updated": "2025-10-18T10:30:45",
  "functions": [
    {
      "name": "math/add",
      "params": ["a", "b"],
      "signature": "(a, b)",
      "doc": "Add two numbers together"
    }
  ]
}
```

**Execute function:**
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{"name": "math/add", "kwargs": {"a": 5, "b": 3}}'
```

Response:
```json
{
  "status": "success",
  "result": 8,
  "function": "math/add"
}
```

**Reload functions manually:**
```bash
curl -X POST http://localhost:5000/reload_functions
```

### Example Functions

**Calculator (`functions/calc/advanced.py`):**
```python
import math

def run(expression):
    """Evaluate mathematical expression"""
    allowed = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'pi': math.pi
    }
    return eval(expression, {"__builtins__": {}}, allowed)
```

Usage: `<run:calc/advanced expression="sqrt(16) + 5">`

**Data analysis (`functions/data/stats.py`):**
```python
def run(numbers):
    """Calculate statistics"""
    nums = [float(x) for x in numbers.split(',')]
    return {
        'mean': sum(nums) / len(nums),
        'min': min(nums),
        'max': max(nums)
    }
```

Usage: `<run:data/stats numbers="10,20,30,40">`

### Function Logging

All executions logged to `function_calls.log`:

```json
{"timestamp": "2025-10-18T10:30:45", "function": "math/add", "args": "[]", "kwargs": "{'a': 5, 'b': 3}", "result": "8", "status": "success"}
```

View logs:
```bash
tail -f function_calls.log
grep '"status": "error"' function_calls.log
```

## Prompt Strategies

| Strategy | Use Case | Output Style |
|----------|----------|--------------|
| **Direct** | Quick facts | Concise, focused answer |
| **Detailed** | Comprehensive info | Thorough with examples |
| **Chain-of-Thought** | Complex questions | Step-by-step reasoning |
| **Reasoning** | Deep analysis | Explicit thinking process |
| **Analytical** | Critical thinking | Structured analysis with evidence |
| **Comparative** | Compare/contrast | Highlights similarities and differences |
| **Extractive** | Fact extraction | Direct quotes and key information |
| **ELI5** | Simplification | Simple terms, uses analogies |

## Configuration

Edit `app.py`:

```python
# Folders
DEFAULT_DOCS_FOLDER = "documents"
UPLOAD_FOLDER = "uploaded_docs"

# Processing
CHUNK_SIZE = 300              # Characters per chunk
CHUNK_OVERLAP = 30            # Overlap between chunks
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Retrieval
TOP_K_FOLDERS = 2             # Folders to search
TOP_K_CHUNKS = 3              # Chunks per folder

# LLM
LLM_MODEL = "llama3.2:3b"
LLM_TIMEOUT = 120             # Seconds
PROMPT_STRATEGY = "direct"    # Default strategy

# Functions
REBUILD_DEBOUNCE = 2          # Seconds before reloading functions
```

## API Endpoints

### Document & Query Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/` | POST | Upload document |
| `/ask` | POST | Submit question |
| `/doc/<path>` | GET | Download document |
| `/health` | GET | Health check (JSON) |
| `/stats` | GET | Index statistics (JSON) |

### Function Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/functions` | GET | List all functions (JSON) |
| `/run_function` | POST | Execute function (JSON) |
| `/function/<name>` | GET | Get function info (JSON) |
| `/reload_functions` | POST | Reload all functions |

### Example API Calls

**Query with auto-execution:**
```bash
curl -X POST -d "question=What is 10 plus 5?" \
     http://localhost:5000/ask
```

**Execute function directly:**
```bash
curl -X POST http://localhost:5000/run_function \
  -H "Content-Type: application/json" \
  -d '{"name": "text/summarize", "kwargs": {"text": "Long text", "max_length": 20}}'
```

## Supported File Types

- `.txt` - Text files (UTF-8, Shift-JIS, CP932, etc.)
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents

Maximum file size: 50MB (configurable)

## Project Structure

```
.
├── app.py                    # Main Flask application
├── functions_manager.py      # Function loading & execution
├── functions_watcher.py      # Hot reload for functions
├── manage_functions.py       # CLI tool
├── templates/
│   └── index.html           # Web interface with functions tab
├── documents/               # Default documents (auto-created)
│   ├── general/
│   ├── technical/
│   └── research/
├── uploaded_docs/           # User uploads (auto-created)
├── functions/               # Dynamic functions (auto-created)
│   ├── math/
│   ├── text/
│   └── utils/
├── functions_list.json      # Auto-generated function registry
├── function_calls.log       # Execution log
└── requirements.txt
```

## Performance Optimization

### Low-end Hardware (2-4 cores)
```python
CHUNK_SIZE = 200
TOP_K_FOLDERS = 1
TOP_K_CHUNKS = 2
LLM_MODEL = "phi3:mini"
torch.set_num_threads(2)
```

### High-end Hardware (8+ cores)
```python
CHUNK_SIZE = 500
TOP_K_FOLDERS = 3
TOP_K_CHUNKS = 5
torch.set_num_threads(4)
```

## Troubleshooting

### Functions Not Loading

**Check logs:**
```bash
python manage_functions.py list
```

**Common issues:**
- Syntax errors in function files
- Files starting with `_` (ignored by design)
- Import errors

**Debug:**
```bash
python debug_functions.py
```

### Functions Not Executing

**Verify syntax:**
- ✅ Correct: `<run:math/add a=5 b=3>`
- ❌ Wrong: `<run:math.add a=5 b=3>` (use `/` not `.`)

**Enable auto-detection:**
Auto-detection is enabled by default for math operations in questions.

### Ollama Not Responding
```bash
# Check status
ollama list

# Restart service
pkill ollama
ollama serve
```

### Slow Performance
- Use smaller model: `phi3:mini` or `tinyllama`
- Reduce `TOP_K_FOLDERS` and `TOP_K_CHUNKS`
- Decrease `CHUNK_SIZE`

## Security Notes

**Function Safety:**
- Functions run in isolated namespaces
- No `eval()` or `exec()` on user input
- File operations restricted to project directories
- Consider adding timeouts for long-running functions

**General Security:**
1. Change secret key in production
2. Add authentication for multi-user deployments
3. Implement rate limiting
4. Validate all file uploads
5. Use environment variables for secrets

## Development

### Add Custom Function

1. Create file: `functions/category/function_name.py`
2. Define function with docstring
3. System auto-loads within 2 seconds

```python
def run(param1, param2):
    """Your function description"""
    # Your logic
    return result
```

### Add Custom Prompt Template
```python
PROMPT_TEMPLATES["custom"] = """Context: {context}

Question: {question}

Your custom instructions here."""
```

### Debug Mode
```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Add tests for new functions
4. Commit changes
5. Open pull request

## License

MIT License - see [LICENSE](LICENSE.md) file

## Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Watchdog](https://github.com/gorakhargosh/watchdog) - File monitoring

## Roadmap

### Core Features
- [ ] Multi-user authentication
- [ ] Document versioning
- [ ] Export search results
- [ ] GPU acceleration
- [ ] Advanced filtering

### Function System
- [ ] Function marketplace/sharing
- [ ] Async function execution
- [ ] Function chaining
- [ ] Sandbox isolation
- [ ] Type validation

---

**Made with ❤️ for privacy-focused AI document search with extensible function calling**