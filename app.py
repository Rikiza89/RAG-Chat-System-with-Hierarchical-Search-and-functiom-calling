import os
import re
import faiss
import numpy as np
import subprocess
import json
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, jsonify
from sentence_transformers import SentenceTransformer
import fitz
import docx
from werkzeug.utils import secure_filename
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
from datetime import datetime
from collections import defaultdict
import logging
from pathlib import Path

from functions_manager import get_function_manager
from functions_watcher import start_functions_watcher

# ================= CONFIG ==================
DEFAULT_DOCS_FOLDER = "documents"
UPLOAD_FOLDER = "uploaded_docs"
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
TOP_K_FOLDERS = 2  # Number of relevant folders to search
TOP_K_CHUNKS = 3   # Number of chunks per folder
LLM_MODEL = "llama3.2:3b"
LLM_TIMEOUT = 360
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
REBUILD_DEBOUNCE = 2  # seconds to wait before rebuilding after file changes

# Prompt templates
PROMPT_TEMPLATES = {
    "direct": """Context: {context}

Question: {question}

Answer concisely based only on the context above.""",
    
    "detailed": """Context: {context}

Question: {question}

Provide a comprehensive and detailed answer based on the context. Include relevant examples and explanations.""",
    
    "chain_of_thought": """Context: {context}

Question: {question}

Let's think step by step:
1. First, identify the key information in the context
2. Then, analyze how it relates to the question
3. Finally, provide a clear answer

Answer:""",
    
    "reasoning": """Context: {context}

Question: {question}

<think>
First, analyze the context and break down the question into components.
</think>

Provide a clear answer based on your analysis.""",
    
    "analytical": """Context: {context}

Question: {question}

Analyze the context carefully and provide:
1. Direct answer
2. Supporting evidence from context
3. Any relevant implications or connections""",
    
    "comparative": """Context: {context}

Question: {question}

Compare and contrast the information in the context, then answer the question by highlighting similarities, differences, and key points.""",
    
    "extractive": """Context: {context}

Question: {question}

Extract the most relevant information from the context and synthesize it into a clear, factual answer. Quote key phrases when appropriate.""",
    
    "eli5": """Context: {context}

Question: {question}

Explain the answer in simple terms as if explaining to someone unfamiliar with the topic. Use analogies if helpful."""
}

PROMPT_STRATEGY = "direct"

# Models that output reasoning without tags (need special handling)
REASONING_MODELS = ["qwen", "deepseek", "r1"]

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================= FLASK APP =================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# ================= GLOBALS =================
global_chunks = []
global_index = None
global_embed_model = None
chunk_metadata = []  # Stores {chunk, folder, filename, timestamp}
folder_indices = {}  # folder_name -> list of chunk indices
last_index_update = None
rebuild_lock = threading.Lock()
rebuild_timer = None
index_stats = {"total_chunks": 0, "total_files": 0, "folders": {}}
function_manager = None
functions_observer = None

# ================= ERROR CLASSES =================
class DocumentLoadError(Exception):
    """Raised when document loading fails"""
    pass

class IndexBuildError(Exception):
    """Raised when index building fails"""
    pass

class LLMError(Exception):
    """Raised when LLM call fails"""
    pass

import re
import json
from typing import Dict, List, Any, Optional

def detect_and_execute_functions(answer_text: str, question: str, function_manager) -> tuple:
    """
    Multi-strategy function detection and execution
    
    Strategies:
    1. Explicit tags: <run:func a=1>
    2. Auto-detection: parse question for calculable expressions
    3. Intent-based: detect calculation requests in answer
    4. Tool-use format: JSON function calls
    """
    
    if not function_manager:
        return answer_text, []
    
    # Strategy 1: Explicit tags (existing)
    explicit_results = parse_explicit_tags(answer_text, function_manager)
    
    # Strategy 2: Auto-detect from question
    auto_results = auto_detect_from_question(question, function_manager)
    
    # Strategy 3: Detect math expressions in answer
    expression_results = detect_math_expressions(answer_text, function_manager)
    
    # Combine all results
    all_results = explicit_results + auto_results + expression_results
    
    # Process and format
    processed_text = answer_text
    function_outputs = []
    
    for result in all_results:
        if result['result']['status'] == 'success':
            # Append result to answer
            func_name = result['function']
            result_value = result['result']['result']
            
            # Add visual separator
            addition = f"\n\n➤ **Function Result:** `{func_name}` = **{result_value}**"
            processed_text += addition
            
            function_outputs.append({
                "function": func_name,
                "status": "success",
                "result": result_value,
                "args": result.get('parsed_kwargs', {}),
                "trigger": result.get('trigger', 'explicit')
            })
    
    return processed_text, function_outputs


def parse_explicit_tags(text: str, manager) -> List[Dict]:
    """Parse explicit <run:func> tags"""
    results = manager.parse_and_execute_from_text(text)
    for r in results:
        r['trigger'] = 'explicit_tag'
    return results


def auto_detect_from_question(question: str, manager) -> List[Dict]:
    """
    Auto-detect function calls from question patterns
    
    Patterns:
    - "What is X plus Y" -> math/add
    - "Calculate X * Y" -> math/multiply
    - "Summarize this text" -> text/summarize
    """
    results = []
    
    # Pattern 1: Addition
    add_patterns = [
        r'what\s+is\s+(\d+)\s+plus\s+(\d+)',
        r'calculate\s+(\d+)\s*\+\s*(\d+)',
        r'add\s+(\d+)\s+and\s+(\d+)',
        r'(\d+)\s+\+\s+(\d+)',
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            result = manager.execute_function('math/add', kwargs={'a': a, 'b': b})
            results.append({
                'function': 'math/add',
                'parsed_kwargs': {'a': a, 'b': b},
                'result': result,
                'trigger': 'auto_question',
                'match': match.group(0)
            })
            break  # Only trigger once
    
    # Pattern 2: Multiplication
    mult_patterns = [
        r'what\s+is\s+(\d+)\s+times\s+(\d+)',
        r'calculate\s+(\d+)\s*\*\s*(\d+)',
        r'multiply\s+(\d+)\s+by\s+(\d+)',
        r'(\d+)\s+×\s+(\d+)',
    ]
    
    for pattern in mult_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            result = manager.execute_function('math/multiply', kwargs={'a': a, 'b': b})
            results.append({
                'function': 'math/multiply',
                'parsed_kwargs': {'a': a, 'b': b},
                'result': result,
                'trigger': 'auto_question',
                'match': match.group(0)
            })
            break
    
    return results


def detect_math_expressions(answer_text: str, manager) -> List[Dict]:
    """
    Detect mathematical expressions in answer and compute them
    
    Pattern: "X + Y = Z" or "X + Y" alone
    """
    results = []
    
    # Look for simple arithmetic in answer
    patterns = [
        (r'(\d+)\s*\+\s*(\d+)\s*=\s*\d+', 'math/add'),
        (r'(\d+)\s*\*\s*(\d+)\s*=\s*\d+', 'math/multiply'),
    ]
    
    for pattern, func_name in patterns:
        match = re.search(pattern, answer_text)
        if match:
            a = int(match.group(1))
            b = int(match.group(2))
            
            result = manager.execute_function(func_name, kwargs={'a': a, 'b': b})
            
            # Only add if not already computed
            if result['status'] == 'success':
                results.append({
                    'function': func_name,
                    'parsed_kwargs': {'a': a, 'b': b},
                    'result': result,
                    'trigger': 'auto_answer',
                    'match': match.group(0)
                })
    
    return results


def enhance_prompt_with_functions(context: str, question: str, function_manager) -> str:
    """
    Enhance the prompt to inform LLM about available functions
    """
    if not function_manager or not function_manager.function_registry:
        return ""
    
    # Get top 10 most relevant functions
    available_funcs = list(function_manager.function_registry.keys())[:10]
    
    func_descriptions = []
    for func_name in available_funcs:
        func_data = function_manager.function_registry[func_name]
        func_descriptions.append(
            f"- {func_name}{func_data['signature']}: {func_data['doc']}"
        )
    
    functions_info = "\n".join(func_descriptions)
    
    enhanced_prompt = f"""Available Functions:
{functions_info}

If you need to call a function, use this syntax:
<run:function_name arg1=value1 arg2=value2>

For example: <run:math/add a=15 b=27>

Context: {context}

Question: {question}

Answer the question. If calculation is needed, include the function call in your answer."""
    
    return enhanced_prompt
# ================= HELPERS =================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_folder_name(name):
    """Sanitize folder name for safe file system operations"""
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

def is_japanese(text):
    """Detect if text contains significant Japanese characters"""
    if not text:
        return False
    jp_chars = re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9faf]", text)
    ratio = len(jp_chars) / max(len(text), 1)
    return ratio > 0.2

def detect_language(docs):
    """Detect predominant language and select appropriate model"""
    sample = " ".join(docs[:5])[:2000] if docs else ""
    if is_japanese(sample):
        logger.info("Japanese content detected")
        return "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    else:
        logger.info("Using multilingual model")
        return "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def check_ollama_available():
    """Check if Ollama is installed and accessible"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.error(f"Ollama not available: {e}")
        return False

def check_model_available(model_name):
    """Check if specific Ollama model is downloaded"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0:
            return model_name in result.stdout
        return False
    except Exception as e:
        logger.error(f"Failed to check model availability: {e}")
        return False

def process_answer_with_functions(answer_text, question=""):
    """
    Enhanced function processing with multiple detection strategies
    """
    global function_manager
    
    if not function_manager:
        return answer_text, []
    
    all_results = []
    
    # Strategy 1: Explicit tags <run:func>
    explicit = function_manager.parse_and_execute_from_text(answer_text)
    all_results.extend(explicit)
    
    # Strategy 2: Auto-detect from question
    if question:
        auto_results = auto_detect_from_question(question)
        all_results.extend(auto_results)
    
    # Build output
    processed_text = answer_text
    function_outputs = []
    
    # If no explicit tags but we have auto-detected functions
    if not explicit and auto_results:
        processed_text += "\n\n---\n**🔢 Automated Calculation:**\n"
    
    for result in all_results:
        if result['result']['status'] == 'success':
            func_name = result['function']
            result_value = result['result']['result']
            trigger = result.get('trigger', 'explicit')
            
            # Format based on trigger type
            if trigger == 'explicit':
                # Replace the tag with result
                if 'match' in result:
                    replacement = f"**{result_value}**"
                    processed_text = processed_text.replace(result['match'], replacement)
            else:
                # Append for auto-detected
                args_str = ', '.join(f"{k}={v}" for k, v in result['parsed_kwargs'].items())
                processed_text += f"\n`{func_name}({args_str})` = **{result_value}** ✅"
            
            function_outputs.append({
                "function": func_name,
                "status": "success",
                "result": result_value,
                "args": result.get('parsed_kwargs', {}),
                "trigger": trigger
            })
    
    return processed_text, function_outputs


def auto_detect_from_question(question):
    """Auto-detect calculations from question text"""
    global function_manager
    results = []
    
    # Addition patterns
    add_patterns = [
        r'what\s+is\s+(\d+)\s+plus\s+(\d+)',
        r'calculate\s+(\d+)\s*\+\s*(\d+)',
        r'(\d+)\s*\+\s*(\d+)',
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            result = function_manager.execute_function('math/add', kwargs={'a': a, 'b': b})
            results.append({
                'function': 'math/add',
                'parsed_kwargs': {'a': a, 'b': b},
                'result': result,
                'trigger': 'auto',
                'match': match.group(0)
            })
            break
    
    # Multiplication patterns
    mult_patterns = [
        r'what\s+is\s+(\d+)\s+times\s+(\d+)',
        r'calculate\s+(\d+)\s*\*\s*(\d+)',
        r'(\d+)\s*\*\s*(\d+)',
    ]
    
    for pattern in mult_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            a, b = int(match.group(1)), int(match.group(2))
            result = function_manager.execute_function('math/multiply', kwargs={'a': a, 'b': b})
            results.append({
                'function': 'math/multiply',
                'parsed_kwargs': {'a': a, 'b': b},
                'result': result,
                'trigger': 'auto',
                'match': match.group(0)
            })
            break
    
    return results

# ================= FILE LOADING =================

def load_txt(path):
    """Load text file with multiple encoding attempts"""
    encodings = ['utf-8', 'shift_jis', 'cp932', 'euc_jp', 'iso2022_jp', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
                if content.strip():  # Verify content is not empty
                    logger.info(f"Loaded {os.path.basename(path)} with {encoding}")
                    return content
        except (UnicodeDecodeError, LookupError):
            continue
        except Exception as e:
            logger.error(f"Unexpected error reading {path} with {encoding}: {e}")
            continue
    
    # Last resort: ignore errors
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if content.strip():
                logger.warning(f"Loaded {os.path.basename(path)} with errors ignored")
                return content
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        raise DocumentLoadError(f"Could not read file {path}: {e}")
    
    raise DocumentLoadError(f"File {path} is empty or unreadable")

def load_pdf(path):
    """Load PDF file with error handling"""
    try:
        text = ""
        with fitz.open(path) as pdf:
            if len(pdf) == 0:
                raise DocumentLoadError(f"PDF {path} has no pages")
            
            for page_num, page in enumerate(pdf):
                try:
                    page_text = page.get_text()
                    text += page_text
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num} from {path}: {e}")
                    continue
        
        if not text.strip():
            raise DocumentLoadError(f"PDF {path} contains no extractable text")
        
        return text
    except fitz.FileDataError as e:
        raise DocumentLoadError(f"Corrupted PDF {path}: {e}")
    except Exception as e:
        raise DocumentLoadError(f"Failed to load PDF {path}: {e}")

def load_docx(path):
    """Load DOCX file with error handling"""
    try:
        doc = docx.Document(path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
        if not text.strip():
            raise DocumentLoadError(f"DOCX {path} contains no text")
        
        return text
    except docx.opc.exceptions.PackageNotFoundError:
        raise DocumentLoadError(f"Invalid DOCX file {path}")
    except Exception as e:
        raise DocumentLoadError(f"Failed to load DOCX {path}: {e}")

def load_document(filepath):
    """Load single document with appropriate loader"""
    ext = filepath.lower().split('.')[-1]
    
    try:
        if ext == "txt":
            return load_txt(filepath)
        elif ext == "pdf":
            return load_pdf(filepath)
        elif ext == "docx":
            return load_docx(filepath)
        else:
            raise DocumentLoadError(f"Unsupported file type: {ext}")
    except DocumentLoadError:
        raise
    except Exception as e:
        raise DocumentLoadError(f"Unexpected error loading {filepath}: {e}")

def load_documents_from_folder(folder_path):
    """Load all documents from a folder, returns dict of filename -> content"""
    documents = {}
    
    if not os.path.exists(folder_path):
        logger.warning(f"Folder does not exist: {folder_path}")
        return documents
    
    try:
        files = os.listdir(folder_path)
    except PermissionError:
        logger.error(f"Permission denied accessing folder: {folder_path}")
        return documents
    except Exception as e:
        logger.error(f"Error listing folder {folder_path}: {e}")
        return documents
    
    for filename in files:
        if not allowed_file(filename):
            continue
        
        filepath = os.path.join(folder_path, filename)
        
        # Skip directories
        if os.path.isdir(filepath):
            continue
        
        try:
            content = load_document(filepath)
            documents[filename] = content
            logger.info(f"Loaded: {filename} ({len(content)} chars)")
        except DocumentLoadError as e:
            logger.error(f"Skipping {filename}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error with {filename}: {e}")
            continue
    
    return documents

def scan_folder_structure(base_folder):
    """
    Scan folder structure and return organized documents
    Returns: {folder_name: {filename: content}}
    """
    structure = defaultdict(dict)
    
    if not os.path.exists(base_folder):
        logger.warning(f"Base folder does not exist: {base_folder}")
        return structure
    
    try:
        # Check if base folder has subdirectories
        items = os.listdir(base_folder)
        has_subdirs = any(os.path.isdir(os.path.join(base_folder, item)) for item in items)
        
        if has_subdirs:
            # Hierarchical structure: documents/{category}/file.txt
            for item in items:
                subfolder_path = os.path.join(base_folder, item)
                if os.path.isdir(subfolder_path):
                    docs = load_documents_from_folder(subfolder_path)
                    if docs:
                        structure[item] = docs
                        logger.info(f"Loaded folder '{item}': {len(docs)} files")
        else:
            # Flat structure: put all in 'general' category
            docs = load_documents_from_folder(base_folder)
            if docs:
                structure["general"] = docs
                logger.info(f"Loaded flat structure: {len(docs)} files")
    
    except Exception as e:
        logger.error(f"Error scanning folder structure {base_folder}: {e}")
    
    return structure

def chunk_text(text):
    """Split text into overlapping chunks"""
    if not text or not text.strip():
        return []
    
    chunks = []
    text = text.strip()
    
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = text[i : i + CHUNK_SIZE].strip()
        if len(chunk) > 50:  # Minimum chunk size
            chunks.append(chunk)
    
    return chunks if chunks else [text]  # Return full text if no chunks created

# ================= INDEX BUILDING =================

def rebuild_index():
    """Rebuild FAISS index with hierarchical folder organization"""
    global global_chunks, global_index, global_embed_model
    global chunk_metadata, folder_indices, last_index_update, index_stats
    
    with rebuild_lock:
        try:
            logger.info("Starting index rebuild...")
            
            # Scan both document folders
            all_structures = {}
            for base_folder in [DEFAULT_DOCS_FOLDER, UPLOAD_FOLDER]:
                structure = scan_folder_structure(base_folder)
                for folder_name, docs in structure.items():
                    # Prefix with base folder type for uniqueness
                    folder_key = f"{os.path.basename(base_folder)}_{folder_name}"
                    all_structures[folder_key] = {
                        "docs": docs,
                        "base": base_folder
                    }
            
            if not all_structures:
                logger.warning("No documents found in any folder")
                global_chunks = []
                global_index = None
                global_embed_model = None
                chunk_metadata.clear()
                folder_indices.clear()
                index_stats = {"total_chunks": 0, "total_files": 0, "folders": {}}
                return
            
            # Prepare all text for language detection
            sample_texts = []
            for folder_data in all_structures.values():
                sample_texts.extend(list(folder_data["docs"].values())[:2])
            
            # Load embedding model
            embed_model_name = detect_language(sample_texts)
            try:
                model = SentenceTransformer(embed_model_name)
                model.to('cpu')
                import torch
                torch.set_num_threads(2)
            except Exception as e:
                raise IndexBuildError(f"Failed to load embedding model: {e}")
            
            # Process documents folder by folder
            all_chunks = []
            all_metadata = []
            folder_indices_temp = defaultdict(list)
            stats = {"total_chunks": 0, "total_files": 0, "folders": {}}
            
            for folder_name, folder_data in all_structures.items():
                folder_chunks = []
                folder_files = 0
                
                for filename, content in folder_data["docs"].items():
                    try:
                        doc_chunks = chunk_text(content)
                        
                        for chunk in doc_chunks:
                            chunk_idx = len(all_chunks)
                            all_chunks.append(chunk)
                            all_metadata.append({
                                "folder": folder_name,
                                "filename": filename,
                                "base_folder": folder_data["base"],
                                "timestamp": datetime.now().isoformat()
                            })
                            folder_indices_temp[folder_name].append(chunk_idx)
                            folder_chunks.append(chunk)
                        
                        folder_files += 1
                    except Exception as e:
                        logger.error(f"Failed to chunk {filename} in {folder_name}: {e}")
                        continue
                
                stats["folders"][folder_name] = {
                    "chunks": len(folder_chunks),
                    "files": folder_files
                }
                stats["total_chunks"] += len(folder_chunks)
                stats["total_files"] += folder_files
                
                logger.info(f"Folder '{folder_name}': {len(folder_chunks)} chunks from {folder_files} files")
            
            if not all_chunks:
                raise IndexBuildError("No valid chunks created from documents")
            
            # Create embeddings in batches
            logger.info(f"Creating embeddings for {len(all_chunks)} chunks...")
            batch_size = 8
            all_embeddings = []
            
            try:
                for i in range(0, len(all_chunks), batch_size):
                    batch = all_chunks[i:i+batch_size]
                    emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
                    all_embeddings.append(emb)
                
                embeddings = np.vstack(all_embeddings)
            except Exception as e:
                raise IndexBuildError(f"Failed to create embeddings: {e}")
            
            # Build FAISS index
            try:
                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim)
                faiss.normalize_L2(embeddings)
                index.add(embeddings)
            except Exception as e:
                raise IndexBuildError(f"Failed to build FAISS index: {e}")
            
            # Update globals
            global_chunks = all_chunks
            global_index = index
            global_embed_model = model
            chunk_metadata = all_metadata
            folder_indices = dict(folder_indices_temp)
            last_index_update = datetime.now()
            index_stats = stats
            
            logger.info(f"Index rebuilt successfully: {len(all_chunks)} chunks, {len(folder_indices)} folders")
            logger.info(f"Updated at {last_index_update.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except IndexBuildError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during index rebuild: {e}")
            raise IndexBuildError(f"Index rebuild failed: {e}")

def debounced_rebuild():
    """Debounced rebuild to avoid multiple rapid rebuilds"""
    global rebuild_timer
    
    if rebuild_timer:
        rebuild_timer.cancel()
    
    rebuild_timer = threading.Timer(REBUILD_DEBOUNCE, safe_rebuild)
    rebuild_timer.start()

def safe_rebuild():
    """Safely rebuild index with error handling"""
    try:
        rebuild_index()
    except IndexBuildError as e:
        logger.error(f"Index rebuild failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during rebuild: {e}")

# ================= RETRIEVAL =================

def retrieve_hierarchical(query, top_k_folders=TOP_K_FOLDERS, top_k_chunks=TOP_K_CHUNKS):
    """
    Two-stage retrieval:
    1. Find most relevant folders based on query
    2. Retrieve top chunks from those folders
    """
    global global_chunks, global_index, global_embed_model, chunk_metadata, folder_indices
    
    if global_index is None or global_embed_model is None:
        logger.warning("No index available for retrieval")
        return []
    
    try:
        # Encode query
        q_vec = global_embed_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_vec)
        
        # Stage 1: Find relevant folders
        folder_scores = defaultdict(float)
        
        for folder_name, chunk_indices in folder_indices.items():
            if not chunk_indices:
                continue
            
            # Get embeddings for this folder's chunks
            folder_vecs = np.array([global_index.reconstruct(int(idx)) for idx in chunk_indices[:100]])
            
            # Calculate similarity scores
            similarities = np.dot(folder_vecs, q_vec.T).flatten()
            folder_scores[folder_name] = float(np.max(similarities))
        
        # Get top folders
        top_folders = sorted(folder_scores.items(), key=lambda x: x[1], reverse=True)[:top_k_folders]
        logger.info(f"Top folders for query: {[f[0] for f in top_folders]}")
        
        # Stage 2: Retrieve chunks from top folders
        results = []
        seen_chunks = set()
        
        for folder_name, _ in top_folders:
            chunk_indices = folder_indices[folder_name]
            
            # Search within this folder
            folder_chunks = [global_chunks[idx] for idx in chunk_indices]
            folder_embeddings = np.array([global_index.reconstruct(int(idx)) for idx in chunk_indices])
            
            # Calculate similarities
            similarities = np.dot(folder_embeddings, q_vec.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k_chunks]
            
            for local_idx in top_indices:
                global_idx = chunk_indices[local_idx]
                chunk = global_chunks[global_idx]
                
                # Avoid duplicates
                if chunk in seen_chunks:
                    continue
                seen_chunks.add(chunk)
                
                metadata = chunk_metadata[global_idx]
                results.append({
                    "chunk": chunk,
                    "folder": metadata["folder"],
                    "filename": metadata["filename"],
                    "score": float(similarities[local_idx])
                })
        
        logger.info(f"Retrieved {len(results)} chunks from {len(top_folders)} folders")
        return results
    
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []

# ================= LLM CALL =================

def generate_prompt(context, question, strategy="direct"):
    """Generate prompt based on selected strategy"""
    template = PROMPT_TEMPLATES.get(strategy, PROMPT_TEMPLATES["direct"])
    return template.format(context=context, question=question)

def generate_prompt_with_functions(context, question, strategy="direct"):
    """
    Enhanced prompt that tells LLM about available functions
    """
    global function_manager
    
    # Get base prompt
    base_template = PROMPT_TEMPLATES.get(strategy, PROMPT_TEMPLATES["direct"])
    
    # Add function instructions if available
    func_instructions = ""
    if function_manager and function_manager.function_registry:
        available = list(function_manager.function_registry.keys())[:5]
        func_list = '\n'.join(f"  - {f}" for f in available)
        
        func_instructions = f"""

Available Functions:
{func_list}

To use a function, include: <run:function_name arg=value>
Example: <run:math/add a=15 b=27>
"""
    
    # Build prompt
    prompt = base_template.format(context=context, question=question)
    prompt = prompt + func_instructions
    
    return prompt

def ollama_generate(prompt, strategy="direct"):
    """Call Ollama with error handling and retry logic"""
    if not check_ollama_available():
        raise LLMError("Ollama is not running. Please start Ollama service.")
    
    if not check_model_available(LLM_MODEL):
        raise LLMError(f"Model '{LLM_MODEL}' not found. Please run: ollama pull {LLM_MODEL}")
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Ollama (attempt {attempt + 1}/{max_retries})...")
            result = subprocess.run(
                ["ollama", "run", LLM_MODEL],
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=LLM_TIMEOUT
            )
            
            if result.returncode != 0:
                err = result.stderr.decode("utf-8", errors="ignore")
                logger.error(f"Ollama error: {err}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise LLMError(f"Ollama returned error: {err}")
            
            response = result.stdout.decode("utf-8", errors="ignore")
            return response if response.strip() else "No response generated."
        
        except subprocess.TimeoutExpired:
            logger.error("Ollama timeout")
            if attempt < max_retries - 1:
                continue
            raise LLMError(f"Request timed out after {LLM_TIMEOUT} seconds. Try a smaller model.")
        
        except FileNotFoundError:
            raise LLMError("Ollama command not found. Please install Ollama.")
        
        except Exception as e:
            logger.error(f"Ollama exception: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise LLMError(f"Unexpected error: {str(e)}")
    
    raise LLMError("All retry attempts failed")

# ================= FILE WATCHER =================

class DocsFolderHandler(FileSystemEventHandler):
    """Watch for file changes and trigger index rebuild"""
    
    def on_created(self, event):
        if self._should_process(event):
            logger.info(f"New file detected: {event.src_path}")
            debounced_rebuild()
    
    def on_modified(self, event):
        if self._should_process(event):
            logger.info(f"File modified: {event.src_path}")
            debounced_rebuild()
    
    def on_deleted(self, event):
        if self._should_process(event):
            logger.info(f"File deleted: {event.src_path}")
            debounced_rebuild()
    
    def _should_process(self, event):
        """Check if event should trigger rebuild"""
        if event.is_directory:
            return False
        
        path = event.src_path.lower()
        return any(path.endswith(ext) for ext in [".txt", ".pdf", ".docx"])

def start_watcher():
    """Start file system watcher"""
    event_handler = DocsFolderHandler()
    observer = Observer()
    
    # Watch both folders
    for folder in [DEFAULT_DOCS_FOLDER, UPLOAD_FOLDER]:
        if os.path.exists(folder):
            observer.schedule(event_handler, path=folder, recursive=True)
            logger.info(f"Watching folder: {folder}")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ================= FLASK ROUTES =================

@app.route("/", methods=["GET", "POST"])
def index():
    """Main page with upload and document list"""
    if request.method == "POST":
        try:
            if "file" not in request.files:
                flash("No file selected", "error")
                return redirect(request.url)
            
            file = request.files["file"]
            folder_name = request.form.get("folder", "general").strip()
            
            if file.filename == "":
                flash("No file selected", "error")
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash(f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}", "error")
                return redirect(request.url)
            
            # Sanitize and create folder
            folder_name = sanitize_folder_name(folder_name) or "general"
            target_folder = os.path.join(UPLOAD_FOLDER, folder_name)
            os.makedirs(target_folder, exist_ok=True)
            
            # Save file
            filename = secure_filename(file.filename)
            filepath = os.path.join(target_folder, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                flash(f"File '{filename}' already exists in folder '{folder_name}'", "warning")
                return redirect(url_for("index"))
            
            file.save(filepath)
            flash(f"Uploaded '{filename}' to folder '{folder_name}'", "success")
            
            # Trigger rebuild
            debounced_rebuild()
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            flash(f"Upload failed: {str(e)}", "error")
        
        return redirect(url_for("index"))
    
    # GET request - show document structure
    try:
        doc_structure = {}
        for base_folder in [DEFAULT_DOCS_FOLDER, UPLOAD_FOLDER]:
            structure = scan_folder_structure(base_folder)
            base_name = "Default" if base_folder == DEFAULT_DOCS_FOLDER else "Uploaded"
            for folder, docs in structure.items():
                key = f"{base_name}_{folder}"
                doc_structure[key] = list(docs.keys())
        
        return render_template(
            "index.html",
            doc_structure=doc_structure,
            last_index_update=last_index_update,
            index_stats=index_stats,
            current_strategy=PROMPT_STRATEGY,
            available_strategies=list(PROMPT_TEMPLATES.keys())
        )
    
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        flash("Error loading documents", "error")
        return render_template(
            "index.html",
            doc_structure={},
            last_index_update=None,
            index_stats={},
            current_strategy=PROMPT_STRATEGY,
            available_strategies=list(PROMPT_TEMPLATES.keys())
        )

@app.route("/ask", methods=["POST"])
def ask():
    """Handle question answering with function execution support"""
    try:
        question = request.form.get("question", "").strip()
        strategy = request.form.get("strategy", PROMPT_STRATEGY)
        
        if not question:
            flash("Please enter a question", "error")
            return redirect(url_for("index"))
        
        if len(question) > 1000:
            flash("Question too long (max 1000 characters)", "error")
            return redirect(url_for("index"))
        
        # Retrieve relevant chunks
        logger.info(f"Processing question: {question[:100]}...")
        retrieved = retrieve_hierarchical(question)
        
        if not retrieved:
            answer = "No relevant documents found. Please upload documents first."
            thinking = ""
            sources = []
            function_outputs = []  # Initialize empty list
        else:
            # Build context from retrieved chunks
            context = "\n\n".join([
                f"[From {r['folder']}/{r['filename']}]\n{r['chunk']}"
                for r in retrieved
            ])
            
            # Generate prompt
            # prompt = generate_prompt(context, question, strategy)
            prompt = generate_prompt_with_functions(context, question, strategy)
            
            # Call LLM
            try:
                raw_answer = ollama_generate(prompt, strategy)
                
                # Extract thinking and answer
                thinking = ""
                answer = raw_answer
                
                think_match = re.search(r'<think>(.*?)</think>', raw_answer, re.DOTALL)
                if think_match:
                    thinking = think_match.group(1).strip()
                    answer = re.sub(r'<think>.*?</think>', '', raw_answer, flags=re.DOTALL).strip()
                
                # Process answer for function calls
                # answer, function_outputs = process_answer_with_functions(answer, question)
                from functions.auto_detector import enhanced_process_answer_with_functions
                answer, function_outputs = enhanced_process_answer_with_functions(answer, question, function_manager)
            except LLMError as e:
                logger.error(f"LLM error: {e}")
                answer = f"Error generating answer: {str(e)}"
                thinking = ""
                function_outputs = []
            
            # Prepare sources
            sources = []
            for r in retrieved:
                snippet = r["chunk"][:150].replace("\n", " ")
                if len(r["chunk"]) > 150:
                    snippet += "..."
                
                sources.append({
                    "folder": r["folder"],
                    "filename": r["filename"],
                    "snippet": snippet,
                    "score": r["score"]
                })
        
        # Get document structure for display
        doc_structure = {}
        for base_folder in [DEFAULT_DOCS_FOLDER, UPLOAD_FOLDER]:
            structure = scan_folder_structure(base_folder)
            base_name = "Default" if base_folder == DEFAULT_DOCS_FOLDER else "Uploaded"
            for folder, docs in structure.items():
                key = f"{base_name}_{folder}"
                doc_structure[key] = list(docs.keys())
        
        return render_template(
            "index.html",
            question=question,
            answer=answer,
            thinking=thinking,
            sources=sources,
            function_outputs=function_outputs,
            doc_structure=doc_structure,
            last_index_update=last_index_update,
            index_stats=index_stats,
            current_strategy=strategy,
            available_strategies=list(PROMPT_TEMPLATES.keys())
        )
    
    except Exception as e:
        logger.error(f"Error in ask route: {e}")
        flash(f"Error processing question: {str(e)}", "error")
        return redirect(url_for("index"))

@app.route("/health")
def health():
    """Health check endpoint with function manager status"""
    try:
        global function_manager
        
        status = {
            "status": "healthy",
            "ollama_available": check_ollama_available(),
            "model_available": check_model_available(LLM_MODEL),
            "index_built": global_index is not None,
            "total_chunks": len(global_chunks) if global_chunks else 0,
            "total_folders": len(folder_indices),
            "last_update": last_index_update.isoformat() if last_index_update else None,
            "functions": {
                "enabled": function_manager is not None,
                "total": len(function_manager.function_registry) if function_manager else 0,
                "last_update": function_manager.get_functions_list().get("last_updated") if function_manager else None
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/doc/<path:doc_path>")
def serve_doc(doc_path):
    """Serve document files"""
    try:
        # Parse path: base_folder_name/filename
        parts = doc_path.split("/", 1)
        if len(parts) != 2:
            flash("Invalid document path", "error")
            return redirect(url_for("index"))
        
        base_and_folder, filename = parts
        
        # Determine base folder
        if base_and_folder.startswith("Default_"):
            base_folder = DEFAULT_DOCS_FOLDER
            subfolder = base_and_folder[8:]  # Remove "Default_"
        elif base_and_folder.startswith("Uploaded_"):
            base_folder = UPLOAD_FOLDER
            subfolder = base_and_folder[9:]  # Remove "Uploaded_"
        else:
            flash("Invalid folder path", "error")
            return redirect(url_for("index"))
        
        # Build full path
        folder_path = os.path.join(base_folder, subfolder)
        
        if not os.path.exists(folder_path):
            flash("Folder not found", "error")
            return redirect(url_for("index"))
        
        return send_from_directory(folder_path, filename, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error serving document: {e}")
        flash("Error accessing document", "error")
        return redirect(url_for("index"))

@app.route("/stats")
def stats():
    """Return index statistics"""
    try:
        return jsonify(index_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB", "error")
    return redirect(url_for("index"))

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal error: {e}")
    flash("An internal error occurred", "error")
    return redirect(url_for("index"))

@app.route("/functions", methods=["GET"])
def list_functions():
    """Get list of all available functions"""
    try:
        global function_manager
        if not function_manager:
            return jsonify({"error": "Function manager not initialized"}), 500
        
        functions_list = function_manager.get_functions_list()
        return jsonify(functions_list)
    
    except Exception as e:
        logger.error(f"Error listing functions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/run_function", methods=["POST"])
def run_function():
    """Execute a function with given arguments"""
    try:
        global function_manager
        if not function_manager:
            return jsonify({"error": "Function manager not initialized"}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        func_name = data.get("name")
        if not func_name:
            return jsonify({"error": "Function name required"}), 400
        
        # Get arguments
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        
        # Execute function
        result = function_manager.execute_function(
            func_name,
            args=args,
            kwargs=kwargs
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error running function: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/function/<path:func_name>", methods=["GET"])
def get_function_info(func_name):
    """Get information about a specific function"""
    try:
        global function_manager
        if not function_manager:
            return jsonify({"error": "Function manager not initialized"}), 500
        
        info = function_manager.get_function_info(func_name)
        
        if not info:
            return jsonify({
                "error": f"Function '{func_name}' not found",
                "available": list(function_manager.function_registry.keys())
            }), 404
        
        return jsonify(info)
    
    except Exception as e:
        logger.error(f"Error getting function info: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/reload_functions", methods=["POST"])
def reload_functions():
    """Manually reload all functions"""
    try:
        global function_manager
        if not function_manager:
            return jsonify({"error": "Function manager not initialized"}), 500
        
        count = function_manager.scan_and_load()
        
        return jsonify({
            "status": "success",
            "message": f"Reloaded {count} functions",
            "total": count
        })
    
    except Exception as e:
        logger.error(f"Error reloading functions: {e}")
        return jsonify({"error": str(e)}), 500

# ================= MAIN =================

def initialize_folders():
    """Create necessary folders with example structure"""
    try:
        # Create base folders
        os.makedirs(DEFAULT_DOCS_FOLDER, exist_ok=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Create example category folders in default documents
        example_categories = ["general", "technical", "research"]
        for category in example_categories:
            category_path = os.path.join(DEFAULT_DOCS_FOLDER, category)
            os.makedirs(category_path, exist_ok=True)
        
        logger.info("Folder structure initialized")
        
        # Create README in default folder
        readme_path = os.path.join(DEFAULT_DOCS_FOLDER, "README.txt")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("""RAG System Document Organization
=====================================

This system uses hierarchical folder organization for better document retrieval.

Folder Structure:
- documents/{category}/file.txt
- uploaded_docs/{category}/file.txt

Example categories:
- general: General knowledge, FAQs
- technical: Technical documentation, manuals
- research: Research papers, articles
- policies: Company policies, guidelines
- guides: How-to guides, tutorials

You can create your own categories by:
1. Creating subfolders in the documents directory
2. Uploading files through the web interface with category selection

The system will automatically detect and index documents by category.
""")
            logger.info("Created README file")
    
    except Exception as e:
        logger.error(f"Error initializing folders: {e}")

def startup_checks():
    """Perform startup checks and warnings"""
    logger.info("=" * 60)
    logger.info("RAG System Startup")
    logger.info("=" * 60)
    
    # Check Ollama
    if not check_ollama_available():
        logger.warning("⚠️  Ollama is not running!")
        logger.warning("   Please start Ollama: ollama serve")
    else:
        logger.info("✓ Ollama is running")
        
        if not check_model_available(LLM_MODEL):
            logger.warning(f"⚠️  Model '{LLM_MODEL}' not found!")
            logger.warning(f"   Please download: ollama pull {LLM_MODEL}")
        else:
            logger.info(f"✓ Model '{LLM_MODEL}' is available")
    
    # Check folders
    for folder in [DEFAULT_DOCS_FOLDER, UPLOAD_FOLDER]:
        if os.path.exists(folder):
            file_count = sum(1 for _, _, files in os.walk(folder) 
                           for f in files if allowed_file(f))
            logger.info(f"✓ Found {file_count} documents in {folder}")
        else:
            logger.warning(f"⚠️  Folder not found: {folder}")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        # Initialize folders
        initialize_folders()
        startup_checks()
        
        # Initialize function manager
        logger.info("Initializing function manager...")
        function_manager = get_function_manager()
        func_count = function_manager.scan_and_load()
        logger.info(f"✓ Function manager initialized with {func_count} functions")
        
        # Build initial index
        logger.info("Building initial index...")
        try:
            rebuild_index()
            logger.info("✓ Initial index built successfully")
        except IndexBuildError as e:
            logger.error(f"Failed to build initial index: {e}")
            logger.warning("System will start without index. Upload documents to create index.")
        except Exception as e:
            logger.error(f"Unexpected error during index build: {e}")
        
        # Start document folder watcher
        doc_watcher_thread = threading.Thread(target=start_watcher, daemon=True)
        doc_watcher_thread.start()
        logger.info("✓ Document watcher started")
        
        # Start functions folder watcher
        functions_observer = start_functions_watcher(function_manager)
        logger.info("✓ Functions watcher started")
        
        # Print function summary
        if func_count > 0:
            logger.info("\n" + "="*60)
            logger.info("Available Functions:")
            for func_name in sorted(function_manager.function_registry.keys()):
                func_data = function_manager.function_registry[func_name]
                logger.info(f"  • {func_name} {func_data['signature']}")
            logger.info("="*60 + "\n")
        
        # Start Flask app
        logger.info("Starting Flask server on http://0.0.0.0:5000")
        logger.info("Press Ctrl+C to stop")
        app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
    
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        if functions_observer:
            functions_observer.stop()
            functions_observer.join()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    
