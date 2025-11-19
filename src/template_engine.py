"""
Template Engine - Loads and fills HTML templates with data
"""
import os
from pathlib import Path
from typing import Dict, List, Any


class TemplateEngine:
    """Manages HTML template loading and rendering"""

    def __init__(self, templates_dir: str = 'templates'):
        self.templates_dir = Path(templates_dir)
        self.template_cache = {}

    def load_template(self, template_path: str) -> str:
        """Load a template file and cache it"""
        if template_path in self.template_cache:
            return self.template_cache[template_path]

        full_path = self.templates_dir / template_path
        with open(full_path, 'r', encoding='utf-8') as f:
            template = f.read()

        self.template_cache[template_path] = template
        return template

    def render(self, template_path: str, data: Dict[str, Any]) -> str:
        """Render a template with data"""
        template = self.load_template(template_path)
        return self._fill_placeholders(template, data)

    def _fill_placeholders(self, template: str, data: Dict[str, Any]) -> str:
        """Replace {placeholder} with data values"""
        result = template
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            # Convert None to empty string
            if value is None:
                value = ''
            # Convert lists to empty string (should be handled separately)
            if isinstance(value, (list, dict)):
                value = ''
            result = result.replace(placeholder, str(value))

        # Remove any unfilled placeholders
        # result = re.sub(r'\{[^}]+\}', '', result)

        return result

    def render_quick_verdict_card(self, platform_data: Dict[str, Any]) -> str:
        """Render a quick verdict card component"""
        # Generate rating stars
        rating = float(platform_data.get('rating', 5))
        stars_html = self._generate_stars(rating)

        data = {
            'featured_class': ' featured' if platform_data.get('featured', False) else '',
            'platform_id': self._slugify(platform_data.get('name', '')),
            'category_label': platform_data.get('category_label', 'Best Overall'),
            'category_title': platform_data.get('category_title', 'Top Pick'),
            'logo_url': platform_data.get('logo_url', ''),
            'platform_name': platform_data.get('name', ''),
            'rating_text': f"{rating} out of 5 stars",
            'rating_stars': stars_html,
            'rating_value': f"{rating}/5",
            'features_list': self._render_list_items(platform_data.get('features', [])),
            'badge_text': platform_data.get('badge', 'BEST'),
            'review_anchor': self._slugify(platform_data.get('name', '')) + '-review'
        }

        return self.render('components/quick_verdict_card.html', data)

    def render_platform_card(self, platform_data: Dict[str, Any]) -> str:
        """Render a detailed platform review card"""
        platform_id = self._slugify(platform_data.get('name', ''))
        rating = float(platform_data.get('rating', 5))

        # Generate stats items
        stats_items = ''
        for stat in platform_data.get('stats', []):
            highlight_class = ' highlight' if stat.get('highlight', False) else ''
            stats_items += f'''        <div class="stat-item">
            <div class="stat-label">{stat.get('label', '')}</div>
            <div class="stat-value{highlight_class}">{stat.get('value', '')}</div>
        </div>
'''

        # Generate fees table
        fees_content = self._render_fee_table(platform_data.get('fees', {}))

        # Generate sports content
        sports_content = self._render_sports_content(platform_data.get('sports', {}))

        data = {
            'platform_id': platform_id,
            'header_image': platform_data.get('header_image', ''),
            'rating_stars': '★' * int(rating),
            'rating_value': f"{rating}/5",
            'logo_url': platform_data.get('logo_url', ''),
            'platform_name': platform_data.get('name', ''),
            'tagline': platform_data.get('tagline', ''),
            'stats_items': stats_items,
            'affiliate_link': platform_data.get('affiliate_link', '#'),
            'cta_note': platform_data.get('cta_note', ''),
            'overview_content': platform_data.get('overview', ''),
            'fees_content': fees_content,
            'sports_content': sports_content,
            'pros_list': self._render_list_items(platform_data.get('pros', [])),
            'cons_list': self._render_list_items(platform_data.get('cons', []))
        }

        return self.render('components/platform_card.html', data)

    def render_faq_item(self, faq_data: Dict[str, Any], faq_id: int) -> str:
        """Render an FAQ item"""
        data = {
            'faq_id': str(faq_id),
            'question': faq_data.get('question', ''),
            'answer': faq_data.get('answer', '')
        }

        return self.render('components/faq_item.html', data)

    def render_content_card(self, content: str) -> str:
        """Render a content card"""
        data = {'content': content}
        return self.render('components/content_card.html', data)

    def _generate_stars(self, rating: float) -> str:
        """Generate star rating HTML"""
        full_stars = int(rating)
        stars_html = ''

        for i in range(full_stars):
            stars_html += '<span class="star" aria-hidden="true">★</span>\n                        '

        remaining = 5 - full_stars
        for i in range(remaining):
            stars_html += '<span class="star empty" aria-hidden="true">☆</span>\n                        '

        return stars_html.strip()

    def _render_list_items(self, items: List[str]) -> str:
        """Render list items as <li> elements"""
        if not items:
            return ''

        html = ''
        for item in items:
            html += f'                <li>{item}</li>\n'

        return html.rstrip()

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text

    def _render_fee_table(self, fees_data: Dict[str, Any]) -> str:
        """Render fee table for the Fees tab"""
        if not fees_data:
            # Default fee structure
            fees_data = {
                'Deposit Fees': 'FREE',
                'Withdrawal Fees': 'Network fees only',
                'Trading Fees': 'N/A',
                'Inactivity Fees': 'None'
            }

        html = '<table class="fee-table">\n'
        html += '    <tbody>\n'

        for fee_type, fee_value in fees_data.items():
            # Add class based on fee value
            value_class = 'free' if fee_value.upper() in ['FREE', 'NONE', '0%', '0'] else ''
            html += '        <tr class="fee-row">\n'
            html += f'            <th scope="row" class="fee-label">{fee_type}</th>\n'
            html += f'            <td class="fee-value {value_class}">{fee_value}</td>\n'
            html += '        </tr>\n'

        html += '    </tbody>\n'
        html += '</table>\n'

        # Add additional fee information if provided
        if isinstance(fees_data, dict) and 'notes' in fees_data:
            html += f'<p class="fee-notes">{fees_data["notes"]}</p>\n'

        return html

    def _render_sports_content(self, sports_data: Dict[str, Any]) -> str:
        """Render sports coverage content"""
        if not sports_data:
            # Default content
            return '<p>Comprehensive sports betting coverage including football, basketball, tennis, and more.</p>'

        html = ''

        # If sports_data is a dict with detailed structure
        if isinstance(sports_data, dict):
            # Add intro paragraph
            if 'intro' in sports_data:
                html += f'<p>{sports_data["intro"]}</p>\n'

            # Add sports list
            if 'sports_list' in sports_data:
                html += '<div class="sports-grid">\n'
                for sport in sports_data['sports_list']:
                    html += f'    <div class="sport-item">{sport}</div>\n'
                html += '</div>\n'

            # Add additional details
            if 'details' in sports_data:
                html += f'<p>{sports_data["details"]}</p>\n'

        # If sports_data is a simple string
        elif isinstance(sports_data, str):
            html = f'<p>{sports_data}</p>'

        return html
