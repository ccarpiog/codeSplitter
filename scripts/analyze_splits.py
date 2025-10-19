#!/usr/bin/env python3
"""
Analyze code files to identify logical split points.
Helps determine where to split large files.
"""

import re
import sys
from pathlib import Path


def analyze_file(filepath):
    """
    Analyze a code file to identify logical sections and potential split points.
    
    Returns dict with:
        - total_lines: total line count
        - functions: list of function definitions with line numbers
        - classes: list of class definitions with line numbers
        - imports: line range of import statements
        - sections: identified logical sections
    """
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}
    
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    analysis = {
        "file": str(path),
        "total_lines": len(lines),
        "functions": [],
        "classes": [],
        "imports": {"start": None, "end": None},
        "sections": []
    }
    
    # Detect file type
    ext = path.suffix.lower()
    
    # Pattern definitions based on file type
    if ext in ['.py']:
        func_pattern = r'^(async\s+)?def\s+(\w+)'
        class_pattern = r'^class\s+(\w+)'
        import_pattern = r'^(from\s+.+\s+import|import\s+)'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        func_pattern = r'^(export\s+)?(async\s+)?function\s+(\w+)|^(export\s+)?const\s+(\w+)\s*=\s*(async\s+)?.*=>|^(export\s+)?const\s+(\w+)\s*=\s*(async\s+)?function'
        class_pattern = r'^(export\s+)?class\s+(\w+)'
        import_pattern = r'^(import\s+|export\s+.+\s+from)'
    elif ext in ['.java']:
        func_pattern = r'^\s*(public|private|protected|static|\s)+\s+\w+\s+(\w+)\s*\('
        class_pattern = r'^(public\s+)?class\s+(\w+)'
        import_pattern = r'^import\s+'
    else:
        # Generic patterns
        func_pattern = r'function\s+(\w+)|def\s+(\w+)'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'^(import|#include|using)'
    
    # Track imports section
    import_started = False
    import_ended = False
    
    # Analyze line by line
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip empty lines and comments for pattern matching
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue
        
        # Check for imports
        if re.match(import_pattern, line):
            if not import_started:
                analysis["imports"]["start"] = i
                import_started = True
            analysis["imports"]["end"] = i
        elif import_started and not import_ended and not re.match(import_pattern, line):
            import_ended = True
        
        # Check for functions
        func_match = re.match(func_pattern, line)
        if func_match:
            # Extract function name from groups
            func_name = next((g for g in func_match.groups() if g and not g in ['export', 'async', 'const', '=>']), 'unknown')
            analysis["functions"].append({
                "name": func_name,
                "line": i,
                "definition": stripped[:50] + "..." if len(stripped) > 50 else stripped
            })
        
        # Check for classes
        class_match = re.match(class_pattern, line)
        if class_match:
            class_name = next((g for g in class_match.groups() if g and g not in ['export', 'public']), 'unknown')
            analysis["classes"].append({
                "name": class_name,
                "line": i,
                "definition": stripped[:50] + "..." if len(stripped) > 50 else stripped
            })
        
        # Check for section markers (comments that might indicate sections)
        if re.match(r'^[/#\*]+\s*[-=]+', stripped) or re.match(r'^[/#\*]+\s*[A-Z][A-Z\s]+[A-Z]', stripped):
            analysis["sections"].append({
                "line": i,
                "marker": stripped[:50]
            })
    
    return analysis


def suggest_splits(analysis, target_size=200):
    """
    Suggest split points based on file analysis.
    
    Args:
        analysis: Result from analyze_file()
        target_size: Target lines per file
    
    Returns:
        List of suggested splits
    """
    if "error" in analysis:
        return []
    
    suggestions = []
    total_lines = analysis["total_lines"]
    
    if total_lines <= target_size:
        return []
    
    # Group related functions/classes
    logical_breaks = []
    
    # Add class boundaries as logical breaks
    for cls in analysis["classes"]:
        logical_breaks.append((cls["line"], f"class {cls['name']}"))
    
    # Add major function groups
    for func in analysis["functions"]:
        logical_breaks.append((func["line"], f"function {func['name']}"))
    
    # Sort by line number
    logical_breaks.sort(key=lambda x: x[0])
    
    # Suggest splits
    if logical_breaks:
        chunks = []
        current_start = 1
        
        for i, (line, label) in enumerate(logical_breaks):
            # Check if we should split here
            if line - current_start >= target_size:
                chunks.append({
                    "start": current_start,
                    "end": line - 1,
                    "lines": line - current_start,
                    "description": f"Section before {label}"
                })
                current_start = line
        
        # Add final chunk
        if current_start < total_lines:
            chunks.append({
                "start": current_start,
                "end": total_lines,
                "lines": total_lines - current_start + 1,
                "description": "Final section"
            })
        
        suggestions = chunks
    else:
        # Simple split by size
        num_chunks = (total_lines + target_size - 1) // target_size
        for i in range(num_chunks):
            start = i * target_size + 1
            end = min((i + 1) * target_size, total_lines)
            suggestions.append({
                "start": start,
                "end": end,
                "lines": end - start + 1,
                "description": f"Chunk {i+1}/{num_chunks}"
            })
    
    return suggestions


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze code files for splitting')
    parser.add_argument('file', help='File to analyze')
    parser.add_argument('--target-size', type=int, default=200,
                       help='Target lines per split (default: 200)')
    parser.add_argument('--suggest', action='store_true',
                       help='Suggest split points')
    
    args = parser.parse_args()
    
    # Analyze the file
    analysis = analyze_file(args.file)
    
    if "error" in analysis:
        print(f"Error: {analysis['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Print analysis
    print(f"File: {analysis['file']}")
    print(f"Total lines: {analysis['total_lines']}")
    
    if analysis["imports"]["start"]:
        print(f"\nImports: lines {analysis['imports']['start']}-{analysis['imports']['end']}")
    
    if analysis["classes"]:
        print(f"\nClasses ({len(analysis['classes'])}):")
        for cls in analysis["classes"][:10]:  # Show first 10
            print(f"  Line {cls['line']:4}: {cls['name']}")
        if len(analysis["classes"]) > 10:
            print(f"  ... and {len(analysis['classes']) - 10} more")
    
    if analysis["functions"]:
        print(f"\nFunctions ({len(analysis['functions'])}):")
        for func in analysis["functions"][:10]:  # Show first 10
            print(f"  Line {func['line']:4}: {func['name']}")
        if len(analysis["functions"]) > 10:
            print(f"  ... and {len(analysis['functions']) - 10} more")
    
    if args.suggest:
        suggestions = suggest_splits(analysis, args.target_size)
        if suggestions:
            print(f"\nSuggested splits (target size: {args.target_size} lines):")
            for i, split in enumerate(suggestions, 1):
                print(f"  {i}. Lines {split['start']:4}-{split['end']:4} ({split['lines']:3} lines): {split['description']}")
            
            # Generate extraction plan
            print("\nExtraction plan (JSON):")
            plan = []
            base_name = Path(args.file).stem
            ext = Path(args.file).suffix
            for i, split in enumerate(suggestions, 1):
                plan.append({
                    "source": args.file,
                    "target": f"{base_name}_part{i}{ext}",
                    "start": split["start"],
                    "end": split["end"]
                })
            print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    import json
    main()
