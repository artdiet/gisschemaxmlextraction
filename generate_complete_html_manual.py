#!/usr/bin/env python3
"""
Generate complete HTML manual for Building_A attributes with all domain data
Reads from the extracted domain data and builds a comprehensive HTML reference
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from collections import OrderedDict

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

def parse_building_a_fields(xml_file):
    """Parse Building_A fields and their domain information"""
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
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
        return None, None
    
    # Extract fields with domains
    fields_data = OrderedDict()
    
    fields_array = building_a.find(".//FieldArray[@xsi:type='esri:ArrayOfField']", namespaces)
    if fields_array is None:
        return None, None
    
    for field in fields_array.findall("Field[@xsi:type='esri:Field']", namespaces):
        field_name = field.find("Name", namespaces).text
        field_type = field.find("Type", namespaces).text
        field_alias = field.find("AliasName", namespaces)
        if field_alias is not None:
            field_alias = field_alias.text
        else:
            field_alias = field_name
        
        # Store field info
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
                    domain_data = all_domains[domain_name]
                    field_info['domain_description'] = domain_data['description']
                    field_info['domain_type'] = 'CodedValue' if 'CodedValue' in domain_data['type'] else 'Range'
                    field_info['domain_values'] = domain_data.get('values', [])
                    field_info['min_value'] = domain_data.get('min_value')
                    field_info['max_value'] = domain_data.get('max_value')
        
        fields_data[field_name] = field_info
    
    return fields_data, all_domains

def generate_html_header():
    """Generate HTML header with CSS styling"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Building_A Feature Class - Complete Attribute Reference Manual</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 40px;
            padding: 10px;
            background-color: #ecf0f1;
            border-left: 4px solid #3498db;
        }
        .field-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            margin-top: 30px;
        }
        .field-name {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.2em;
        }
        .field-alias {
            color: #7f8c8d;
            font-style: italic;
            margin-left: 10px;
        }
        .field-type {
            background-color: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .domain-description {
            margin: 10px 0;
            padding: 10px;
            background-color: #e8f5e8;
            border-left: 3px solid #27ae60;
            font-style: italic;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background-color: white;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 10px;
            border: 1px solid #ddd;
            vertical-align: top;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f8ff;
        }
        .code {
            font-family: 'Courier New', monospace;
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .range-info {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .no-domain {
            color: #7f8c8d;
            font-style: italic;
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 3px solid #bdc3c7;
        }
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .toc h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .toc-section {
            margin-bottom: 20px;
        }
        .toc-section h4 {
            color: #34495e;
            margin-bottom: 10px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }
        .toc-list {
            columns: 2;
            column-gap: 30px;
        }
        .toc-list li {
            margin-bottom: 5px;
            break-inside: avoid;
        }
        .toc-list a {
            text-decoration: none;
            color: #3498db;
        }
        .toc-list a:hover {
            text-decoration: underline;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background-color: #3498db;
            color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
        }
        .stat-label {
            font-size: 0.9em;
        }
        .large-domain-note {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        .field-section {
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">'''

def generate_toc(fields_with_domains, fields_without_domains):
    """Generate table of contents"""
    html = '''
        <h1>Building_A Feature Class - Complete Attribute Reference Manual</h1>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Total Fields</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Fields with Domains</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{}</div>
                <div class="stat-label">Simple Fields</div>
            </div>
        </div>

        <div class="toc">
            <h3>Table of Contents</h3>
            
            <div class="toc-section">
                <h4>Fields with Domain Constraints ({} fields)</h4>
                <ul class="toc-list">'''.format(
        len(fields_with_domains) + len(fields_without_domains),
        len(fields_with_domains),
        len(fields_without_domains),
        len(fields_with_domains)
    )
    
    # Add domain fields to TOC
    for field_name, field_info in fields_with_domains.items():
        html += f'<li><a href="#{field_name}">{field_info["alias"]} ({field_name})</a></li>\n'
    
    html += '''
                </ul>
            </div>
            
            <div class="toc-section">
                <h4>Simple Fields ({} fields)</h4>
                <ul class="toc-list">'''.format(len(fields_without_domains))
    
    # Add simple fields to TOC
    for field_name, field_info in fields_without_domains.items():
        html += f'<li><a href="#{field_name}">{field_info["alias"]} ({field_name})</a></li>\n'
    
    html += '''
                </ul>
            </div>
        </div>'''
    
    return html

def generate_field_html(field_name, field_info):
    """Generate HTML for a single field"""
    # Determine field type display
    type_display = field_info['type'].replace('esriFieldType', '')
    
    html = f'''
        <div class="field-section" id="{field_name}">
            <div class="field-info">
                <div class="field-name">{field_name}<span class="field-alias">({field_info['alias']})</span><span class="field-type">{type_display}</span></div>
            </div>'''
    
    if field_info['has_domain']:
        # Add domain description
        html += f'''
            <div class="domain-description">
                {field_info.get('domain_description', 'No description available.')}
            </div>'''
        
        if field_info['domain_type'] == 'Range':
            # Range domain
            html += f'''
            <div class="range-info">
                <strong>Range Domain:</strong> Minimum value: <span class="code">{field_info['min_value']}</span>, 
                Maximum value: <span class="code">{field_info['max_value']}</span>
            </div>'''
        
        elif field_info['domain_type'] == 'CodedValue':
            # Coded value domain
            values = field_info.get('domain_values', [])
            
            if len(values) > 50:
                # Large domain - show summary
                html += f'''
            <div class="large-domain-note">
                <strong>Large Domain:</strong> This field has {len(values)} possible values. 
                Showing first 20 values. Complete list available in CSV files.
            </div>
            <table>
                <thead>
                    <tr><th>Display Name</th><th>Code Value</th></tr>
                </thead>
                <tbody>'''
                
                # Show first 20 values
                for value in values[:20]:
                    html += f'<tr><td>{value["name"]}</td><td class="code">{value["code"]}</td></tr>\n'
                
                html += f'''
                    <tr><td colspan="2"><em>... and {len(values) - 20} more values</em></td></tr>
                </tbody>
            </table>'''
            
            else:
                # Normal domain - show all values
                html += '''
            <table>
                <thead>
                    <tr><th>Display Name</th><th>Code Value</th></tr>
                </thead>
                <tbody>'''
                
                for value in values:
                    html += f'<tr><td>{value["name"]}</td><td class="code">{value["code"]}</td></tr>\n'
                
                html += '''
                </tbody>
            </table>'''
    
    else:
        # No domain
        html += f'''
            <div class="no-domain">
                This field accepts free-form input with no predefined constraints.
            </div>'''
    
    html += '</div>\n'
    return html

def main():
    xml_file = Path("DATABASE_EXPORT.XML")
    output_file = Path("building_a_complete_manual.html")
    
    print(f"Processing {xml_file}...")
    
    # Parse fields and domains
    fields_data, all_domains = parse_building_a_fields(xml_file)
    
    if not fields_data:
        print("Error: Could not parse Building_A fields")
        return
    
    # Separate fields with and without domains
    fields_with_domains = OrderedDict()
    fields_without_domains = OrderedDict()
    
    for field_name, field_info in fields_data.items():
        if field_info['has_domain']:
            fields_with_domains[field_name] = field_info
        else:
            fields_without_domains[field_name] = field_info
    
    print(f"Found {len(fields_with_domains)} fields with domains")
    print(f"Found {len(fields_without_domains)} fields without domains")
    
    # Generate HTML
    html_content = generate_html_header()
    html_content += generate_toc(fields_with_domains, fields_without_domains)
    
    # Fields with domains section
    html_content += '''
        <h2>Fields with Domain Constraints</h2>
        <p>The following fields have predefined domain values that constrain the allowable inputs. 
        Each field includes a detailed description and complete list of valid options.</p>'''
    
    for field_name, field_info in fields_with_domains.items():
        html_content += generate_field_html(field_name, field_info)
    
    # Fields without domains section
    html_content += '''
        <h2>Simple Fields (No Domain Constraints)</h2>
        <p>The following fields do not have domain constraints and accept free-form input:</p>'''
    
    for field_name, field_info in fields_without_domains.items():
        html_content += generate_field_html(field_name, field_info)
    
    # Footer
    html_content += '''
        <h2>File References</h2>
        <ul>
            <li><strong>Complete Metadata:</strong> <code>building_a_complete_metadata.csv</code> - All 32 metadata properties for each field</li>
            <li><strong>Detailed Domains:</strong> <code>building_a_domains_detailed.csv</code> - All domain values with descriptions</li>
            <li><strong>Columnar Format:</strong> <code>building_a_domains_columnar.csv</code> - Pick lists in column format</li>
            <li><strong>All Fields Summary:</strong> <code>building_a_all_fields.csv</code> - Overview of all fields</li>
        </ul>

        <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; text-align: center;">
            <p>Generated from geodatabase XML schema • Building_A Feature Class Complete Reference</p>
            <p>Total: {} fields ({} with domains, {} without domains)</p>
        </footer>
    </div>
</body>
</html>'''.format(
        len(fields_data),
        len(fields_with_domains),
        len(fields_without_domains)
    )
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nGenerated complete HTML manual: {output_file}")
    print(f"Total size: {len(html_content)} characters")
    print(f"Includes {len(fields_with_domains)} domain fields and {len(fields_without_domains)} simple fields")

if __name__ == "__main__":
    main()