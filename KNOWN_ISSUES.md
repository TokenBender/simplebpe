# KNOWN_ISSUES AND RESOLUTIONS

This document tracks bugs, issues, and their resolution history for the BPE tokenizer implementation. It serves as both a knowledge base for troubleshooting and a reference for future development decisions.

## Issue Management Process

1. **Issue Identification**
   - All bugs and issues must be documented here with a unique ID
   - Critical bugs should be addressed immediately and linked to PR.md
   - Issues should be categorized by component and priority

2. **Investigation Protocol**
   - Document all investigation approaches systematically
   - Include exact error messages and conditions that trigger the issue
   - Record environment details when relevant (OS, Python version, etc.)

3. **Resolution Tracking**
   - Document all attempted fixes and their outcomes
   - Record the final resolution with implementation details
   - Cross-reference with PR.md requirement/bugfix IDs
   - Update lessons learned to prevent similar issues

4. **Knowledge Transfer**
   - Extract reusable patterns or anti-patterns from resolutions
   - Link related issues to establish patterns when applicable
   - Document workarounds clearly when full resolution isn't possible

## Issue Categories

- **BUG**: Functionality not working as intended
- **PERF**: Performance-related issue
- **SEC**: Security vulnerability
- **COMP**: Compatibility issue
- **DOC**: Documentation error or omission

## Issue Tracking Format

Each issue is documented with the following information:
- **ID**: Unique identifier (e.g., BUG-001)
- **Title**: Brief description
- **Category**: BUG, PERF, SEC, COMP, DOC
- **Status**: Open, In Progress, Resolved, Won't Fix
- **Component**: Which part of the codebase is affected
- **Priority**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Reporter**: Who identified the issue
- **Assigned To**: Who is responsible for fixing
- **Created Date**: When the issue was identified
- **Resolution Date**: When the issue was resolved
- **Related PRs**: Cross-reference to requirements in PR.md
- **Description**: Detailed explanation of the issue
- **Steps to Reproduce**: Exact steps to trigger the issue
- **Error Message/Stack Trace**: The exact error output, if applicable
- **Investigation History**: Chronological list of investigation findings
- **Resolution Attempts**: Chronological list of approaches tried
- **Root Cause**: Analysis of what caused the issue (once identified)
- **Resolution**: Final solution that fixed the issue (if resolved)
- **Files Changed**: List of files modified to resolve the issue
- **Lessons Learned**: Key takeaways for future development
- **Prevention Strategy**: How to prevent similar issues in the future

## Active Issues

No active issues at this time.

## Closed Issues

### BUG-002: Cell Order Issues in minbpe.ipynb

- **ID**: BUG-002
- **Title**: Cell Order Issues in minbpe.ipynb
- **Category**: BUG
- **Status**: Resolved
- **Component**: minbpe.ipynb Notebook
- **Priority**: P1 (High)
- **Reporter**: TokenBender
- **Assigned To**: TokenBender
- **Created Date**: 2025-05-06
- **Resolution Date**: 2025-05-06
- **Related PRs**: Requirement #32 in PR.md
- **Description**: Cells in minbpe.ipynb were defined in an order that caused runtime errors when executed sequentially.
- **Steps to Reproduce**:
  1. Open minbpe.ipynb
  2. Run cells in order
  3. Cell 18 (benchmarking) failed because it referenced regex_tokenizer before it was defined
- **Investigation History**:
  1. Cells were added in a recent update to add features from Karpathy's implementation
  2. The order of cell execution matters - regression test cells should be self-contained
  3. Found that the RegexTokenizer class needed to be defined before the benchmarking code
- **Resolution Attempts**:
  1. **Approach**: Reorder cells to define dependencies before they're used
     - **Implementation**: Moved the RegexTokenizer class definition earlier in the notebook
     - **Result**: Success - cells now execute in proper order
  2. **Approach**: Restructured benchmarking code
     - **Implementation**: Simplified benchmarking to remove unnecessary code
     - **Result**: Success - benchmarking now runs correctly
- **Root Cause**: Incorrect ordering of cells leading to reference errors
- **Resolution**: Reordered cells and fixed benchmarking code to ensure proper execution order
- **Files Changed**: 
  - `minbpe.ipynb`
- **Lessons Learned**: 
  1. When adding new features to notebooks, always test executing cells in sequential order
  2. Ensure that cell dependencies are properly ordered
  3. Keep regression tests self-contained where possible
- **Prevention Strategy**:
  1. Add clear dependency headers to cells
  2. Consider adding cell dependency tests to validation
  3. Use modular design within notebooks to reduce order dependency

### BUG-001: Vocabulary Serialization Error

- **ID**: BUG-001
- **Title**: Vocabulary Serialization Error in save_vocabulary/load_vocabulary
- **Category**: BUG
- **Status**: Resolved
- **Component**: Vocabulary Management
- **Priority**: P1 (High)
- **Reporter**: Claude
- **Assigned To**: Claude
- **Created Date**: 2025-05-06
- **Resolution Date**: 2025-05-06
- **Related PRs**: Requirement #18 in PR.md
- **Description**: When saving vocabulary to a file and then loading it back, the tokenizer fails with a ValueError because the token pair serialization format causes issues during parsing.
- **Steps to Reproduce**:
  1. Create a BPETokenizer and train it on some text
  2. Call `save_vocabulary()` to save the vocabulary to a file
  3. Create a new BPETokenizer instance
  4. Call `load_vocabulary()` with the same file
  5. Observe the error
- **Error Message**: `ValueError: too many values to unpack (expected 2)`
- **Investigation History**:
  1. Reviewed the load_vocabulary function to understand the parsing logic
  2. Identified that the serialization format used commas as separators
  3. Determined that Python list string representations (e.g., `[97, 98]`) also contain commas
  4. Found that this created ambiguity when trying to split the merge string
- **Resolution Attempts**:
  1. **Approach**: Used comma (`,`) as separator in the token pair serialization
     - **Implementation**: `f"{list(k[0])},{list(k[1])}"`
     - **Result**: Failed because list representations contain commas, confusing the parser
     - **Reason**: The comma in list string representation (e.g., `[97, 98]`) conflicts with the comma used as separator
   
  2. **Approach**: Used pipe character (`|`) as separator instead of comma
     - **Implementation**: `f"{list(k[0])}|{list(k[1])}"`
     - **Result**: Success - the pipe character doesn't appear in list string representations
     - **Reason**: The pipe character creates a clear, unambiguous boundary between the two token lists

- **Root Cause**: The comma separator conflicted with commas in the string representation of Python lists.
- **Resolution**: Changed the separator in token pair serialization from comma to pipe character, and updated the parsing logic in the load_vocabulary function.
- **Files Changed**: 
  - `bpe_tokenizer.ipynb` (Cell 7: BPETokenizer.load_vocabulary)
  - `bpe_tokenizer.ipynb` (Cell 13: CompleteBPETokenizer.load_vocabulary)
- **Test Cases**:
  - Save and load vocabulary with various token types
  - Verify loaded vocabulary matches original
  - Ensure token pairs with nested lists are handled correctly
- **Lessons Learned**: 
  1. When serializing complex data structures as strings, use separators that cannot appear in the data itself
  2. For nested structures, consider using more robust serialization approaches like JSON with custom encoders/decoders
  3. Always test serialization/deserialization with a variety of edge cases, including tokens with special characters
  4. Implement comprehensive validation checks when parsing serialized data
- **Prevention Strategy**:
  1. Add automated tests for serialization/deserialization
  2. Create helper functions that sanitize/validate serialized data
  3. Consider adding a versioning scheme to serialized formats to allow for backward compatibility

## Won't Fix

No issues in this category yet.

## Issue Metrics

**Resolution Time Averages:**
- Critical (P0): N/A (no P0 issues yet)
- High (P1): Same day
- Medium (P2): N/A (no P2 issues yet) 
- Low (P3): N/A (no P3 issues yet)

**Issue Distribution by Component:**
- Vocabulary Management: 1

**Common Root Causes:**
1. Data format assumptions: 1 issue