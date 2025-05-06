#!/usr/bin/env python3
"""
Test script to verify that minbpe.ipynb executes without errors.
Used to validate fixes for BUG-002: Cell order issues in minbpe.ipynb
"""
import os
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import argparse

def check_notebook_exists(notebook_path):
    """Check if the notebook exists and is not empty."""
    if not os.path.exists(notebook_path):
        print(f"❌ ERROR: Notebook file does not exist: {notebook_path}")
        return False
        
    if os.path.getsize(notebook_path) == 0:
        print(f"❌ ERROR: Notebook file is empty: {notebook_path}")
        return False
        
    return True

def run_minbpe_notebook(max_cell=None, verbose=False):
    """
    Run all cells in the minbpe.ipynb notebook sequentially.
    Validates that the notebook cells execute without errors.
    
    Args:
        max_cell (int): Maximum cell number to execute (1-based index)
        verbose (bool): Print detailed execution information
        
    Returns:
        bool: True if all cells execute successfully, False otherwise
    """
    notebook_path = os.path.join(os.path.dirname(__file__), 'minbpe.ipynb')
    
    if not check_notebook_exists(notebook_path):
        print("❗ The notebook file is missing or empty. This test cannot proceed.")
        print("This might happen if an error occurred during a previous editing operation.")
        print("Please restore the notebook from a backup or previous commit.")
        return False
    
    try:
        # Load the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Count total cells
        total_cells = len(nb.cells)
        code_cells = sum(1 for cell in nb.cells if cell.cell_type == 'code')
        
        if verbose:
            print(f"Notebook: {notebook_path}")
            print(f"Total cells: {total_cells}")
            print(f"Code cells: {code_cells}")
            
        # Determine how many cells to execute
        cells_to_execute = total_cells
        if max_cell is not None:
            cells_to_execute = min(max_cell, total_cells)
            
        if verbose:
            print(f"Will execute up to cell #{cells_to_execute}")
        
        # Create an execution processor
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        
        # Execute cells one at a time to identify specific failures
        for i in range(cells_to_execute):
            # Only execute code cells
            if nb.cells[i].cell_type != 'code':
                if verbose:
                    print(f"Cell {i+1}: [markdown] - skipping")
                continue
                
            if verbose:
                print(f"Executing cell {i+1}/{cells_to_execute}... ", end="", flush=True)
            else:
                print(f"Cell {i+1}... ", end="", flush=True)
            
            try:
                # Create a truncated notebook with cells up to current
                truncated_nb = nbformat.v4.new_notebook(
                    metadata=nb.metadata,
                    cells=nb.cells[:i+1]
                )
                
                # Execute cells in the context of prior cells
                ep.preprocess(truncated_nb)
                print("✓")
                
            except Exception as e:
                print("❌")
                print(f"\nError in cell {i+1}:")
                print(f"Cell content:\n{nb.cells[i].source}")
                print(f"\nError: {str(e)}")
                return False
        
        print(f"\n✅ Successfully executed {cells_to_execute} cells")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading or processing the notebook: {str(e)}")
        return False

def validate_regex_tokenizer():
    """
    Specifically validates if the RegexTokenizer class is defined before it's used.
    
    Returns:
        bool: True if validation passes, False otherwise
    """
    notebook_path = os.path.join(os.path.dirname(__file__), 'minbpe.ipynb')
    
    if not check_notebook_exists(notebook_path):
        return False
    
    try:
        # Load the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Find where RegexTokenizer is defined and where it's first used
        regex_tokenizer_defined = None
        regex_tokenizer_used = None
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != 'code':
                continue
                
            if 'class RegexTokenizer' in cell.source:
                regex_tokenizer_defined = i
                
            if regex_tokenizer_defined is None and 'regex_tokenizer' in cell.source:
                regex_tokenizer_used = i
                
            if regex_tokenizer_defined is not None and regex_tokenizer_used is not None:
                break
        
        # Print validation results
        if regex_tokenizer_defined is None:
            print("❌ RegexTokenizer class not found in the notebook!")
            return False
            
        if regex_tokenizer_used is None:
            print("✓ RegexTokenizer class is never used before being defined.")
            return True
            
        if regex_tokenizer_used < regex_tokenizer_defined:
            print(f"❌ RegexTokenizer is used in cell {regex_tokenizer_used+1} before being defined in cell {regex_tokenizer_defined+1}!")
            return False
        else:
            print(f"✓ RegexTokenizer is defined in cell {regex_tokenizer_defined+1} before being used in later cells.")
            return True
            
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test and fix minbpe.ipynb notebook execution')
    parser.add_argument('--validate', action='store_true', help='Validate RegexTokenizer cell order')
    parser.add_argument('--run', type=int, nargs='?', const=0, help='Run notebook cells up to specified number (0 for all)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output')
    
    args = parser.parse_args()
    
    notebook_path = os.path.join(os.path.dirname(__file__), 'minbpe.ipynb')
    
    if not check_notebook_exists(notebook_path):
        print("❗ The test cannot proceed due to issues with the notebook file.")
        print("Please restore the minbpe.ipynb file from a backup or previous commit.")
        sys.exit(1)
    
    if args.validate:
        print("Validating RegexTokenizer cell order...")
        success = validate_regex_tokenizer()
        
    else:  # Default to running the notebook
        if args.run is None:
            args.run = 0  # Run all cells by default
            
        max_cell = None if args.run <= 0 else args.run
        print(f"Running minbpe.ipynb cells{' (all)' if max_cell is None else f' up to {max_cell}'}...")
        success = run_minbpe_notebook(max_cell, args.verbose)
        
    sys.exit(0 if success else 1)