"""
Content Parser - Extracts structured data from raw documents
"""
import re
import csv
from io import StringIO
from typing import Dict, List, Any


class ContentParser:
    """Parses raw text documents into structured data"""

    def __init__(self, content: str):
        self.raw_content = content
        self.lines = content.split('\n')
        self.current_line = 0

    def parse(self) -> Dict[str, Any]:
        """Parse the entire document into structured data"""
        document = {
            'metadata': self._parse_metadata(),
            'sections': self._parse_content_sections(),
        }
        return document

    def _parse_metadata(self) -> Dict[str, Any]:
        """Extract metadata from document header"""
        metadata = {
            'target_keyword': '',
            'target_geo': '',
            'url_slug': '',
            'meta_title': '',
            'meta_description': '',
            'notes': '',
            'featured_image': {}
        }

        for i, line in enumerate(self.lines):
            if line.startswith('Target Keyword:'):
                metadata['target_keyword'] = line.replace('Target Keyword:', '').strip()
            elif line.startswith('Target Geo:'):
                metadata['target_geo'] = line.replace('Target Geo:', '').strip()
            elif line.strip() == 'URL Slug:' and i + 1 < len(self.lines):
                metadata['url_slug'] = self.lines[i + 1].strip()
            elif line.startswith('Meta Title'):
                metadata['meta_title'] = self.lines[i + 1].strip() if i + 1 < len(self.lines) else ''
            elif line.startswith('Meta Description'):
                metadata['meta_description'] = self.lines[i + 1].strip() if i + 1 < len(self.lines) else ''
            elif line.startswith('Notes for MJ:'):
                # Capture notes until we hit "Content" section
                notes_lines = []
                j = i + 1
                while j < len(self.lines) and not self.lines[j].startswith('Content'):
                    notes_lines.append(self.lines[j])
                    j += 1
                metadata['notes'] = '\n'.join(notes_lines).strip()
            elif line.startswith('Featured image:'):
                # Capture featured image details
                j = i + 1
                img_lines = []
                while j < len(self.lines) and self.lines[j].strip() and not self.lines[j].startswith('SEO Title:'):
                    img_lines.append(self.lines[j].strip())
                    j += 1
                if img_lines:
                    metadata['featured_image']['description'] = img_lines[0] if len(img_lines) > 0 else ''
                    # Look for SEO Title and ALT Tag
                    for k, img_line in enumerate(self.lines[i:i+10]):
                        if img_line.startswith('SEO Title:'):
                            metadata['featured_image']['seo_title'] = img_line.replace('SEO Title:', '').strip()
                        elif img_line.startswith('ALT Tag:'):
                            metadata['featured_image']['alt_tag'] = img_line.replace('ALT Tag:', '').strip()
            elif line.strip() == 'Content':
                self.current_line = i + 1
                break

        return metadata

    def _parse_content_sections(self) -> List[Dict[str, Any]]:
        """Parse the main content into sections"""
        sections = []
        i = self.current_line

        while i < len(self.lines):
            line = self.lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check for heading
            heading_match = re.match(r'^(.+?)\s*\(h([1-6])\)$', line)
            if heading_match:
                heading_text = heading_match.group(1)
                heading_level = int(heading_match.group(2))

                # Extract content until next heading
                content_lines = []
                i += 1
                while i < len(self.lines):
                    next_line = self.lines[i].strip()
                    # Check if this is another heading
                    if re.match(r'^.+?\s*\(h[1-6]\)$', next_line):
                        break
                    content_lines.append(self.lines[i])
                    i += 1

                content = '\n'.join(content_lines).strip()

                # Parse special section types
                section_data = {
                    'type': self._detect_section_type(heading_text, content),
                    'heading': heading_text,
                    'level': heading_level,
                    'content': content
                }

                # Parse special content types
                if section_data['type'] == 'comparison_table':
                    section_data['table_data'] = self._parse_csv_table(content)
                elif section_data['type'] == 'platform_review':
                    section_data['review_data'] = self._parse_platform_review(heading_text, content)
                elif section_data['type'] == 'disclaimer':
                    section_data['disclaimer_data'] = self._parse_disclaimer(content)

                sections.append(section_data)
            else:
                i += 1

        return sections

    def _detect_section_type(self, heading: str, content: str) -> str:
        """Detect the type of section based on heading and content"""
        heading_lower = heading.lower()
        content_lower = content.lower()

        # Check for disclaimer/notice
        if 'notice' in heading_lower or 'disclaimer' in heading_lower:
            return 'disclaimer'

        # Check for comparison table (CSV content)
        if content.strip().startswith('csv'):
            return 'comparison_table'

        # Check for FAQ
        if 'faq' in heading_lower or 'frequently asked' in heading_lower:
            return 'faq_section'

        # Check for platform reviews (numbered headings with platform names)
        if re.match(r'^\d+\.\s+\w+', heading):
            return 'platform_review'

        # Check for verdict/conclusion
        if 'verdict' in heading_lower or 'conclusion' in heading_lower:
            return 'verdict'

        # Default to standard section
        return 'standard'

    def _parse_csv_table(self, content: str) -> List[Dict[str, Any]]:
        """Parse CSV table content"""
        # Remove 'csv' marker
        csv_content = re.sub(r'^csv\s*\n', '', content, flags=re.MULTILINE).strip()

        # Parse CSV
        csv_reader = csv.DictReader(StringIO(csv_content))
        return list(csv_reader)

    def _parse_platform_review(self, heading: str, content: str) -> Dict[str, Any]:
        """Parse platform review section"""
        review_data = {
            'platform_name': '',
            'tagline': '',
            'intro': '',
            'pros': [],
            'cons': [],
            'details': {},
            'verdict': ''
        }

        # Extract platform name and tagline from heading
        match = re.match(r'^\d+\.\s+(.+?)\s*-\s*(.+)$', heading)
        if match:
            review_data['platform_name'] = match.group(1).strip()
            review_data['tagline'] = match.group(2).strip()
        else:
            review_data['platform_name'] = heading

        # Parse content
        lines = content.split('\n')
        current_section = 'intro'
        intro_lines = []

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith('Pros:'):
                current_section = 'pros'
            elif line_stripped.startswith('Cons:'):
                current_section = 'cons'
            elif 'Compatibility:' in line_stripped or 'Compliance:' in line_stripped:
                current_section = 'details'
            elif line_stripped.startswith('Verdict:'):
                current_section = 'verdict'
            elif line_stripped.startswith('•'):
                # List item
                item = line_stripped.replace('•', '').strip()
                if current_section == 'pros':
                    review_data['pros'].append(item)
                elif current_section == 'cons':
                    review_data['cons'].append(item)
            elif current_section == 'intro' and line_stripped:
                intro_lines.append(line_stripped)
            elif current_section == 'verdict' and line_stripped:
                review_data['verdict'] += line_stripped + ' '
            elif current_section == 'details' and ':' in line_stripped:
                key, value = line_stripped.split(':', 1)
                review_data['details'][key.strip()] = value.strip()

        review_data['intro'] = ' '.join(intro_lines)
        review_data['verdict'] = review_data['verdict'].strip()

        return review_data

    def _parse_disclaimer(self, content: str) -> Dict[str, Any]:
        """Parse disclaimer content into structured sections"""
        disclaimer_data = {
            'sections': []
        }

        lines = content.split('\n')
        current_section = {'title': '', 'content': []}

        for line in lines:
            line_stripped = line.strip()

            # Check if this is a section title (ends with colon)
            if line_stripped.endswith(':') and not line_stripped.startswith('•'):
                # Save previous section if it has content
                if current_section['title'] or current_section['content']:
                    disclaimer_data['sections'].append({
                        'title': current_section['title'],
                        'content': current_section['content']
                    })
                # Start new section
                current_section = {
                    'title': line_stripped.rstrip(':'),
                    'content': []
                }
            elif line_stripped:
                current_section['content'].append(line_stripped)

        # Add last section
        if current_section['title'] or current_section['content']:
            disclaimer_data['sections'].append({
                'title': current_section['title'],
                'content': current_section['content']
            })

        return disclaimer_data


def parse_document(file_path: str) -> Dict[str, Any]:
    """Parse a document file and return structured data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = ContentParser(content)
    return parser.parse()
