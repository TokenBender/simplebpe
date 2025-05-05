import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys

def run_notebook_cells(notebook_path, upto_cell=None):
    """
    Run cells in a Jupyter notebook up to a specified cell number
    
    Args:
        notebook_path: Path to the Jupyter notebook
        upto_cell: Run cells up to this number (1-based index, inclusive)
    """
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Create an execution processor
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    
    # Calculate how many cells to run
    cells_to_run = upto_cell if upto_cell is not None else len(nb.cells)
    
    print(f"Running {cells_to_run} cells from notebook: {notebook_path}")
    
    # Execute the notebook up to the specified cell
    try:
        # Create a truncated notebook with just the cells we want to run
        truncated_nb = nbformat.v4.new_notebook(
            metadata=nb.metadata,
            cells=nb.cells[:cells_to_run]
        )
        
        # Execute the cells
        ep.preprocess(truncated_nb)
        
        print(f"Successfully executed {cells_to_run} cells")
        return True
    except Exception as e:
        # Get the cell number where the error occurred
        cell_num = getattr(e, 'cell_index', None)
        if cell_num is not None:
            print(f"Error occurred in cell {cell_num + 1}")
            print(f"Cell content:\n{nb.cells[cell_num].source}")
        
        print(f"Error executing notebook: {str(e)}")
        return False

if __name__ == "__main__":
    notebook_path = '/Users/abhishekmishra/Documents/tokenizer_from_scratch/bpe_tokenizer.ipynb'
    
    # Default to running up to cell 8 (testing vocabulary management)
    upto_cell = 8
    
    # Allow command-line override
    if len(sys.argv) > 1:
        try:
            upto_cell = int(sys.argv[1])
        except ValueError:
            print(f"Invalid cell number: {sys.argv[1]}")
            sys.exit(1)
    
    success = run_notebook_cells(notebook_path, upto_cell)
    
    if success:
        print("✅ Notebook executed successfully up to cell", upto_cell)
        sys.exit(0)
    else:
        print("❌ Notebook execution failed")
        sys.exit(1)