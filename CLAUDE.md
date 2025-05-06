# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal
Create an educational, monolithic BPE tokenizer implementation as a Jupyter notebook inspired by Karpathy's minbpe, focusing on clarity and learning progression.

## Commands
- Run Jupyter notebook: `jupyter notebook bpe_tokenizer.ipynb`
- Install dependencies: `pip install -r requirements.txt` (jupyter, numpy, matplotlib)

## Mandatory Requirement Management Process
1. **Generate expectations for every requirement**
   - Define specific, measurable success criteria before implementation
   - Document expected inputs, outputs, and behavior
   - Add requirement to PR.md with TODO status

2. **Implement evaluation checkpoints**
   - Create notebook cells that validate success criteria
   - Include assertions to verify correctness at each step
   - Display intermediate states visually for verification

3. **Perform success/failure evaluation**
   - Include test cells after each implementation section
   - Document exact pass/fail status in PR.md
   - Report metrics against defined success criteria

4. **Root cause analysis of failures**
   - For any failures, identify specific code causing issues
   - Document possible solutions with expected outcomes
   - Update PR.md with findings and status

5. **Status tracking and updates**
   - PR.md MUST be updated whenever a requirement is modified
   - Changes to requirements must include updated success criteria
   - Keep user informed of all requirement status changes

## Development Accountability Framework
1. **Requirement Definition**
   - Each notebook section must have explicit, measurable success criteria
   - Define test cases with specific inputs and expected outputs
   - Document edge cases that must be handled correctly

2. **Implementation Checkpoints**
   - Every algorithm section must validate assumptions with assertions
   - All core functions must include input validation and error checks
   - Implementation must match pseudocode specification exactly

3. **Evaluation Protocol**
   - Report pass/fail status for each test case with exact metrics
   - Document any discrepancies between expected and actual results
   - Identify root causes for failures with specific code references
   - Track and report code coverage percentage for all tests

4. **Documentation Requirements**
   - Each algorithm step must reference corresponding academic sources
   - Code must include step-by-step explanations with expected outputs
   - Implementation choices must be justified with performance metrics

## Notebook Style Guidelines
- Monolithic structure with clear markdown section headers and separation of concerns
- Every function must include pre/post condition comments
- Use type hints with explicit validation for all parameters
- Follow PEP 8 with 100 character line limit
- Include visualization cells showing tokenization progress
- Mix explanatory markdown cells with implementation code cells
- Each section should be independently runnable for educational purposes

## Objective Success Criteria
- 100% test coverage for core algorithm functions
- Identical output to reference implementation on benchmark texts
- O(n) time complexity for tokenization with explicit measurements
- Comprehensive error handling covering all identified edge cases
- Zero regression in test suite between implementation iterations

## Automated Task Management and Commit Protocol

1. **Task Structure Definition**
   - All tasks must follow format `TASK-NNN: Brief description`
   - Tasks categorized as: FEATURE, BUGFIX, REFACTOR, DOCS, TEST
   - Each task includes: description, acceptance criteria, and related files

2. **Automated Task Completion Workflow**
   ```
   <task-complete>
   id: TASK-123
   type: FEATURE|BUGFIX|REFACTOR|DOCS|TEST
   title: Brief descriptive title
   files_changed:
     - path/to/file1.py
     - path/to/file2.py
   description: |
     Detailed description of what was done to complete the task.
     Multiple lines are allowed.
   requirement_id: #N (from PR.md)
   bug_id: BUG-NNN (from KNOWN_ISSUES.md, if applicable)
   </task-complete>
   ```

3. **Project File Updates**
   - When `<task-complete>` block is processed:
     - PR.md: Update requirement status to COMPLETE
     - KNOWN_ISSUES.md: Update bug status to RESOLVED (if applicable)
     - Commit changes with standardized message:
       - Format: `[TASK-NNN] type: title`
       - Example: `[TASK-123] BUGFIX: Fix tokenization issue with Unicode characters`

4. **Quality Assurance Requirements**
   - All tests must pass before marking a task complete
   - Changes must match original requirements
   - Changes must be verified against acceptance criteria

5. **Documentation Updates**
   - All completed tasks must update relevant documentation
   - PR.md: Add completion date, implementation details
   - Add entry to the change log at the bottom of PR.md
   - Link related tasks, bugs, and issues together

## Bug Tracking and Issue Resolution
1. **Maintain a bug tracker in KNOWN_ISSUES.md**
   - Document each bug with a unique ID, description, and component affected
   - Record all approaches tried for each bug, both successful and unsuccessful
   - Include error messages, stack traces, and detailed resolution attempts
   - Identify root causes and final solutions for resolved issues

2. **Bug Resolution Protocol**
   - For any error encountered, first check KNOWN_ISSUES.md for similar problems
   - Try previously successful approaches before attempting new solutions
   - Document new bugs immediately upon discovery
   - Update issue status promptly after resolution attempts
   - If multiple approaches fail, add "Won't Fix" status with justification

3. **Learning from Failures**
   - Record lessons learned from each bug for future reference
   - Recognize when to give up on approaches that show little promise
   - Document workarounds when perfect solutions aren't feasible
   - Use known issues as input for design improvements