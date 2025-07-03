#!/usr/bin/env python3
"""
Script to extract and analyze all field metadata properties from DATABASE_EXPORT.XML
for the Building_A feature class and other feature classes.
"""

import xml.etree.ElementTree as ET
import re
from collections import defaultdict

def extract_field_metadata(xml_file):
    """Extract all field metadata from the XML file."""
    
    # Parse the XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    print(f"Debug: Root element: {root.tag}")
    print(f"Debug: Root attributes: {root.attrib}")
    
    # Find all elements to understand the structure
    all_elements = set()
    for elem in root.iter():
        all_elements.add(elem.tag)
    print(f"Debug: Found {len(all_elements)} unique element types")
    for elem_type in sorted(all_elements):
        if 'DataElement' in elem_type or 'Field' in elem_type:
            print(f"  - {elem_type}")
    
    # Define namespaces
    ns = {
        'esri': 'http://www.esri.com/schemas/ArcGIS/10.8',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Find all DataElement elements that are feature classes
    # Look for elements with xsi:type attribute containing DEFeatureClass
    feature_classes = []
    data_elements_found = 0
    for elem in root.iter():
        if elem.tag == 'DataElement' or elem.tag.endswith('}DataElement'):
            data_elements_found += 1
            xsi_type = elem.get('{http://www.w3.org/2001/XMLSchema-instance}type')
            if xsi_type and 'DEFeatureClass' in xsi_type:
                feature_classes.append(elem)
                print(f"Debug: Found feature class: {elem.find('Name').text if elem.find('Name') is not None else 'Unknown'}")
    
    print(f"Debug: Found {data_elements_found} DataElement elements, {len(feature_classes)} are feature classes")
    
    field_metadata_properties = set()
    field_examples = []
    
    for fc in feature_classes:
        fc_name = fc.find("Name")
        if fc_name is not None:
            fc_name_text = fc_name.text
            
            # Find all fields in this feature class
            fields = []
            for elem in fc.iter():
                if elem.tag == 'Field' or elem.tag.endswith('}Field'):
                    fields.append(elem)
            
            print(f"Debug: Feature class {fc_name_text} has {len(fields)} fields")
            
            for field in fields:
                field_data = {}
                field_data['FeatureClass'] = fc_name_text
                
                # Extract all child elements from the field
                for child in field:
                    # Remove namespace prefix for cleaner property names
                    tag_name = child.tag
                    if tag_name.startswith('{'):
                        tag_name = tag_name.split('}')[1]
                    
                    field_metadata_properties.add(tag_name)
                    
                    if tag_name == 'Domain':
                        # Handle domain specially
                        domain_type = child.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}type', '')
                        field_data[tag_name] = f"Type: {domain_type}"
                        
                        # Get domain name
                        domain_name = child.find("DomainName")
                        if domain_name is not None:
                            field_data[tag_name] += f", Name: {domain_name.text}"
                    elif tag_name == 'GeometryDef':
                        # Handle geometry definition specially
                        geom_type = child.find("GeometryType")
                        if geom_type is not None:
                            field_data[tag_name] = f"Type: {geom_type.text}"
                    else:
                        field_data[tag_name] = child.text if child.text else ''
                
                # Add attributes if any
                for attr_name, attr_value in field.attrib.items():
                    if attr_name.startswith('{http://www.w3.org/2001/XMLSchema-instance}'):
                        clean_attr = attr_name.replace('{http://www.w3.org/2001/XMLSchema-instance}', 'xsi:')
                        field_metadata_properties.add(clean_attr)
                        field_data[clean_attr] = attr_value
                
                field_examples.append(field_data)
    
    return field_metadata_properties, field_examples

def find_fields_with_most_metadata(field_examples, top_n=5):
    """Find fields with the most metadata properties."""
    field_scores = []
    for field in field_examples:
        score = sum(1 for key, value in field.items() if value and value.strip())
        field_scores.append((score, field))
    
    # Sort by score descending
    field_scores.sort(key=lambda x: x[0], reverse=True)
    return field_scores[:top_n]

def analyze_field_types(field_examples):
    """Analyze different field types and their specific properties."""
    type_analysis = defaultdict(list)
    
    for field in field_examples:
        field_type = field.get('Type', 'Unknown')
        type_analysis[field_type].append(field)
    
    return type_analysis

def main():
    xml_file = "/home/art/Projects/gis schema extraction/DATABASE_EXPORT.XML"
    
    print("Extracting field metadata from DATABASE_EXPORT.XML...")
    
    properties, examples = extract_field_metadata(xml_file)
    
    print(f"\n=== ALL POSSIBLE FIELD METADATA PROPERTIES ({len(properties)}) ===")
    for prop in sorted(properties):
        print(f"- {prop}")
    
    print(f"\n=== FIELDS WITH MOST COMPLETE METADATA ===")
    top_fields = find_fields_with_most_metadata(examples, 3)
    
    for i, (score, field) in enumerate(top_fields, 1):
        print(f"\n--- Field #{i} (Score: {score} properties) ---")
        print(f"Feature Class: {field.get('FeatureClass', 'Unknown')}")
        print(f"Field Name: {field.get('Name', 'Unknown')}")
        print(f"Field Type: {field.get('Type', 'Unknown')}")
        
        # Print all properties except the basic ones we already showed
        for key, value in sorted(field.items()):
            if key not in ['FeatureClass', 'Name', 'Type'] and value and str(value).strip():
                print(f"  {key}: {value}")
    
    print(f"\n=== BUILDING_A SPECIFIC ANALYSIS ===")
    building_a_fields = [f for f in examples if f.get('FeatureClass') == 'Building_A']
    print(f"Number of fields in Building_A: {len(building_a_fields)}")
    
    # Show a few example fields from Building_A
    print("\n--- Sample Building_A Fields ---")
    for i, field in enumerate(building_a_fields[:3]):
        print(f"\nField {i+1}: {field.get('Name', 'Unknown')}")
        for key, value in sorted(field.items()):
            if key != 'FeatureClass' and value and str(value).strip():
                print(f"  {key}: {value}")
    
    print(f"\n=== FIELD TYPE ANALYSIS ===")
    type_analysis = analyze_field_types(examples)
    
    for field_type, fields in sorted(type_analysis.items()):
        print(f"\n{field_type}: {len(fields)} fields")
        # Show unique properties for this field type
        type_properties = set()
        for field in fields:
            type_properties.update(k for k, v in field.items() if v and str(v).strip())
        print(f"  Properties: {', '.join(sorted(type_properties))}")

if __name__ == "__main__":
    main()