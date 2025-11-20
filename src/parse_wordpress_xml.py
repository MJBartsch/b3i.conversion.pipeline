#!/usr/bin/env python3
"""
WordPress XML Parser - Converts WordPress export XML to JSON and extracts images

Usage:
    python src/parse_wordpress_xml.py <xml_file>

Example:
    python src/parse_wordpress_xml.py b3itech.WordPress.2025-11-20.xml
"""
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import re


def parse_php_serialized_metadata(serialized_str):
    """
    Parse PHP serialized metadata string to extract key information
    This is a simplified parser for the specific metadata format we see
    """
    metadata = {}

    # Extract width
    width_match = re.search(r's:5:"width";i:(\d+)', serialized_str)
    if width_match:
        metadata['width'] = int(width_match.group(1))

    # Extract height
    height_match = re.search(r's:6:"height";i:(\d+)', serialized_str)
    if height_match:
        metadata['height'] = int(height_match.group(1))

    # Extract file
    file_match = re.search(r's:4:"file";s:\d+:"([^"]+)"', serialized_str)
    if file_match:
        metadata['file'] = file_match.group(1)

    # Extract filesize
    filesize_match = re.search(r's:8:"filesize";i:(\d+)', serialized_str)
    if filesize_match:
        metadata['filesize'] = int(filesize_match.group(1))

    return metadata


def parse_wordpress_xml(xml_file):
    """Parse WordPress XML export and extract all content"""

    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define namespaces
    namespaces = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
    }

    # Extract site info
    channel = root.find('channel')
    site_info = {
        'title': channel.find('title').text if channel.find('title') is not None else '',
        'link': channel.find('link').text if channel.find('link') is not None else '',
        'description': channel.find('description').text if channel.find('description') is not None else '',
        'base_url': channel.find('wp:base_blog_url', namespaces).text if channel.find('wp:base_blog_url', namespaces) is not None else ''
    }

    # Extract all items
    items = channel.findall('item')

    attachments = []
    posts = []
    pages = []

    for item in items:
        # Get post type
        post_type_elem = item.find('wp:post_type', namespaces)
        post_type = post_type_elem.text if post_type_elem is not None else ''

        # Get post status
        status_elem = item.find('wp:status', namespaces)
        status = status_elem.text if status_elem is not None else ''

        # Extract common fields
        title_elem = item.find('title')
        title = title_elem.text if title_elem is not None else ''

        link_elem = item.find('link')
        link = link_elem.text if link_elem is not None else ''

        pub_date_elem = item.find('pubDate')
        pub_date = pub_date_elem.text if pub_date_elem is not None else ''

        post_id_elem = item.find('wp:post_id', namespaces)
        post_id = int(post_id_elem.text) if post_id_elem is not None and post_id_elem.text else 0

        parent_id_elem = item.find('wp:post_parent', namespaces)
        parent_id = int(parent_id_elem.text) if parent_id_elem is not None and parent_id_elem.text else 0

        # Process attachments (images)
        if post_type == 'attachment':
            attachment_url_elem = item.find('wp:attachment_url', namespaces)
            attachment_url = attachment_url_elem.text if attachment_url_elem is not None else ''

            # Extract metadata from postmeta
            metadata = {}
            postmeta_items = item.findall('wp:postmeta', namespaces)
            for meta in postmeta_items:
                meta_key_elem = meta.find('wp:meta_key', namespaces)
                meta_value_elem = meta.find('wp:meta_value', namespaces)

                if meta_key_elem is not None and meta_value_elem is not None:
                    key = meta_key_elem.text
                    value = meta_value_elem.text if meta_value_elem.text else ''

                    if key == '_wp_attached_file':
                        metadata['_wp_attached_file'] = value
                    elif key == '_wp_attachment_metadata':
                        metadata['_wp_attachment_metadata'] = value
                        # Also parse the serialized metadata
                        parsed_meta = parse_php_serialized_metadata(value)
                        metadata.update(parsed_meta)

            attachment_data = {
                'id': post_id,
                'title': title,
                'url': attachment_url,
                'link': link,
                'status': status,
                'pub_date': pub_date,
                'parent_id': parent_id,
                'metadata': metadata
            }

            attachments.append(attachment_data)

        # Process posts
        elif post_type == 'post':
            content_elem = item.find('content:encoded', namespaces)
            content = content_elem.text if content_elem is not None else ''

            excerpt_elem = item.find('excerpt:encoded', namespaces)
            excerpt = excerpt_elem.text if excerpt_elem is not None else ''

            post_data = {
                'id': post_id,
                'title': title,
                'link': link,
                'pub_date': pub_date,
                'status': status,
                'content': content,
                'excerpt': excerpt
            }

            posts.append(post_data)

        # Process pages
        elif post_type == 'page':
            content_elem = item.find('content:encoded', namespaces)
            content = content_elem.text if content_elem is not None else ''

            page_data = {
                'id': post_id,
                'title': title,
                'link': link,
                'status': status,
                'content': content
            }

            pages.append(page_data)

    return {
        'site_info': site_info,
        'attachments': attachments,
        'posts': posts,
        'pages': pages
    }


def update_images_json(new_data, images_json_path='images.json'):
    """Update images.json file with new attachments"""

    # Load existing images.json if it exists
    if Path(images_json_path).exists():
        with open(images_json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {
            'site_info': {},
            'attachments': []
        }

    # Update site info if available
    if new_data.get('site_info'):
        existing_data['site_info'] = new_data['site_info']

    # Create a set of existing attachment IDs to avoid duplicates
    existing_ids = {att['id'] for att in existing_data.get('attachments', [])}

    # Add new attachments that don't already exist
    new_attachments = []
    updated_count = 0

    for attachment in new_data.get('attachments', []):
        if attachment['id'] not in existing_ids:
            new_attachments.append(attachment)
        else:
            # Update existing attachment
            for i, existing_att in enumerate(existing_data['attachments']):
                if existing_att['id'] == attachment['id']:
                    existing_data['attachments'][i] = attachment
                    updated_count += 1
                    break

    # Append new attachments
    existing_data['attachments'].extend(new_attachments)

    # Sort by ID for consistency
    existing_data['attachments'].sort(key=lambda x: x['id'])

    # Write updated data
    with open(images_json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    return len(new_attachments), updated_count


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/parse_wordpress_xml.py <xml_file>")
        print("\nExample:")
        print("  python src/parse_wordpress_xml.py b3itech.WordPress.2025-11-20.xml")
        sys.exit(1)

    xml_file = sys.argv[1]

    if not Path(xml_file).exists():
        print(f"Error: File not found: {xml_file}")
        sys.exit(1)

    print(f"Parsing WordPress XML: {xml_file}")
    print("=" * 60)

    # Parse XML
    data = parse_wordpress_xml(xml_file)

    print(f"\n✓ Parsed WordPress export:")
    print(f"  Site: {data['site_info']['title']}")
    print(f"  Attachments (images): {len(data['attachments'])}")
    print(f"  Posts: {len(data['posts'])}")
    print(f"  Pages: {len(data['pages'])}")

    # Save full data to JSON
    output_file = Path(xml_file).stem + '.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved full export to: {output_file}")

    # Update images.json
    print(f"\nUpdating images.json...")
    new_count, updated_count = update_images_json(data)

    print(f"✓ Updated images.json:")
    print(f"  New attachments added: {new_count}")
    print(f"  Existing attachments updated: {updated_count}")
    print(f"  Total attachments in images.json: {new_count + updated_count}")

    print("\n" + "=" * 60)
    print("Conversion complete!")


if __name__ == '__main__':
    main()
