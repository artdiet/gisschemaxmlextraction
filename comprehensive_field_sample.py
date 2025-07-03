#!/usr/bin/env python3
"""
Extract complete field definitions with domains from DATABASE_EXPORT.XML
to show the full metadata structure available.
"""

import xml.etree.ElementTree as ET

def extract_complete_sample():
    """Extract a complete field sample with domain from Building_A."""
    
    # Parse the XML
    tree = ET.parse("/home/art/Projects/gis schema extraction/DATABASE_EXPORT.XML")
    root = tree.getroot()
    
    # Find Building_A feature class
    building_a = None
    for elem in root.iter():
        if elem.tag == 'DataElement' or elem.tag.endswith('}DataElement'):
            xsi_type = elem.get('{http://www.w3.org/2001/XMLSchema-instance}type')
            if xsi_type and 'DEFeatureClass' in xsi_type:
                name_elem = elem.find("Name")
                if name_elem is not None and name_elem.text == 'Building_A':
                    building_a = elem
                    break
    
    if not building_a:
        print("Building_A not found!")
        return
    
    # Find the buildingCondition field (has a domain)
    building_condition_field = None
    for elem in building_a.iter():
        if elem.tag == 'Field' or elem.tag.endswith('}Field'):
            name_elem = elem.find("Name")
            if name_elem is not None and name_elem.text == 'buildingCondition':
                building_condition_field = elem
                break
    
    if building_condition_field:
        print("=== COMPLETE FIELD DEFINITION SAMPLE ===")
        print("Field: buildingCondition from Building_A feature class")
        print("This field has a coded value domain, showing complete metadata structure:\n")
        
        # Pretty print the XML
        ET.indent(building_condition_field, space="  ")
        xml_str = ET.tostring(building_condition_field, encoding='unicode')
        print(xml_str)
        
        # Also find and show the domain definition
        domain = building_condition_field.find("Domain")
        if domain:
            domain_name = domain.find("DomainName")
            if domain_name is not None:
                domain_name_text = domain_name.text
                
                # Find the domain definition at the workspace level
                domains = root.find("WorkspaceDefinition/Domains")
                if domains:
                    for domain_def in domains:
                        name_elem = domain_def.find("DomainName")
                        if name_elem is not None and name_elem.text == domain_name_text:
                            print(f"\n=== COMPLETE DOMAIN DEFINITION: {domain_name_text} ===")
                            ET.indent(domain_def, space="  ")
                            domain_xml = ET.tostring(domain_def, encoding='unicode')
                            print(domain_xml[:2000] + "..." if len(domain_xml) > 2000 else domain_xml)
                            break

if __name__ == "__main__":
    extract_complete_sample()