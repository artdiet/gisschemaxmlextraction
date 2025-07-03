# GIS Schema Extraction Workflow

## Project Overview
This project extracts domain and range values from geodatabase XML exports to create pick lists for Palantir Foundry data collection.

## Standard Workflow

### 1. Input Requirements
- **File**: `DATABASE_EXPORT.XML` - Geodatabase XML export file
- **Target**: Extract domain values for feature classes (especially Building_A)

### 2. Extraction Process

#### Step 1: Run Domain Extraction
```bash
python3 extract_building_domains.py
```
This creates:
- `building_a_domains.csv` - Detailed format with all metadata
- `building_a_domains.json` - JSON format for programmatic access

#### Step 2: Generate Columnar Format
```bash
python3 extract_building_domains_columnar.py
```
This creates:
- `building_a_domains_columnar.csv` - Attributes as columns, values as rows
- `building_a_domains_codes_only.csv` - Just the codes without display names

### 3. Output File Formats

#### Standard CSV Format (`building_a_domains.csv`)
```
Field Name | Field Alias | Domain Type | Domain Name | Option Name | Option Code | Min Value | Max Value
```
- One row per domain value
- Includes both coded values and range domains
- Best for detailed analysis

#### Columnar CSV Format (`building_a_domains_columnar.csv`)
```
Attribute 1 | Attribute 2 | Attribute 3 | ...
Option 1    | Option 1    | Option 1    | ...
Option 2    | Option 2    | Option 2    | ...
```
- Attributes as column headers
- Domain values listed vertically
- Best for visual comparison and Palantir import

### 4. Domain Types Handled

#### Coded Value Domains
- Pick lists with predefined options
- Each option has a display name and code
- Examples: Building Condition, Country, Installation Name

#### Range Domains
- Numeric ranges with min/max values
- Examples: Building Condition Index (-1 to 100)

### 5. Common Attributes with Domains

Key Building_A attributes typically include:
- `buildingCondition` - Structural condition states
- `buildingOpStatus` - Operational status
- `country` - Country codes
- `installationId` - Installation identifiers
- `areaSizeUom` - Units of measurement
- `isRealProperty` - Yes/No/TBD options

### 6. Customization

To extract domains for other feature classes:
1. Modify the script to search for different feature class names
2. Update the output file names accordingly
3. Run both extraction scripts

### 7. Integration with Palantir Foundry

The columnar CSV format is optimized for Foundry import:
- Each column represents a field's valid values
- Empty cells indicate fewer options for that field
- Codes match the geodatabase schema exactly

### 8. Validation Steps

Before using in production:
1. Verify all expected fields are present
2. Check domain value counts match source
3. Ensure special characters are properly encoded
4. Test import with sample data

## Important Notes

- XML parsing uses namespaces: `http://www.esri.com/schemas/ArcGIS/10.8`
- UTF-8 encoding is used for all outputs
- Large domains (like installations) may have thousands of values
- Range domains show as "Range: min to max" in columnar format