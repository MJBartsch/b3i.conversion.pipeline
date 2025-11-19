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

    def build_page(self, document: Dict[str, Any],
                   images: Dict = None,
                   affiliate_links: Dict = None) -> str:
        """Build a page, auto-detecting the page type"""
        page_type = self._detect_page_type(document)

        if page_type == 'single_casino_review':
            return self.build_single_casino_review_page(document, images, affiliate_links)
        else:
            return self.build_platform_comparison_page(document, images, affiliate_links)

    def _detect_page_type(self, document: Dict[str, Any]) -> str:
        """Detect whether this is a comparison page or single casino review"""
        sections = document.get('sections', [])

        # Check for comparison table or multiple platform reviews
        has_comparison = any(s.get('type') == 'comparison_table' for s in sections)
        platform_count = sum(1 for s in sections if s.get('type') == 'platform_review')

        # If multiple platforms or comparison table, it's a comparison page
        if has_comparison or platform_count > 1:
            return 'platform_comparison'

        return 'single_casino_review'

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

    def build_single_casino_review_page(self, document: Dict[str, Any],
                                        images: Dict = None,
                                        affiliate_links: Dict = None) -> str:
        """Build a single casino review page"""

        page_type = 'single_casino_review'
        section_order = self.structure_config['page_types'][page_type]['section_order']

        # Extract and organize content
        content_map = self._map_single_review_content(document, images, affiliate_links)

        # Build page sections in order
        sections_html = []
        for section_name in section_order:
            section_html = self._build_section(section_name, content_map, document)
            if section_html:
                sections_html.append(section_html)

        # Assemble final page
        return self._assemble_page(document, sections_html)

    def _map_single_review_content(self, document: Dict, images: Dict, affiliate_links: Dict) -> Dict:
        """Map content for single casino review"""

        metadata = document.get('metadata', {})
        sections = document.get('sections', [])

        # Extract casino info including pros/cons
        casino_info = self._extract_casino_info(sections)
        casino_info.update(self._extract_pros_cons(sections))

        content_map = {
            'metadata': metadata,
            'article_header': self._extract_article_header(sections),
            'casino_info': casino_info,
            'tab_content': self._extract_tab_content(sections),
            'content_sections': sections,  # All sections for flexible rendering
            'faqs': self._extract_faqs(sections),
            'references': self._extract_references(sections),
            'images': images or {},  # Store images dictionary for lookups
            'affiliate_links': affiliate_links or {}  # Store affiliate links
        }

        return content_map

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
                        'answer': answer  # Don't add <p> tags here, let renderer handle it
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

    def _extract_casino_info(self, sections: List[Dict]) -> Dict:
        """Extract basic casino information from early sections"""
        casino_info = {
            'name': '',
            'rating': '0/10',
            'pros': [],
            'cons': []
        }

        # Try to extract casino name from title
        if sections and sections[0].get('level') == 1:
            title = sections[0].get('heading', '')
            # Extract casino name from patterns like "Is Casumo Worth It" or "888 Casino Review"
            import re

            # Try pattern "Is X Worth It"
            worth_match = re.search(r'Is\s+([A-Z][a-zA-Z0-9\s]+?)\s+Worth', title)
            if worth_match:
                casino_info['name'] = worth_match.group(1).strip()
            # Try pattern "X Review 2025"
            elif 'Review' in title:
                casino_info['name'] = re.sub(r'\s+Review.*', '', title).strip()
                casino_info['name'] = re.sub(r'\s+\d{4}.*', '', casino_info['name']).strip()

        # Look for rating in early sections
        for section in sections[:10]:
            content = section.get('content', '')
            heading = section.get('heading', '')

            # Look for rating pattern like "Overall: 3.6/5" or "6.9/10"
            import re
            rating_match = re.search(r'Overall[:\s]+(\d+\.?\d*)/(\d+)', content + ' ' + heading, re.IGNORECASE)
            if rating_match:
                score = rating_match.group(1)
                total = rating_match.group(2)
                casino_info['rating'] = f"{score}/{total}"
                break

        return casino_info

    def _extract_pros_cons(self, sections: List[Dict]) -> Dict:
        """Extract pros and cons from the pros/cons section"""
        pros = []
        cons = []

        for section in sections:
            heading = section.get('heading', '')
            content = section.get('content', '')

            # Look for pros/cons table
            if ('Pros' in heading and 'Cons' in heading) or 'Pros and Cons' in heading:
                # Check if it's a tab-delimited table
                if '\t' in content:
                    lines = [l.strip() for l in content.split('\n') if l.strip() and '\t' in l]
                    for line in lines[1:]:  # Skip header
                        columns = [c.strip() for c in line.split('\t')]
                        if len(columns) >= 2:
                            if columns[0]:
                                pros.append(columns[0])
                            if columns[1]:
                                cons.append(columns[1])
                break

        return {'pros': pros, 'cons': cons}

    def _extract_tab_content(self, sections: List[Dict]) -> Dict:
        """Extract content for platform card tabs"""
        tab_content = {
            'overview': '',
            'bonuses': '',
            'games': '',
        }

        overview_sections = []
        bonus_sections = []
        game_sections = []

        for section in sections:
            heading = section.get('heading', '').lower()
            content = section.get('content', '')
            level = section.get('level', 2)

            # Skip very early sections (header) and late sections (FAQ, references)
            if level == 1 or any(skip in heading for skip in ['faq', 'frequentlyasked', 'reference', 'citation']):
                continue

            # Skip if content is empty or has tables
            if not content or '\t' in content:
                continue

            # If content has image metadata, extract text before the metadata
            if self._has_image_metadata(content):
                # Split by image metadata markers
                parts = content.split('Alt Text:')
                if parts and len(parts[0].strip()) > 50:
                    content = parts[0].strip()
                else:
                    continue

            # Clean the content - remove separator lines and extra whitespace
            content = content.replace('________________________________________', '').strip()

            # Skip if content is too short after cleaning
            if len(content) < 50:
                continue

            # Overview content - early general sections
            if any(keyword in heading for keyword in ['safe', 'legit', 'license', 'overview', 'about']):
                overview_sections.append(content)

            # Bonus content
            elif any(keyword in heading for keyword in ['bonus', 'welcome', 'promotion', 'offer', 'wagering']):
                # Skip sports betting sections in bonuses
                if 'sport' not in heading:
                    bonus_sections.append(content)

            # Game content
            elif any(keyword in heading for keyword in ['game', 'slot', 'live', 'rtp', 'provider', 'software']):
                # Skip FAQ sections about games
                if 'can i play' not in heading and 'for free' not in heading:
                    game_sections.append(content)

        # Combine sections into tab content with cleaned text
        if overview_sections:
            tab_content['overview'] = '<p>' + '</p>\n<p>'.join(overview_sections[:3]) + '</p>'  # First 3 sections

        if bonus_sections:
            tab_content['bonuses'] = '<p>' + '</p>\n<p>'.join(bonus_sections[:3]) + '</p>'

        if game_sections:
            tab_content['games'] = '<p>' + '</p>\n<p>'.join(game_sections[:3]) + '</p>'

        return tab_content

    # ===== Single Casino Review Section Builders =====

    def _build_single_quick_verdict_section(self, content_map: Dict, document: Dict) -> str:
        """Build quick verdict for single casino review with 3 category cards"""
        casino_info = content_map.get('casino_info', {})
        casino_name = casino_info.get('name', 'This Casino')
        rating = casino_info.get('rating', '0/10')
        platform_id = self._slugify(casino_name)

        # Extract rating details
        try:
            rating_num = float(rating.split('/')[0])
            total_stars = int(rating.split('/')[1])
        except:
            rating_num = 0
            total_stars = 10

        # Generate star rating with half stars
        full_stars = int(rating_num)
        has_half = (rating_num - full_stars) >= 0.5
        empty_stars = total_stars - full_stars - (1 if has_half else 0)

        stars_html = ''
        for i in range(full_stars):
            stars_html += '<span class="star" aria-hidden="true">★</span>'
        if has_half:
            stars_html += '<span class="star half" aria-hidden="true">★</span>'
        for i in range(empty_stars):
            stars_html += '<span class="star empty" aria-hidden="true">☆</span>'

        # Get pros for feature list
        pros = casino_info.get('pros', [])
        top_features = pros[:4] if pros else ['Licensed & Regulated', 'Secure Gaming', 'Fair Play Certified']

        html = '<section class="quick-verdict">\n'
        html += '    <div class="qv-header">\n'
        html += f'        <h2 class="qv-title">Quick Answer: Is {self._escape_html(casino_name)} Safe and Legit?</h2>\n'
        html += f'        <p class="qv-subtitle">Yes, {self._escape_html(casino_name)} operates under verified licensing, but earns <strong>{self._escape_html(rating)}</strong> overall.</p>\n'
        html += '        <div class="qv-updated">Last updated: <time datetime="2025-11">November 2025</time></div>\n'
        html += '    </div>\n\n'

        # Three category cards
        html += '    <div class="qv-categories">\n'

        # Card 1: Overall Rating (Featured)
        html += '        <div class="qv-category featured">\n'
        html += '            <div class="qv-category-header">\n'
        html += '                <span class="qv-category-label">Overall Rating</span>\n'
        html += '                <h3 class="qv-category-title">Our Verdict</h3>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-body">\n'
        html += '                <div class="qv-platform-logo">\n'
        # Get logo image from content_map
        images = content_map.get('images', {})
        logo_img = self._get_image_html(images, f'{platform_id}-logo.png', width=90, height=90, loading='eager')
        if '<img' in logo_img:
            # Add title attribute
            logo_img = logo_img.replace('<img', f'<img title="{self._escape_html(casino_name)}"')
        html += f'                    {logo_img}\n'
        html += '                </div>\n'
        html += '                <div class="qv-winner-link">\n'
        html += f'                    <h3 class="qv-winner-name" style="margin-top: 0;">\n'
        html += f'                        {self._escape_html(casino_name)}\n'
        html += '                        <div class="qv-winner-rating">\n'
        html += f'                            <span class="qv-rating-stars" role="img" aria-label="{self._escape_html(rating)} stars">\n'
        html += f'                                {stars_html}\n'
        html += '                            </span>\n'
        html += f'                            <span class="rating-value" aria-hidden="true">{self._escape_html(rating)}</span>\n'
        html += '                        </div>\n'
        html += '                    </h3>\n'
        html += '                    <ul class="qv-winner-features">\n'
        for feature in top_features:
            html += f'                        <li>{self._escape_html(feature)}</li>\n'
        html += '                    </ul>\n'

        # Badge based on rating
        if rating_num >= 8:
            badge_text = 'EXCELLENT'
            badge_color = '#28a745'
        elif rating_num >= 6:
            badge_text = 'GOOD'
            badge_color = '#17a2b8'
        elif rating_num >= 4:
            badge_text = 'MIXED REVIEWS'
            badge_color = '#dc3545'
        else:
            badge_text = 'BELOW AVERAGE'
            badge_color = '#dc3545'

        html += f'                    <span class="qv-highlight-badge" style="background-color: {badge_color};">{badge_text}</span>\n'
        html += '                </div>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-footer">\n'
        html += '                <a href="#detailed-review" class="qv-view-details" aria-label="View full detailed review">\n'
        html += '                    Read Full Review\n'
        html += '                    <span class="qv-arrow" aria-hidden="true">↓</span>\n'
        html += '                </a>\n'
        html += '            </div>\n'
        html += '        </div>\n\n'

        # Card 2: Top Concern - User Reviews
        html += '        <div class="qv-category">\n'
        html += '            <div class="qv-category-header">\n'
        html += '                <span class="qv-category-label">Top Concern</span>\n'
        html += '                <h3 class="qv-category-title">User Reviews</h3>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-body">\n'
        html += '                <div class="qv-platform-logo">\n'
        html += '                    <span style="font-size: 48px;" aria-hidden="true">⚠️</span>\n'
        html += '                </div>\n'
        html += '                <div class="qv-winner-link">\n'
        html += '                    <h3 class="qv-winner-name" style="margin-top: 0;">\n'
        html += '                        Customer Feedback\n'
        html += '                        <div class="qv-winner-rating">\n'
        html += '                            <span class="qv-rating-stars" role="img" aria-label="User rating">\n'
        html += '                                <span class="star" aria-hidden="true">★</span><span class="star" aria-hidden="true">★</span><span class="star empty" aria-hidden="true">☆</span><span class="star empty" aria-hidden="true">☆</span><span class="star empty" aria-hidden="true">☆</span>\n'
        html += '                            </span>\n'
        html += '                            <span class="rating-value" aria-hidden="true">Mixed</span>\n'
        html += '                        </div>\n'
        html += '                    </h3>\n'
        html += '                    <ul class="qv-winner-features">\n'
        html += '                        <li>User reviews vary</li>\n'
        html += '                        <li>Verify current status</li>\n'
        html += '                        <li>Check recent feedback</li>\n'
        html += '                    </ul>\n'
        html += '                    <span class="qv-highlight-badge" style="background-color: #ffc107;">CHECK REVIEWS</span>\n'
        html += '                </div>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-footer">\n'
        html += '                <a href="#user-reviews" class="qv-view-details" aria-label="View user reviews section">\n'
        html += '                    View Reviews\n'
        html += '                    <span class="qv-arrow" aria-hidden="true">→</span>\n'
        html += '                </a>\n'
        html += '            </div>\n'
        html += '        </div>\n\n'

        # Card 3: Best Feature - Game Selection
        html += '        <div class="qv-category">\n'
        html += '            <div class="qv-category-header">\n'
        html += '                <span class="qv-category-label">Best Feature</span>\n'
        html += '                <h3 class="qv-category-title">Game Selection</h3>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-body">\n'
        html += '                <div class="qv-platform-logo">\n'
        html += '                    <span style="font-size: 48px;" aria-hidden="true">🎰</span>\n'
        html += '                </div>\n'
        html += '                <div class="qv-winner-link">\n'
        html += '                    <h3 class="qv-winner-name" style="margin-top: 0;">\n'
        html += '                        Wide Selection\n'
        html += '                        <div class="qv-winner-rating">\n'
        html += '                            <span class="qv-rating-stars" role="img" aria-label="5 out of 5 stars">\n'
        html += '                                <span class="star" aria-hidden="true">★</span><span class="star" aria-hidden="true">★</span><span class="star" aria-hidden="true">★</span><span class="star" aria-hidden="true">★</span><span class="star" aria-hidden="true">★</span>\n'
        html += '                            </span>\n'
        html += '                            <span class="rating-value" aria-hidden="true">5/5</span>\n'
        html += '                        </div>\n'
        html += '                    </h3>\n'
        html += '                    <ul class="qv-winner-features">\n'
        html += '                        <li>Extensive game library</li>\n'
        html += '                        <li>Top providers</li>\n'
        html += '                        <li>Regular updates</li>\n'
        html += '                    </ul>\n'
        html += '                    <span class="qv-highlight-badge">EXCELLENT</span>\n'
        html += '                </div>\n'
        html += '            </div>\n'
        html += '            <div class="qv-category-footer">\n'
        html += '                <a href="#games" class="qv-view-details" aria-label="View games section">\n'
        html += '                    View Games\n'
        html += '                    <span class="qv-arrow" aria-hidden="true">→</span>\n'
        html += '                </a>\n'
        html += '            </div>\n'
        html += '        </div>\n'
        html += '    </div>\n\n'

        # Trust signals
        html += '    <div class="qv-trust-signals">\n'
        html += '        <div class="qv-trust-item">\n'
        html += '            <span class="qv-trust-icon" aria-hidden="true">✓</span>\n'
        html += '            Licensed & Regulated\n'
        html += '        </div>\n'
        html += '        <div class="qv-trust-item">\n'
        html += '            <span class="qv-trust-icon" aria-hidden="true">✓</span>\n'
        html += '            Secure Gaming\n'
        html += '        </div>\n'
        html += '        <div class="qv-trust-item">\n'
        html += '            <span class="qv-trust-icon" aria-hidden="true">✓</span>\n'
        html += '            Fair Play Certified\n'
        html += '        </div>\n'
        html += '        <div class="qv-trust-item">\n'
        html += '            <span class="qv-trust-icon" aria-hidden="true">✓</span>\n'
        html += '            Responsible Gambling\n'
        html += '        </div>\n'
        html += '    </div>\n'
        html += '</section>\n\n'

        return html

    def _build_single_platform_card_section(self, content_map: Dict, document: Dict) -> str:
        """Build single platform card with enhanced tabs"""
        casino_info = content_map.get('casino_info', {})
        casino_name = casino_info.get('name', 'Casino')
        rating = casino_info.get('rating', '0/10')
        platform_id = self._slugify(casino_name)

        # Get tab content, pros/cons, and images
        tab_content = content_map.get('tab_content', {})
        pros = casino_info.get('pros', [])
        cons = casino_info.get('cons', [])
        images = content_map.get('images', {})

        # Extract rating number for stars
        try:
            rating_num = float(rating.split('/')[0])
            total_stars = int(rating.split('/')[1])
            stars = '★' * int(rating_num) + '☆' * (total_stars - int(rating_num))
        except:
            rating_num = 0
            total_stars = 10
            stars = '★★★★★☆☆☆☆☆'
            rating = '0/10'

        # Card header with banner image
        html = '<div class="platform-card" id="detailed-review">\n'
        banner_url = f'https://b3i.tech/wp-content/uploads/2025/11/{platform_id}-banner.jpg'
        html += f'    <div class="card-header" style="--bg-image: url(\'{banner_url}\'); background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url(\'{banner_url}\'); background-size: cover; background-position: center;">\n'
        html += f'        <div class="platform-rating"><span role="img" aria-label="{self._escape_html(rating)} stars">{stars}</span> {self._escape_html(rating)}</div>\n'
        html += '        <div class="header-content">\n'
        html += '            <div class="platform-logo">\n'
        logo_img = self._get_image_html(images, f'{platform_id}-logo.png', width=120, height=120, loading='lazy')
        if '<img' in logo_img:
            logo_img = logo_img.replace('<img', f'<img title="{self._escape_html(casino_name)}"')
        html += f'                {logo_img}\n'
        html += '            </div>\n'
        html += f'            <p class="platform-tagline">{self._escape_html(casino_name)} • Comprehensive Review</p>\n'
        html += '        </div>\n'
        html += '    </div>\n\n'

        # Stats bar with more details
        html += '    <div class="stats-bar">\n'
        html += '        <div class="stat-item">\n'
        html += '            <div class="stat-label">Founded</div>\n'
        html += '            <div class="stat-value highlight">2012</div>\n'
        html += '        </div>\n'
        html += '        <div class="stat-item">\n'
        html += '            <div class="stat-label">Total Games</div>\n'
        html += '            <div class="stat-value highlight">1,000+</div>\n'
        html += '        </div>\n'
        html += '        <div class="stat-item">\n'
        html += '            <div class="stat-label">Withdrawal Time</div>\n'
        html += '            <div class="stat-value">1-3 days</div>\n'
        html += '        </div>\n'
        html += '        <div class="stat-item">\n'
        html += '            <div class="stat-label">Min Deposit</div>\n'
        html += '            <div class="stat-value highlight">£10</div>\n'
        html += '        </div>\n'
        html += '        <div class="stat-item">\n'
        html += '            <div class="stat-label">Rating</div>\n'
        html += f'            <div class="stat-value">{self._escape_html(rating)}</div>\n'
        html += '        </div>\n'
        html += '    </div>\n\n'

        # CTA section before tabs
        html += '    <div class="cta-section">\n'
        html += f'        <a href="https://b3i.tech/visit/{platform_id}" class="cta-button" rel="nofollow noopener noreferrer" target="_blank" aria-label="Visit {self._escape_html(casino_name)} website (opens in new window)">\n'
        html += f'            Visit {self._escape_html(casino_name)}\n'
        html += '            <span class="visually-hidden">(opens in new window)</span>\n'
        html += '            <span aria-hidden="true">→</span>\n'
        html += '        </a>\n'
        html += '        <p class="cta-note">18+ Only • BeGambleAware.org • T&Cs Apply</p>\n'
        html += '    </div>\n\n'

        # Tabbed content
        html += '    <div class="tabs-container">\n'
        html += '        <div class="tab-nav" role="tablist">\n'
        html += f'            <button class="tab-button active" role="tab" data-tab="{platform_id}-overview" aria-selected="true" aria-controls="{platform_id}-overview" id="tab-{platform_id}-overview">Overview</button>\n'
        html += f'            <button class="tab-button" role="tab" data-tab="{platform_id}-bonuses" aria-controls="{platform_id}-bonuses" id="tab-{platform_id}-bonuses">Bonuses</button>\n'
        html += f'            <button class="tab-button" role="tab" data-tab="{platform_id}-games" aria-controls="{platform_id}-games" id="tab-{platform_id}-games">Games</button>\n'
        html += f'            <button class="tab-button" role="tab" data-tab="{platform_id}-proscons" aria-controls="{platform_id}-proscons" id="tab-{platform_id}-proscons">Pros & Cons</button>\n'
        html += '        </div>\n\n'

        html += '        <div class="tab-content">\n'

        # Overview Tab with rating breakdown table and CTA
        html += f'            <div class="tab-pane active" role="tabpanel" id="{platform_id}-overview" aria-labelledby="tab-{platform_id}-overview">\n'
        html += f'                <h3>How Do We Rate {self._escape_html(casino_name)}?</h3>\n'
        overview_content = tab_content.get('overview', '')
        if overview_content:
            html += f'                {overview_content}\n\n'
        else:
            html += f'                <p>{self._escape_html(casino_name)} is a licensed online casino offering a wide range of games and features.</p>\n\n'

        # Add overview image if available
        overview_img = self._get_image_html(images, f'{platform_id}-uk-deposit-bonus-promo.webp')
        if overview_img:
            html += f'                {overview_img}\n\n'

        # Rating breakdown table
        html += '                <p><strong>Rating Breakdown:</strong></p>\n'
        html += '                <table class="fee-table">\n'
        html += f'                    <caption class="visually-hidden">{self._escape_html(casino_name)} Rating Breakdown</caption>\n'
        html += '                    <tbody>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Licensing & Legitimacy</th>\n'
        html += '                            <td class="fee-value free">5/5 - Verified licenses</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Game Selection</th>\n'
        html += '                            <td class="fee-value free">5/5 - Extensive library</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Payment Speed</th>\n'
        html += '                            <td class="fee-value">4/5 - Fast when verified</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Customer Service</th>\n'
        html += '                            <td class="fee-value">3/5 - 24/7 chat available</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">User Satisfaction</th>\n'
        html += '                            <td class="fee-value">3/5 - Mixed reviews</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Mobile Experience</th>\n'
        html += '                            <td class="fee-value free">5/5 - Excellent apps</td>\n'
        html += '                        </tr>\n'
        html += '                    </tbody>\n'
        html += '                </table>\n\n'

        # CTA within tab
        html += '                <div class="cta-section">\n'
        html += f'                    <a href="https://b3i.tech/visit/{platform_id}" class="cta-button" rel="nofollow noopener noreferrer" target="_blank" aria-label="Visit {self._escape_html(casino_name)} (opens in new window)">\n'
        html += f'                        Explore {self._escape_html(casino_name)}\n'
        html += '                        <span class="visually-hidden">(opens in new window)</span>\n'
        html += '                        <span aria-hidden="true">→</span>\n'
        html += '                    </a>\n'
        html += '                    <p class="cta-note">New players only • Wagering requirements apply</p>\n'
        html += '                </div>\n'
        html += '            </div>\n\n'

        # Bonuses Tab with table and CTA
        html += f'            <div class="tab-pane" role="tabpanel" id="{platform_id}-bonuses" aria-labelledby="tab-{platform_id}-bonuses">\n'
        html += f'                <h3>What Welcome Bonus Does {self._escape_html(casino_name)} Offer?</h3>\n'
        bonus_content = tab_content.get('bonuses', '')
        if bonus_content:
            html += f'                {bonus_content}\n\n'
        else:
            html += '                <p>Check the casino website for current welcome bonus and promotional offers.</p>\n\n'

        # Add bonus image if available
        bonus_img = self._get_image_html(images, f'{platform_id}-casino-welcome-bonus-popup.webp')
        if bonus_img:
            html += f'                {bonus_img}\n\n'

        # Bonus details table
        html += '                <table class="fee-table">\n'
        html += '                    <caption class="visually-hidden">Welcome Bonus Details</caption>\n'
        html += '                    <tbody>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Bonus Amount</th>\n'
        html += '                            <td class="fee-value free">100% up to £100</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Minimum Deposit</th>\n'
        html += '                            <td class="fee-value">£10</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Wagering Requirements</th>\n'
        html += '                            <td class="fee-value">30x bonus + deposit</td>\n'
        html += '                        </tr>\n'
        html += '                        <tr class="fee-row">\n'
        html += '                            <th scope="row" class="fee-label">Time Limit</th>\n'
        html += '                            <td class="fee-value">30 days</td>\n'
        html += '                        </tr>\n'
        html += '                    </tbody>\n'
        html += '                </table>\n\n'

        html += '                <p style="margin-top: 16px;"><strong>Important Terms:</strong></p>\n'
        html += '                <ul>\n'
        html += '                    <li>Must opt-in before depositing</li>\n'
        html += '                    <li>Slots contribute 100%, table games vary</li>\n'
        html += '                    <li>Some games may be excluded</li>\n'
        html += '                    <li>Verify current terms on casino website</li>\n'
        html += '                </ul>\n\n'

        html += '                <div class="cta-section">\n'
        html += f'                    <a href="https://b3i.tech/visit/{platform_id}" class="cta-button" rel="nofollow noopener noreferrer" target="_blank" aria-label="Claim bonus (opens in new window)">\n'
        html += '                        Claim Your Bonus\n'
        html += '                        <span class="visually-hidden">(opens in new window)</span>\n'
        html += '                        <span aria-hidden="true">→</span>\n'
        html += '                    </a>\n'
        html += '                    <p class="cta-note">T&Cs apply • 18+ only • BeGambleAware.org</p>\n'
        html += '                </div>\n'
        html += '            </div>\n\n'

        # Games Tab with CTA
        html += f'            <div class="tab-pane" role="tabpanel" id="{platform_id}-games" aria-labelledby="tab-{platform_id}-games">\n'
        html += f'                <h3 id="games">How Many Games Does {self._escape_html(casino_name)} Have?</h3>\n'
        games_content = tab_content.get('games', '')
        if games_content:
            html += f'                {games_content}\n\n'
        else:
            html += '                <p>Wide selection of slots, table games, and live casino options available.</p>\n\n'

        # Add games image if available
        games_img = self._get_image_html(images, f'{platform_id}-casino-popular-slot-games-lobby.webp')
        if games_img:
            html += f'                {games_img}\n\n'

        html += '                <h4>Game Categories</h4>\n'
        html += '                <ul>\n'
        html += '                    <li><strong>Slots:</strong> Wide variety of themes and features</li>\n'
        html += '                    <li><strong>Live Casino:</strong> Real dealers and immersive gameplay</li>\n'
        html += '                    <li><strong>Table Games:</strong> Blackjack, roulette, baccarat variants</li>\n'
        html += '                    <li><strong>Jackpots:</strong> Progressive and fixed jackpot games</li>\n'
        html += '                </ul>\n\n'

        html += '                <div class="cta-section">\n'
        html += f'                    <a href="https://b3i.tech/visit/{platform_id}" class="cta-button" rel="nofollow noopener noreferrer" target="_blank" aria-label="Explore games (opens in new window)">\n'
        html += '                        Explore All Games\n'
        html += '                        <span class="visually-hidden">(opens in new window)</span>\n'
        html += '                        <span aria-hidden="true">→</span>\n'
        html += '                    </a>\n'
        html += '                    <p class="cta-note">1,000+ games • High RTP • Demo mode available</p>\n'
        html += '                </div>\n'
        html += '            </div>\n\n'

        # Pros & Cons Tab with follow-up paragraph
        html += f'            <div class="tab-pane" role="tabpanel" id="{platform_id}-proscons" aria-labelledby="tab-{platform_id}-proscons">\n'
        html += '                <div class="proscons-grid">\n'
        html += '                    <div class="pros-section">\n'
        html += '                        <h4><span aria-hidden="true">✓</span> Pros</h4>\n'
        html += '                        <ul class="pros-list">\n'
        if pros:
            for pro in pros:
                html += f'                            <li>{self._escape_html(pro)}</li>\n'
        else:
            html += '                            <li>Licensed and regulated</li>\n'
            html += '                            <li>Wide game selection</li>\n'
            html += '                            <li>Secure platform</li>\n'
        html += '                        </ul>\n'
        html += '                    </div>\n'
        html += '                    <div class="cons-section">\n'
        html += '                        <h4><span aria-hidden="true">✗</span> Cons</h4>\n'
        html += '                        <ul class="cons-list">\n'
        if cons:
            for con in cons:
                html += f'                            <li>{self._escape_html(con)}</li>\n'
        else:
            html += '                            <li>Wagering requirements apply</li>\n'
            html += '                            <li>Verification required</li>\n'
            html += '                            <li>Terms and conditions apply</li>\n'
        html += '                        </ul>\n'
        html += '                    </div>\n'
        html += '                </div>\n\n'

        html += f'                <p style="margin-top: 1.5rem;">{self._escape_html(casino_name)} presents a balance of strengths and areas for consideration. The {self._escape_html(rating)} rating reflects the overall evaluation of licensing, games, payments, and user experience.</p>\n'
        html += '            </div>\n'

        html += '        </div>\n'
        html += '    </div>\n\n'

        html += '    <div class="risk-warning">\n'
        html += '        <p><strong>18+ Only:</strong> Please gamble responsibly. Visit BeGambleAware.org for support.</p>\n'
        html += '    </div>\n'
        html += '</div>\n\n'

        return html

    def _build_content_sections_section(self, content_map: Dict, document: Dict) -> str:
        """Build general content sections"""
        sections = content_map.get('content_sections', [])
        html = ''

        # Skip header, FAQ, and reference sections
        skip_patterns = ['FAQ', 'Frequently Asked', 'Reference', 'Citation', 'Final Verdict', 'Conclusion']

        for section in sections:
            heading = section.get('heading', '')
            content = section.get('content', '')
            level = section.get('level', 2)

            # Skip if it's a special section we handle elsewhere
            if any(pattern in heading for pattern in skip_patterns):
                continue

            # Only render h2 and h3 sections
            if level in [2, 3]:
                heading_id = self._slugify(heading)

                if level == 2:
                    html += f'<section class="content-section" aria-labelledby="{heading_id}">\n'
                    html += f'    <h2 id="{heading_id}">{self._escape_html(heading)}</h2>\n'
                elif level == 3:
                    html += f'    <h3>{self._escape_html(heading)}</h3>\n'

                if content:
                    # Check if content contains a table
                    if self._has_inline_table(content):
                        table_html = self._render_inline_table(content, heading)
                        html += table_html
                    # Check if content contains image metadata
                    elif self._has_image_metadata(content):
                        image_html = self._render_image_from_metadata(content)
                        html += image_html
                    else:
                        # Regular paragraph rendering
                        paragraphs = [p.strip() for p in content.split('\n') if p.strip() and not p.startswith('_')]
                        for para in paragraphs:
                            html += f'    <p>{self._escape_html(para)}</p>\n'

                if level == 2:
                    html += '</section>\n\n'

        return html

    def _build_faq_simple_section(self, content_map: Dict, document: Dict) -> str:
        """Build FAQ section with simple h2/h3 format (no accordion)"""
        faqs = content_map.get('faqs', [])

        if not faqs:
            return ''

        html = '<section class="content-section">\n'
        html += '    <h2>Frequently Asked Questions</h2>\n\n'

        for faq in faqs:
            question = faq.get('question', '')
            answer = faq.get('answer', '')

            html += f'    <h3>{self._escape_html(question)}</h3>\n'
            html += f'    <p>{self._escape_html(answer)}</p>\n\n'

        html += '</section>\n\n'

        return html

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

    def _has_inline_table(self, content: str) -> bool:
        """Detect if content contains a tab-delimited table"""
        lines = [l for l in content.split('\n') if l.strip()]
        if len(lines) < 2:
            return False

        # Check if lines contain tabs (indicating columns)
        tab_lines = sum(1 for line in lines if '\t' in line)
        return tab_lines >= 2  # At least header + 1 data row

    def _render_inline_table(self, content: str, heading: str) -> str:
        """Render tab-delimited table as HTML"""
        lines = [l.strip() for l in content.split('\n') if l.strip() and '\t' in l]

        if not lines:
            return ''

        # Determine table type based on heading
        is_pros_cons = 'Pros' in heading and 'Cons' in heading
        is_payment = 'Payment' in heading or 'Method' in heading or 'Deposit' in heading or 'Withdrawal' in heading
        is_fee = 'Fee' in heading or 'Cost' in heading

        # Choose table class
        if is_fee or is_payment:
            table_class = 'fee-table'
        else:
            table_class = 'platform-table'

        html = ''

        # For pros/cons table, render as two-column proscons-grid
        if is_pros_cons:
            html += '    <div class="proscons-grid">\n'

            # Parse pros and cons
            pros = []
            cons = []

            for line in lines[1:]:  # Skip header
                columns = [c.strip() for c in line.split('\t')]
                if len(columns) >= 2:
                    if columns[0]:
                        pros.append(columns[0])
                    if columns[1]:
                        cons.append(columns[1])

            html += '        <div class="pros-section">\n'
            html += '            <h4><span aria-hidden="true">✓</span> Pros</h4>\n'
            html += '            <ul class="pros-list">\n'
            for pro in pros:
                html += f'                <li>{self._escape_html(pro)}</li>\n'
            html += '            </ul>\n'
            html += '        </div>\n'

            html += '        <div class="cons-section">\n'
            html += '            <h4><span aria-hidden="true">✗</span> Cons</h4>\n'
            html += '            <ul class="cons-list">\n'
            for con in cons:
                html += f'                <li>{self._escape_html(con)}</li>\n'
            html += '            </ul>\n'
            html += '        </div>\n'
            html += '    </div>\n'

            return html

        # Regular table rendering
        html += f'    <table class="{table_class}">\n'

        # Header row
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('\t')]

        html += '        <thead>\n'
        html += '            <tr>\n'
        for header in headers:
            html += f'                <th scope="col">{self._escape_html(header)}</th>\n'
        html += '            </tr>\n'
        html += '        </thead>\n'

        # Data rows
        html += '        <tbody>\n'
        for line in lines[1:]:
            columns = [c.strip() for c in line.split('\t')]

            html += '            <tr class="fee-row">\n'
            for i, col in enumerate(columns):
                # First column is row header for fee tables
                if i == 0 and (is_fee or is_payment):
                    html += f'                <th scope="row" class="fee-label">{self._escape_html(col)}</th>\n'
                else:
                    # Add 'free' class if value indicates no fee
                    value_class = ''
                    col_upper = col.upper()
                    if any(word in col_upper for word in ['FREE', 'INSTANT', 'NONE', '0%']):
                        value_class = ' free'

                    html += f'                <td class="fee-value{value_class}">{self._escape_html(col)}</td>\n'

            html += '            </tr>\n'

        html += '        </tbody>\n'
        html += '    </table>\n'

        return html

    def _has_image_metadata(self, content: str) -> bool:
        """Detect if content contains image metadata block"""
        return ('Alt Text:' in content or 'File Name:' in content) and not '\t' in content

    def _render_image_from_metadata(self, content: str) -> str:
        """Extract image metadata and render as figure with img tag"""
        lines = [l.strip() for l in content.split('\n') if l.strip()]

        alt_text = ''
        file_name = ''
        caption = ''

        current_field = None
        for line in lines:
            if line.startswith('Alt Text:'):
                current_field = 'alt'
                alt_text = line.replace('Alt Text:', '').strip()
            elif line.startswith('File Name:'):
                current_field = 'file'
                file_name = line.replace('File Name:', '').strip()
            elif line.startswith('Caption:'):
                current_field = 'caption'
                caption = line.replace('Caption:', '').strip()
            elif current_field and not line.endswith(':'):
                # Continuation of previous field
                if current_field == 'alt':
                    alt_text += ' ' + line
                elif current_field == 'file':
                    file_name += line
                elif current_field == 'caption':
                    caption += ' ' + line

        if not file_name:
            return ''

        # Build image path (assuming images are in wp-content/uploads)
        # User can adjust base path as needed
        image_url = f"/wp-content/uploads/{file_name}"

        html = '    <figure style="margin: 1.5rem 0;">\n'
        html += f'        <img src="{image_url}" alt="{self._escape_html(alt_text)}" '
        html += 'style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" loading="lazy" />\n'

        if caption:
            # Remove separator lines from caption
            caption = caption.replace('________________________________________', '').strip()
            if caption:
                html += f'        <figcaption style="text-align: center; font-size: 0.875rem; color: #6e6e73; margin-top: 0.5rem;">'
                html += f'{self._escape_html(caption)}</figcaption>\n'

        html += '    </figure>\n'

        return html

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text

    def _get_image(self, images: Dict, filename: str) -> Dict:
        """Look up image by filename from images dictionary"""
        if not images:
            return None

        # Try direct filename lookup
        if filename in images:
            return images[filename]

        # Try case-insensitive lookup
        filename_lower = filename.lower()
        for key, img in images.items():
            if key.lower() == filename_lower:
                return img

        return None

    def _get_image_html(self, images: Dict, filename: str, width: int = None, height: int = None, loading: str = "lazy") -> str:
        """Generate HTML for an image with proper alt text and caption"""
        img = self._get_image(images, filename)

        if not img:
            # Fallback to hardcoded URL if image not found in dictionary
            url = f"https://b3i.tech/wp-content/uploads/2025/11/{filename}"
            alt = filename.replace('-', ' ').replace('.webp', '').replace('.png', '').title()
            return f'<img src="{url}" alt="{alt}" loading="{loading}" />'

        url = img.get('url', '')
        alt = img.get('metadata', {}).get('_wp_attachment_image_alt', img.get('title', ''))
        caption = img.get('metadata', {}).get('caption', '')

        # Build image tag
        img_attrs = f'src="{url}" alt="{self._escape_html(alt)}"'
        if width:
            img_attrs += f' width="{width}"'
        if height:
            img_attrs += f' height="{height}"'
        img_attrs += f' loading="{loading}"'

        img_html = f'<img {img_attrs} />'

        # Wrap in figure if there's a caption
        if caption:
            html = '<figure style="margin: 1.5rem 0;">\n'
            html += f'    {img_html}\n'
            html += f'    <figcaption style="text-align: center; font-size: 0.875rem; color: #6e6e73; margin-top: 0.5rem;">{self._escape_html(caption)}</figcaption>\n'
            html += '</figure>'
            return html

        return img_html
