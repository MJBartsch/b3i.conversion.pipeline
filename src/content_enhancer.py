"""
Content Enhancer - Adds images, affiliate links, and internal links to HTML
"""
import json
import re
from typing import Dict, List, Any, Tuple


class ContentEnhancer:
    """Enhances HTML content with images, affiliate links, and internal links"""

    def __init__(self, images_path: str = 'images.json',
                 affiliate_links_path: str = 'affiliate-links.json',
                 config_path: str = 'config/template_config.json'):

        # Load images
        with open(images_path, 'r') as f:
            images_data = json.load(f)
            self.images = images_data.get('attachments', [])

        # Load affiliate links
        with open(affiliate_links_path, 'r') as f:
            links_data = json.load(f)
            self.affiliate_links = {
                link['title']: link for link in links_data.get('affiliate_links', [])
            }

        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Build image lookup index
        self._build_image_index()

    def _build_image_index(self):
        """Build searchable index of images by keywords"""
        self.image_index = {
            'logos': [],
            'featured': [],
            'screenshots': [],
            'all': self.images
        }

        logo_keywords = self.config['image_matching']['logo_keywords']
        featured_keywords = self.config['image_matching']['featured_keywords']
        screenshot_keywords = self.config['image_matching']['screenshot_keywords']

        for img in self.images:
            title_lower = img.get('title', '').lower()

            if any(kw in title_lower for kw in logo_keywords):
                self.image_index['logos'].append(img)
            if any(kw in title_lower for kw in featured_keywords):
                self.image_index['featured'].append(img)
            if any(kw in title_lower for kw in screenshot_keywords):
                self.image_index['screenshots'].append(img)

    def find_image(self, search_term: str, image_type: str = 'logo') -> Dict[str, Any]:
        """Find best matching image for a search term"""
        search_lower = search_term.lower()

        # Get relevant image set
        image_set = self.image_index.get(image_type + 's', self.image_index['all'])

        # Find best match
        best_match = None
        best_score = 0

        for img in image_set:
            title = img.get('title', '').lower()
            score = 0

            # Exact match
            if search_lower in title:
                score = 100

            # Partial word matches
            search_words = search_lower.split()
            for word in search_words:
                if word in title:
                    score += 20

            if score > best_score:
                best_score = score
                best_match = img

        return best_match

    def get_affiliate_link(self, platform_name: str) -> Dict[str, Any]:
        """Get affiliate link for a platform"""
        # Try exact match first
        if platform_name in self.affiliate_links:
            return self.affiliate_links[platform_name]

        # Try case-insensitive match
        platform_lower = platform_name.lower()
        for name, link in self.affiliate_links.items():
            if name.lower() == platform_lower:
                return link

        # Try partial match
        for name, link in self.affiliate_links.items():
            if platform_lower in name.lower() or name.lower() in platform_lower:
                return link

        return None

    def insert_affiliate_links(self, html: str) -> str:
        """Insert affiliate links for casino/platform names in HTML"""
        casino_names = self.config['affiliate_link_patterns']['casino_names']

        for casino_name in casino_names:
            affiliate_link = self.get_affiliate_link(casino_name)

            if affiliate_link:
                # Simple pattern to match casino name as whole word
                pattern = r'\b' + re.escape(casino_name) + r'\b'

                # Create replacement with affiliate link
                target_url = affiliate_link.get('target_url', '#')
                replacement = f'<a href="{target_url}" rel="nofollow sponsored" target="_blank">{casino_name}</a>'

                # Find all matches and only replace if not already in a link
                matches = list(re.finditer(pattern, html))
                replacements_made = 0

                # Process matches in reverse to maintain positions
                for match in reversed(matches):
                    if replacements_made >= 3:  # Limit to 3 replacements
                        break

                    start, end = match.span()

                    # Check if this match is inside an existing anchor tag
                    before = html[:start]
                    after = html[end:]

                    # Simple check: look for unclosed <a tag before and </a> after
                    in_link = before.rfind('<a') > before.rfind('</a>') if '</a>' in before else before.rfind('<a') >= 0

                    if not in_link:
                        html = html[:start] + replacement + html[end:]
                        replacements_made += 1

        return html

    def insert_images_in_html(self, html: str, platform_names: List[str] = None) -> str:
        """Insert images into HTML where appropriate"""
        if not platform_names:
            return html

        # Find platform review sections and add logos
        for platform_name in platform_names:
            logo = self.find_image(platform_name, 'logo')

            if logo:
                # Find the platform review section
                section_pattern = rf'(<section[^>]*id="{re.escape(platform_name.lower())}[^"]*"[^>]*>)'

                def add_logo(match):
                    section_start = match.group(1)
                    img_tag = self._create_image_tag(logo, platform_name)
                    return f'{section_start}\n    <div class="platform-logo">{img_tag}</div>'

                html = re.sub(section_pattern, add_logo, html, flags=re.IGNORECASE)

        return html

    def _create_image_tag(self, image: Dict[str, Any], alt_text: str = '') -> str:
        """Create an HTML image tag from image data"""
        url = image.get('url', '')
        title = image.get('title', alt_text)

        if not alt_text:
            alt_text = title

        return f'<img src="{url}" alt="{alt_text}" title="{title}" loading="lazy" />'

    def add_internal_links(self, html: str, all_pages: List[Dict[str, str]] = None) -> str:
        """Add internal links between related content"""
        if not all_pages:
            return html

        # For each page, find keyword mentions and link to related pages
        for page in all_pages:
            page_title = page.get('title', '')
            page_url = page.get('url', '')

            if not page_title or not page_url:
                continue

            # Create pattern to match page title
            pattern = r'\b' + re.escape(page_title) + r'\b'

            # Replace first occurrence with internal link
            replacement = f'<a href="{page_url}">{page_title}</a>'
            html = re.sub(pattern, replacement, html, count=1)

        return html

    def enhance_html(self, html: str, platform_names: List[str] = None,
                    related_pages: List[Dict[str, str]] = None) -> str:
        """Apply all enhancements to HTML"""
        # Insert affiliate links
        html = self.insert_affiliate_links(html)

        # Insert images
        if platform_names:
            html = self.insert_images_in_html(html, platform_names)

        # Add internal links
        if related_pages:
            html = self.add_internal_links(html, related_pages)

        return html
