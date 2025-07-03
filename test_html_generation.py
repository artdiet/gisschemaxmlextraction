#!/usr/bin/env python3
"""
Unit tests for HTML manual generation
Tests to ensure all fields are properly included and linked
"""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from bs4 import BeautifulSoup
import sys

class TestHTMLGeneration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test data by parsing the XML file"""
        cls.xml_file = Path("DATABASE_EXPORT.XML")
        cls.html_file = Path("building_a_complete_manual.html")
        
        # Parse XML to get expected field list
        cls.expected_fields = cls._parse_expected_fields()
        print(f"Expected fields from XML: {len(cls.expected_fields)}")
    
    @classmethod
    def _parse_expected_fields(cls):
        """Parse XML to get the actual field list from Building_A"""
        tree = ET.parse(cls.xml_file)
        root = tree.getroot()
        
        namespaces = {
            'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        
        # Find Building_A feature class
        building_a = None
        for feature_class in root.findall(".//DataElement[@xsi:type='esri:DEFeatureClass']", namespaces):
            name_elem = feature_class.find("Name", namespaces)
            if name_elem is not None and name_elem.text == "Building_A":
                building_a = feature_class
                break
        
        if not building_a:
            return []
        
        fields = []
        fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
        if fields_array:
            for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
                field_name = field.find("Name", namespaces).text
                fields.append(field_name)
        
        return fields
    
    def setUp(self):
        """Set up for each test"""
        if not self.html_file.exists():
            self.skipTest(f"HTML file {self.html_file} does not exist. Run generation script first.")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
        
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
    
    def test_html_file_exists(self):
        """Test that HTML file was created"""
        self.assertTrue(self.html_file.exists(), "HTML manual file should exist")
    
    def test_html_is_valid(self):
        """Test that HTML is valid and parseable"""
        self.assertIsNotNone(self.soup, "HTML should be parseable")
        self.assertEqual(self.soup.find('html')['lang'], 'en', "HTML should have proper language attribute")
    
    def test_all_fields_have_anchors(self):
        """Test that all expected fields have anchor IDs in the HTML"""
        missing_anchors = []
        
        for field_name in self.expected_fields:
            anchor = self.soup.find(id=field_name)
            if not anchor:
                missing_anchors.append(field_name)
        
        if missing_anchors:
            print(f"Missing anchors for fields: {missing_anchors[:10]}...")  # Show first 10
        
        self.assertEqual(len(missing_anchors), 0, 
                        f"All {len(self.expected_fields)} fields should have anchor IDs. Missing: {len(missing_anchors)}")
    
    def test_all_fields_in_toc(self):
        """Test that all fields appear in the table of contents"""
        # Find all TOC links
        toc_links = self.soup.select('.toc a[href^="#"]')
        toc_field_names = []
        
        for link in toc_links:
            href = link.get('href')
            if href and href.startswith('#'):
                field_name = href[1:]  # Remove the #
                toc_field_names.append(field_name)
        
        missing_from_toc = set(self.expected_fields) - set(toc_field_names)
        
        if missing_from_toc:
            print(f"Missing from TOC: {list(missing_from_toc)[:10]}...")  # Show first 10
        
        self.assertEqual(len(missing_from_toc), 0,
                        f"All fields should be in TOC. Missing: {len(missing_from_toc)}")
    
    def test_specific_fields_present(self):
        """Test that specific important fields are present"""
        important_fields = ['country', 'buildingCondition', 'installationId', 'buildingOpStatus']
        
        for field_name in important_fields:
            with self.subTest(field=field_name):
                # Check anchor exists
                anchor = self.soup.find(id=field_name)
                self.assertIsNotNone(anchor, f"Field {field_name} should have an anchor")
                
                # Check TOC link exists
                toc_link = self.soup.find('a', href=f'#{field_name}')
                self.assertIsNotNone(toc_link, f"Field {field_name} should have a TOC link")
    
    def test_domain_fields_have_content(self):
        """Test that domain fields have proper content structure"""
        domain_fields = ['country', 'buildingCondition', 'buildingOpStatus']
        
        for field_name in domain_fields:
            with self.subTest(field=field_name):
                # Find the field section
                field_section = self.soup.find(id=field_name)
                if field_section:
                    # Should have field info
                    field_info = field_section.find(class_='field-info')
                    self.assertIsNotNone(field_info, f"{field_name} should have field-info section")
                    
                    # Should have domain description or table
                    has_domain_desc = field_section.find(class_='domain-description') is not None
                    has_table = field_section.find('table') is not None
                    has_large_domain_note = field_section.find(class_='large-domain-note') is not None
                    
                    self.assertTrue(has_domain_desc or has_table or has_large_domain_note,
                                   f"{field_name} should have domain content")
    
    def test_field_count_in_html(self):
        """Test that the HTML reports correct field counts"""
        # Find all field sections
        field_sections = self.soup.find_all(class_='field-section')
        html_field_count = len(field_sections)
        
        self.assertEqual(html_field_count, len(self.expected_fields),
                        f"HTML should contain {len(self.expected_fields)} field sections, found {html_field_count}")
    
    def test_no_duplicate_ids(self):
        """Test that there are no duplicate IDs in the HTML"""
        all_ids = []
        for element in self.soup.find_all(id=True):
            all_ids.append(element.get('id'))
        
        unique_ids = set(all_ids)
        self.assertEqual(len(all_ids), len(unique_ids), "All IDs should be unique")
    
    def test_css_styling_present(self):
        """Test that CSS styling is included"""
        style_tag = self.soup.find('style')
        self.assertIsNotNone(style_tag, "HTML should include CSS styling")
        
        style_content = style_tag.string
        required_classes = ['.field-info', '.domain-description', '.field-section', '.toc']
        
        for css_class in required_classes:
            self.assertIn(css_class, style_content, f"CSS should include {css_class} styling")
    
    def test_large_domains_handled(self):
        """Test that large domains are handled appropriately"""
        # Fields known to have large domains
        large_domain_fields = ['country', 'installationId', 'installationName']
        
        for field_name in large_domain_fields:
            with self.subTest(field=field_name):
                field_section = self.soup.find(id=field_name)
                if field_section:
                    # Should have either a large domain note or a table with limited rows
                    large_domain_note = field_section.find(class_='large-domain-note')
                    table = field_section.find('table')
                    
                    if table:
                        rows = table.find_all('tr')[1:]  # Exclude header
                        # Should limit rows for large domains
                        self.assertLessEqual(len(rows), 25, 
                                           f"{field_name} table should limit rows for large domains")
                    
                    # Should have some indication it's a large domain
                    has_indication = (large_domain_note is not None or 
                                    (table and "more values" in str(table)))
                    self.assertTrue(has_indication, 
                                   f"{field_name} should indicate it's a large domain")

def run_field_coverage_analysis():
    """Run detailed analysis of field coverage"""
    print("\n" + "="*60)
    print("FIELD COVERAGE ANALYSIS")
    print("="*60)
    
    # Parse expected fields
    xml_file = Path("DATABASE_EXPORT.XML")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    namespaces = {
        'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }
    
    # Find Building_A feature class
    building_a = None
    for feature_class in root.findall(".//DataElement[@xsi:type='esri:DEFeatureClass']", namespaces):
        name_elem = feature_class.find("Name", namespaces)
        if name_elem is not None and name_elem.text == "Building_A":
            building_a = feature_class
            break
    
    expected_fields = []
    fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
    if fields_array:
        for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
            field_name = field.find("Name", namespaces).text
            expected_fields.append(field_name)
    
    print(f"Expected fields from XML: {len(expected_fields)}")
    
    # Check HTML file
    html_file = Path("building_a_complete_manual.html")
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check anchors
        found_anchors = []
        missing_anchors = []
        
        for field_name in expected_fields:
            anchor = soup.find(id=field_name)
            if anchor:
                found_anchors.append(field_name)
            else:
                missing_anchors.append(field_name)
        
        print(f"Fields with anchors: {len(found_anchors)}")
        print(f"Missing anchors: {len(missing_anchors)}")
        
        if missing_anchors:
            print(f"Missing anchor fields: {missing_anchors}")
        
        # Check specific important fields
        important_fields = ['country', 'buildingCondition', 'installationId', 'buildingOpStatus']
        print(f"\nChecking important fields:")
        for field in important_fields:
            anchor = soup.find(id=field)
            toc_link = soup.find('a', href=f'#{field}')
            print(f"  {field}: anchor={'✓' if anchor else '✗'}, toc={'✓' if toc_link else '✗'}")
    
    else:
        print("HTML file not found!")

if __name__ == '__main__':
    # Run coverage analysis first
    run_field_coverage_analysis()
    
    # Then run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    unittest.main(verbosity=2)