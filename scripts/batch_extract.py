#!/usr/bin/env python3
"""
Batch extract multiple line ranges from files.
Processes extraction plans defined in JSON or command line.
"""

import json
import sys
from pathlib import Path
from extract_lines import extract_lines


def process_batch(extractions):
    """
    Process multiple extraction operations.

    Args:
        extractions: List of extraction dictionaries with keys:
            - source: source file path
            - target: target file path
            - start: start line (1-indexed)
            - end: end line (1-indexed)
            - mode: optional, 'copy' (default) or 'move'

    Returns:
        List of results for each extraction
    """
    results = []

    for i, extraction in enumerate(extractions, 1):
        print(f"[{i}/{len(extractions)}] Processing: {extraction['source']} -> {extraction['target']}")

        result = extract_lines(
            extraction['source'],
            extraction['target'],
            extraction['start'],
            extraction['end'],
            mode=extraction.get('mode', 'copy')
        )
        
        results.append({
            "extraction": extraction,
            "result": result
        })
        
        if "error" in result:
            print(f"  ✗ Error: {result['error']}")
        else:
            print(f"  ✓ Extracted lines {result['extracted_range']}")
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch extract line ranges from files')
    parser.add_argument('--json', '-j', help='JSON file with extraction plan')
    parser.add_argument('--plan', '-p', help='JSON string with extraction plan')
    
    args = parser.parse_args()
    
    if args.json:
        # Load from JSON file
        with open(args.json, 'r') as f:
            extractions = json.load(f)
    elif args.plan:
        # Parse JSON string
        extractions = json.loads(args.plan)
    else:
        # Example plan format
        print("Usage: batch_extract.py --json plan.json")
        print("   or: batch_extract.py --plan '[{\"source\":\"app.js\",\"target\":\"utils.js\",\"start\":50,\"end\":100}]'")
        print("\nExample plan.json:")
        print(json.dumps([
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
                "end": 150
            }
        ], indent=2))
        sys.exit(1)
    
    # Process the extractions
    results = process_batch(extractions)
    
    # Summary
    successful = sum(1 for r in results if r["result"].get("success"))
    failed = len(results) - successful
    
    print(f"\n{'='*50}")
    print(f"Completed: {successful} successful, {failed} failed")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
