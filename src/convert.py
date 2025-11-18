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
from src.page_builder import PageBuilder
from src.content_enhancer import ContentEnhancer


def load_data_files():
    """Load images and affiliate links from JSON files"""
    images = {}
    affiliate_links = {}

    # Load images.json
    images_path = Path('data/images.json')
    if images_path.exists():
        with open(images_path, 'r', encoding='utf-8') as f:
            images_data = json.load(f)
            images = {img['title']: img for img in images_data}

    # Load affiliate-links.json
    links_path = Path('data/affiliate-links.json')
    if links_path.exists():
        with open(links_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)
            affiliate_links = {link['casino_name']: link for link in links_data}

    return images, affiliate_links


def extract_platform_names(document: Dict) -> list:
    """Extract platform names from document for internal linking"""
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
        output_file = f"converted_files/{input_path.stem}.html"

    print(f"Converting: {input_file} -> {output_file}")

    # Step 1: Load data files
    print("  [1/4] Loading data files...")
    images, affiliate_links = load_data_files()
    print(f"        Loaded {len(images)} images and {len(affiliate_links)} affiliate links")

    # Step 2: Parse the document
    print("  [2/4] Parsing document...")
    document = parse_document(input_file)

    # Step 3: Build HTML with PageBuilder
    print("  [3/4] Building HTML with structured sections...")
    page_builder = PageBuilder()
    html = page_builder.build_platform_comparison_page(document, images, affiliate_links)

    # Step 4: Add internal linking (optional enhancement) - TODO: implement later
    print("  [4/4] Finalizing HTML...")
    # Internal linking can be added later with proper page mapping

    # Write output
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Conversion complete: {output_file}")

    return output_file


def batch_convert(input_directory: str = 'raw_documents', output_directory: str = 'converted_files'):
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
