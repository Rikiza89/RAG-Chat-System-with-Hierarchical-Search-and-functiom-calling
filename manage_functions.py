#!/usr/bin/env python3
"""
CLI tool for managing functions
Usage:
    python manage_functions.py list
    python manage_functions.py info <function_name>
    python manage_functions.py run <function_name> [args...]
    python manage_functions.py test
"""

import sys
import json
import argparse
from functions_manager import get_function_manager

def list_functions(manager):
    """List all available functions"""
    functions_data = manager.get_functions_list()
    
    print(f"\n{'='*60}")
    print(f"Available Functions ({functions_data.get('total_functions', 0)})")
    print(f"Last Updated: {functions_data.get('last_updated', 'Unknown')}")
    print(f"{'='*60}\n")
    
    if not functions_data.get('functions'):
        print("No functions loaded. Add .py files to the functions/ directory.")
        return
    
    for func in functions_data['functions']:
        print(f"📦 {func['name']}")
        print(f"   Params: {', '.join(func['params']) if func['params'] else 'none'}")
        print(f"   Doc: {func['doc']}")
        print(f"   Path: {func['path']}")
        print()

def show_function_info(manager, func_name):
    """Show detailed info about a function"""
    info = manager.get_function_info(func_name)
    
    if not info:
        print(f"❌ Function '{func_name}' not found")
        print(f"Available functions: {', '.join(manager.function_registry.keys())}")
        return
    
    print(f"\n{'='*60}")
    print(f"Function: {info['name']}")
    print(f"{'='*60}")
    print(f"Signature: {info['signature']}")
    print(f"Parameters: {', '.join(info['params']) if info['params'] else 'none'}")
    print(f"Description: {info['doc']}")
    print(f"Path: {info['path']}")
    print()

def run_function(manager, func_name, args_list):
    """Run a function with given arguments"""
    print(f"\n🚀 Running function: {func_name}")
    print(f"Arguments: {args_list}")
    
    # Parse arguments as key=value pairs
    kwargs = {}
    positional = []
    
    for arg in args_list:
        if '=' in arg:
            key, value = arg.split('=', 1)
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
        else:
            # Try to convert positional args
            try:
                if arg.replace('.', '').replace('-', '').isdigit():
                    arg = float(arg) if '.' in arg else int(arg)
            except:
                pass
            positional.append(arg)
    
    # Execute
    result = manager.execute_function(func_name, args=positional, kwargs=kwargs)
    
    print(f"\n{'='*60}")
    if result['status'] == 'success':
        print(f"✅ Success!")
        print(f"Result: {result['result']}")
    else:
        print(f"❌ Error!")
        print(f"Error: {result['error']}")
        if 'signature' in result:
            print(f"Expected signature: {result['signature']}")
    print(f"{'='*60}\n")

def test_all_functions(manager):
    """Test all functions with sample data"""
    print(f"\n{'='*60}")
    print("Testing All Functions")
    print(f"{'='*60}\n")
    
    test_cases = {
        "math/add": {"kwargs": {"a": 5, "b": 3}},
        "math/multiply": {"kwargs": {"a": 4, "b": 7}},
        "math/add/add_three": {"kwargs": {"a": 1, "b": 2, "c": 3}},
        "text/summarize": {"kwargs": {"text": "This is a test text that needs summarization.", "max_length": 20}},
        "text/translate": {"kwargs": {"text": "Hello World", "target_lang": "es"}},
        "utils/format": {"kwargs": {"text": "hello world", "style": "title"}},
    }
    
    results = []
    for func_name, test_data in test_cases.items():
        print(f"Testing: {func_name}")
        result = manager.execute_function(func_name, **test_data)
        
        if result['status'] == 'success':
            print(f"  ✅ Result: {result['result']}")
            results.append(True)
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
            results.append(False)
        print()
    
    success_count = sum(results)
    total_count = len(results)
    print(f"{'='*60}")
    print(f"Test Results: {success_count}/{total_count} passed")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="Manage dynamic functions")
    parser.add_argument('command', choices=['list', 'info', 'run', 'test', 'reload'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    
    args = parser.parse_args()
    
    # Initialize function manager
    manager = get_function_manager()
    manager.scan_and_load()
    
    if args.command == 'list':
        list_functions(manager)
    
    elif args.command == 'info':
        if not args.args:
            print("❌ Please specify a function name")
            sys.exit(1)
        show_function_info(manager, args.args[0])
    
    elif args.command == 'run':
        if not args.args:
            print("❌ Please specify a function name")
            sys.exit(1)
        func_name = args.args[0]
        func_args = args.args[1:]
        run_function(manager, func_name, func_args)
    
    elif args.command == 'test':
        test_all_functions(manager)
    
    elif args.command == 'reload':
        print("🔄 Reloading functions...")
        count = manager.scan_and_load()
        print(f"✅ Loaded {count} functions")

if __name__ == "__main__":
    main()
