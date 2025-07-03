#!/usr/bin/env python3
"""
Complete extraction of domain values from geodatabase XML for Building_A feature class
Includes domain descriptions and ensures all fields are captured
"""

import xml.etree.ElementTree as ET
import csv
import json
from pathlib import Path
from collections import OrderedDict

def parse_all_domains(root, namespaces):
    """Extract all domain definitions from the workspace level"""
    domains = {}
    
    # Find all domains at the workspace level
    domains_array = root.find(".//Domains[@xsi:type='esri:ArrayOfDomain']", namespaces)
    if domains_array is not None:
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
                        domain_info['values'].append({
                            'name': name,
                            'code': code
                        })
            elif 'RangeDomain' in domain_type:
                min_val = domain.find("MinValue", namespaces).text
                max_val = domain.find("MaxValue", namespaces).text
                domain_info['min_value'] = min_val
                domain_info['max_value'] = max_val
            
            domains[domain_name] = domain_info
    
    return domains

def parse_building_a_complete(xml_file):
    """Parse geodatabase XML and extract all Building_A fields with their domains"""
    
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespaces
    namespaces = {
        'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }
    
    # First, extract all domains from workspace level
    all_domains = parse_all_domains(root, namespaces)
    print(f"Found {len(all_domains)} domain definitions at workspace level")
    
    # Find Building_A feature class
    building_a = None
    for feature_class in root.findall(".//DataElement[@xsi:type='esri:DEFeatureClass']", namespaces):
        name_elem = feature_class.find("Name", namespaces)
        if name_elem is not None and name_elem.text == "Building_A":
            building_a = feature_class
            break
    
    if not building_a:
        print("Building_A feature class not found!")
        return None, None
    
    # Extract all fields
    all_fields = OrderedDict()
    fields_with_domains = OrderedDict()
    
    fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
    if fields_array is None:
        print("No fields found in Building_A")
        return None, None
    
    field_count = 0
    for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
        field_count += 1
        field_name = field.find("Name", namespaces).text
        field_type = field.find("Type", namespaces).text
        field_alias = field.find("AliasName", namespaces)
        if field_alias is not None:
            field_alias = field_alias.text
        else:
            field_alias = field_name
        
        # Store all field info
        field_info = {
            'name': field_name,
            'alias': field_alias,
            'type': field_type,
            'has_domain': False,
            'domain_name': None
        }
        
        # Check for inline domain definition
        domain = field.find("Domain", namespaces)
        if domain is not None:
            domain_name = domain.find("DomainName", namespaces)
            if domain_name is not None:
                domain_name = domain_name.text
                field_info['has_domain'] = True
                field_info['domain_name'] = domain_name
                
                # Get domain info from workspace domains
                if domain_name in all_domains:
                    domain_data = all_domains[domain_name]
                    fields_with_domains[field_name] = {
                        'alias': field_alias,
                        'field_type': field_type,
                        'domain_name': domain_name,
                        'domain_type': 'CodedValue' if 'CodedValue' in domain_data['type'] else 'Range',
                        'domain_description': domain_data['description'],
                        'values': domain_data.get('values', []),
                        'min_value': domain_data.get('min_value'),
                        'max_value': domain_data.get('max_value')
                    }
        
        all_fields[field_name] = field_info
    
    print(f"Total fields in Building_A: {field_count}")
    print(f"Fields with domains: {len(fields_with_domains)}")
    
    return all_fields, fields_with_domains

def export_complete_csv(all_fields, fields_with_domains, output_file):
    """Export complete field list with domain information"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Field Name', 'Field Alias', 'Field Type', 'Has Domain', 'Domain Name', 
                        'Domain Type', 'Domain Description', 'Sample Values'])
        
        # Write all fields
        for field_name, field_info in all_fields.items():
            sample_values = ''
            domain_type = ''
            domain_desc = ''
            
            if field_info['has_domain'] and field_name in fields_with_domains:
                domain_data = fields_with_domains[field_name]
                domain_type = domain_data['domain_type']
                domain_desc = domain_data['domain_description']
                
                if domain_type == 'CodedValue':
                    # Show first 3 values as samples
                    samples = []
                    for i, val in enumerate(domain_data['values'][:3]):
                        samples.append(f"{val['name']} ({val['code']})")
                    if len(domain_data['values']) > 3:
                        samples.append(f"... +{len(domain_data['values'])-3} more")
                    sample_values = '; '.join(samples)
                else:
                    sample_values = f"Range: {domain_data['min_value']} to {domain_data['max_value']}"
            
            writer.writerow([
                field_name,
                field_info['alias'],
                field_info['type'],
                'Yes' if field_info['has_domain'] else 'No',
                field_info['domain_name'] or '',
                domain_type,
                domain_desc,
                sample_values
            ])

def export_detailed_domains_csv(fields_with_domains, output_file):
    """Export detailed domain values with descriptions"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Field Name', 'Field Alias', 'Domain Name', 'Domain Description', 
                        'Domain Type', 'Option Name', 'Option Code', 'Min Value', 'Max Value'])
        
        # Write data
        for field_name, field_info in fields_with_domains.items():
            if field_info['domain_type'] == 'CodedValue':
                # Write each coded value as a separate row
                for value in field_info['values']:
                    writer.writerow([
                        field_name,
                        field_info['alias'],
                        field_info['domain_name'],
                        field_info['domain_description'],
                        field_info['domain_type'],
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
                    field_info['domain_name'],
                    field_info['domain_description'],
                    field_info['domain_type'],
                    '',  # Option name (empty for range domains)
                    '',  # Option code (empty for range domains)
                    field_info['min_value'],
                    field_info['max_value']
                ])

def main():
    # Input and output files
    xml_file = Path("DATABASE_EXPORT.XML")
    complete_fields_csv = Path("building_a_all_fields.csv")
    detailed_domains_csv = Path("building_a_domains_detailed.csv")
    
    print(f"Processing {xml_file}...")
    
    # Parse XML and extract all data
    all_fields, fields_with_domains = parse_building_a_complete(xml_file)
    
    if all_fields:
        # Export complete field list
        export_complete_csv(all_fields, fields_with_domains, complete_fields_csv)
        print(f"\nExported complete field list to: {complete_fields_csv}")
        
        # Export detailed domains
        export_detailed_domains_csv(fields_with_domains, detailed_domains_csv)
        print(f"Exported detailed domains to: {detailed_domains_csv}")
        
        # Print summary
        print("\nSummary:")
        print(f"Total fields: {len(all_fields)}")
        print(f"Fields with domains: {len(fields_with_domains)}")
        print(f"\nFields without domains: {len(all_fields) - len(fields_with_domains)}")
        
        # List fields without domains
        fields_without_domains = [name for name, info in all_fields.items() if not info['has_domain']]
        if fields_without_domains:
            print("\nFields without domains:")
            for field in fields_without_domains[:10]:
                print(f"  - {field}")
            if len(fields_without_domains) > 10:
                print(f"  ... and {len(fields_without_domains) - 10} more")
    else:
        print("No fields found or error occurred.")

if __name__ == "__main__":
    main()