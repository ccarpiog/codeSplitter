#!/usr/bin/env python3
"""
Extract specific line ranges from a source file to a target file.
Efficient, context-preserving file splitting utility.
"""

import sys
import os
import argparse
from pathlib import Path


def extract_lines(source_file, target_file, start_line, end_line, mode='copy', create_dirs=True):
    """
    Extract lines from source file to target file.

    Args:
        source_file: Path to source file
        target_file: Path to target file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)
        mode: 'copy' to keep in source (default), 'move' to remove from source
        create_dirs: Whether to create parent directories for target file

    Returns:
        dict with extraction results
    """
    source_path = Path(source_file)
    target_path = Path(target_file)

    # Validate source file exists
    if not source_path.exists():
        return {"error": f"Source file not found: {source_file}"}

    # Validate source file is writable if mode is 'move'
    if mode == 'move':
        if not os.access(source_path, os.W_OK):
            return {"error": f"Source file is not writable: {source_file}. Cannot use 'move' mode on read-only files. Use 'copy' mode instead."}
        # Check if parent directory is writable (in case file is in read-only filesystem)
        if not os.access(source_path.parent, os.W_OK):
            return {"error": f"Source directory is not writable: {source_path.parent}. Cannot use 'move' mode in read-only filesystem. Use 'copy' mode instead."}
    
    # Read source file
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": f"Error reading source file: {e}"}
    
    # Validate line numbers
    total_lines = len(lines)
    if start_line < 1 or start_line > total_lines:
        return {"error": f"Invalid start_line {start_line}. File has {total_lines} lines."}
    if end_line < start_line:
        return {"error": f"end_line {end_line} cannot be less than start_line {start_line}"}
    if end_line > total_lines:
        end_line = total_lines  # Adjust to file end
    
    # Extract the lines (convert to 0-indexed)
    extracted_lines = lines[start_line-1:end_line]

    # Validate target directory is writable
    target_dir = target_path.parent
    if target_dir.exists():
        if not os.access(target_dir, os.W_OK):
            return {"error": f"Target directory is not writable: {target_dir}. Cannot write to read-only filesystem."}
    else:
        # Check if we can create the directory
        if create_dirs:
            # Find the first existing parent directory
            parent = target_dir
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            if not os.access(parent, os.W_OK):
                return {"error": f"Cannot create target directory in read-only location: {parent}"}
        else:
            return {"error": f"Target directory does not exist: {target_dir}"}

    # Validate target file is writable if it exists
    if target_path.exists() and not os.access(target_path, os.W_OK):
        return {"error": f"Target file is not writable: {target_file}. Cannot write to read-only file."}

    # Create target directory if needed
    if create_dirs:
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return {"error": f"Failed to create target directory: {e}"}
    
    # Handle target file
    target_exists = target_path.exists()
    try:
        if target_exists:
            # Check if file ends with newline before appending
            needs_newline = False
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    f.seek(0, 2)  # Seek to end
                    if f.tell() > 0:
                        f.seek(f.tell() - 1)
                        last_char = f.read(1)
                        needs_newline = (last_char != '\n')
            except Exception as e:
                # If we can't read the file, proceed anyway
                pass

            # Append to existing file
            with open(target_path, 'a', encoding='utf-8') as f:
                if needs_newline:
                    f.write('\n')
                f.writelines(extracted_lines)
            action = "appended"
        else:
            # Create new file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.writelines(extracted_lines)
            action = "created"
    except OSError as e:
        if e.errno == 30:  # EROFS - Read-only file system
            return {"error": f"Cannot write to target file in read-only filesystem: {target_file}. Error: {e}"}
        else:
            return {"error": f"Failed to write to target file: {e}"}
    
    # Handle source file if mode is 'move'
    if mode == 'move':
        # Remove extracted lines from source
        remaining_lines = lines[:start_line-1] + lines[end_line:]
        try:
            with open(source_path, 'w', encoding='utf-8') as f:
                f.writelines(remaining_lines)
            source_action = "removed from source"
        except OSError as e:
            if e.errno == 30:  # EROFS - Read-only file system
                return {"error": f"Cannot modify source file in read-only filesystem: {source_file}. Use --mode copy instead. Error: {e}"}
            else:
                return {"error": f"Failed to modify source file: {e}"}
    else:
        source_action = "kept in source"
    
    return {
        "success": True,
        "lines_extracted": len(extracted_lines),
        "target_file": str(target_path),
        "target_action": action,
        "source_action": source_action,
        "extracted_range": f"{start_line}-{end_line}"
    }


def main():
    parser = argparse.ArgumentParser(description='Extract line ranges from files')
    parser.add_argument('source', help='Source file path')
    parser.add_argument('target', help='Target file path')
    parser.add_argument('start', type=int, help='Start line number (1-indexed)')
    parser.add_argument('end', type=int, help='End line number (1-indexed, inclusive)')
    parser.add_argument('--mode', choices=['move', 'copy'], default='copy',
                       help='Copy lines (keep in source, default) or move (remove from source)')
    parser.add_argument('--no-create-dirs', action='store_true',
                       help='Do not create parent directories for target file')
    
    args = parser.parse_args()
    
    result = extract_lines(
        args.source, 
        args.target, 
        args.start, 
        args.end,
        mode=args.mode,
        create_dirs=not args.no_create_dirs
    )
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✓ Extracted lines {result['extracted_range']} ({result['lines_extracted']} lines)")
        print(f"  Target: {result['target_file']} ({result['target_action']})")
        print(f"  Source: {result['source_action']}")


if __name__ == "__main__":
    main()
