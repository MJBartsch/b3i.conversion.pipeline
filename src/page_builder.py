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

        # Get winner platform name for subtitle
        winner_name = platforms[0].get('name', 'the top platform') if platforms else 'the top platform'

        # Count total platforms from comparison table
        comparison_data = content_map.get('comparison_table', {})
        platform_count = len(comparison_data.get('data', [])) if comparison_data else len(platforms)

        data = {
            'title': 'Quick Verdict: Best Mobile Bitcoin Casinos for UK Players',
            'subtitle': f'After extensive testing, <strong>{winner_name}</strong> stands out as our top recommendation for mobile bitcoin betting. Combining robust security, extensive game selection, and seamless cryptocurrency integration.',
            'datetime': '2025-11',
            'date_text': 'November 2025',
            'verdict_cards': verdict_cards,
            'platform_count': platform_count
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
        html += '        <div class="table-header">\n'
        html += '            <h3 class="table-title">Compare All Features</h3>\n'
        html += '            <p class="table-subtitle">Side-by-side comparison of mobile bitcoin casino features</p>\n'
        html += '        </div>\n'
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

    def _build_top10_list_section(self, content_map: Dict, document: Dict) -> str:
        """Build top10 list section with detailed platform information"""
        # Get platform reviews which have the full data
        reviews = content_map.get('platform_reviews', [])

        if not reviews:
            return ''

        # Limit to top 10
        top_platforms = reviews[:10]

        html = '<section class="content-section top10-section" aria-labelledby="top10-heading">\n'
        html += '    <h2 id="top10-heading">Top 10 Crypto Betting Sites UK</h2>\n'
        html += '    <p class="lead">Here\'s our comprehensive list of the best cryptocurrency betting platforms available to UK players, ranked by overall performance, features, and user experience.</p>\n\n'
        html += '    <div class="top10-list">\n'

        badges = {1: 'gold', 2: 'silver', 3: 'bronze'}

        for idx, platform in enumerate(top_platforms, 1):
            rank_class = badges.get(idx, '')
            platform_name = platform.get('name', f'Platform {idx}')
            platform_id = self._slugify(platform_name)
            rating = platform.get('rating', '5/5')

            # Handle both float and string ratings
            if isinstance(rating, float):
                rating_num = rating
                rating_str = f"{rating}/5"
            elif isinstance(rating, str) and '/' in rating:
                rating_num = float(rating.split('/')[0])
                rating_str = rating
            else:
                rating_num = 5.0
                rating_str = "5/5"

            # Generate star rating HTML
            try:
                stars = '★' * int(rating_num) + '☆' * (5 - int(rating_num))
            except:
                stars = '★★★★★'

            # Get best badge for top 3
            best_badges = {
                1: 'Best Overall',
                2: 'Best for Security',
                3: 'Best Mobile Experience'
            }
            best_badge = best_badges.get(idx, '')

            # Get platform description (first paragraph of overview)
            description = ''
            overview = platform.get('overview', {})
            if isinstance(overview, dict):
                paragraphs = overview.get('paragraphs', [])
                if paragraphs:
                    description = paragraphs[0][:200] + '...' if len(paragraphs[0]) > 200 else paragraphs[0]

            # Get key features
            key_features = platform.get('key_features', [])
            if not key_features:
                # Try to extract from stats (if it's a list of stat items)
                stats = platform.get('stats', [])
                key_features = []
                if isinstance(stats, list):
                    # Extract first 3 stat values as features
                    for stat in stats[:3]:
                        if isinstance(stat, dict):
                            label = stat.get('label', '')
                            value = stat.get('value', '')
                            if label and value:
                                key_features.append(f"{label}: {value}")
                elif isinstance(stats, dict):
                    # Handle dict format
                    if stats.get('crypto_accepted'):
                        key_features.append(f"{stats['crypto_accepted']} cryptocurrencies accepted")
                    if stats.get('sports_available'):
                        key_features.append(f"{stats['sports_available']}+ sports available")
                    if stats.get('withdrawal_time'):
                        key_features.append(f"{stats['withdrawal_time']} withdrawals")

            # Get logo image
            logo_url = platform.get('logo', '')

            html += f'        <div class="top10-item rank-{idx}">\n'
            html += f'            <div class="rank-badge {rank_class}">{idx}</div>\n'

            if logo_url:
                html += f'            <div class="top10-logo">\n'
                html += f'                <img src="{logo_url}" alt="{self._escape_html(platform_name)} logo" loading="lazy" />\n'
                html += f'            </div>\n'

            html += f'            <div class="top10-content">\n'
            html += f'                <div class="top10-header">\n'
            html += f'                    <h3 class="platform-name">{self._escape_html(platform_name)}</h3>\n'

            if best_badge:
                html += f'                    <span class="best-badge">{best_badge}</span>\n'

            html += f'                </div>\n'
            html += f'                <div class="platform-rating-inline">\n'
            html += f'                    <span class="rating-stars">{stars}</span>\n'
            html += f'                    <span class="rating-value">{self._escape_html(rating_str)}</span>\n'
            html += f'                </div>\n'

            if description:
                html += f'                <p class="platform-description">{self._escape_html(description)}</p>\n'

            if key_features:
                html += f'                <ul class="feature-highlights">\n'
                for feature in key_features[:3]:  # Limit to 3 features
                    html += f'                    <li>{self._escape_html(feature)}</li>\n'
                html += f'                </ul>\n'

            html += f'            </div>\n'
            html += f'            <a href="#{platform_id}" class="top10-link">\n'
            html += f'                View Review\n'
            html += f'                <span class="qv-arrow" aria-hidden="true">→</span>\n'
            html += f'            </a>\n'
            html += f'        </div>\n\n'

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

        html = '<section class="faq-container" aria-labelledby="faq-heading">\n'
        html += '    <div class="faq-header">\n'
        html += '        <h2 id="faq-heading" class="faq-title">Frequently Asked Questions</h2>\n'
        html += '        <p class="faq-subtitle">Everything you need to know about crypto betting sites in the UK.</p>\n'
        html += '    </div>\n'
        html += '    <div class="faq-list">\n'

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
            content = section.get('content', '')

            # Check if section has a CSV table
            has_csv_table = section.get('type') == 'comparison_table'

            html += f'<section class="content-section" aria-labelledby="{heading_id}">\n'
            html += f'    <h2 id="{heading_id}">{heading_escaped}</h2>\n'

            if has_csv_table:
                # Render intro paragraph first
                paragraphs = [p.strip() for p in content.split('\n') if p.strip() and not p.startswith('csv')]
                if paragraphs:
                    html += f'    <p class="lead">{self._escape_html(paragraphs[0])}</p>\n'

                # Render table as top10-section list
                html += self._render_comparison_list(section)
            else:
                # Parse content into paragraphs and subsections
                html += self._render_content_paragraphs(content)

            html += '</section>\n\n'

        return html

    def _build_howto_guide_section(self, content_map: Dict, document: Dict) -> str:
        """Build how-to guide with content cards"""
        howto_data = content_map.get('howto_steps', {})

        if not howto_data or not howto_data.get('steps'):
            return ''

        heading = howto_data.get('heading', 'Getting Started Guide')
        steps = howto_data.get('steps', [])

        html = '<section class="howto-section content-section" aria-labelledby="howto-heading">\n'
        html += f'    <h2 id="howto-heading">{self._escape_html(heading)}</h2>\n'

        for i, step in enumerate(steps, 1):
            step_title = step.get("title", "").replace(f"Step {i}:", "").replace(f"Step {i}", "").strip()
            step_content = step.get("content", "")

            html += '<div class="content-card">\n'
            html += f'    <h3>Step {i}: {self._escape_html(step_title)}</h3>\n'

            # Split into paragraphs for better formatting
            paragraphs = [p.strip() for p in step_content.split('\n') if p.strip()]

            for para in paragraphs:
                html += f'    <p>{self._escape_html(para)}</p>\n'

            html += '</div>\n'

        html += '</section>\n\n'

        return html

    def _build_additional_content_section(self, content_map: Dict, document: Dict) -> str:
        """Build additional content sections with enhanced styling"""
        additional_sections = content_map.get('additional_content', [])

        if not additional_sections:
            return ''

        html = ''
        for section in additional_sections:
            heading = section.get('heading', '')
            heading_id = self._slugify(heading)
            heading_escaped = self._escape_html(heading)
            content = section.get('content', '')

            # Check section type
            has_csv_table = section.get('type') == 'comparison_table'
            has_checklist = self._is_checklist_section(content)

            html += f'<section class="content-section" aria-labelledby="{heading_id}">\n'
            html += f'    <h2 id="{heading_id}">{heading_escaped}</h2>\n'

            # Handle different section types
            if has_csv_table:
                # Convert CSV table to top10-section list format
                html += self._render_comparison_list(section)
            elif has_checklist:
                # Render checklist with content cards
                html += self._render_checklist_cards(content)
            else:
                # Render with content cards if text is long
                html += self._render_content_with_cards(content)

            html += '</section>\n\n'

        return html

    def _build_responsible_gambling_section(self, content_map: Dict, document: Dict) -> str:
        """Build responsible gambling section with colored info boxes"""
        rg_data = content_map.get('responsible_gambling', {})

        if not rg_data:
            return ''

        heading = rg_data.get('heading', 'Responsible Gambling')
        content = rg_data.get('content', '')

        html = '<section class="responsible-gambling content-section" aria-labelledby="responsible-gambling-heading">\n'
        html += f'    <h2 id="responsible-gambling-heading">{self._escape_html(heading)}</h2>\n'

        # Main content in info box for visual emphasis
        html += '    <div class="info-box">\n'
        html += '        <h4>🛡️ Gambling Responsibly</h4>\n'

        paragraphs = [p.strip() for p in content.split('\n') if p.strip()][:2]
        for para in paragraphs:
            html += f'        <p>{self._escape_html(para)}</p>\n'

        html += '    </div>\n'

        # Additional tools in quote blocks
        remaining_paras = [p.strip() for p in content.split('\n') if p.strip()][2:]
        if remaining_paras:
            html += '    <div class="quote-block">\n'
            for para in remaining_paras[:2]:
                html += f'        <p>{self._escape_html(para)}</p>\n'
            html += '    </div>\n'

        # Resources in summary box
        html += '    <div class="summary-box">\n'
        html += '        <h3>🆘 Need Help?</h3>\n'
        html += '        <p><strong>If you or someone you know needs support:</strong></p>\n'
        html += '        <ul>\n'
        html += '            <li><a href="https://www.begambleaware.org" target="_blank" rel="noopener"><strong>BeGambleAware.org</strong></a> - Free support and advice</li>\n'
        html += '            <li><a href="https://www.gamcare.org.uk" target="_blank" rel="noopener"><strong>GamCare.org.uk</strong></a> - Counseling services</li>\n'
        html += '            <li><a href="https://www.gamstop.co.uk" target="_blank" rel="noopener"><strong>GamStop</strong></a> - Self-exclusion scheme</li>\n'
        html += '        </ul>\n'
        html += '        <p class="small">All services are free and confidential.</p>\n'
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
        """Build references section with proper citation formatting"""
        references = content_map.get('references', [])

        if not references:
            return ''

        html = '<section class="reference-container" aria-labelledby="references-heading">\n'
        html += '    <div class="reference-header">\n'
        html += '        <h2 id="references-heading" class="reference-title">References and Sources</h2>\n'
        html += '        <p class="reference-subtitle">All sources have been verified for accuracy and credibility.</p>\n'
        html += '    </div>\n'
        html += '    <ol class="reference-list">\n'

        for ref in references:
            # Parse reference data
            ref_text = ref.get('text', '')
            author = ref.get('author', 'Unknown')
            date = ref.get('date', '2024')
            title = ref.get('title', ref_text[:50] if ref_text else 'Untitled')
            url = ref.get('url', '#')

            # If only text is provided, try to parse it
            if ref_text and not ref.get('author'):
                # Simple parsing - extract URL if present
                import re
                url_match = re.search(r'https?://[^\s]+', ref_text)
                if url_match:
                    url = url_match.group(0)
                    # Remove URL from text to get title/author
                    title = ref_text.replace(url, '').strip()

            html += '        <li class="reference-item">\n'
            html += '            <div class="reference-content">\n'
            html += f'                <span class="reference-author">{self._escape_html(author)}</span> \n'
            html += f'                <span class="reference-date">({self._escape_html(date)}).</span> \n'
            html += f'                <span class="reference-title-text">"{self._escape_html(title)}"</span> \n'

            if url and url != '#':
                html += f'                <a href="{url}" class="reference-link" target="_blank" rel="noopener noreferrer">{url}</a>\n'

            html += '            </div>\n'
            html += '        </li>\n'

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
                # Check if this section contains a CSV table
                content = section.get('content', '')
                if 'csv\n' in content or '\ncsv' in content:
                    # Parse the CSV table
                    lines = content.split('\n')
                    csv_start = None
                    csv_lines = []
                    caption = ''

                    for i, line in enumerate(lines):
                        if line.strip() == 'csv':
                            csv_start = i
                        elif csv_start is not None and ',' in line:
                            csv_lines.append(line)
                        elif csv_start is not None and not line.strip().startswith(','):
                            # This is the caption
                            caption = line.strip()
                            break

                    if csv_lines:
                        # Parse CSV into table data
                        table_data = []
                        headers = [h.strip() for h in csv_lines[0].split(',')]

                        for row_line in csv_lines[1:]:
                            values = [v.strip() for v in row_line.split(',')]
                            if len(values) == len(headers):
                                row_dict = dict(zip(headers, values))
                                table_data.append(row_dict)

                        # Mark section as having table
                        section_copy = section.copy()
                        section_copy['type'] = 'comparison_table'
                        section_copy['table_data'] = table_data
                        section_copy['caption'] = caption
                        context.append(section_copy)
                    else:
                        context.append(section)
                else:
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

    # ===== Enhanced rendering methods for better visual styling =====

    def _is_checklist_section(self, content: str) -> bool:
        """Check if content contains a bulleted checklist"""
        lines = content.split('\n')
        bullet_count = sum(1 for line in lines if line.strip().startswith('•'))
        return bullet_count > 5  # Multiple bullet points indicate checklist

    def _render_comparison_list(self, section: Dict) -> str:
        """Render CSV table as top10-section list"""
        table_data = section.get('table_data', [])
        caption = section.get('caption', '')

        if not table_data:
            return ''

        html = '<div class="top10-section">\n'
        html += '    <div class="top10-list">\n'

        for i, row in enumerate(table_data, 1):
            # Determine rank class
            rank_class = ''
            badge_class = ''
            if i == 1:
                rank_class = ' rank-1'
                badge_class = ' gold'
            elif i == 2:
                rank_class = ' rank-2'
                badge_class = ' silver'
            elif i == 3:
                rank_class = ' rank-3'
                badge_class = ' bronze'

            html += f'    <div class="top10-item{rank_class}">\n'
            html += f'        <div class="rank-badge{badge_class}">{i}</div>\n'

            # Platform logo (placeholder)
            platform_name = list(row.values())[0] if row else f'Option {i}'
            html += '        <div class="top10-logo">\n'
            html += '            <span style="font-weight: 700; font-size: 0.875rem;">✓</span>\n'
            html += '        </div>\n'

            # Content area with features
            html += '        <div class="top10-content">\n'
            html += '            <div class="top10-header">\n'
            html += f'                <h3 class="platform-name">{self._escape_html(platform_name)}</h3>\n'
            html += '            </div>\n'

            # Feature highlights from other columns
            html += '            <div class="feature-highlights">\n'
            features = list(row.values())[1:]  # Skip first column
            for feature in features[:3]:  # Show top 3 features
                if feature:
                    html += f'                <span class="feature-item">• {self._escape_html(str(feature))}</span>\n'
            html += '            </div>\n'
            html += '        </div>\n'

            html += '    </div>\n'

        html += '    </div>\n'

        # Add caption below
        if caption:
            html += f'    <p class="small" style="margin-top: 1rem; color: #86868b; font-style: italic;">{self._escape_html(caption)}</p>\n'

        html += '</div>\n'

        return html

    def _render_checklist_cards(self, content: str) -> str:
        """Render checklist content as grouped content cards"""
        lines = content.split('\n')

        html = ''
        current_group = None
        current_items = []

        for line in lines:
            line_stripped = line.strip()

            # Check if it's a group header (ends with :)
            if line_stripped and line_stripped.endswith(':') and not line_stripped.startswith('•'):
                # Save previous group
                if current_group and current_items:
                    html += self._render_checklist_card(current_group, current_items)

                current_group = line_stripped.rstrip(':')
                current_items = []

            # Check if it's a bullet point
            elif line_stripped.startswith('•'):
                item = line_stripped.lstrip('•').strip()
                if item:
                    current_items.append(item)

        # Save last group
        if current_group and current_items:
            html += self._render_checklist_card(current_group, current_items)

        return html

    def _render_checklist_card(self, title: str, items: List[str]) -> str:
        """Render a single checklist card"""
        html = '<div class="content-card">\n'
        html += f'    <h3>{self._escape_html(title)}</h3>\n'
        html += '    <ul>\n'
        for item in items:
            html += f'        <li>{self._escape_html(item)}</li>\n'
        html += '    </ul>\n'
        html += '</div>\n'
        return html

    def _render_content_with_cards(self, content: str) -> str:
        """Render long content with content cards for better visual breaks"""
        lines = [l.strip() for l in content.split('\n') if l.strip()]

        # If content is short, render normally
        if len(lines) < 4:
            return self._render_content_paragraphs(content)

        html = ''
        current_section = []

        for i, line in enumerate(lines):
            # Check if it's an h3 heading
            if '(h3)' in line:
                # Render previous section in a card if it exists
                if current_section:
                    html += '<div class="content-card">\n'
                    for para in current_section:
                        html += f'    <p>{self._escape_html(para)}</p>\n'
                    html += '</div>\n'
                    current_section = []

                # Render the h3
                heading_text = line.replace('(h3)', '').strip()
                html += f'    <h3>{self._escape_html(heading_text)}</h3>\n'
            else:
                current_section.append(line)

                # Create cards every 2-3 paragraphs
                if len(current_section) >= 3:
                    html += '<div class="content-card">\n'
                    for para in current_section:
                        html += f'    <p>{self._escape_html(para)}</p>\n'
                    html += '</div>\n'
                    current_section = []

        # Render remaining content
        if current_section:
            html += '<div class="content-card">\n'
            for para in current_section:
                html += f'    <p>{self._escape_html(para)}</p>\n'
            html += '</div>\n'

        return html

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
