#!/usr/bin/env python3
"""
Main Conversion Script - Converts raw documents to HTML

Usage:
    python src/convert.py <input_file> [output_file]

Example:
    python src/convert.py raw_documents/sample.txt output/sample.html
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.content_parser import parse_document
from src.html_generator_v2 import HTMLGeneratorV2 as HTMLGenerator
from src.content_enhancer import ContentEnhancer


def extract_platform_names(document: Dict) -> list:
    """Extract platform names from document for image/link matching"""
    platform_names = []

    for section in document.get('sections', []):
        if section.get('type') == 'platform_review':
            review_data = section.get('review_data', {})
            platform_name = review_data.get('platform_name', '')
            if platform_name:
                platform_names.append(platform_name)

        elif section.get('type') == 'comparison_table':
            table_data = section.get('table_data', [])
            for row in table_data:
                casino = row.get('Casino', '')
                if casino:
                    platform_names.append(casino)

    return platform_names


def convert_document(input_file: str, output_file: str = None) -> str:
    """Convert a document from raw text to HTML"""

    # Default output file if not specified
    if not output_file:
        input_path = Path(input_file)
        output_file = f"output/{input_path.stem}.html"

    print(f"Converting: {input_file} -> {output_file}")

    # Step 1: Parse the document
    print("  [1/4] Parsing document...")
    document = parse_document(input_file)

    # Step 2: Generate HTML
    print("  [2/4] Generating HTML...")
    generator = HTMLGenerator()
    html = generator.generate_full_page(document)

    # Step 3: Extract platform names for enhancement
    print("  [3/4] Extracting platform names...")
    platform_names = extract_platform_names(document)
    print(f"        Found {len(platform_names)} platforms: {', '.join(platform_names[:5])}...")

    # Step 4: Enhance HTML with images and affiliate links
    print("  [4/4] Enhancing HTML (images, affiliate links)...")
    enhancer = ContentEnhancer()
    html = enhancer.enhance_html(html, platform_names=platform_names)

    # Write output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Conversion complete: {output_file}")

    return output_file


def batch_convert(input_directory: str = 'raw_documents', output_directory: str = 'output'):
    """Convert all documents in a directory"""
    input_path = Path(input_directory)
    output_path = Path(output_directory)

    # Create output directory
    output_path.mkdir(exist_ok=True)

    # Find all text files
    txt_files = list(input_path.glob('*.txt'))

    if not txt_files:
        print(f"No .txt files found in {input_directory}")
        return

    print(f"\nBatch converting {len(txt_files)} documents...")
    print("=" * 60)

    results = []
    for txt_file in txt_files:
        output_file = output_path / f"{txt_file.stem}.html"
        try:
            convert_document(str(txt_file), str(output_file))
            results.append({'file': txt_file.name, 'status': 'success', 'output': str(output_file)})
        except Exception as e:
            print(f"✗ Error converting {txt_file.name}: {e}")
            results.append({'file': txt_file.name, 'status': 'error', 'error': str(e)})

    print("\n" + "=" * 60)
    print("Batch conversion summary:")
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'error')
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    return results


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Convert single file:")
        print("    python src/convert.py <input_file> [output_file]")
        print()
        print("  Batch convert all files in raw_documents/:")
        print("    python src/convert.py --batch")
        print()
        print("Examples:")
        print("  python src/convert.py raw_documents/sample.txt")
        print("  python src/convert.py raw_documents/sample.txt output/my_page.html")
        print("  python src/convert.py --batch")
        sys.exit(1)

    # Batch mode
    if sys.argv[1] == '--batch':
        batch_convert()
    else:
        # Single file mode
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_document(input_file, output_file)


if __name__ == '__main__':
    main()
