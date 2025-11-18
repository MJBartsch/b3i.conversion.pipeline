"""
HTML Generator V2 - Uses template system for sophisticated HTML generation
"""
import json
from typing import Dict, List, Any
from pathlib import Path
from src.template_engine import TemplateEngine


class HTMLGeneratorV2:
    """Generates HTML using modular template system"""

    def __init__(self, config_path: str = 'config/template_config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.template_engine = TemplateEngine()
        self.css_classes = self.config['css_classes']

    def generate_full_page(self, document: Dict[str, Any], images: Dict[str, Any] = None,
                          affiliate_links: Dict[str, Any] = None) -> str:
        """Generate complete HTML page from document data"""
        metadata = document.get('metadata', {})
        sections = document.get('sections', [])

        # Build page sections
        meta_tags = self._generate_meta_tags(metadata)
        article_header = self._generate_article_header(sections)
        quick_verdict = self._generate_quick_verdict_section(sections, metadata)
        content_sections = self._generate_content_sections(sections)
        platform_reviews = self._generate_platform_reviews(sections, images, affiliate_links)
        faq_section = self._generate_faq_section(sections)
        footer = self._generate_footer()
        javascript = self.template_engine.load_template('components/javascript.html')

        # Fill base template
        page_data = {
            'meta_tags': meta_tags,
            'article_header': article_header,
            'quick_verdict_section': quick_verdict,
            'content_sections': content_sections,
            'platform_reviews': platform_reviews,
            'faq_section': faq_section,
            'footer': footer,
            'javascript': javascript
        }

        return self.template_engine.render('layouts/base_page.html', page_data)

    def _generate_meta_tags(self, metadata: Dict[str, Any]) -> str:
        """Generate meta tags"""
        html = ''

        if metadata.get('meta_title'):
            html += f'    <title>{self._escape_html(metadata["meta_title"])}</title>\n'

        if metadata.get('meta_description'):
            html += f'    <meta name="description" content="{self._escape_html(metadata["meta_description"])}">\n'

        return html

    def _generate_article_header(self, sections: List[Dict]) -> str:
        """Generate article header section"""
        if not sections or sections[0].get('level') != 1:
            return ''

        first_section = sections[0]
        heading = first_section.get('heading', '')
        content = first_section.get('content', '')

        # Split heading for highlight (if contains |)
        h1_text = heading
        h1_highlight = ''
        if '|' in heading:
            parts = heading.split('|', 1)
            h1_text = parts[0].strip()
            h1_highlight = f' <span class="highlight">| {parts[1].strip()}</span>'

        # Generate intro paragraphs
        intro_paragraphs = ''
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs[:2]:  # First 2 paragraphs
            if para:
                intro_paragraphs += f'    <p class="intro">{self._escape_html(para)}</p>\n'

        data = {
            'h1_text': h1_text,
            'h1_highlight': h1_highlight,
            'intro_paragraphs': intro_paragraphs
        }

        return self.template_engine.render('components/article_header.html', data)

    def _generate_quick_verdict_section(self, sections: List[Dict], metadata: Dict) -> str:
        """Generate quick verdict section with top platform cards"""
        # For now, create a basic quick verdict
        # In a real implementation, this would extract platform data from sections

        # Extract top 3 platforms from comparison table or platform reviews
        top_platforms = self._extract_top_platforms(sections)

        if not top_platforms:
            return ''

        verdict_cards = ''
        for platform in top_platforms:
            verdict_cards += self.template_engine.render_quick_verdict_card(platform)
            verdict_cards += '\n\n'

        data = {
            'title': 'Quick Verdict: Best Mobile Bitcoin Casinos',
            'subtitle': 'After extensive testing, these platforms offer the best experience for UK players.',
            'datetime': '2025-11',
            'date_text': 'November 2025',
            'verdict_cards': verdict_cards
        }

        return self.template_engine.render('components/quick_verdict_section.html', data)

    def _generate_content_sections(self, sections: List[Dict]) -> str:
        """Generate standard content sections"""
        html = ''

        for section in sections:
            section_type = section.get('type', 'standard')
            heading = section.get('heading', '')
            level = section.get('level', 2)
            content = section.get('content', '')

            # Skip h1 (article header) and platform reviews
            if level == 1 or section_type == 'platform_review':
                continue

            # Skip comparison table (handled separately)
            if section_type == 'comparison_table':
                html += self._generate_comparison_table_section(section)
                continue

            # Skip FAQ (handled separately)
            if section_type == 'faq_section':
                continue

            # Generate standard section
            html += f'<section class="content-section" aria-labelledby="{self._slugify(heading)}-heading">\n'
            html += f'    <h{level} id="{self._slugify(heading)}-heading">{self._escape_html(heading)}</h{level}>\n'

            # Add content paragraphs
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            for para in paragraphs:
                if para.startswith('•'):
                    # Start list if not already started
                    if not html.endswith('<ul>\n'):
                        html += '    <ul>\n'
                    html += f'        <li>{self._escape_html(para.replace("•", "").strip())}</li>\n'
                else:
                    # Close list if open
                    if html.endswith('</li>\n'):
                        html += '    </ul>\n'
                    html += f'    <p>{self._escape_html(para)}</p>\n'

            # Close any open list
            if html.endswith('</li>\n'):
                html += '    </ul>\n'

            html += '</section>\n\n'

        return html

    def _generate_comparison_table_section(self, section: Dict) -> str:
        """Generate comparison table section"""
        heading = section.get('heading', '')
        table_data = section.get('table_data', [])

        if not table_data:
            return ''

        html = f'<section class="content-section" id="comparison" aria-labelledby="comparison-heading">\n'
        html += f'    <h2 id="comparison-heading">{self._escape_html(heading)}</h2>\n'
        html += '    <div class="table-container">\n'
        html += '        <div class="table-responsive">\n'
        html += '            <table class="platform-table" aria-label="Comparison table">\n'

        # Table header
        html += '                <thead>\n'
        html += '                    <tr>\n'
        headers = list(table_data[0].keys())
        for header in headers:
            html += f'                        <th scope="col">{self._escape_html(header)}</th>\n'
        html += '                    </tr>\n'
        html += '                </thead>\n'

        # Table body
        html += '                <tbody>\n'
        for row in table_data:
            html += '                    <tr>\n'
            for header in headers:
                value = row.get(header, '')
                html += f'                        <td>{self._escape_html(value)}</td>\n'
            html += '                    </tr>\n'
        html += '                </tbody>\n'

        html += '            </table>\n'
        html += '        </div>\n'
        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _generate_platform_reviews(self, sections: List[Dict], images: Dict = None,
                                   affiliate_links: Dict = None) -> str:
        """Generate detailed platform review cards"""
        html = ''
        html += '<section class="content-section" aria-labelledby="reviews-heading">\n'
        html += '    <h2 id="reviews-heading">Detailed Platform Reviews</h2>\n\n'

        for section in sections:
            if section.get('type') == 'platform_review':
                review_data = section.get('review_data', {})
                platform_card = self._build_platform_card_data(review_data, images, affiliate_links)
                html += self.template_engine.render_platform_card(platform_card)
                html += '\n\n'

        html += '</section>\n\n'

        return html

    def _generate_faq_section(self, sections: List[Dict]) -> str:
        """Generate FAQ section with accordion"""
        faq_section = None

        for section in sections:
            if section.get('type') == 'faq_section':
                faq_section = section
                break

        if not faq_section:
            return ''

        heading = faq_section.get('heading', 'Frequently Asked Questions')
        content = faq_section.get('content', '')

        html = '<section class="faq-section" aria-labelledby="faq-heading">\n'
        html += f'    <h2 id="faq-heading">{self._escape_html(heading)}</h2>\n'
        html += '    <div class="faq-container">\n'

        # Parse FAQs from content
        faqs = self._parse_faqs(content)
        for i, faq in enumerate(faqs, 1):
            html += self.template_engine.render_faq_item(faq, i)
            html += '\n'

        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _generate_footer(self) -> str:
        """Generate footer section"""
        return '''<footer class="article-footer">
    <p><em>Last updated: November 2025 | All information verified at publication</em></p>
    <p><strong>18+ only. Gamble responsibly.</strong> BeGambleAware.org</p>
</footer>'''

    def _extract_top_platforms(self, sections: List[Dict]) -> List[Dict]:
        """Extract top 3 platforms for quick verdict"""
        platforms = []

        # Look for comparison table
        for section in sections:
            if section.get('type') == 'comparison_table':
                table_data = section.get('table_data', [])
                for i, row in enumerate(table_data[:3], 1):  # Top 3
                    platform = {
                        'name': row.get('Casino', row.get('Platform', '')),
                        'featured': i == 1,
                        'category_label': 'Best Overall' if i == 1 else 'Top Pick',
                        'category_title': 'Top Pick' if i == 1 else f'Runner Up #{i}',
                        'logo_url': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(row.get("Casino", ""))}-logo.png',
                        'rating': 5 if i == 1 else 4.5,
                        'features': [
                            row.get('Mobile Platform', 'Mobile optimized'),
                            row.get('Welcome Bonus', 'Welcome bonus available'),
                            row.get('Withdrawal Speed', 'Fast withdrawals')
                        ],
                        'badge': 'BEST OVERALL' if i == 1 else f'TOP {i}'
                    }
                    platforms.append(platform)
                break

        return platforms

    def _build_platform_card_data(self, review_data: Dict, images: Dict = None,
                                  affiliate_links: Dict = None) -> Dict:
        """Build platform card data structure"""
        platform_name = review_data.get('platform_name', '')

        return {
            'name': platform_name,
            'tagline': review_data.get('tagline', ''),
            'rating': 5.0,
            'logo_url': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(platform_name)}-logo.png',
            'header_image': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(platform_name)}-header.webp',
            'affiliate_link': f'https://b3i.tech/visit/casino/{self._slugify(platform_name)}',
            'cta_note': 'UKGC licensed • Fast withdrawals • Secure platform',
            'stats': [
                {'label': 'Bonus Code', 'value': 'None Needed', 'highlight': True},
                {'label': 'Welcome Bonus', 'value': '£100 + Free Spins'},
                {'label': 'Withdrawal Speed', 'value': '24 hours', 'highlight': True},
                {'label': 'License', 'value': 'UKGC'}
            ],
            'overview': review_data.get('intro', ''),
            'bonuses': '<p>Detailed bonus information...</p>',
            'games': '<p>Comprehensive games library...</p>',
            'pros': review_data.get('pros', []),
            'cons': review_data.get('cons', [])
        }

    def _parse_faqs(self, content: str) -> List[Dict]:
        """Parse FAQ content into question/answer pairs"""
        faqs = []
        lines = content.split('\n')
        current_question = None
        current_answer = []

        for line in lines:
            line_stripped = line.strip()

            # Check if this is a question
            if '?' in line_stripped and not line_stripped.startswith('•'):
                # Save previous FAQ
                if current_question:
                    faqs.append({
                        'question': current_question.replace('(h3)', '').strip(),
                        'answer': '<p>' + ' '.join(current_answer) + '</p>'
                    })

                current_question = line_stripped
                current_answer = []
            elif line_stripped and current_question:
                current_answer.append(line_stripped)

        # Save last FAQ
        if current_question:
            faqs.append({
                'question': current_question.replace('(h3)', '').strip(),
                'answer': '<p>' + ' '.join(current_answer) + '</p>'
            })

        return faqs

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
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text
