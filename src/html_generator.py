"""
HTML Generator - Converts structured data into HTML with appropriate CSS classes
"""
import json
import re
from typing import Dict, List, Any


class HTMLGenerator:
    """Generates HTML from structured content data"""

    def __init__(self, config_path: str = 'config/template_config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.css_classes = self.config['css_classes']

    def generate_full_page(self, document: Dict[str, Any], images: Dict[str, Any] = None,
                          affiliate_links: Dict[str, Any] = None) -> str:
        """Generate complete HTML page from document data"""
        metadata = document.get('metadata', {})
        sections = document.get('sections', [])

        html_parts = []

        # DOCTYPE and head
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="en-GB">')
        html_parts.append('<head>')
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')

        if metadata.get('meta_title'):
            html_parts.append(f'    <title>{self._escape_html(metadata["meta_title"])}</title>')
        if metadata.get('meta_description'):
            html_parts.append(f'    <meta name="description" content="{self._escape_html(metadata["meta_description"])}">')

        html_parts.append('    <link rel="stylesheet" href="Stylesheet.css">')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('')

        # Main wrapper div
        html_parts.append(f'<div class="{self.css_classes["main_wrapper"]}" id="main-content">')
        html_parts.append('<article>')

        # Generate sections
        for i, section in enumerate(sections):
            section_html = self._generate_section(section, i == 0, images, affiliate_links)
            if section_html:
                html_parts.append(section_html)
                html_parts.append('')

        # Close main structure
        html_parts.append('</article>')
        html_parts.append('</div>')
        html_parts.append('')
        html_parts.append('</body>')
        html_parts.append('</html>')

        return '\n'.join(html_parts)

    def _generate_section(self, section: Dict[str, Any], is_first: bool,
                         images: Dict = None, affiliate_links: Dict = None) -> str:
        """Generate HTML for a single section"""
        section_type = section.get('type', 'standard')
        heading = section.get('heading', '')
        level = section.get('level', 2)
        content = section.get('content', '')

        # Handle first section as article header
        if is_first and level == 1:
            return self._generate_article_header(heading, content)

        # Route to specific generators based on section type
        if section_type == 'disclaimer':
            return self._generate_disclaimer(heading, section.get('disclaimer_data', {}))
        elif section_type == 'comparison_table':
            return self._generate_comparison_table(heading, section.get('table_data', []))
        elif section_type == 'platform_review':
            return self._generate_platform_review(heading, section.get('review_data', {}), images, affiliate_links)
        elif section_type == 'faq_section':
            return self._generate_faq_section(heading, content)
        elif section_type == 'verdict':
            return self._generate_verdict_section(heading, content)
        else:
            return self._generate_standard_section(heading, level, content)

    def _generate_article_header(self, heading: str, content: str) -> str:
        """Generate article header section"""
        html = []
        html.append(f'<header class="{self.css_classes["article_header"]}">')
        html.append(f'    <h1>{self._escape_html(heading)}</h1>')

        # Split content into intro paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs[:2]:  # Limit to first 2 paragraphs for intro
            if para:
                html.append(f'    <p class="{self.css_classes["intro"]}">{self._escape_html(para)}</p>')

        html.append('</header>')
        html.append('')
        html.append('<div>')
        html.append('    [elementor-template id="1128"]')
        html.append('</div>')

        return '\n'.join(html)

    def _generate_disclaimer(self, heading: str, disclaimer_data: Dict[str, Any]) -> str:
        """Generate disclaimer box"""
        html = []
        html.append(f'<section class="{self.css_classes["disclaimer"]}" aria-labelledby="disclaimer-heading">')
        html.append(f'    <h2 id="disclaimer-heading">{self._escape_html(heading)}</h2>')

        sections = disclaimer_data.get('sections', [])
        for section in sections:
            if section.get('title'):
                html.append(f'    <h3>{self._escape_html(section["title"])}</h3>')

            for line in section.get('content', []):
                if line.startswith('•'):
                    # Convert to list
                    if not html[-1].strip().endswith('<ul>'):
                        html.append('    <ul>')
                    html.append(f'        <li>{self._escape_html(line.replace("•", "").strip())}</li>')
                else:
                    # Close list if open
                    if html[-1].strip().endswith('</li>'):
                        html.append('    </ul>')
                    html.append(f'    <p>{self._escape_html(line)}</p>')

            # Close any open list
            if html[-1].strip().endswith('</li>'):
                html.append('    </ul>')

        html.append('</section>')
        return '\n'.join(html)

    def _generate_comparison_table(self, heading: str, table_data: List[Dict[str, Any]]) -> str:
        """Generate comparison table from CSV data"""
        if not table_data:
            return ''

        html = []
        html.append(f'<section class="{self.css_classes["content_section"]}">')
        html.append(f'    <h2>{self._escape_html(heading)}</h2>')
        html.append(f'    <div class="{self.css_classes["table_container"]}">')
        html.append('        <table class="comparison-table">')

        # Table header
        html.append('            <thead>')
        html.append('                <tr>')
        headers = list(table_data[0].keys())
        for header in headers:
            html.append(f'                    <th>{self._escape_html(header)}</th>')
        html.append('                </tr>')
        html.append('            </thead>')

        # Table body
        html.append('            <tbody>')
        for row in table_data:
            html.append('                <tr>')
            for header in headers:
                value = row.get(header, '')
                html.append(f'                    <td>{self._escape_html(value)}</td>')
            html.append('                </tr>')
        html.append('            </tbody>')

        html.append('        </table>')
        html.append('    </div>')
        html.append('</section>')
        return '\n'.join(html)

    def _generate_platform_review(self, heading: str, review_data: Dict[str, Any],
                                  images: Dict = None, affiliate_links: Dict = None) -> str:
        """Generate platform review section"""
        platform_name = review_data.get('platform_name', '')
        tagline = review_data.get('tagline', '')
        intro = review_data.get('intro', '')
        pros = review_data.get('pros', [])
        cons = review_data.get('cons', [])
        verdict = review_data.get('verdict', '')

        html = []
        html.append(f'<section class="{self.css_classes["platform_review"]}" id="{self._slugify(platform_name)}-review">')
        html.append(f'    <h3>{self._escape_html(heading)}</h3>')

        if intro:
            html.append(f'    <p>{self._escape_html(intro)}</p>')

        # Pros and Cons
        if pros or cons:
            html.append(f'    <div class="{self.css_classes["pros_cons"]}">')

            if pros:
                html.append('        <div class="pros">')
                html.append('            <h4>Pros:</h4>')
                html.append(f'            <ul class="{self.css_classes["pros_list"]}">')
                for pro in pros:
                    html.append(f'                <li>{self._escape_html(pro)}</li>')
                html.append('            </ul>')
                html.append('        </div>')

            if cons:
                html.append('        <div class="cons">')
                html.append('            <h4>Cons:</h4>')
                html.append(f'            <ul class="{self.css_classes["cons_list"]}">')
                for con in cons:
                    html.append(f'                <li>{self._escape_html(con)}</li>')
                html.append('            </ul>')
                html.append('        </div>')

            html.append('    </div>')

        # Additional details
        details = review_data.get('details', {})
        if details:
            for key, value in details.items():
                html.append(f'    <p><strong>{self._escape_html(key)}:</strong> {self._escape_html(value)}</p>')

        # Verdict
        if verdict:
            html.append(f'    <p><strong>Verdict:</strong> {self._escape_html(verdict)}</p>')

        html.append('</section>')
        return '\n'.join(html)

    def _generate_faq_section(self, heading: str, content: str) -> str:
        """Generate FAQ section"""
        html = []
        html.append(f'<section class="{self.css_classes["faq_section"]}">')
        html.append(f'    <h2>{self._escape_html(heading)}</h2>')

        # Parse FAQs from content
        lines = content.split('\n')
        current_question = None
        current_answer = []

        for line in lines:
            line_stripped = line.strip()
            # Check if this looks like a question (ends with ?) or has h3 marker
            if '?' in line_stripped or '(h3)' in line_stripped:
                # Save previous FAQ if exists
                if current_question:
                    html.append(f'    <div class="{self.css_classes["faq_item"]}">')
                    html.append(f'        <h3>{self._escape_html(current_question)}</h3>')
                    html.append(f'        <p>{self._escape_html(" ".join(current_answer))}</p>')
                    html.append('    </div>')

                current_question = line_stripped.replace('(h3)', '').strip()
                current_answer = []
            elif line_stripped and current_question:
                current_answer.append(line_stripped)

        # Save last FAQ
        if current_question:
            html.append(f'    <div class="{self.css_classes["faq_item"]}">')
            html.append(f'        <h3>{self._escape_html(current_question)}</h3>')
            html.append(f'        <p>{self._escape_html(" ".join(current_answer))}</p>')
            html.append('    </div>')

        html.append('</section>')
        return '\n'.join(html)

    def _generate_verdict_section(self, heading: str, content: str) -> str:
        """Generate verdict/conclusion section"""
        html = []
        html.append(f'<section class="verdict-section {self.css_classes["content_section"]}">')
        html.append(f'    <h2>{self._escape_html(heading)}</h2>')

        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs:
            html.append(f'    <p>{self._escape_html(para)}</p>')

        html.append('</section>')
        return '\n'.join(html)

    def _generate_standard_section(self, heading: str, level: int, content: str) -> str:
        """Generate standard content section"""
        html = []
        html.append(f'<section class="{self.css_classes["content_section"]}">')
        html.append(f'    <h{level}>{self._escape_html(heading)}</h{level}>')

        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs:
            # Check if this is a list item
            if para.startswith('•'):
                if not html[-1].strip().endswith('<ul>'):
                    html.append('    <ul>')
                html.append(f'        <li>{self._escape_html(para.replace("•", "").strip())}</li>')
            else:
                # Close list if open
                if html[-1].strip().endswith('</li>'):
                    html.append('    </ul>')
                html.append(f'    <p>{self._escape_html(para)}</p>')

        # Close any open list
        if html[-1].strip().endswith('</li>'):
            html.append('    </ul>')

        html.append('</section>')
        return '\n'.join(html)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ''
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text
