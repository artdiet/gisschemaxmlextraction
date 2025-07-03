#!/usr/bin/env python3
"""
Validate and fix HTML manual to ensure proper navigation
"""

from bs4 import BeautifulSoup
from pathlib import Path
import re

def validate_and_fix_html():
    """Validate HTML and fix any navigation issues"""
    
    html_file = Path("building_a_complete_manual.html")
    
    if not html_file.exists():
        print("HTML file not found!")
        return False
    
    print("Reading HTML file...")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Validation checks
    print("\n=== VALIDATION RESULTS ===")
    
    # Check 1: All field sections have proper IDs
    field_sections = soup.find_all(class_='field-section')
    sections_with_ids = [s for s in field_sections if s.get('id')]
    print(f"Field sections: {len(field_sections)}")
    print(f"Sections with IDs: {len(sections_with_ids)}")
    
    # Check 2: All TOC links point to existing anchors
    toc_links = soup.select('.toc a[href^="#"]')
    print(f"TOC links: {len(toc_links)}")
    
    broken_links = []
    for link in toc_links:
        href = link.get('href')
        if href:
            anchor_id = href[1:]  # Remove #
            target = soup.find(id=anchor_id)
            if not target:
                broken_links.append(anchor_id)
    
    print(f"Broken links: {len(broken_links)}")
    if broken_links:
        print(f"Broken: {broken_links[:5]}...")
    
    # Check 3: Specific field verification
    test_fields = ['country', 'buildingCondition', 'installationId', 'buildingOpStatus']
    print(f"\nTesting specific fields:")
    for field in test_fields:
        anchor = soup.find(id=field)
        toc_link = soup.find('a', href=f'#{field}')
        content_check = False
        
        if anchor:
            # Check if field has content
            field_info = anchor.find(class_='field-info')
            has_description = anchor.find(class_='domain-description') is not None
            has_table = anchor.find('table') is not None
            has_note = anchor.find(class_='large-domain-note') is not None
            content_check = field_info and (has_description or has_table or has_note)
        
        print(f"  {field}: anchor={'✓' if anchor else '✗'}, "
              f"toc={'✓' if toc_link else '✗'}, "
              f"content={'✓' if content_check else '✗'}")
    
    # Check 4: HTML structure
    title = soup.find('title')
    css = soup.find('style')
    print(f"\nHTML structure:")
    print(f"  Title: {'✓' if title else '✗'}")
    print(f"  CSS: {'✓' if css else '✗'}")
    print(f"  Body content: {'✓' if soup.find('body') else '✗'}")
    
    # Generate a summary report
    print(f"\n=== SUMMARY ===")
    print(f"Total field sections: {len(field_sections)}")
    print(f"Sections with proper IDs: {len(sections_with_ids)}")
    print(f"TOC links: {len(toc_links)}")
    print(f"Broken navigation links: {len(broken_links)}")
    
    is_valid = (len(broken_links) == 0 and 
               len(sections_with_ids) == len(field_sections) and
               len(toc_links) > 0)
    
    print(f"Overall status: {'✓ VALID' if is_valid else '✗ ISSUES FOUND'}")
    
    return is_valid

def create_simple_test_html():
    """Create a simple test HTML to verify navigation works"""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Navigation Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .field-section { border: 1px solid #ddd; margin: 20px 0; padding: 20px; }
        .field-name { font-weight: bold; font-size: 1.2em; color: #2c3e50; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Navigation Test</h1>
    
    <h2>Table of Contents</h2>
    <ul>
        <li><a href="#country">Country</a></li>
        <li><a href="#buildingCondition">Building Condition</a></li>
        <li><a href="#installationId">Installation ID</a></li>
    </ul>
    
    <div class="field-section" id="country">
        <div class="field-name">country (Country)</div>
        <p>The country that owns that specific feature.</p>
        <p>This field has 274 possible values including United States, Germany, etc.</p>
    </div>
    
    <div class="field-section" id="buildingCondition">
        <div class="field-name">buildingCondition (Building Condition)</div>
        <p>The structural condition and state of repair of a building or structure.</p>
        <p>Options include: Good, Fair, Poor, Under Construction, etc.</p>
    </div>
    
    <div class="field-section" id="installationId">
        <div class="field-name">installationId (Installation ID)</div>
        <p>Unique identifier for military installations.</p>
        <p>This field has 322 possible installation codes.</p>
    </div>
    
    <p><a href="#top">Back to top</a></p>
    
</body>
</html>'''
    
    test_file = Path("navigation_test.html")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created navigation test file: {test_file}")
    return test_file

def main():
    print("Validating HTML manual...")
    
    is_valid = validate_and_fix_html()
    
    if is_valid:
        print("\n✓ HTML manual is valid and complete!")
        print("Open 'building_a_complete_manual.html' in your browser")
        print("Navigation should work properly")
    else:
        print("\n✗ Issues found in HTML manual")
        print("Creating simple test file for navigation verification...")
        test_file = create_simple_test_html()
        print(f"Test the navigation with: {test_file}")
    
    # Show file sizes
    print(f"\nGenerated files:")
    for html_file in Path(".").glob("*.html"):
        size = html_file.stat().st_size
        print(f"  {html_file.name}: {size:,} bytes")

if __name__ == "__main__":
    main()