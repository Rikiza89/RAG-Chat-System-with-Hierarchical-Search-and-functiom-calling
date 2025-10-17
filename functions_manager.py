"""
Dynamic Function Loading and Management System
Handles discovery, loading, and execution of Python functions
"""

import os
import json
import importlib.util
import inspect
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
import threading

logger = logging.getLogger(__name__)

class FunctionManager:
    """Manages dynamic function loading and execution"""
    
    def __init__(self, functions_dir: str = "functions"):
        self.functions_dir = functions_dir
        self.function_registry: Dict[str, Dict[str, Any]] = {}
        self.json_path = "functions_list.json"
        self.lock = threading.Lock()
        
        # Initialize functions directory
        os.makedirs(self.functions_dir, exist_ok=True)
        logger.info(f"Function manager initialized with directory: {self.functions_dir}")
    
    def scan_and_load(self) -> int:
        """
        Scan functions directory and load all valid Python functions
        Returns: Number of functions loaded
        """
        with self.lock:
            try:
                logger.info(f"Scanning functions directory: {self.functions_dir}")
                old_count = len(self.function_registry)
                self.function_registry.clear()
                
                # Walk through all subdirectories
                for root, dirs, files in os.walk(self.functions_dir):
                    # Skip __pycache__ and hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('_') and not d.startswith('.')]
                    
                    for filename in files:
                        if not filename.endswith('.py') or filename.startswith('_'):
                            continue
                        
                        filepath = os.path.join(root, filename)
                        self._load_module(filepath)
                
                new_count = len(self.function_registry)
                logger.info(f"Function registry updated: {old_count} -> {new_count} functions")
                
                # Update JSON metadata
                self._update_json()
                
                return new_count
            
            except Exception as e:
                logger.error(f"Error scanning functions: {e}")
                return 0
    
    def _load_module(self, filepath: str):
        """Load a single Python module and extract callable functions"""
        try:
            # Calculate relative path for function naming
            rel_path = os.path.relpath(filepath, self.functions_dir)
            module_name = rel_path.replace(os.sep, '/').replace('.py', '')
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                logger.warning(f"Could not load spec for {filepath}")
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract callable functions (skip private ones)
            functions_found = 0
            for name, obj in inspect.getmembers(module):
                if name.startswith('_'):
                    continue
                
                if inspect.isfunction(obj):
                    func_key = f"{module_name}/{name}" if name != "run" else module_name
                    
                    # Get function signature and docstring
                    sig = inspect.signature(obj)
                    doc = inspect.getdoc(obj) or "No description available"
                    
                    self.function_registry[func_key] = {
                        "module": module,
                        "func": obj,
                        "path": filepath,
                        "signature": str(sig),
                        "doc": doc.split('\n')[0],  # First line only
                        "params": [param for param in sig.parameters.keys()]
                    }
                    functions_found += 1
                    logger.debug(f"Loaded function: {func_key}")
            
            if functions_found > 0:
                logger.info(f"Loaded {functions_found} function(s) from {os.path.basename(filepath)}")
        
        except Exception as e:
            logger.error(f"Error loading module {filepath}: {e}")
    
    def _update_json(self):
        """Update functions_list.json with current registry"""
        try:
            functions_list = {
                "last_updated": datetime.now().isoformat(),
                "total_functions": len(self.function_registry),
                "functions": []
            }
            
            for func_name, func_data in sorted(self.function_registry.items()):
                functions_list["functions"].append({
                    "name": func_name,
                    "params": func_data["params"],
                    "signature": func_data["signature"],
                    "doc": func_data["doc"],
                    "path": func_data["path"]
                })
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(functions_list, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated {self.json_path} with {len(self.function_registry)} functions")
        
        except Exception as e:
            logger.error(f"Error updating JSON: {e}")
    
    def get_functions_list(self) -> Dict[str, Any]:
        """Get current functions list as dict"""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "last_updated": None,
                    "total_functions": 0,
                    "functions": []
                }
        except Exception as e:
            logger.error(f"Error reading functions list: {e}")
            return {"error": str(e)}
    
    def execute_function(self, func_name: str, args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a function by name with given arguments
        
        Args:
            func_name: Name of the function (e.g., "math/add" or "math/add/run")
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Dict with status, result, or error
        """
        args = args or []
        kwargs = kwargs or {}
        
        try:
            # Check if function exists
            if func_name not in self.function_registry:
                return {
                    "status": "error",
                    "error": f"Function '{func_name}' not found",
                    "available": list(self.function_registry.keys())
                }
            
            func_data = self.function_registry[func_name]
            func = func_data["func"]
            
            # Execute function
            logger.info(f"Executing function: {func_name} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            
            # Log execution
            self._log_execution(func_name, args, kwargs, result, None)
            
            return {
                "status": "success",
                "result": result,
                "function": func_name
            }
        
        except TypeError as e:
            error_msg = f"Invalid arguments for {func_name}: {str(e)}"
            logger.error(error_msg)
            self._log_execution(func_name, args, kwargs, None, error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "signature": self.function_registry.get(func_name, {}).get("signature", "unknown")
            }
        
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            logger.error(f"Error executing {func_name}: {e}")
            self._log_execution(func_name, args, kwargs, None, error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    def _log_execution(self, func_name: str, args: List, kwargs: Dict, result: Any, error: Optional[str]):
        """Log function execution to file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "function": func_name,
                "args": str(args),
                "kwargs": str(kwargs),
                "result": str(result) if result is not None else None,
                "error": error,
                "status": "error" if error else "success"
            }
            
            log_file = "function_calls.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
    
    def parse_and_execute_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse text for function calls in format: <run:function_name arg1=val1 arg2=val2>
        Supports both math/add and math.add syntax
        
        Args:
            text: Text to parse for function calls
        
        Returns:
            List of execution results
        """
        import re
        
        results = []
        # Updated pattern to match both / and . as separators
        pattern = r'<run:([\w/.]+)(.*?)>'
        
        matches = re.finditer(pattern, text)
        
        for match in matches:
            func_name = match.group(1)
            # Normalize: convert dots to slashes for consistency
            func_name = func_name.replace('.', '/')
            args_str = match.group(2).strip()
            
            # Parse arguments
            kwargs = {}
            if args_str:
                # Parse key=value pairs
                arg_pattern = r'(\w+)=([^\s]+)'
                for arg_match in re.finditer(arg_pattern, args_str):
                    key = arg_match.group(1)
                    value = arg_match.group(2)
                    
                    # Try to convert to appropriate type
                    try:
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        elif value.replace('.', '').replace('-', '').isdigit():
                            value = float(value) if '.' in value else int(value)
                    except:
                        pass  # Keep as string
                    
                    kwargs[key] = value
            
            # Execute function
            result = self.execute_function(func_name, kwargs=kwargs)
            results.append({
                "match": match.group(0),
                "function": func_name,
                "parsed_kwargs": kwargs,
                "result": result
            })
        
        return results
    
    def get_function_info(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific function"""
        if func_name in self.function_registry:
            func_data = self.function_registry[func_name]
            return {
                "name": func_name,
                "params": func_data["params"],
                "signature": func_data["signature"],
                "doc": func_data["doc"],
                "path": func_data["path"]
            }
        return None


# Singleton instance
_function_manager = None

def get_function_manager(functions_dir: str = "functions") -> FunctionManager:
    """Get or create function manager singleton"""
    global _function_manager
    if _function_manager is None:
        _function_manager = FunctionManager(functions_dir)
    return _function_manager