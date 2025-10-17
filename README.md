# RAG Chat System with Hierarchical Search

A robust Retrieval-Augmented Generation (RAG) system with intelligent folder-based document organization and local LLM integration via Ollama.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- 🗂️ **Hierarchical Document Organization** - Organize documents by category/topic for intelligent search
- 🔍 **Two-Stage Retrieval** - Searches relevant folders first, then finds best matching content
- 🤖 **Local LLM Integration** - Uses Ollama for privacy-focused, offline AI responses
- 🧠 **8 Prompt Strategies** - Direct, Detailed, Chain-of-Thought, Reasoning, Analytical, Comparative, Extractive, ELI5
- 🌍 **Multilingual Support** - Handles English, Japanese, and other languages
- 🤔 **Smart Reasoning Detection** - Auto-detects thinking process for Qwen/DeepSeek/R1 models
- 📊 **Real-time Monitoring** - Index statistics and health check endpoints
- 🔄 **Auto-indexing** - Watches folders and automatically updates index on file changes
- 💪 **Robust Error Handling** - Graceful degradation with comprehensive logging
- 🎨 **Modern UI** - Drag-and-drop uploads, collapsible folders, relevance scores

## Architecture

```
┌─────────────┐
│   Upload    │
│  Documents  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Hierarchical File System   │
│  documents/{category}/file  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Sentence Transformers     │
│   (Embeddings + FAISS)      │
└──────────┬──────────────────┘
           │
           ▼
     ┌─────────┐
     │  Query  │
     └────┬────┘
          │
          ▼
┌──────────────────────┐
│  Stage 1: Find Top   │
│  Relevant Folders    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Stage 2: Retrieve   │
│  Best Chunks         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Ollama LLM         │
│   (llama3.2:3b)      │
└──────────┬───────────┘
           │
           ▼
      ┌────────┐
      │ Answer │
      └────────┘
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

## Prompt Strategies

The system includes 8 different prompt strategies:

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

### Reasoning Model Support

For models like Qwen, DeepSeek, and R1 that naturally output reasoning without tags, the system automatically:
- Detects reasoning patterns ("Let me think...", "First...", etc.)
- Separates thinking process from final answer
- Displays reasoning in collapsible UI section

Configure reasoning models:
```python
REASONING_MODELS = ["qwen", "deepseek", "r1"]  # Auto-detected
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

### 3. Access Web Interface

Open browser to `http://localhost:5000`

### 4. Add Documents

**Option A: Web Upload**
1. Enter category name (e.g., "technical", "research")
2. Drag-and-drop or select file
3. System auto-indexes

**Option B: Manual**
```bash
mkdir -p documents/technical
cp manual.pdf documents/technical/
# System auto-detects and indexes
```

### 5. Ask Questions

Enter questions in the web interface. The system:
1. Finds relevant folders
2. Retrieves best matching content
3. Generates contextual answers
4. Shows sources with relevance scores

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
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/` | POST | Upload document |
| `/ask` | POST | Submit question |
| `/doc/<path>` | GET | Download document |
| `/health` | GET | Health check (JSON) |
| `/stats` | GET | Index statistics (JSON) |

### Example API Calls

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Query:**
```bash
curl -X POST -d "question=What is machine learning?" \
     http://localhost:5000/ask
```

**Upload:**
```bash
curl -X POST -F "file=@document.pdf" -F "folder=research" \
     http://localhost:5000/
```

## Supported File Types

- `.txt` - Text files (UTF-8, Shift-JIS, CP932, etc.)
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents

Maximum file size: 50MB (configurable)

## Project Structure

```
.
├── app.py          # Main application
├── templates/
│   └── index.html  # Web interface
├── documents/               # Default documents (auto-created)
│   ├── general/
│   ├── technical/
│   └── research/
├── uploaded_docs/           # User uploads (auto-created)
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

### Index Not Building
- Check logs for specific file errors
- Remove corrupted files
- Verify file permissions

### Encoding Issues
System tries multiple encodings automatically. For persistent issues, add encodings in `load_txt()`.

## Development

### Run in Debug Mode
```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

### View Logs
```bash
python app.py 2>&1 | tee app.log
```

### Add Custom Prompt Template
```python
PROMPT_TEMPLATES["custom"] = """Context: {context}

Question: {question}

Your custom instructions here."""
```

## Security Notes

**For Production:**
1. Change secret key: `app.secret_key = os.environ.get("SECRET_KEY")`
2. Use HTTPS/SSL
3. Add authentication
4. Limit file uploads
5. Implement rate limiting
6. Use environment variables for sensitive config

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## License

MIT License - see [LICENSE](LICENSE.md) file

## Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Flask](https://flask.palletsprojects.com/) - Web framework

## Roadmap

- [ ] Multi-user authentication
- [ ] Document versioning
- [ ] Export search results
- [ ] GPU acceleration
- [ ] Docker deployment
- [ ] REST API documentation
- [ ] Advanced filtering
- [ ] Document preview

---

**Made with ❤️ for privacy-focused AI document search**
