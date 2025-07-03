# CSV File Reading Guide for GIS Team

## Quick Reference - Which File to Use

| **Use Case** | **File to Use** | **Size** | **Description** |
|--------------|----------------|----------|-----------------|
| 📖 **Browse/Reference** | `building_a_complete_manual.html` | 91KB | Interactive web guide with all fields |
| 🔧 **Data Integration** | `building_a_domains_detailed.csv` | 884KB | Complete domain data for import |
| 📊 **Foundry Import** | `building_a_domains_columnar.csv` | 323KB | Pick lists in column format |
| ⚙️ **Technical Specs** | `building_a_complete_metadata.csv` | 16KB | All field properties & constraints |
| 📋 **Field Overview** | `building_a_all_fields.csv` | 11KB | Summary of all 85 fields |

---

## File Descriptions & How to Read

### 1. 📖 `building_a_complete_manual.html` - **START HERE**
**Best for:** Browsing and understanding the data structure

**How to use:**
- Open in any web browser (Chrome, Firefox, Safari)
- Use Table of Contents to jump to specific fields
- Click field names to see all valid options
- Large domains show first 20 values + note about complete data

**What you'll see:**
- Field descriptions from the original GIS schema
- Pick list options with display names and codes
- Field types (String, Integer, etc.)
- Range constraints for numeric fields

---

### 2. 🔧 `building_a_domains_detailed.csv` - **For Data Integration**
**Best for:** Setting up data validation rules and import processes

**Structure:**
```
Field Name | Field Alias | Domain Name | Domain Description | Domain Type | Option Name | Option Code | Min Value | Max Value
```

**How to read:**
- **One row per domain option** (not per field)
- **Field Name**: Technical field name (e.g., `buildingCondition`)
- **Field Alias**: Human-readable name (e.g., "Building Condition") 
- **Domain Description**: Explanation of what the field represents
- **Option Name**: Display value (e.g., "Good")
- **Option Code**: Database value (e.g., "good")

**Example rows:**
```csv
buildingCondition,Building Condition,StructuralCondition,"The structural condition...",CodedValue,Good,good,,
buildingCondition,Building Condition,StructuralCondition,"The structural condition...",CodedValue,Fair,fair,,
buildingCondition,Building Condition,StructuralCondition,"The structural condition...",CodedValue,Poor,poor,,
```

**📌 Key Point:** To get all options for one field, filter by the "Field Name" column

---

### 3. 📊 `building_a_domains_columnar.csv` - **For Foundry/System Import**
**Best for:** Direct import into data collection systems

**Structure:**
- **Column headers** = Field names
- **Rows below** = Valid options for each field
- **Empty cells** = Field has fewer options than others

**How to read:**
```csv
buildingCondition,country,installationId,...
Good,United States (US),aawz - ACC AMIC,...
Fair,Germany (DE),abaa - Abston ANGS,...
Poor,France (FR),acjp - Los Angeles AFB,...
```

**📌 Key Point:** Read vertically - each column shows all valid values for that field

---

### 4. ⚙️ `building_a_complete_metadata.csv` - **For Technical Analysis**
**Best for:** Understanding field specifications and constraints

**Structure:**
- **One row per field** (85 rows total)
- **32 columns** with all technical properties

**Key columns:**
- `name`: Field name
- `alias_name`: Display name
- `type`: Data type (esriFieldTypeString, etc.)
- `length`: Maximum field length
- `is_nullable`: Can be empty (true/false)
- `required`: Must have value (true/false)
- `has_domain`: Has pick list (true/false)
- `domain_description`: What the field represents
- `domain_values_count`: Number of pick list options

**📌 Key Point:** This tells you HOW to structure the field, not WHAT values it can contain

---

### 5. 📋 `building_a_all_fields.csv` - **For Quick Overview**
**Best for:** Getting a summary of all fields and their constraints

**Structure:**
```
Field Name | Field Alias | Field Type | Has Domain | Domain Name | Domain Type | Domain Description | Sample Values
```

**How to read:**
- **Has Domain**: "Yes" = has pick list, "No" = free text/numeric
- **Sample Values**: First few options for quick reference
- **Domain Description**: What the field is used for

**📌 Key Point:** Good starting point to understand which fields need pick lists

---

## Common Questions & Answers

### Q: How do I find all valid values for the "country" field?
**A:** Two options:
1. **HTML Manual**: Open HTML file, click "Country" in table of contents
2. **CSV**: Open `building_a_domains_detailed.csv`, filter by Field Name = "country"

### Q: Which fields require pick lists vs. free text?
**A:** Open `building_a_all_fields.csv`, look at "Has Domain" column:
- **"Yes"** = Must use pick list values
- **"No"** = Free text/numeric input allowed

### Q: What's the difference between Option Name and Option Code?
**A:** 
- **Option Name**: What users see ("United States")
- **Option Code**: What gets stored in database ("usa")

### Q: How many total pick list options are there?
**A:** The system has **740 total domain definitions** across all fields. Building_A uses **32 of these domains**.

### Q: Which fields have the most options?
**A:** From the data:
- **country**: 274 options (all countries)
- **installationId**: 322 options (military installations)  
- **rpsuid**: 2,076 options (site identifiers)
- **siteId**: 2,099 options (site codes)

### Q: Are these descriptions from the original GIS system?
**A:** **Yes** - All domain descriptions are extracted directly from the original geodatabase XML schema, not generated content.

---

## Integration Tips

### For Data Collection Systems:
1. Use `building_a_domains_detailed.csv` to build dropdown menus
2. Store the "Option Code" in your database
3. Display the "Option Name" to users
4. Use "Domain Description" for field help text

### For Data Validation:
1. Check `building_a_complete_metadata.csv` for field requirements
2. Enforce pick list constraints where "Has Domain" = "Yes"  
3. Apply length limits from "length" column
4. Validate required fields from "required" column

### For User Training:
1. Share the HTML manual for easy browsing
2. Print domain descriptions for reference cards
3. Use field aliases (display names) in your interface
4. Explain the difference between display values and codes

---

## Support Files
- **Validation Scripts**: Test completeness and accuracy
- **Generation Scripts**: Recreate files from new XML exports
- **WORKFLOW_NOTES.md**: Technical details for developers
- **FILE_SUMMARY.md**: Complete file inventory

---

*Questions? The HTML manual is the most user-friendly starting point. All CSV files contain the same core data in different formats optimized for different use cases.*