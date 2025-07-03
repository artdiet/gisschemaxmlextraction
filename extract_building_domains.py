#!/usr/bin/env python3
"""
Extract domain values from geodatabase XML for Building_A feature class
and save them to CSV format for Palantir Foundry integration
"""

import xml.etree.ElementTree as ET
import csv
import json
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
                        'name': name,
                        'code': code
                    })
            
            domain_fields[field_name] = {
                'alias': field_alias,
                'domain_name': domain_name,
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
                'domain_name': domain_name,
                'domain_type': 'Range',
                'min_value': min_val,
                'max_value': max_val
            }
    
    return domain_fields

def export_to_csv(domain_fields, output_file):
    """Export domain values to CSV format"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Field Name', 'Field Alias', 'Domain Type', 'Domain Name', 'Option Name', 'Option Code', 'Min Value', 'Max Value'])
        
        # Write data
        for field_name, field_info in domain_fields.items():
            if field_info['domain_type'] == 'CodedValue':
                # Write each coded value as a separate row
                for value in field_info['values']:
                    writer.writerow([
                        field_name,
                        field_info['alias'],
                        field_info['domain_type'],
                        field_info['domain_name'],
                        value['name'],
                        value['code'],
                        '',  # Min value (empty for coded domains)
                        ''   # Max value (empty for coded domains)
                    ])
            elif field_info['domain_type'] == 'Range':
                # Write range domain
                writer.writerow([
                    field_name,
                    field_info['alias'],
                    field_info['domain_type'],
                    field_info['domain_name'],
                    '',  # Option name (empty for range domains)
                    '',  # Option code (empty for range domains)
                    field_info['min_value'],
                    field_info['max_value']
                ])

def export_to_json(domain_fields, output_file):
    """Export domain values to JSON format for easier processing"""
    
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(domain_fields, jsonfile, indent=2, ensure_ascii=False)

def main():
    # Input and output files
    xml_file = Path("DATABASE_EXPORT.XML")
    csv_output = Path("building_a_domains.csv")
    json_output = Path("building_a_domains.json")
    
    print(f"Processing {xml_file}...")
    
    # Parse XML and extract domains
    domain_fields = parse_geodatabase_xml(xml_file)
    
    if domain_fields:
        print(f"\nFound {len(domain_fields)} fields with domains in Building_A:")
        for field_name, field_info in domain_fields.items():
            print(f"  - {field_name} ({field_info['alias']}): {field_info['domain_type']} domain")
            if field_info['domain_type'] == 'CodedValue':
                print(f"    Options: {len(field_info['values'])}")
        
        # Export to CSV
        export_to_csv(domain_fields, csv_output)
        print(f"\nExported to CSV: {csv_output}")
        
        # Export to JSON
        export_to_json(domain_fields, json_output)
        print(f"Exported to JSON: {json_output}")
        
        # Print summary
        print("\nSummary of domains:")
        print("-" * 50)
        for field_name, field_info in domain_fields.items():
            print(f"\n{field_info['alias']} ({field_name}):")
            if field_info['domain_type'] == 'CodedValue':
                for value in field_info['values'][:5]:  # Show first 5 values
                    print(f"  - {value['name']} = {value['code']}")
                if len(field_info['values']) > 5:
                    print(f"  ... and {len(field_info['values']) - 5} more options")
            else:
                print(f"  Range: {field_info['min_value']} to {field_info['max_value']}")
    else:
        print("No domain fields found or error occurred.")

if __name__ == "__main__":
    main()