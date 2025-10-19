---
name: code-splitter
description: Efficiently split and reorganize large code files by extracting specific line ranges to new files. Provides tools for analyzing code structure, planning splits at logical boundaries (classes, functions), and executing extractions without loading entire file contents into context. Ideal for refactoring monolithic files, extracting components, reorganizing codebases, and managing large files in Claude Code.
---

# Code Splitter

Extract specific line ranges from code files to new files efficiently, without consuming context by showing entire file contents.

## Core Capability

Instead of reading entire files into context, simply specify:
- Source file and line range to extract
- Target file for the extracted code
- Whether to move (remove from source) or copy

## Primary Tools

### extract_lines.py - Single Extraction
Extract a specific line range from one file to another.

```bash
# Copy lines 50-150 from app.js to utils.js (default - keeps source intact)
python scripts/extract_lines.py app.js utils.js 50 150

# Move lines (remove from source) - use with caution
python scripts/extract_lines.py app.js utils.js 50 150 --mode move
```

### batch_extract.py - Multiple Extractions
Process multiple extractions at once using a JSON plan.

```bash
# Execute extraction plan
python scripts/batch_extract.py --json split_plan.json

# Or inline JSON
python scripts/batch_extract.py --plan '[{"source":"app.js","target":"header.js","start":1,"end":50}]'
```

### analyze_splits.py - Analyze & Plan
Understand file structure and generate split suggestions.

```bash
# Analyze file structure
python scripts/analyze_splits.py src/large_file.js

# Get split suggestions (target 200 lines per file)
python scripts/analyze_splits.py src/large_file.js --suggest --target-size 200
```

## Workflow Examples

### Quick Function Extraction
When user says: "Move the validateUser function from app.js to validators.js"

1. Identify the line range (e.g., lines 45-67)
2. Run: `python scripts/extract_lines.py app.js validators.js 45 67`
3. Add necessary imports to both files

### Large File Refactoring
When user says: "Split this 1000-line component file into smaller modules"

1. Analyze: `python scripts/analyze_splits.py component.jsx --suggest`
2. Create extraction plan based on logical boundaries
3. Execute: `python scripts/batch_extract.py --json plan.json`
4. Update import statements

### Reorganize by Feature
When splitting a file into feature-based modules:

```json
[
  {"source": "api.js", "target": "features/auth.js", "start": 1, "end": 200},
  {"source": "api.js", "target": "features/users.js", "start": 201, "end": 400},
  {"source": "api.js", "target": "features/products.js", "start": 401, "end": 600}
]
```

## Key Benefits

- **Context Efficient**: No need to load entire file contents into context
- **Precise Control**: Specify exact line ranges to extract
- **Batch Operations**: Split large files into multiple parts in one operation
- **Preserves Structure**: Maintains code formatting and indentation
- **Smart Analysis**: Identifies logical split points (classes, functions, sections)

## Advanced Patterns

For detailed patterns and examples, see: `references/patterns.md`

This includes:
- Common splitting patterns
- Best practices for different languages
- Complex refactoring examples
- Tips for efficient usage in Claude Code

## Important Notes

- Line numbers are 1-indexed (same as editor line numbers)
- **Default mode is 'copy'** which keeps the source file intact (non-destructive)
- Use `--mode move` to remove extracted lines from source (use with caution)
- Target files are created/appended automatically
- Parent directories are created as needed
- Validates filesystem write permissions before attempting modifications
- Provides clear error messages for read-only filesystems
- After splitting, manually add import/export statements as needed

## Safety Features

- **Non-destructive by default**: Copy mode prevents accidental data loss
- **Permission validation**: Checks write permissions before modifying files
- **Read-only filesystem detection**: Prevents errors when working with read-only locations
- **Clear error messages**: Provides actionable guidance when operations fail

## Resources

### scripts/
- `extract_lines.py` - Extract specific line ranges from files
- `batch_extract.py` - Process multiple extractions from JSON plan
- `analyze_splits.py` - Analyze file structure and suggest split points

### references/
- `patterns.md` - Common splitting patterns, best practices, and complex examples
