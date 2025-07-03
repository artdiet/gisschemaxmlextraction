#!/usr/bin/env python3
"""
Final comprehensive analysis of field metadata from DATABASE_EXPORT.XML
for the Building_A feature class and other feature classes.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

def extract_field_metadata(xml_file):
    """Extract all field metadata from the XML file."""
    
    # Parse the XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find all DataElement elements that are feature classes
    feature_classes = []
    for elem in root.iter():
        if elem.tag == 'DataElement' or elem.tag.endswith('}DataElement'):
            xsi_type = elem.get('{http://www.w3.org/2001/XMLSchema-instance}type')
            if xsi_type and 'DEFeatureClass' in xsi_type:
                feature_classes.append(elem)
    
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
                        
                        # Get additional geometry properties
                        has_z = child.find("HasZ")
                        has_m = child.find("HasM")
                        if has_z is not None:
                            field_data[tag_name] += f", HasZ: {has_z.text}"
                        if has_m is not None:
                            field_data[tag_name] += f", HasM: {has_m.text}"
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

def find_complete_field_examples(field_examples):
    """Find examples of fields with different combinations of metadata."""
    
    # Group by field type and feature class
    examples_by_type = defaultdict(list)
    
    for field in field_examples:
        key = (field.get('Type', 'Unknown'), field.get('FeatureClass', 'Unknown'))
        examples_by_type[key].append(field)
    
    # Find the most complete example for each type
    complete_examples = []
    for key, fields in examples_by_type.items():
        # Find field with most properties
        best_field = max(fields, key=lambda f: len([v for v in f.values() if v and str(v).strip()]))
        complete_examples.append(best_field)
    
    return complete_examples

def analyze_building_a_fields(field_examples):
    """Detailed analysis of Building_A fields."""
    
    building_a_fields = [f for f in field_examples if f.get('FeatureClass') == 'Building_A']
    
    # Analyze field types
    type_counts = Counter(f.get('Type', 'Unknown') for f in building_a_fields)
    
    # Find fields with domains
    domain_fields = [f for f in building_a_fields if f.get('Domain')]
    
    # Find fields with default values
    default_fields = [f for f in building_a_fields if f.get('DefaultValue')]
    
    # Find required vs optional fields
    required_fields = [f for f in building_a_fields if f.get('Required') == 'true']
    nullable_fields = [f for f in building_a_fields if f.get('IsNullable') == 'true']
    
    return {
        'total_fields': len(building_a_fields),
        'type_counts': type_counts,
        'domain_fields': domain_fields,
        'default_fields': default_fields,
        'required_fields': required_fields,
        'nullable_fields': nullable_fields,
        'all_fields': building_a_fields
    }

def main():
    xml_file = "/home/art/Projects/gis schema extraction/DATABASE_EXPORT.XML"
    
    print("=== COMPREHENSIVE FIELD METADATA ANALYSIS ===")
    print("Analyzing DATABASE_EXPORT.XML for Building_A feature class\n")
    
    properties, examples = extract_field_metadata(xml_file)
    
    print(f"=== ALL POSSIBLE FIELD METADATA PROPERTIES ({len(properties)}) ===")
    for prop in sorted(properties):
        print(f"• {prop}")
    
    print(f"\n=== BUILDING_A DETAILED ANALYSIS ===")
    building_analysis = analyze_building_a_fields(examples)
    
    print(f"Total fields in Building_A: {building_analysis['total_fields']}")
    
    print(f"\nField Type Distribution:")
    for field_type, count in building_analysis['type_counts'].most_common():
        print(f"  • {field_type}: {count} fields")
    
    print(f"\nFields with Domains: {len(building_analysis['domain_fields'])}")
    for field in building_analysis['domain_fields'][:5]:  # Show first 5
        print(f"  • {field.get('Name', 'Unknown')}: {field.get('Domain', 'N/A')}")
    
    print(f"\nFields with Default Values: {len(building_analysis['default_fields'])}")
    for field in building_analysis['default_fields']:
        print(f"  • {field.get('Name', 'Unknown')}: '{field.get('DefaultValue', 'N/A')}'")
    
    print(f"\nRequired Fields: {len(building_analysis['required_fields'])}")
    for field in building_analysis['required_fields']:
        print(f"  • {field.get('Name', 'Unknown')} ({field.get('Type', 'Unknown')})")
    
    print(f"\n=== EXAMPLE FIELD DEFINITIONS WITH COMPLETE METADATA ===")
    
    # Show examples of different field types with all their metadata
    field_type_examples = {
        'esriFieldTypeString': None,
        'esriFieldTypeInteger': None,
        'esriFieldTypeDouble': None,
        'esriFieldTypeDate': None,
        'esriFieldTypeGeometry': None,
        'esriFieldTypeOID': None,
        'esriFieldTypeGlobalID': None
    }
    
    for field in building_analysis['all_fields']:
        field_type = field.get('Type')
        if field_type in field_type_examples and field_type_examples[field_type] is None:
            field_type_examples[field_type] = field
    
    for field_type, example in field_type_examples.items():
        if example:
            print(f"\n--- {field_type} Example: {example.get('Name', 'Unknown')} ---")
            for prop, value in sorted(example.items()):
                if prop not in ['FeatureClass', 'Name', 'Type'] and value and str(value).strip():
                    print(f"  {prop}: {value}")
    
    print(f"\n=== COMPREHENSIVE FIELD METADATA TEMPLATE ===")
    print("Based on analysis, here are ALL possible field metadata properties:")
    print("""
<Field xsi:type='esri:Field'>
    <Name>field_name</Name>
    <Type>esriFieldType*</Type>
    <IsNullable>true/false</IsNullable>
    <Length>number</Length>
    <Precision>number</Precision>
    <Scale>number</Scale>
    <Required>true/false</Required>
    <Editable>true/false</Editable>
    <AliasName>display_name</AliasName>
    <ModelName>model_name</ModelName>
    <DefaultValue xsi:type='xs:string'>default_value</DefaultValue>
    <Domain xsi:type='esri:CodedValueDomain' or 'esri:RangeDomain'>
        <DomainName>domain_name</DomainName>
        <FieldType>field_type</FieldType>
        <MergePolicy>merge_policy</MergePolicy>
        <SplitPolicy>split_policy</SplitPolicy>
        <Description>domain_description</Description>
        <Owner>owner</Owner>
        <!-- CodedValueDomain specific -->
        <CodedValues xsi:type='esri:ArrayOfCodedValue'>
            <CodedValue xsi:type='esri:CodedValue'>
                <Name>display_name</Name>
                <Code xsi:type='xs:string'>code_value</Code>
            </CodedValue>
        </CodedValues>
        <!-- RangeDomain specific -->
        <MaxValue xsi:type='xs:type'>max_value</MaxValue>
        <MinValue xsi:type='xs:type'>min_value</MinValue>
    </Domain>
    <GeometryDef xsi:type='esri:GeometryDef'> <!-- For geometry fields only -->
        <AvgNumPoints>number</AvgNumPoints>
        <GeometryType>esriGeometry*</GeometryType>
        <HasM>true/false</HasM>
        <HasZ>true/false</HasZ>
        <SpatialReference>spatial_reference_info</SpatialReference>
        <GridSize0>number</GridSize0>
    </GeometryDef>
</Field>
    """)

if __name__ == "__main__":
    main()