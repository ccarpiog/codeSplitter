# Code Splitter

A Claude Code skill for efficiently splitting and reorganizing large code files by extracting specific line ranges to new files. This skill provides tools for analyzing code structure, planning splits at logical boundaries (classes, functions), and executing extractions without loading entire file contents into context.

## Overview

Code Splitter helps you refactor monolithic files, extract components, and reorganize codebases efficiently. Instead of loading entire files into context, you can specify exact line ranges to extract, making it ideal for working with large files in Claude Code.

## Key Features

- **Context Efficient**: Extract code without loading entire files into context
- **Precise Control**: Specify exact line ranges to extract
- **Batch Operations**: Split large files into multiple parts in one operation
- **Smart Analysis**: Automatically identify logical split points (classes, functions, sections)
- **Safety First**: Non-destructive by default with permission validation
- **Multiple Languages**: Support for Python, JavaScript/TypeScript, Java, and more

## Installation

This skill is designed to work with Claude Code. The scripts require Python 3.6 or higher.

```bash
# Verify Python is available
python3 --version
```

## Tools

### 1. extract_lines.py - Single Extraction

Extract a specific line range from one file to another.

**Usage:**
```bash
# Copy lines 50-150 from app.js to utils.js (default - keeps source intact)
python3 scripts/extract_lines.py app.js utils.js 50 150

# Move lines (remove from source) - use with caution
python3 scripts/extract_lines.py app.js utils.js 50 150 --mode move
```

**Parameters:**
- `source`: Source file path
- `target`: Target file path
- `start`: Start line number (1-indexed)
- `end`: End line number (1-indexed, inclusive)
- `--mode`: `copy` (default, non-destructive) or `move` (removes from source)
- `--no-create-dirs`: Don't create parent directories for target file

**Features:**
- Line numbers are 1-indexed (matching editor line numbers)
- Creates target directories automatically
- Validates write permissions before modifying files
- Provides clear error messages for read-only filesystems
- Appends to existing target files with proper newline handling

### 2. batch_extract.py - Multiple Extractions

Process multiple extractions at once using a JSON plan.

**Usage:**
```bash
# Execute extraction plan from file
python3 scripts/batch_extract.py --json split_plan.json

# Or inline JSON
python3 scripts/batch_extract.py --plan '[{"source":"app.js","target":"header.js","start":1,"end":50}]'
```

**JSON Plan Format:**
```json
[
  {
    "source": "app.js",
    "target": "components/header.js",
    "start": 10,
    "end": 50
  },
  {
    "source": "app.js",
    "target": "components/footer.js",
    "start": 100,
    "end": 150,
    "mode": "copy"
  }
]
```

**Features:**
- Process multiple extractions in sequence
- Progress tracking for each extraction
- Summary of successful and failed operations
- Supports all extract_lines.py options per extraction

### 3. analyze_splits.py - Analyze & Plan

Understand file structure and generate split suggestions automatically.

**Usage:**
```bash
# Analyze file structure
python3 scripts/analyze_splits.py src/large_file.js

# Get split suggestions (target 200 lines per file)
python3 scripts/analyze_splits.py src/large_file.js --suggest --target-size 200
```

**Parameters:**
- `file`: File to analyze
- `--suggest`: Generate split suggestions
- `--target-size`: Target lines per split (default: 200)

**Features:**
- Detects functions, classes, and imports
- Identifies logical section markers
- Suggests split points at logical boundaries
- Generates JSON extraction plans automatically
- Supports Python, JavaScript/TypeScript, Java, and generic patterns

## Workflow Examples

### Quick Function Extraction

**Task:** "Move the validateUser function from app.js to validators.js"

1. Identify the line range (e.g., lines 45-67)
2. Run extraction:
   ```bash
   python3 scripts/extract_lines.py app.js validators.js 45 67
   ```
3. Add necessary imports to both files

### Large File Refactoring

**Task:** "Split this 1000-line component file into smaller modules"

1. Analyze the file:
   ```bash
   python3 scripts/analyze_splits.py component.jsx --suggest
   ```
2. Review the generated JSON plan
3. Execute the refactor:
   ```bash
   python3 scripts/batch_extract.py --json plan.json
   ```
4. Update import statements in all files

### Reorganize by Feature

Split a monolithic API file into feature-based modules:

```json
[
  {"source": "api.js", "target": "features/auth.js", "start": 1, "end": 200},
  {"source": "api.js", "target": "features/users.js", "start": 201, "end": 400},
  {"source": "api.js", "target": "features/products.js", "start": 401, "end": 600}
]
```

## Common Patterns

### Extract Class to New File

```bash
# Analyze first
python3 scripts/analyze_splits.py src/app.js

# Extract specific class (e.g., lines 50-200)
python3 scripts/extract_lines.py src/app.js src/UserClass.js 50 200
```

### Split Large File into Modules

```bash
# Generate a plan
python3 scripts/analyze_splits.py src/monolith.js --suggest --target-size 150 > plan.json

# Review and edit plan.json if needed

# Execute the plan
python3 scripts/batch_extract.py --json plan.json
```

### Extract Utilities

```json
[
  {
    "source": "app.js",
    "target": "utils/validation.js",
    "start": 100,
    "end": 150
  },
  {
    "source": "app.js",
    "target": "utils/formatting.js",
    "start": 200,
    "end": 250
  }
]
```

## Best Practices

### Before Splitting

1. **Always analyze first** - Use analyze_splits.py to understand structure
2. **Check dependencies** - Ensure extracted code dependencies are handled
3. **Plan imports** - You'll need to add import statements manually after splitting
4. **Test in copy mode** - Use default copy mode to test extractions safely

### During Splitting

1. **Work top-to-bottom** - When doing multiple extractions, process in order
2. **Use descriptive filenames** - Name targets based on their content
3. **Create logical groupings** - Group related functionality together
4. **Validate permissions** - Ensure target locations are writable

### After Splitting

1. **Update imports/exports** - Add necessary import and export statements
2. **Test thoroughly** - Ensure code still runs after reorganization
3. **Clean up** - Remove duplicate imports or unnecessary code
4. **Update documentation** - Reflect new file structure in docs

## Safety Features

- **Non-destructive by default**: Copy mode prevents accidental data loss
- **Permission validation**: Checks write permissions before modifying files
- **Read-only filesystem detection**: Prevents errors when working with read-only locations
- **Clear error messages**: Provides actionable guidance when operations fail
- **Filesystem safety**: Validates all paths and permissions before operations

## Tips for Claude Code

1. **Minimize context usage**: Instead of showing full file content, just specify line ranges
   - "Extract lines 50-100 from app.js to newfile.js"
   - "Split config.py: lines 1-200 to db_config.py, lines 201-400 to api_config.py"

2. **Use batch mode**: For multiple splits, create a JSON plan and execute once

3. **Leverage analysis**: Let analyze_splits.py identify logical boundaries automatically

4. **Chain operations**: Combine analysis → planning → execution in a workflow

## Project Structure

```
code-splitter/
├── README.md                    # This file
├── SKILL.md                     # Skill metadata and instructions
├── scripts/
│   ├── extract_lines.py        # Single extraction tool
│   ├── batch_extract.py        # Batch extraction tool
│   └── analyze_splits.py       # File analysis and planning tool
└── references/
    └── patterns.md             # Common patterns and examples
```

## Examples

### Example 1: Extract React Component

```bash
# Analyze the component file
python3 scripts/analyze_splits.py src/Dashboard.jsx

# Extract header component (lines 15-65)
python3 scripts/extract_lines.py src/Dashboard.jsx src/components/DashboardHeader.jsx 15 65

# Extract sidebar component (lines 66-120)
python3 scripts/extract_lines.py src/Dashboard.jsx src/components/DashboardSidebar.jsx 66 120
```

### Example 2: Split Utility Module

```bash
# Create a plan for splitting utilities
cat > split_utils.json << 'EOF'
[
  {
    "source": "src/utils.js",
    "target": "src/utils/validation.js",
    "start": 1,
    "end": 100
  },
  {
    "source": "src/utils.js",
    "target": "src/utils/formatting.js",
    "start": 101,
    "end": 200
  },
  {
    "source": "src/utils.js",
    "target": "src/utils/helpers.js",
    "start": 201,
    "end": 300
  }
]
EOF

# Execute the split
python3 scripts/batch_extract.py --json split_utils.json
```

### Example 3: Analyze and Auto-Split

```bash
# Analyze and get automatic split suggestions
python3 scripts/analyze_splits.py src/monolith.py --suggest --target-size 250 > auto_plan.json

# Review the generated plan
cat auto_plan.json

# Execute if satisfied
python3 scripts/batch_extract.py --json auto_plan.json
```

## Error Handling

The tools provide clear error messages for common issues:

- **File not found**: Indicates which source file is missing
- **Invalid line range**: Shows valid range for the file
- **Permission denied**: Explains which file/directory lacks write permissions
- **Read-only filesystem**: Suggests using copy mode instead of move mode

## Language Support

The analyzer recognizes patterns in:

- **Python**: Functions, classes, imports
- **JavaScript/TypeScript**: Functions, arrow functions, classes, imports, exports
- **Java**: Methods, classes, imports
- **Generic**: Falls back to basic pattern matching for other languages

## Limitations

- Import statements must be added manually after splitting
- Does not analyze cross-file dependencies automatically
- Line numbers must be determined by user or through analysis
- Cannot handle binary files or very large files that exceed memory

## Contributing

This is a Claude Code skill. Improvements and pattern additions are welcome in the `references/patterns.md` file.

## License

This skill is part of Claude Code and follows the same license terms.

## Support

For issues or questions about Claude Code skills, visit the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code).

---

**Quick Start:**
```bash
# Analyze a file
python3 scripts/analyze_splits.py myfile.js

# Extract some lines
python3 scripts/extract_lines.py myfile.js newfile.js 10 50

# Batch extract with a plan
python3 scripts/batch_extract.py --json plan.json
```
