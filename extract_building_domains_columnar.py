#!/usr/bin/env python3
"""
Extract domain values from geodatabase XML for Building_A feature class
and save them in columnar CSV format (attributes as columns, options as rows)
"""

import xml.etree.ElementTree as ET
import csv
from pathlib import Path

def parse_geodatabase_xml(xml_file):
    """Parse geodatabase XML and extract Building_A field domains"""
    
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespaces
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
        print("Building_A feature class not found!")
        return None
    
    # Extract fields with domains
    domain_fields = {}
    
    fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
    if fields_array is None:
        print("No fields found in Building_A")
        return None
    
    for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
        field_name = field.find("Name", namespaces).text
        field_alias = field.find("AliasName", namespaces)
        if field_alias is not None:
            field_alias = field_alias.text
        else:
            field_alias = field_name
            
        # Check for CodedValueDomain
        domain = field.find("Domain[@xsi:type='esri:CodedValueDomain']", namespaces)
        if domain:
            domain_name = domain.find("DomainName", namespaces).text
            coded_values = []
            
            values_array = domain.find("CodedValues[@xsi:type='esri:ArrayOfCodedValue']", namespaces)
            if values_array:
                for coded_value in values_array.findall("CodedValue[@xsi:type='esri:CodedValue']", namespaces):
                    name = coded_value.find("Name", namespaces).text
                    code = coded_value.find("Code", namespaces).text
                    coded_values.append({
                        'display': f"{name} ({code})",
                        'name': name,
                        'code': code
                    })
            
            domain_fields[field_name] = {
                'alias': field_alias,
                'domain_type': 'CodedValue',
                'values': coded_values
            }
        
        # Check for RangeDomain
        range_domain = field.find("Domain[@xsi:type='esri:RangeDomain']", namespaces)
        if range_domain:
            domain_name = range_domain.find("DomainName", namespaces).text
            min_val = range_domain.find("MinValue", namespaces).text
            max_val = range_domain.find("MaxValue", namespaces).text
            
            domain_fields[field_name] = {
                'alias': field_alias,
                'domain_type': 'Range',
                'values': [{
                    'display': f"Range: {min_val} to {max_val}",
                    'name': f"{min_val} to {max_val}",
                    'code': ''
                }]
            }
    
    return domain_fields

def export_to_columnar_csv(domain_fields, output_file):
    """Export domain values to columnar CSV format"""
    
    # Find the maximum number of values across all fields
    max_values = max(len(field_info['values']) for field_info in domain_fields.values())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Create header row with field names (using aliases for readability)
        headers = []
        field_order = []
        for field_name, field_info in sorted(domain_fields.items()):
            headers.append(f"{field_info['alias']} ({field_name})")
            field_order.append(field_name)
        
        writer.writerow(headers)
        
        # Write value rows
        for i in range(max_values):
            row = []
            for field_name in field_order:
                values = domain_fields[field_name]['values']
                if i < len(values):
                    row.append(values[i]['display'])
                else:
                    row.append('')  # Empty cell if this field has fewer values
            writer.writerow(row)

def export_codes_only_csv(domain_fields, output_file):
    """Export only the codes in columnar format"""
    
    # Find the maximum number of values across all fields
    max_values = max(len(field_info['values']) for field_info in domain_fields.values())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Create header row with field names
        headers = []
        field_order = []
        for field_name, field_info in sorted(domain_fields.items()):
            headers.append(field_name)
            field_order.append(field_name)
        
        writer.writerow(headers)
        
        # Write code value rows
        for i in range(max_values):
            row = []
            for field_name in field_order:
                values = domain_fields[field_name]['values']
                if i < len(values):
                    if domain_fields[field_name]['domain_type'] == 'Range':
                        row.append(values[i]['name'])  # For range, use the range description
                    else:
                        row.append(values[i]['code'])  # For coded values, use the code
                else:
                    row.append('')  # Empty cell if this field has fewer values
            writer.writerow(row)

def main():
    # Input and output files
    xml_file = Path("DATABASE_EXPORT.XML")
    columnar_output = Path("building_a_domains_columnar.csv")
    codes_output = Path("building_a_domains_codes_only.csv")
    
    print(f"Processing {xml_file}...")
    
    # Parse XML and extract domains
    domain_fields = parse_geodatabase_xml(xml_file)
    
    if domain_fields:
        print(f"\nFound {len(domain_fields)} fields with domains in Building_A")
        
        # Export to columnar CSV with display values
        export_to_columnar_csv(domain_fields, columnar_output)
        print(f"\nExported columnar format with display values to: {columnar_output}")
        
        # Export to columnar CSV with codes only
        export_codes_only_csv(domain_fields, codes_output)
        print(f"Exported columnar format with codes only to: {codes_output}")
        
        # Print summary
        print("\nColumn headers created:")
        for field_name, field_info in sorted(domain_fields.items()):
            print(f"  - {field_info['alias']} ({field_name}): {len(field_info['values'])} values")
        
    else:
        print("No domain fields found or error occurred.")

if __name__ == "__main__":
    main()