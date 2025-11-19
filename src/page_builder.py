"""
Page Builder - Builds complete pages following defined structures
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from src.template_engine import TemplateEngine


class PageBuilder:
    """Builds pages following predefined section structures"""

    def __init__(self, structure_config_path: str = 'config/page_structure.json'):
        with open(structure_config_path, 'r') as f:
            self.structure_config = json.load(f)

        self.template_engine = TemplateEngine()

    def build_platform_comparison_page(self, document: Dict[str, Any],
                                      images: Dict = None,
                                      affiliate_links: Dict = None) -> str:
        """Build a platform comparison page following the defined structure"""

        page_type = 'platform_comparison'
        section_order = self.structure_config['page_types'][page_type]['section_order']

        # Extract and organize content by section
        content_map = self._map_content_to_sections(document, images, affiliate_links)

        # Build page sections in order
        sections_html = []
        for section_name in section_order:
            section_html = self._build_section(section_name, content_map, document)
            if section_html:
                sections_html.append(section_html)

        # Assemble final page
        return self._assemble_page(document, sections_html)

    def _map_content_to_sections(self, document: Dict, images: Dict, affiliate_links: Dict) -> Dict:
        """Map parsed document content to template sections"""

        metadata = document.get('metadata', {})
        sections = document.get('sections', [])

        content_map = {
            'metadata': metadata,
            'article_header': self._extract_article_header(sections),
            'quick_verdict_platforms': self._extract_top_platforms(sections),
            'context_sections': self._extract_context_sections(sections),
            'comparison_table': self._extract_comparison_table(sections),
            'platform_reviews': self._extract_platform_reviews(sections, images, affiliate_links),
            'howto_steps': self._extract_howto_sections(sections),
            'additional_content': self._extract_additional_content(sections),
            'responsible_gambling': self._extract_responsible_gambling(sections),
            'conclusion': self._extract_conclusion(sections),
            'faqs': self._extract_faqs(sections),
            'references': self._extract_references(sections)
        }

        return content_map

    def _build_section(self, section_name: str, content_map: Dict, document: Dict) -> str:
        """Build individual section HTML"""

        section_def = self.structure_config['section_definitions'].get(section_name, {})

        # Check if section is required or has content
        if not section_def:
            return ''

        # Route to specific section builder
        builder_method = f'_build_{section_name}_section'
        if hasattr(self, builder_method):
            return getattr(self, builder_method)(content_map, document)

        return ''

    def _build_article_header_section(self, content_map: Dict, document: Dict) -> str:
        """Build article header"""
        header_data = content_map.get('article_header', {})

        if not header_data:
            return ''

        h1_text = header_data.get('heading', '')
        h1_highlight = ''

        # Split heading for highlight (if contains |)
        if '|' in h1_text:
            parts = h1_text.split('|', 1)
            h1_text = parts[0].strip()
            h1_highlight = f' <span class="highlight">| {parts[1].strip()}</span>'

        # Generate intro paragraphs
        intro_paragraphs = ''
        paragraphs = header_data.get('intro_paragraphs', [])
        for para in paragraphs[:2]:  # First 2 paragraphs
            if para:
                intro_paragraphs += f'    <p class="intro">{self._escape_html(para)}</p>\n'

        data = {
            'h1_text': h1_text,
            'h1_highlight': h1_highlight,
            'intro_paragraphs': intro_paragraphs
        }

        return self.template_engine.render('components/article_header.html', data)

    def _build_elementor_placeholder_section(self, content_map: Dict, document: Dict) -> str:
        """Build elementor placeholder"""
        return '''<div>
    [elementor-template id="1128"]
</div>

'''

    def _build_quick_verdict_section(self, content_map: Dict, document: Dict) -> str:
        """Build quick verdict section"""
        platforms = content_map.get('quick_verdict_platforms', [])

        if not platforms:
            return ''

        verdict_cards = ''
        for platform in platforms:
            verdict_cards += self.template_engine.render_quick_verdict_card(platform)
            verdict_cards += '\n\n'

        data = {
            'title': 'Quick Verdict: Best Mobile Bitcoin Casinos for UK Players',
            'subtitle': 'After extensive testing, these platforms offer the best experience.',
            'datetime': '2025-11',
            'date_text': 'November 2025',
            'verdict_cards': verdict_cards
        }

        return self.template_engine.render('components/quick_verdict_section.html', data)

    def _build_comparison_table_section(self, content_map: Dict, document: Dict) -> str:
        """Build comparison table section"""
        table_data = content_map.get('comparison_table', {})

        if not table_data:
            return ''

        heading = table_data.get('heading', 'Platform Comparison')
        rows = table_data.get('data', [])

        if not rows:
            return ''

        html = f'<section class="content-section" id="comparison" aria-labelledby="comparison-heading">\n'
        html += f'    <h2 id="comparison-heading">{self._escape_html(heading)}</h2>\n'
        html += '    <div class="table-container">\n'
        html += '        <div class="table-responsive">\n'
        html += '            <table class="platform-table" aria-label="Comparison table">\n'

        # Table header
        html += '                <thead>\n'
        html += '                    <tr>\n'
        headers = list(rows[0].keys())
        for header in headers:
            html += f'                        <th scope="col">{self._escape_html(header)}</th>\n'
        html += '                    </tr>\n'
        html += '                </thead>\n'

        # Table body
        html += '                <tbody>\n'
        for row in rows:
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

    def _build_detailed_reviews_section(self, content_map: Dict, document: Dict) -> str:
        """Build detailed platform review cards"""
        reviews = content_map.get('platform_reviews', [])

        if not reviews:
            return ''

        html = '<section class="content-section" aria-labelledby="reviews-heading">\n'
        html += '    <h2 id="reviews-heading">Detailed Platform Reviews</h2>\n'
        html += '    <p class="lead">In-depth analysis of each platform with comprehensive feature breakdowns.</p>\n\n'

        for review in reviews:
            html += self.template_engine.render_platform_card(review)
            html += '\n\n'

        html += '</section>\n\n'

        return html

    def _build_faq_section(self, content_map: Dict, document: Dict) -> str:
        """Build FAQ section"""
        faqs = content_map.get('faqs', [])

        if not faqs:
            return ''

        html = '<section class="faq-section" aria-labelledby="faq-heading">\n'
        html += '    <h2 id="faq-heading">Frequently Asked Questions</h2>\n'
        html += '    <p class="lead">Common questions about mobile bitcoin casinos answered.</p>\n'
        html += '    <div class="faq-container">\n'

        for i, faq in enumerate(faqs, 1):
            html += self.template_engine.render_faq_item(faq, i)
            html += '\n'

        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _build_context_section_section(self, content_map: Dict, document: Dict) -> str:
        """Build initial context/understanding sections"""
        context_sections = content_map.get('context_sections', [])

        if not context_sections:
            return ''

        html = ''
        for section in context_sections:
            heading = section.get('heading', '')
            heading_id = self._slugify(heading)
            heading_escaped = self._escape_html(heading)

            html += f'<section class="content-section" aria-labelledby="{heading_id}">\n'
            html += f'    <h2 id="{heading_id}">{heading_escaped}</h2>\n'

            # Parse content into paragraphs and subsections
            content = section.get('content', '')
            html += self._render_content_paragraphs(content)

            html += '</section>\n\n'

        return html

    def _build_howto_guide_section(self, content_map: Dict, document: Dict) -> str:
        """Build how-to guide with steps"""
        howto_data = content_map.get('howto_steps', {})

        if not howto_data or not howto_data.get('steps'):
            return ''

        heading = howto_data.get('heading', 'Getting Started Guide')
        steps = howto_data.get('steps', [])

        html = '<section class="howto-section content-section" aria-labelledby="howto-heading">\n'
        html += f'    <h2 id="howto-heading">{self._escape_html(heading)}</h2>\n'
        html += '    <div class="howto-steps">\n'

        for i, step in enumerate(steps, 1):
            html += '        <div class="howto-step">\n'
            html += f'            <div class="step-number">{i}</div>\n'
            html += '            <div class="step-content">\n'
            html += f'                <h3 class="step-title">{self._escape_html(step.get("title", ""))}</h3>\n'
            html += f'                <p>{self._escape_html(step.get("content", ""))}</p>\n'
            html += '            </div>\n'
            html += '        </div>\n'

        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _build_additional_content_section(self, content_map: Dict, document: Dict) -> str:
        """Build additional content sections"""
        additional_sections = content_map.get('additional_content', [])

        if not additional_sections:
            return ''

        html = ''
        for section in additional_sections:
            heading = section.get('heading', '')
            heading_id = self._slugify(heading)
            heading_escaped = self._escape_html(heading)

            html += f'<section class="content-section" aria-labelledby="{heading_id}">\n'
            html += f'    <h2 id="{heading_id}">{heading_escaped}</h2>\n'

            # Parse content into paragraphs and subsections
            content = section.get('content', '')
            html += self._render_content_paragraphs(content)

            html += '</section>\n\n'

        return html

    def _build_responsible_gambling_section(self, content_map: Dict, document: Dict) -> str:
        """Build responsible gambling section"""
        rg_data = content_map.get('responsible_gambling', {})

        if not rg_data:
            return ''

        heading = rg_data.get('heading', 'Responsible Gambling')
        content = rg_data.get('content', '')

        html = '<section class="responsible-gambling content-section" aria-labelledby="responsible-gambling-heading">\n'
        html += f'    <h2 id="responsible-gambling-heading">{self._escape_html(heading)}</h2>\n'
        html += '    <div class="rg-content">\n'

        # Render content paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs:
            html += f'        <p>{self._escape_html(para)}</p>\n'

        html += '    </div>\n'
        html += '    <div class="rg-resources">\n'
        html += '        <p><strong>Need help?</strong></p>\n'
        html += '        <ul>\n'
        html += '            <li><a href="https://www.begambleaware.org" target="_blank" rel="noopener">BeGambleAware.org</a></li>\n'
        html += '            <li><a href="https://www.gamcare.org.uk" target="_blank" rel="noopener">GamCare.org.uk</a></li>\n'
        html += '            <li><a href="https://www.gamstop.co.uk" target="_blank" rel="noopener">GamStop (Self-Exclusion)</a></li>\n'
        html += '        </ul>\n'
        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _build_conclusion_section(self, content_map: Dict, document: Dict) -> str:
        """Build conclusion section"""
        conclusion_data = content_map.get('conclusion', {})

        if not conclusion_data:
            return ''

        heading = conclusion_data.get('heading', 'Conclusion')
        content = conclusion_data.get('content', '')

        html = '<section class="conclusion-section content-section" aria-labelledby="conclusion-heading">\n'
        html += f'    <h2 id="conclusion-heading">{self._escape_html(heading)}</h2>\n'

        # Render content paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        for para in paragraphs:
            html += f'    <p class="conclusion-text">{self._escape_html(para)}</p>\n'

        html += '</section>\n\n'

        return html

    def _build_references_section(self, content_map: Dict, document: Dict) -> str:
        """Build references section"""
        references = content_map.get('references', [])

        if not references:
            return ''

        html = '<section class="references-section content-section" aria-labelledby="references-heading">\n'
        html += '    <h2 id="references-heading">References</h2>\n'
        html += '    <ol class="references-list">\n'

        for ref in references:
            html += f'        <li>{self._escape_html(ref.get("text", ""))}</li>\n'

        html += '    </ol>\n'
        html += '</section>\n\n'

        return html

    def _render_content_paragraphs(self, content: str) -> str:
        """Render content with paragraphs and h3 subheadings"""
        html = ''
        lines = content.split('\n')

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if it's an h3 subheading
            if '(h3)' in line_stripped:
                heading_text = line_stripped.replace('(h3)', '').strip()
                html += f'    <h3>{self._escape_html(heading_text)}</h3>\n'
            else:
                # Regular paragraph
                html += f'    <p>{self._escape_html(line_stripped)}</p>\n'

        return html

    def _build_footer_section(self, content_map: Dict, document: Dict) -> str:
        """Build footer"""
        return '''<footer class="article-footer">
    <p><em>Last updated: November 2025 | All information verified at publication</em></p>
    <p><strong>18+ only. Gamble responsibly.</strong> BeGambleAware.org</p>
</footer>'''

    def _extract_article_header(self, sections: List[Dict]) -> Dict:
        """Extract article header data"""
        if not sections or sections[0].get('level') != 1:
            return {}

        first_section = sections[0]
        content = first_section.get('content', '')
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        return {
            'heading': first_section.get('heading', ''),
            'intro_paragraphs': paragraphs[:2]
        }

    def _extract_top_platforms(self, sections: List[Dict]) -> List[Dict]:
        """Extract top 3 platforms for quick verdict"""
        platforms = []

        for section in sections:
            if section.get('type') == 'comparison_table':
                table_data = section.get('table_data', [])
                for i, row in enumerate(table_data[:3], 1):
                    platform = {
                        'name': row.get('Casino', row.get('Platform', '')),
                        'featured': i == 1,
                        'category_label': 'Best Overall' if i == 1 else 'Top Pick',
                        'category_title': 'Top Pick' if i == 1 else f'Runner Up #{i}',
                        'logo_url': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(row.get("Casino", ""))}-logo.png',
                        'rating': 5 if i == 1 else 4.5,
                        'features': [
                            row.get('Mobile Platform', 'Mobile optimized'),
                            row.get('Welcome Bonus', 'Welcome bonus'),
                            row.get('Withdrawal Speed', 'Fast withdrawals')
                        ],
                        'badge': 'BEST OVERALL' if i == 1 else f'TOP {i}'
                    }
                    platforms.append(platform)
                break

        return platforms

    def _extract_comparison_table(self, sections: List[Dict]) -> Dict:
        """Extract main comparison table"""
        for section in sections:
            if section.get('type') == 'comparison_table':
                return {
                    'heading': section.get('heading', 'Comparison Table'),
                    'data': section.get('table_data', [])
                }
        return {}

    def _extract_platform_reviews(self, sections: List[Dict], images: Dict, affiliate_links: Dict) -> List[Dict]:
        """Extract platform review data"""
        reviews = []

        for section in sections:
            if section.get('type') == 'platform_review':
                review_data = section.get('review_data', {})
                platform_name = review_data.get('platform_name', '')

                review = {
                    'name': platform_name,
                    'tagline': review_data.get('tagline', ''),
                    'rating': 5.0,
                    'logo_url': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(platform_name)}-logo.png',
                    'header_image': f'https://b3i.tech/wp-content/uploads/2025/11/{self._slugify(platform_name)}-header.webp',
                    'affiliate_link': f'https://b3i.tech/visit/casino/{self._slugify(platform_name)}',
                    'cta_note': 'Fast withdrawals • Secure platform • Great bonuses',
                    'stats': [
                        {'label': 'License', 'value': 'UKGC', 'highlight': True},
                        {'label': 'Min Deposit', 'value': '£10'},
                        {'label': 'Withdrawal Time', 'value': '24hrs', 'highlight': True},
                        {'label': 'Support', 'value': '24/7'}
                    ],
                    'overview': f'<p>{review_data.get("intro", "")}</p>',
                    'bonuses': '<p>Comprehensive bonus information available.</p>',
                    'games': '<p>Extensive games library with top providers.</p>',
                    'pros': review_data.get('pros', []),
                    'cons': review_data.get('cons', [])
                }
                reviews.append(review)

        return reviews

    def _extract_faqs(self, sections: List[Dict]) -> List[Dict]:
        """Extract FAQ data"""
        faqs = []

        # Find the FAQ section header
        faq_index = None
        for i, section in enumerate(sections):
            if section.get('type') == 'faq_section':
                faq_index = i
                break

        if faq_index is None:
            return []

        # Collect all h3 sections that follow the FAQ h2 until next h2
        for i in range(faq_index + 1, len(sections)):
            section = sections[i]

            # Stop when we hit the next h2 section
            if section.get('level') == 2:
                break

            # Collect h3 sections as FAQ items
            if section.get('level') == 3:
                question = section.get('heading', '')
                answer = section.get('content', '')

                if question:
                    faqs.append({
                        'question': question,
                        'answer': f'<p>{self._escape_html(answer)}</p>'
                    })

        return faqs

    def _parse_faqs(self, content: str) -> List[Dict]:
        """Parse FAQ content into Q&A pairs"""
        faqs = []
        lines = content.split('\n')
        current_question = None
        current_answer = []

        for line in lines:
            line_stripped = line.strip()

            if '?' in line_stripped and not line_stripped.startswith('•'):
                if current_question:
                    faqs.append({
                        'question': current_question.replace('(h3)', '').strip(),
                        'answer': '<p>' + ' '.join(current_answer) + '</p>'
                    })

                current_question = line_stripped
                current_answer = []
            elif line_stripped and current_question:
                current_answer.append(line_stripped)

        if current_question:
            faqs.append({
                'question': current_question.replace('(h3)', '').strip(),
                'answer': '<p>' + ' '.join(current_answer) + '</p>'
            })

        return faqs

    def _extract_context_sections(self, sections: List[Dict]) -> List[Dict]:
        """Extract first 2-3 context sections after header"""
        context = []
        context_headings = [
            'What Makes a Mobile Bitcoin Casino Worth Using?',
            'Should You Use a Mobile Bitcoin Casino App or Browser?',
            'How Do Mobile Bitcoin Casino Transactions Work?'
        ]

        for section in sections:
            heading = section.get('heading', '')
            if any(ch in heading for ch in context_headings):
                context.append(section)
                if len(context) >= 3:
                    break

        return context

    def _extract_howto_sections(self, sections: List[Dict]) -> Dict:
        """Extract how-to guide section with steps"""
        for section in sections:
            heading = section.get('heading', '')
            if 'How Do You Start Playing' in heading or 'How to Start' in heading:
                content = section.get('content', '')
                return {
                    'heading': heading,
                    'steps': self._parse_howto_steps(content)
                }
        return {}

    def _parse_howto_steps(self, content: str) -> List[Dict]:
        """Parse step-by-step content"""
        steps = []
        lines = content.split('\n')
        current_step = None
        current_content = []

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('Step '):
                if current_step:
                    steps.append({
                        'title': current_step,
                        'content': ' '.join(current_content)
                    })
                # Extract step title
                current_step = line_stripped
                current_content = []
            elif line_stripped and current_step:
                current_content.append(line_stripped)

        if current_step:
            steps.append({
                'title': current_step,
                'content': ' '.join(current_content)
            })

        return steps

    def _extract_additional_content(self, sections: List[Dict]) -> List[Dict]:
        """Extract remaining content sections"""
        additional = []
        skip_headings = [
            'What Makes a Mobile Bitcoin Casino Worth Using?',
            'Should You Use a Mobile Bitcoin Casino App or Browser?',
            'How Do Mobile Bitcoin Casino Transactions Work?',
            'How Do You Start Playing',
            'How to Start',
            'Frequently Asked Questions',
            'Final Verdict',
            'FAQ'
        ]

        for section in sections:
            heading = section.get('heading', '')
            level = section.get('level', 2)

            # Only get h2 sections
            if level != 2:
                continue

            # Skip sections handled elsewhere
            if any(skip in heading for skip in skip_headings):
                continue

            # Skip platform reviews and comparison tables
            if section.get('type') in ['platform_review', 'comparison_table']:
                continue

            additional.append(section)

        return additional

    def _extract_responsible_gambling(self, sections: List[Dict]) -> Dict:
        """Extract responsible gambling content"""
        for section in sections:
            heading = section.get('heading', '')
            if 'responsible gambling' in heading.lower():
                return {
                    'heading': heading,
                    'content': section.get('content', '')
                }

            # Also check within content for responsible gambling mentions
            content = section.get('content', '')
            if 'responsible gambling tools' in content.lower():
                # Extract relevant paragraphs
                lines = content.split('\n')
                rg_content = []
                capture = False
                for line in lines:
                    if 'responsible gambling' in line.lower():
                        capture = True
                    if capture:
                        rg_content.append(line)

                if rg_content:
                    return {
                        'heading': 'Responsible Gambling',
                        'content': '\n'.join(rg_content)
                    }

        return {}

    def _extract_conclusion(self, sections: List[Dict]) -> Dict:
        """Extract conclusion section"""
        for section in sections:
            heading = section.get('heading', '')
            if 'Final Verdict' in heading or 'Conclusion' in heading:
                return {
                    'heading': heading,
                    'content': section.get('content', '')
                }
        return {}

    def _extract_references(self, sections: List[Dict]) -> List[Dict]:
        """Extract references section"""
        for section in sections:
            heading = section.get('heading', '')
            if 'Reference' in heading or 'Citation' in heading:
                content = section.get('content', '')
                # Parse numbered or bulleted list of references
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                return [{'text': line} for line in lines]
        return []

    def _assemble_page(self, document: Dict, sections_html: List[str]) -> str:
        """Assemble final page HTML"""
        metadata = document.get('metadata', {})

        # Build meta tags
        meta_tags = ''
        if metadata.get('meta_title'):
            meta_tags += f'    <title>{self._escape_html(metadata["meta_title"])}</title>\n'
        if metadata.get('meta_description'):
            meta_tags += f'    <meta name="description" content="{self._escape_html(metadata["meta_description"])}">\n'

        # Load JavaScript
        javascript = self.template_engine.load_template('components/javascript.html')

        # Assemble sections
        all_sections = '\n'.join(sections_html)

        # Build full page
        html = f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
{meta_tags}
    <link rel="stylesheet" href="Stylesheet.css">
</head>
<body>

<div class="crypto-betting-widget" id="main-content">
    <article>
{all_sections}
    </article>
</div>

{javascript}

</body>
</html>'''

        return html

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
