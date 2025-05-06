#!/usr/bin/env python3
"""
Normalize a Jupyter notebook to fix metadata issues.
"""
import sys
import nbformat
from uuid import uuid4

def normalize_notebook(notebook_path):
    """
    Normalize a Jupyter notebook to fix metadata issues.
    """
    print(f"Normalizing notebook: {notebook_path}")
    
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Process each cell to ensure required fields
        for i, cell in enumerate(notebook.cells):
            # Ensure each cell has an ID
            if 'id' not in cell:
                cell['id'] = str(uuid4())
                
            # Ensure all cells have empty metadata if none exists
            if 'metadata' not in cell:
                cell['metadata'] = {}
            
            # Handle cell-type specific fields
            if cell.cell_type == 'code':
                # Ensure code cells have execution_count
                if 'execution_count' not in cell:
                    cell['execution_count'] = None
                    
                # Ensure code cells have empty outputs if none exists
                if 'outputs' not in cell:
                    cell['outputs'] = []
            elif cell.cell_type == 'markdown':
                # Remove outputs from markdown cells (they shouldn't have any)
                if 'outputs' in cell:
                    del cell['outputs']
            
            # Print progress
            print(f"Processed cell {i+1}/{len(notebook.cells)}", end="\r")
        
        # Write the normalized notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
        
        print(f"\nSuccessfully normalized notebook: {notebook_path}")
        return True
        
    except Exception as e:
        print(f"\nError normalizing notebook: {e}")
        return False
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python normalize_notebook.py <notebook_path>")
        sys.exit(1)
        
    notebook_path = sys.argv[1]
    success = normalize_notebook(notebook_path)
    sys.exit(0 if success else 1)