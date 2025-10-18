"""
Excel data processing functions
Requires: pip install openpyxl pandas xlsxwriter
"""

import os
import json
from pathlib import Path

def run(filepath, output_format="summary"):
    """
    Process Excel file and return analysis
    
    Args:
        filepath: Path to Excel file (relative to documents/)
        output_format: 'summary', 'json', 'csv'
    
    Returns:
        Processed data summary
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed. Run: pip install pandas openpyxl"
    
    # Resolve path
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(full_path):
        return f"File not found: {filepath}"
    
    try:
        # Read Excel file
        df = pd.read_excel(full_path, sheet_name=0)
        
        if output_format == "summary":
            return {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "sample": df.head(3).to_dict('records')
            }
        
        elif output_format == "json":
            return df.to_json(orient='records')
        
        elif output_format == "csv":
            csv_path = full_path.replace('.xlsx', '.csv').replace('.xls', '.csv')
            df.to_csv(csv_path, index=False)
            return f"Converted to CSV: {csv_path}"
        
    except Exception as e:
        return f"Error processing Excel: {str(e)}"


def get_sheet_names(filepath):
    """List all sheet names in Excel file"""
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        xl_file = pd.ExcelFile(full_path)
        return xl_file.sheet_names
    except Exception as e:
        return f"Error: {str(e)}"


def read_sheet(filepath, sheet_name, rows=10):
    """Read specific sheet from Excel"""
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        df = pd.read_excel(full_path, sheet_name=sheet_name, nrows=rows)
        return df.to_dict('records')
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_column(filepath, column_name):
    """Analyze specific column statistics"""
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        df = pd.read_excel(full_path, sheet_name=0)
        
        if column_name not in df.columns:
            return f"Column '{column_name}' not found. Available: {df.columns.tolist()}"
        
        col = df[column_name]
        
        # Numeric analysis
        if pd.api.types.is_numeric_dtype(col):
            return {
                "type": "numeric",
                "count": int(col.count()),
                "mean": float(col.mean()),
                "median": float(col.median()),
                "min": float(col.min()),
                "max": float(col.max()),
                "std": float(col.std())
            }
        # Text analysis
        else:
            return {
                "type": "text",
                "count": int(col.count()),
                "unique": int(col.nunique()),
                "top_values": col.value_counts().head(5).to_dict()
            }
    
    except Exception as e:
        return f"Error: {str(e)}"


def filter_rows(filepath, column, value, operator="equals"):
    """
    Filter Excel rows by condition
    
    Args:
        filepath: Excel file path
        column: Column name
        value: Value to filter by
        operator: 'equals', 'contains', 'greater', 'less'
    """
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        df = pd.read_excel(full_path, sheet_name=0)
        
        if column not in df.columns:
            return f"Column '{column}' not found"
        
        if operator == "equals":
            filtered = df[df[column] == value]
        elif operator == "contains":
            filtered = df[df[column].astype(str).str.contains(str(value), na=False)]
        elif operator == "greater":
            filtered = df[df[column] > float(value)]
        elif operator == "less":
            filtered = df[df[column] < float(value)]
        else:
            return "Invalid operator. Use: equals, contains, greater, less"
        
        return {
            "matched_rows": len(filtered),
            "data": filtered.head(10).to_dict('records')
        }
    
    except Exception as e:
        return f"Error: {str(e)}"


def create_pivot(filepath, index_col, values_col, aggfunc="sum"):
    """Create pivot table summary"""
    try:
        import pandas as pd
    except ImportError:
        return "Error: pandas not installed"
    
    full_path = os.path.join('documents', filepath) if not os.path.isabs(filepath) else filepath
    
    try:
        df = pd.read_excel(full_path, sheet_name=0)
        
        pivot = df.groupby(index_col)[values_col].agg(aggfunc)
        
        return {
            "pivot_summary": pivot.to_dict(),
            "total": float(pivot.sum()) if aggfunc == "sum" else None
        }
    
    except Exception as e:
        return f"Error: {str(e)}"
