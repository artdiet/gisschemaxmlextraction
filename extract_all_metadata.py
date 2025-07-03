#!/usr/bin/env python3
"""
Complete metadata extraction for all fields in Building_A feature class
Captures every available metadata property for each field
"""

import xml.etree.ElementTree as ET
import csv
import json
from pathlib import Path
from collections import OrderedDict

def extract_complete_field_metadata(field, namespaces, all_domains):
    """Extract all possible metadata from a field definition"""
    
    metadata = OrderedDict()
    
    # Basic field properties
    metadata['name'] = field.find("Name", namespaces).text if field.find("Name", namespaces) is not None else ''
    metadata['alias_name'] = field.find("AliasName", namespaces).text if field.find("AliasName", namespaces) is not None else ''
    metadata['model_name'] = field.find("ModelName", namespaces).text if field.find("ModelName", namespaces) is not None else ''
    metadata['type'] = field.find("Type", namespaces).text if field.find("Type", namespaces) is not None else ''
    
    # Field constraints and properties
    metadata['is_nullable'] = field.find("IsNullable", namespaces).text if field.find("IsNullable", namespaces) is not None else ''
    metadata['length'] = field.find("Length", namespaces).text if field.find("Length", namespaces) is not None else ''
    metadata['precision'] = field.find("Precision", namespaces).text if field.find("Precision", namespaces) is not None else ''
    metadata['scale'] = field.find("Scale", namespaces).text if field.find("Scale", namespaces) is not None else ''
    metadata['required'] = field.find("Required", namespaces).text if field.find("Required", namespaces) is not None else ''
    metadata['editable'] = field.find("Editable", namespaces).text if field.find("Editable", namespaces) is not None else ''
    
    # Default value
    default_val = field.find("DefaultValue", namespaces)
    metadata['default_value'] = default_val.text if default_val is not None else ''
    metadata['default_value_type'] = default_val.get('{http://www.w3.org/2001/XMLSchema-instance}type') if default_val is not None else ''
    
    # XML schema type
    metadata['xsi_type'] = field.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
    
    # Domain information
    domain = field.find("Domain", namespaces)
    if domain is not None:
        domain_name = domain.find("DomainName", namespaces)
        metadata['has_domain'] = 'true'
        metadata['domain_name'] = domain_name.text if domain_name is not None else ''
        metadata['domain_type'] = domain.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
        metadata['domain_field_type'] = domain.find("FieldType", namespaces).text if domain.find("FieldType", namespaces) is not None else ''
        metadata['domain_merge_policy'] = domain.find("MergePolicy", namespaces).text if domain.find("MergePolicy", namespaces) is not None else ''
        metadata['domain_split_policy'] = domain.find("SplitPolicy", namespaces).text if domain.find("SplitPolicy", namespaces) is not None else ''
        metadata['domain_description'] = domain.find("Description", namespaces).text if domain.find("Description", namespaces) is not None else ''
        metadata['domain_owner'] = domain.find("Owner", namespaces).text if domain.find("Owner", namespaces) is not None else ''
        
        # For coded value domains
        if 'CodedValueDomain' in metadata['domain_type']:
            coded_values = domain.find("CodedValues[@xsi:type='esri:ArrayOfCodedValue']", namespaces)
            if coded_values:
                values_count = len(coded_values.findall("CodedValue[@xsi:type='esri:CodedValue']", namespaces))
                metadata['domain_values_count'] = str(values_count)
            else:
                metadata['domain_values_count'] = '0'
        
        # For range domains
        elif 'RangeDomain' in metadata['domain_type']:
            min_val = domain.find("MinValue", namespaces)
            max_val = domain.find("MaxValue", namespaces)
            metadata['domain_min_value'] = min_val.text if min_val is not None else ''
            metadata['domain_max_value'] = max_val.text if max_val is not None else ''
            metadata['domain_min_value_type'] = min_val.get('{http://www.w3.org/2001/XMLSchema-instance}type') if min_val is not None else ''
            metadata['domain_max_value_type'] = max_val.get('{http://www.w3.org/2001/XMLSchema-instance}type') if max_val is not None else ''
    else:
        metadata['has_domain'] = 'false'
        metadata['domain_name'] = ''
        metadata['domain_type'] = ''
        metadata['domain_field_type'] = ''
        metadata['domain_merge_policy'] = ''
        metadata['domain_split_policy'] = ''
        metadata['domain_description'] = ''
        metadata['domain_owner'] = ''
        metadata['domain_values_count'] = ''
        metadata['domain_min_value'] = ''
        metadata['domain_max_value'] = ''
        metadata['domain_min_value_type'] = ''
        metadata['domain_max_value_type'] = ''
    
    # Geometry definition (for geometry fields)
    geom_def = field.find("GeometryDef", namespaces)
    if geom_def is not None:
        metadata['has_geometry_def'] = 'true'
        metadata['geometry_type'] = geom_def.find("GeometryType", namespaces).text if geom_def.find("GeometryType", namespaces) is not None else ''
        metadata['geometry_has_m'] = geom_def.find("HasM", namespaces).text if geom_def.find("HasM", namespaces) is not None else ''
        metadata['geometry_has_z'] = geom_def.find("HasZ", namespaces).text if geom_def.find("HasZ", namespaces) is not None else ''
        metadata['geometry_avg_points'] = geom_def.find("AvgNumPoints", namespaces).text if geom_def.find("AvgNumPoints", namespaces) is not None else ''
        metadata['geometry_grid_size'] = geom_def.find("GridSize0", namespaces).text if geom_def.find("GridSize0", namespaces) is not None else ''
    else:
        metadata['has_geometry_def'] = 'false'
        metadata['geometry_type'] = ''
        metadata['geometry_has_m'] = ''
        metadata['geometry_has_z'] = ''
        metadata['geometry_avg_points'] = ''
        metadata['geometry_grid_size'] = ''
    
    return metadata

def parse_all_domains(root, namespaces):
    """Extract all domain definitions from the workspace level"""
    domains = {}
    
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
            
            domains[domain_name] = domain_info
    
    return domains

def main():
    xml_file = Path("DATABASE_EXPORT.XML")
    metadata_csv = Path("building_a_complete_metadata.csv")
    metadata_json = Path("building_a_complete_metadata.json")
    
    print(f"Processing {xml_file}...")
    
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespaces
    namespaces = {
        'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }
    
    # Extract all domains
    all_domains = parse_all_domains(root, namespaces)
    
    # Find Building_A feature class
    building_a = None
    for feature_class in root.findall(".//DataElement[@xsi:type='esri:DEFeatureClass']", namespaces):
        name_elem = feature_class.find("Name", namespaces)
        if name_elem is not None and name_elem.text == "Building_A":
            building_a = feature_class
            break
    
    if not building_a:
        print("Building_A feature class not found!")
        return
    
    # Extract all fields with complete metadata
    all_fields_metadata = []
    
    fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
    if fields_array is None:
        print("No fields found in Building_A")
        return
    
    for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
        metadata = extract_complete_field_metadata(field, namespaces, all_domains)
        all_fields_metadata.append(metadata)
    
    print(f"Extracted complete metadata for {len(all_fields_metadata)} fields")
    
    # Export to CSV
    if all_fields_metadata:
        with open(metadata_csv, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all possible column names from all fields
            all_columns = set()
            for field_meta in all_fields_metadata:
                all_columns.update(field_meta.keys())
            
            # Sort columns for consistent output
            columns = sorted(list(all_columns))
            
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for field_meta in all_fields_metadata:
                writer.writerow(field_meta)
        
        print(f"Exported complete metadata to CSV: {metadata_csv}")
        
        # Export to JSON for easier programmatic access
        with open(metadata_json, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_fields_metadata, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Exported complete metadata to JSON: {metadata_json}")
        
        # Print summary of metadata properties found
        print(f"\nMetadata properties found across all fields:")
        all_props = set()
        for field_meta in all_fields_metadata:
            all_props.update(field_meta.keys())
        
        for prop in sorted(all_props):
            print(f"  - {prop}")
        
        print(f"\nTotal metadata properties: {len(all_props)}")
        
        # Show fields with most complete metadata
        print(f"\nFields with domain definitions:")
        domain_fields = [f for f in all_fields_metadata if f['has_domain'] == 'true']
        for field in domain_fields[:10]:
            print(f"  - {field['name']} ({field['alias_name']}): {field['domain_type']}")
        if len(domain_fields) > 10:
            print(f"  ... and {len(domain_fields) - 10} more")

if __name__ == "__main__":
    main()