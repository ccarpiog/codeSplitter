# Code Splitting Patterns and Examples

## Quick Decision Guide

### When to use each script

1. **extract_lines.py** - Single extraction
   - Moving a specific function/class to a new file
   - Quick one-off splits
   - Interactive splitting during refactoring

2. **batch_extract.py** - Multiple extractions
   - Splitting a large file into multiple modules
   - Reorganizing entire codebases
   - Automated refactoring workflows

3. **analyze_splits.py** - Planning splits
   - Understanding file structure before splitting
   - Finding logical breakpoints
   - Generating split plans for review

## Common Splitting Patterns

### Pattern 1: Extract Class to New File

```bash
# Analyze first
python analyze_splits.py src/app.js

# Extract specific class (e.g., lines 50-200)
python extract_lines.py src/app.js src/UserClass.js 50 200
```

### Pattern 2: Split Large File into Modules

```bash
# Generate a plan
python analyze_splits.py src/monolith.js --suggest --target-size 150 > plan.json

# Review and edit plan.json if needed

# Execute the plan
python batch_extract.py --json plan.json
```

### Pattern 3: Extract Utilities

Common pattern for extracting utility functions:

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

### Pattern 4: Reorganize by Feature

Split monolithic files into feature-based modules:

```json
[
  {
    "source": "server.js",
    "target": "features/auth/auth.controller.js",
    "start": 50,
    "end": 200
  },
  {
    "source": "server.js",
    "target": "features/users/users.controller.js", 
    "start": 201,
    "end": 400
  },
  {
    "source": "server.js",
    "target": "features/products/products.controller.js",
    "start": 401,
    "end": 600
  }
]
```

## Best Practices

### Before Splitting

1. **Always analyze first** - Use analyze_splits.py to understand structure
2. **Check dependencies** - Ensure extracted code is self-contained
3. **Plan imports** - You'll need to add import statements manually after splitting

### During Splitting

1. **Use copy mode for testing** - Use `--mode copy` to test extractions without modifying source
2. **Extract in order** - When doing multiple extractions from same file, work top-to-bottom
3. **Create descriptive targets** - Use meaningful filenames that describe the extracted content

### After Splitting

1. **Update imports** - Add necessary import/export statements
2. **Test the split files** - Ensure code still runs after reorganization
3. **Clean up** - Remove any duplicate imports or unnecessary code

## Complex Example: Full Refactor

Refactoring a large React component file:

```bash
# 1. Analyze the structure
python analyze_splits.py src/Dashboard.jsx

# 2. Create extraction plan
cat > refactor_plan.json << 'EOF'
[
  {
    "source": "src/Dashboard.jsx",
    "target": "src/components/DashboardHeader.jsx",
    "start": 15,
    "end": 65
  },
  {
    "source": "src/Dashboard.jsx",
    "target": "src/components/DashboardSidebar.jsx",
    "start": 66,
    "end": 120
  },
  {
    "source": "src/Dashboard.jsx",
    "target": "src/hooks/useDashboardData.js",
    "start": 121,
    "end": 180
  },
  {
    "source": "src/Dashboard.jsx",
    "target": "src/utils/dashboardHelpers.js",
    "start": 181,
    "end": 230
  }
]
EOF

# 3. Execute the refactor
python batch_extract.py --json refactor_plan.json

# 4. The main Dashboard.jsx now only contains the main component
# with imports added for the extracted modules
```

## Tips for Claude Code

When working with these tools in Claude Code:

1. **Minimize context usage**: Instead of showing full file content, just specify:
   - "Extract lines 50-100 from app.js to newfile.js"
   - "Split config.py: lines 1-200 to db_config.py, lines 201-400 to api_config.py"

2. **Use batch mode**: For multiple splits, create a JSON plan and run once:
   ```python
   plan = [
     {"source": "big.js", "target": "part1.js", "start": 1, "end": 200},
     {"source": "big.js", "target": "part2.js", "start": 201, "end": 400}
   ]
   # Save as split_plan.json and run batch_extract.py
   ```

3. **Leverage analysis**: Let analyze_splits.py identify logical boundaries automatically

4. **Chain operations**: Combine analysis → planning → execution in a workflow
