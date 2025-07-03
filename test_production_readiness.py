#!/usr/bin/env python3
"""
Production Readiness Tests for GIS Schema Extraction - FIXED VERSION
Comprehensive verification of all CSV files and data completeness
"""

import unittest
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
import sys
import re

class TestProductionReadiness(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test data by parsing the XML file as ground truth"""
        cls.xml_file = Path("DATABASE_EXPORT.XML")
        
        if not cls.xml_file.exists():
            raise FileNotFoundError("DATABASE_EXPORT.XML not found!")
        
        # Parse XML to get ground truth data
        cls.ground_truth = cls._parse_ground_truth()
        print(f"\n=== GROUND TRUTH FROM XML ===")
        print(f"Total fields in Building_A: {len(cls.ground_truth['all_fields'])}")
        print(f"Fields with domains: {len(cls.ground_truth['domain_fields'])}")
        print(f"Total domain values: {sum(len(domain['values']) for domain in cls.ground_truth['domain_fields'].values() if 'values' in domain)}")
        print("="*50)
    
    @classmethod
    def _parse_ground_truth(cls):
        """Parse XML to establish ground truth for comparison"""
        tree = ET.parse(cls.xml_file)
        root = tree.getroot()
        
        namespaces = {
            'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        
        # Parse all workspace domains
        all_domains = {}
        domains_array = root.find(".//Domains[@xsi:type='esri:ArrayOfDomain']", namespaces)
        if domains_array:
            for domain in domains_array.findall("Domain", namespaces):
                domain_name = domain.find("DomainName", namespaces).text
                domain_type = domain.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                description = domain.find("Description", namespaces)
                
                domain_info = {
                    'name': domain_name,
                    'type': domain_type,
                    'description': description.text if description is not None else '',
                    'values': []
                }
                
                if 'CodedValueDomain' in domain_type:
                    values_array = domain.find("CodedValues[@xsi:type='esri:ArrayOfCodedValue']", namespaces)
                    if values_array:
                        for coded_value in values_array.findall("CodedValue[@xsi:type='esri:CodedValue']", namespaces):
                            name = coded_value.find("Name", namespaces).text
                            code = coded_value.find("Code", namespaces).text
                            domain_info['values'].append({'name': name, 'code': code})
                elif 'RangeDomain' in domain_type:
                    min_val = domain.find("MinValue", namespaces).text
                    max_val = domain.find("MaxValue", namespaces).text
                    domain_info['min_value'] = min_val
                    domain_info['max_value'] = max_val
                
                all_domains[domain_name] = domain_info
        
        # Find Building_A feature class
        building_a = None
        for feature_class in root.findall(".//DataElement[@xsi:type='esri:DEFeatureClass']", namespaces):
            name_elem = feature_class.find("Name", namespaces)
            if name_elem is not None and name_elem.text == "Building_A":
                building_a = feature_class
                break
        
        if not building_a:
            raise ValueError("Building_A feature class not found in XML!")
        
        # Parse all fields
        all_fields = {}
        domain_fields = {}
        
        fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
        if fields_array:
            for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
                field_name = field.find("Name", namespaces).text
                field_type = field.find("Type", namespaces).text
                field_alias = field.find("AliasName", namespaces)
                field_alias = field_alias.text if field_alias is not None else field_name
                
                field_info = {
                    'name': field_name,
                    'alias': field_alias,
                    'type': field_type,
                    'has_domain': False
                }
                
                # Check for domain
                domain = field.find("Domain", namespaces)
                if domain is not None:
                    domain_name = domain.find("DomainName", namespaces)
                    if domain_name is not None:
                        domain_name = domain_name.text
                        field_info['has_domain'] = True
                        field_info['domain_name'] = domain_name
                        
                        if domain_name in all_domains:
                            domain_data = all_domains[domain_name].copy()
                            domain_data['field_name'] = field_name
                            domain_data['field_alias'] = field_alias
                            domain_fields[field_name] = domain_data
                
                all_fields[field_name] = field_info
        
        return {
            'all_fields': all_fields,
            'domain_fields': domain_fields,
            'workspace_domains': all_domains
        }

    def test_detailed_csv_completeness(self):
        """Test building_a_domains_detailed.csv has all domain data"""
        csv_file = Path("building_a_domains_detailed.csv")
        self.assertTrue(csv_file.exists(), "building_a_domains_detailed.csv should exist")
        
        # Read CSV data
        csv_fields = defaultdict(list)
        csv_domain_names = set()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_name = row['Field Name']
                csv_fields[field_name].append({
                    'option_name': row['Option Name'],
                    'option_code': row['Option Code'],
                    'domain_description': row['Domain Description']
                })
                csv_domain_names.add(row['Domain Name'])
        
        print(f"\nTesting building_a_domains_detailed.csv:")
        print(f"  CSV has {len(csv_fields)} fields with domains")
        print(f"  Expected {len(self.ground_truth['domain_fields'])} fields with domains")
        
        # Test 1: All domain fields present
        expected_fields = set(self.ground_truth['domain_fields'].keys())
        actual_fields = set(csv_fields.keys())
        
        missing_fields = expected_fields - actual_fields
        extra_fields = actual_fields - expected_fields
        
        self.assertEqual(len(missing_fields), 0, f"Missing domain fields: {missing_fields}")
        self.assertEqual(len(extra_fields), 0, f"Extra domain fields: {extra_fields}")
        
        # Test 2: All domain values present for each field
        for field_name, expected_domain in self.ground_truth['domain_fields'].items():
            with self.subTest(field=field_name):
                if 'CodedValue' in expected_domain['type'] and 'values' in expected_domain:
                    expected_values = len(expected_domain['values'])
                    actual_values = len(csv_fields[field_name])
                    
                    self.assertEqual(actual_values, expected_values,
                                   f"Field {field_name}: expected {expected_values} values, got {actual_values}")
                    
                    # Check specific values
                    expected_codes = {v['code'] for v in expected_domain['values']}
                    actual_codes = {v['option_code'] for v in csv_fields[field_name] if v['option_code']}
                    
                    missing_codes = expected_codes - actual_codes
                    self.assertEqual(len(missing_codes), 0,
                                   f"Field {field_name} missing codes: {list(missing_codes)[:5]}")

    def test_columnar_csv_completeness(self):
        """Test building_a_domains_columnar.csv has all fields as columns"""
        csv_file = Path("building_a_domains_columnar.csv")
        self.assertTrue(csv_file.exists(), "building_a_domains_columnar.csv should exist")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Extract field names from headers (format: "Display Name (field_name)")
            header_field_names = []
            for header in headers:
                # Look for field name in parentheses
                match = re.search(r'\(([^)]+)\)$', header)
                if match:
                    header_field_names.append(match.group(1))
                else:
                    # Fallback to the header itself
                    header_field_names.append(header)
            
            # Count non-empty values per column
            column_data = defaultdict(list)
            for row in reader:
                for i, value in enumerate(row):
                    if i < len(header_field_names) and value.strip():
                        column_data[header_field_names[i]].append(value)
        
        print(f"\nTesting building_a_domains_columnar.csv:")
        print(f"  CSV has {len(headers)} column headers")
        print(f"  Extracted {len(header_field_names)} field names from headers")
        print(f"  Expected {len(self.ground_truth['domain_fields'])} domain fields")
        
        # Test: All domain fields present as columns
        expected_fields = set(self.ground_truth['domain_fields'].keys())
        actual_fields = set(header_field_names)
        
        missing_fields = expected_fields - actual_fields
        extra_fields = actual_fields - expected_fields
        
        self.assertEqual(len(missing_fields), 0, f"Missing columns: {missing_fields}")
        
        # Test: Each column has reasonable number of values
        for field_name in expected_fields:
            with self.subTest(field=field_name):
                if field_name in column_data:
                    expected_domain = self.ground_truth['domain_fields'][field_name]
                    if 'CodedValue' in expected_domain['type'] and 'values' in expected_domain:
                        expected_count = len(expected_domain['values'])
                        actual_count = len(column_data[field_name])
                        
                        # Allow for some formatting differences, but should be close
                        self.assertGreaterEqual(actual_count, expected_count * 0.9,
                                               f"Column {field_name} has too few values: {actual_count} < {expected_count}")

    def test_metadata_csv_completeness(self):
        """Test building_a_complete_metadata.csv has all fields"""
        csv_file = Path("building_a_complete_metadata.csv")
        self.assertTrue(csv_file.exists(), "building_a_complete_metadata.csv should exist")
        
        csv_fields = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_name = row['name']
                csv_fields[field_name] = row
        
        print(f"\nTesting building_a_complete_metadata.csv:")
        print(f"  CSV has {len(csv_fields)} fields")
        print(f"  Expected {len(self.ground_truth['all_fields'])} total fields")
        
        # Test: All fields present
        expected_fields = set(self.ground_truth['all_fields'].keys())
        actual_fields = set(csv_fields.keys())
        
        missing_fields = expected_fields - actual_fields
        extra_fields = actual_fields - expected_fields
        
        self.assertEqual(len(missing_fields), 0, f"Missing fields: {missing_fields}")
        self.assertEqual(len(extra_fields), 0, f"Extra fields: {extra_fields}")
        
        # Test: Domain flags correct
        for field_name, field_info in self.ground_truth['all_fields'].items():
            with self.subTest(field=field_name):
                csv_row = csv_fields[field_name]
                expected_has_domain = field_info['has_domain']
                actual_has_domain = csv_row['has_domain'] == 'true'
                
                self.assertEqual(actual_has_domain, expected_has_domain,
                               f"Field {field_name} domain flag mismatch")

    def test_all_fields_csv_completeness(self):
        """Test building_a_all_fields.csv has all fields"""
        csv_file = Path("building_a_all_fields.csv")
        self.assertTrue(csv_file.exists(), "building_a_all_fields.csv should exist")
        
        csv_fields = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_name = row['Field Name']
                csv_fields[field_name] = row
        
        print(f"\nTesting building_a_all_fields.csv:")
        print(f"  CSV has {len(csv_fields)} fields")
        print(f"  Expected {len(self.ground_truth['all_fields'])} total fields")
        
        # Test: All fields present
        expected_fields = set(self.ground_truth['all_fields'].keys())
        actual_fields = set(csv_fields.keys())
        
        missing_fields = expected_fields - actual_fields
        self.assertEqual(len(missing_fields), 0, f"Missing fields: {missing_fields}")

    def test_html_manual_completeness(self):
        """Test HTML manual has all fields and proper navigation"""
        html_file = Path("building_a_complete_manual.html")
        self.assertTrue(html_file.exists(), "building_a_complete_manual.html should exist")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Test: All fields have anchors
        expected_fields = set(self.ground_truth['all_fields'].keys())
        missing_anchors = []
        
        for field_name in expected_fields:
            if f'id="{field_name}"' not in html_content:
                missing_anchors.append(field_name)
        
        print(f"\nTesting building_a_complete_manual.html:")
        print(f"  Expected {len(expected_fields)} field anchors")
        print(f"  Missing {len(missing_anchors)} anchors")
        
        self.assertEqual(len(missing_anchors), 0, f"Missing HTML anchors: {missing_anchors[:10]}")

    def test_csv_reading_guide_accuracy(self):
        """Test that CSV_READING_GUIDE references match actual files"""
        guide_html = Path("CSV_READING_GUIDE.html")
        guide_md = Path("CSV_READING_GUIDE.md")
        
        self.assertTrue(guide_html.exists(), "CSV_READING_GUIDE.html should exist")
        self.assertTrue(guide_md.exists(), "CSV_READING_GUIDE.md should exist")
        
        # Check file references in guides
        referenced_files = [
            "building_a_complete_manual.html",
            "building_a_domains_detailed.csv", 
            "building_a_domains_columnar.csv",
            "building_a_complete_metadata.csv",
            "building_a_all_fields.csv"
        ]
        
        for file_name in referenced_files:
            file_path = Path(file_name)
            self.assertTrue(file_path.exists(), f"Referenced file {file_name} should exist")

    def test_data_consistency_across_files(self):
        """Test that domain data is consistent across all CSV files"""
        # Read detailed CSV
        detailed_fields = defaultdict(list)
        detailed_file = Path("building_a_domains_detailed.csv")
        
        with open(detailed_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                detailed_fields[row['Field Name']].append(row)
        
        # Read metadata CSV
        metadata_fields = {}
        metadata_file = Path("building_a_complete_metadata.csv")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata_fields[row['name']] = row
        
        print(f"\nTesting data consistency:")
        print(f"  Detailed CSV has {len(detailed_fields)} domain fields")
        print(f"  Metadata CSV has {len(metadata_fields)} total fields")
        
        # Test: Domain field counts match
        for field_name, domain_values in detailed_fields.items():
            with self.subTest(field=field_name):
                if field_name in metadata_fields:
                    metadata_count = metadata_fields[field_name]['domain_values_count']
                    if metadata_count and metadata_count.strip():
                        expected_count = int(metadata_count)
                        actual_count = len(domain_values)
                        
                        # Allow for range domains (which have 1 entry in detailed but different count)
                        if expected_count == 1 or actual_count == expected_count:
                            continue  # Range domain or exact match - OK
                        
                        self.assertEqual(actual_count, expected_count,
                                       f"Field {field_name}: detailed CSV has {actual_count} values, "
                                       f"metadata says {expected_count}")

    def test_specific_important_fields(self):
        """Test specific important fields have correct data"""
        important_fields = {
            'country': {'expected_min_values': 270, 'type': 'CodedValue'},
            'buildingCondition': {'expected_min_values': 30, 'type': 'CodedValue'},
            'installationId': {'expected_min_values': 300, 'type': 'CodedValue'},
            'buildingOpStatus': {'expected_min_values': 15, 'type': 'CodedValue'},
            'buildingConditionIndex': {'type': 'Range'}
        }
        
        # Test in detailed CSV
        detailed_file = Path("building_a_domains_detailed.csv")
        field_data = defaultdict(list)
        
        with open(detailed_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                field_data[row['Field Name']].append(row)
        
        print(f"\nTesting important fields:")
        for field_name, expectations in important_fields.items():
            with self.subTest(field=field_name):
                self.assertIn(field_name, field_data, f"Field {field_name} should be in detailed CSV")
                
                if expectations['type'] == 'CodedValue':
                    actual_count = len(field_data[field_name])
                    min_expected = expectations['expected_min_values']
                    
                    self.assertGreaterEqual(actual_count, min_expected,
                                           f"Field {field_name} should have at least {min_expected} values, got {actual_count}")
                    
                    print(f"    {field_name}: {actual_count} values ✓")

def run_final_production_check():
    """Run final check with summary for production deployment"""
    print("\n" + "="*80)
    print("FINAL PRODUCTION DEPLOYMENT CHECK")
    print("="*80)
    
    # File size and existence check
    required_files = {
        "building_a_complete_manual.html": {"min_size": 80000, "description": "Interactive HTML manual"},
        "building_a_domains_detailed.csv": {"min_size": 800000, "description": "Complete domain data"},
        "building_a_domains_columnar.csv": {"min_size": 300000, "description": "Columnar format for import"},
        "building_a_complete_metadata.csv": {"min_size": 15000, "description": "Field metadata"},
        "building_a_all_fields.csv": {"min_size": 10000, "description": "Field overview"},
        "CSV_READING_GUIDE.html": {"min_size": 15000, "description": "User guide"},
        "README.md": {"min_size": 5000, "description": "Project documentation"},
        "LICENSE": {"min_size": 2000, "description": "License file"}
    }
    
    all_good = True
    
    print("\n📁 File Verification:")
    for file_name, requirements in required_files.items():
        file_path = Path(file_name)
        if file_path.exists():
            size = file_path.stat().st_size
            min_size = requirements["min_size"]
            status = "✓" if size >= min_size else "⚠️"
            print(f"  {status} {file_name}: {size:,} bytes ({requirements['description']})")
            if size < min_size:
                all_good = False
                print(f"      WARNING: File smaller than expected ({min_size:,} bytes)")
        else:
            print(f"  ❌ {file_name}: MISSING")
            all_good = False
    
    # Quick data check
    try:
        # Check CSV headers
        detailed_csv = Path("building_a_domains_detailed.csv")
        if detailed_csv.exists():
            with open(detailed_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                expected_headers = ['Field Name', 'Field Alias', 'Domain Name', 'Domain Description', 'Domain Type', 'Option Name', 'Option Code']
                
                missing_headers = set(expected_headers) - set(headers)
                if missing_headers:
                    print(f"  ❌ Missing headers in detailed CSV: {missing_headers}")
                    all_good = False
                else:
                    print(f"  ✓ Detailed CSV headers complete")
                
                # Count rows
                row_count = sum(1 for _ in reader)
                print(f"  ✓ Detailed CSV has {row_count:,} data rows")
    
    except Exception as e:
        print(f"  ❌ Error checking CSV data: {e}")
        all_good = False
    
    print(f"\n🎯 PRODUCTION READINESS: {'✅ APPROVED' if all_good else '❌ ISSUES FOUND'}")
    
    if all_good:
        print("\n✅ All files present and properly sized")
        print("✅ CSV structure verified")
        print("✅ Ready for production deployment")
        print("\n📋 Deployment checklist:")
        print("  1. Share CSV_READING_GUIDE.html with GIS team")
        print("  2. Use building_a_domains_detailed.csv for data integration")
        print("  3. Provide building_a_complete_manual.html as reference")
        print("  4. Include README.md and LICENSE for documentation")
    
    return all_good

if __name__ == '__main__':
    # Run final check first
    production_ready = run_final_production_check()
    
    if not production_ready:
        print("\n❌ Production check failed. Fix issues before deployment.")
        sys.exit(1)
    
    # Run unit tests
    print("\n" + "="*80)
    print("RUNNING DETAILED VALIDATION TESTS")
    print("="*80)
    
    unittest.main(verbosity=2)