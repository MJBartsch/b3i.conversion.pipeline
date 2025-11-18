# B3i Conversion Pipeline

Automated system for converting raw Word documents to fully-styled HTML pages with images, affiliate links, and internal linking.

## Overview

This pipeline takes raw document content and transforms it into production-ready HTML pages that:
- Use CSS classes from `Stylesheet.css`
- Include relevant images from your media library
- Insert affiliate links automatically
- Add internal links between related pages
- Follow semantic HTML structure

## Project Structure

```
b3i.conversion.pipeline/
├── src/                        # Source code
│   ├── content_parser.py      # Parses raw documents into structured data
│   ├── html_generator.py      # Generates HTML with CSS classes
│   ├── content_enhancer.py    # Adds images, affiliate links, internal links
│   └── convert.py             # Main conversion script
├── config/                     # Configuration files
│   └── template_config.json   # CSS class mappings, patterns
├── raw_documents/              # Input: Place your .txt documents here
├── output/                     # Output: Generated HTML files
├── templates/                  # HTML templates (if needed for customization)
├── images.json                 # Image library data
├── affiliate-links.json        # Affiliate link data
└── Stylesheet.css             # Your CSS file
```

## Quick Start

### 1. Prepare Your Document

Create a `.txt` file in the `raw_documents/` folder with this structure:

```
Target Keyword: Your Main Keyword
Target Geo: UK
SEO Metadata
URL Slug:
/your-page-url/
Meta Title (58 characters):
Your SEO-Optimized Title
Meta Description (155 characters):
Your SEO-optimized description here.
Notes for MJ:
Any implementation notes here.
Content
Your Main Heading (h1)
Your introduction paragraph goes here...

Section Heading (h2)
Section content...

Subsection Heading (h3)
More detailed content...
```

### 2. Run the Conversion

**Convert a single document:**
```bash
python3 src/convert.py raw_documents/your_document.txt
```

**Convert with custom output path:**
```bash
python3 src/convert.py raw_documents/your_document.txt output/custom_name.html
```

**Batch convert all documents in raw_documents/:**
```bash
python3 src/convert.py --batch
```

### 3. Check the Output

Your HTML file will be in the `output/` directory, ready to use!

## Document Format Guide

### Metadata Section

Every document should start with metadata:

```
Target Keyword: Best Bitcoin Casino
Target Geo: UK
SEO Metadata
URL Slug:
/best-bitcoin-casino/
Meta Title (58 characters):
Best Bitcoin Casino UK 2025
Meta Description (155 characters):
Discover the best bitcoin casinos for UK players...
Notes for MJ:
FAQ set to schema. Keep images under 90kb.
```

### Content Sections

Mark headings with their level in parentheses:

```
Main Page Title (h1)
Introduction paragraph...

First Section (h2)
Section content...

Subsection (h3)
Detailed content...
```

### Special Content Types

#### Comparison Tables

Use CSV format after a heading:

```
Top 10 Platforms (h2)
csv
Rank,Casino,Bonus,Speed
1,Platform A,£100,Instant
2,Platform B,£200,Fast
```

#### Disclaimer Boxes

Any section with "disclaimer" or "notice" in the heading:

```
Important Notice for UK Readers (disclaimer box)
Section Title:
Content here...

Another Section:
More content...
```

#### Platform Reviews

Numbered sections with platform names:

```
1. Platform Name - Descriptive Tagline (h3)
Introduction about this platform...

Pros:
•	First advantage
•	Second advantage

Cons:
•	First disadvantage
•	Second disadvantage

Mobile Compatibility: Details here
UKGC Compliance: Details here

Verdict: Final assessment of the platform...
```

#### FAQs

```
Frequently Asked Questions (h2)

Can I use this platform? (h3)
Answer to the question...

Is it safe? (h3)
Answer about safety...
```

### Lists

Use bullet points with `•` character:

```
Key features:
•	Feature one
•	Feature two
•	Feature three
```

## What the Pipeline Does

### 1. Content Parsing
- Extracts metadata (keywords, SEO data, notes)
- Identifies section types (standard, review, table, FAQ, etc.)
- Parses special structures (pros/cons, tables, disclaimers)
- Maintains heading hierarchy

### 2. HTML Generation
- Generates semantic HTML structure
- Applies appropriate CSS classes from `Stylesheet.css`
- Creates proper heading hierarchy
- Formats tables, lists, and special sections

### 3. Content Enhancement
- **Images**: Automatically matches and inserts relevant images
  - Finds logos for mentioned platforms
  - Uses alt text for SEO
  - Applies lazy loading

- **Affiliate Links**: Automatically links casino/platform names
  - Links first 3 occurrences of each platform
  - Adds nofollow and sponsored attributes
  - Prevents duplicate linking

- **Internal Links**: Creates links between related pages (when configured)

## Configuration

### CSS Class Mapping

Edit `config/template_config.json` to customize CSS classes:

```json
{
  "css_classes": {
    "main_wrapper": "crypto-betting-widget",
    "article_header": "article-header",
    "intro": "intro",
    ...
  }
}
```

### Affiliate Link Patterns

Add platform names to automatically link:

```json
{
  "affiliate_link_patterns": {
    "casino_names": [
      "888Casino",
      "Bet365",
      ...
    ]
  }
}
```

### Image Matching

Configure how images are matched to content:

```json
{
  "image_matching": {
    "logo_keywords": ["logo", "square", "icon"],
    "featured_keywords": ["featured", "hero", "banner"],
    "screenshot_keywords": ["screenshot", "interface", "mobile"]
  }
}
```

## Advanced Usage

### Adding New Platforms

1. Add platform to `affiliate-links.json`
2. Add platform name to `config/template_config.json` under `casino_names`
3. Re-run conversion

### Custom HTML Templates

Modify `src/html_generator.py` to customize HTML output:
- `_generate_article_header()` - Main header
- `_generate_comparison_table()` - Tables
- `_generate_platform_review()` - Review sections
- `_generate_disclaimer()` - Disclaimer boxes

### Image Management

Images are automatically loaded from `images.json`. The system:
- Searches image titles for platform names
- Matches based on image type (logo, featured, screenshot)
- Returns best match based on keyword scoring

## Tips for Best Results

### Document Formatting
1. **Be consistent** with heading markers `(h1)`, `(h2)`, etc.
2. **Use bullet points** (`•`) for lists
3. **Mark special sections** clearly (disclaimer, FAQ, review)
4. **Include CSV tables** with proper headers

### SEO Optimization
1. Keep meta titles under 60 characters
2. Keep meta descriptions under 160 characters
3. Use target keywords in first paragraph
4. Include clear heading hierarchy

### Image Optimization
1. Name image files descriptively
2. Include platform names in image titles
3. Keep images under 90kb (as noted in your requirements)

### Affiliate Links
1. Platform names will be auto-linked (first 3 mentions)
2. Ensure platform names match exactly in `affiliate-links.json`
3. Links get `rel="nofollow sponsored"` automatically

## Troubleshooting

### Conversion Fails
- Check document format matches examples
- Ensure heading markers are correct `(h1)`, `(h2)`, etc.
- Verify CSV tables have proper formatting

### Images Not Appearing
- Check image titles in `images.json`
- Ensure platform names match
- Verify image URLs are accessible

### Links Not Working
- Verify platform names in `affiliate-links.json`
- Check spelling and capitalization
- Ensure JSON syntax is valid

### CSS Classes Wrong
- Review `config/template_config.json`
- Check that class names match `Stylesheet.css`
- Verify section types are detected correctly

## Future Enhancements

Potential additions to the pipeline:
- [ ] WordPress export functionality
- [ ] Schema markup generation for FAQs
- [ ] Image optimization and resizing
- [ ] Link health checking
- [ ] Automated internal linking based on content similarity
- [ ] Support for Word document input (`.docx`)
- [ ] Template variations for different page types

## Support

For issues or questions:
1. Check the examples in `raw_documents/`
2. Review generated HTML in `output/`
3. Verify JSON data files are valid
4. Check Python error messages for specific issues

## License

Proprietary - B3i.tech
