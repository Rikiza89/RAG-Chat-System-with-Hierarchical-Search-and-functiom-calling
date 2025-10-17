"""
File System Watcher for Functions Directory
Monitors changes and triggers function registry rebuild
"""

import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

logger = logging.getLogger(__name__)

class FunctionsWatcher(FileSystemEventHandler):
    """Watch functions directory for changes"""
    
    def __init__(self, function_manager, debounce_seconds=2):
        super().__init__()
        self.function_manager = function_manager
        self.debounce_seconds = debounce_seconds
        self.rebuild_timer = None
        self.lock = threading.Lock()
    
    def on_created(self, event):
        """Handle file creation"""
        if self._should_process(event):
            logger.info(f"Function file created: {event.src_path}")
            self._debounced_rebuild()
    
    def on_modified(self, event):
        """Handle file modification"""
        if self._should_process(event):
            logger.info(f"Function file modified: {event.src_path}")
            self._debounced_rebuild()
    
    def on_deleted(self, event):
        """Handle file deletion"""
        if self._should_process(event):
            logger.info(f"Function file deleted: {event.src_path}")
            self._debounced_rebuild()
    
    def on_moved(self, event):
        """Handle file move/rename"""
        if self._should_process(event):
            logger.info(f"Function file moved: {event.src_path} -> {event.dest_path}")
            self._debounced_rebuild()
    
    def _should_process(self, event):
        """Check if event should trigger rebuild"""
        if event.is_directory:
            return False
        
        # Only process Python files
        path = event.src_path.lower()
        if not path.endswith('.py'):
            return False
        
        # Skip private files
        filename = os.path.basename(path)
        if filename.startswith('_'):
            return False
        
        # Skip __pycache__
        if '__pycache__' in path:
            return False
        
        return True
    
    def _debounced_rebuild(self):
        """Debounced rebuild to avoid multiple rapid rebuilds"""
        with self.lock:
            if self.rebuild_timer:
                self.rebuild_timer.cancel()
            
            self.rebuild_timer = threading.Timer(
                self.debounce_seconds,
                self._rebuild_functions
            )
            self.rebuild_timer.start()
    
    def _rebuild_functions(self):
        """Rebuild function registry"""
        try:
            logger.info("Rebuilding function registry...")
            old_funcs = set(self.function_manager.function_registry.keys())
            
            count = self.function_manager.scan_and_load()
            
            new_funcs = set(self.function_manager.function_registry.keys())
            
            # Log changes
            added = new_funcs - old_funcs
            removed = old_funcs - new_funcs
            
            if added:
                logger.info(f"Functions added: {', '.join(sorted(added))}")
            if removed:
                logger.info(f"Functions removed: {', '.join(sorted(removed))}")
            
            logger.info(f"Function registry rebuilt: {count} total functions")
        
        except Exception as e:
            logger.error(f"Error rebuilding function registry: {e}")


def start_functions_watcher(function_manager, functions_dir="functions"):
    """
    Start file system watcher for functions directory
    
    Args:
        function_manager: FunctionManager instance
        functions_dir: Directory to watch
    
    Returns:
        Observer instance
    """
    if not os.path.exists(functions_dir):
        os.makedirs(functions_dir, exist_ok=True)
        logger.warning(f"Created functions directory: {functions_dir}")
    
    event_handler = FunctionsWatcher(function_manager)
    observer = Observer()
    observer.schedule(event_handler, path=functions_dir, recursive=True)
    observer.start()
    
    logger.info(f"Functions watcher started for: {functions_dir}")
    return observer
