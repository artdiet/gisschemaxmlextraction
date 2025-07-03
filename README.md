# GIS Schema Extraction Tool

**Developed by Maj Art Dietrich, 2025**

A comprehensive tool for extracting domain values and metadata from geodatabase XML exports, specifically designed for Building_A feature class schema extraction and Palantir Foundry integration.

## 📋 Overview

This tool processes geodatabase XML export files to extract:
- Field definitions and metadata
- Domain constraints and pick list values
- Range specifications for numeric fields
- Complete schema documentation

The extracted data is formatted for easy integration into data collection systems, with special focus on Palantir Foundry workflows.

## 🎯 Key Features

- **Complete Field Coverage**: Extracts all 85 Building_A fields with full metadata
- **Domain Extraction**: Processes 740+ domain definitions from geodatabase
- **Multiple Output Formats**: HTML manual, detailed CSV, columnar CSV, metadata CSV
- **Quality Assurance**: Comprehensive unit testing and validation
- **User-Friendly Documentation**: Interactive HTML guides and reference materials

## 📁 Generated Files

| File | Purpose | Size | Description |
|------|---------|------|-------------|
| `building_a_complete_manual.html` | End-user reference | 91KB | Interactive web guide |
| `building_a_domains_detailed.csv` | Data integration | 884KB | Complete domain data |
| `building_a_domains_columnar.csv` | System import | 323KB | Pick lists in columns |
| `building_a_complete_metadata.csv` | Technical specs | 16KB | All field properties |
| `CSV_READING_GUIDE.html` | Team guide | 20KB | How to use the files |

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- Required libraries: `xml.etree.ElementTree`, `csv`, `json`, `pathlib`
- Optional: `beautifulsoup4` (for testing)

### Basic Usage

1. **Place your geodatabase XML export** in the project directory as `DATABASE_EXPORT.XML`

2. **Run the main extraction**:
   ```bash
   python3 extract_building_domains_complete.py
   ```

3. **Generate HTML manual**:
   ```bash
   python3 generate_complete_html_manual.py
   ```

4. **Validate results**:
   ```bash
   python3 test_html_generation.py
   ```

### For GIS Teams
1. Open `CSV_READING_GUIDE.html` in your browser
2. Use `building_a_complete_manual.html` for field reference
3. Import `building_a_domains_detailed.csv` for pick list data

## 📊 Data Extracted

### Building_A Feature Class
- **Total Fields**: 85
- **Fields with Domains**: 32
- **Simple Fields**: 53
- **Domain Definitions**: 740 total

### Key Domain Fields
- `country`: 274 country options
- `buildingCondition`: 35 condition states  
- `installationId`: 322 military installations
- `buildingOpStatus`: 16 operational states

## 🛠️ Scripts Overview

### Core Extraction Scripts
- `extract_building_domains_complete.py` - Main extraction with descriptions
- `extract_all_metadata.py` - Complete metadata extraction
- `generate_complete_html_manual.py` - HTML manual generation

### Quality Assurance
- `test_html_generation.py` - Unit tests for completeness
- `validate_and_fix_html.py` - HTML validation and repair

### Utilities
- `extract_building_domains_columnar.py` - Columnar format generation
- `extract_building_domains.py` - Basic extraction (legacy)

## 📖 Documentation

### User Guides
- `CSV_READING_GUIDE.html` - **Start here** for GIS teams
- `building_a_complete_manual.html` - Interactive field reference
- `FILE_SUMMARY.md` - Complete file inventory

### Technical Documentation
- `WORKFLOW_NOTES.md` - Development workflow and best practices
- `GIS_XML_SCHEMA_EXTRACTION_MANUAL.md` - Comprehensive technical manual
- `CLAUDE.md` - Project-specific workflow notes

## 🧪 Testing

The tool includes comprehensive testing:
- **10 unit tests** for HTML generation
- **Field coverage validation** (85/85 fields verified)
- **Navigation link testing** for HTML manual
- **Domain completeness checks**

Run tests:
```bash
python3 test_html_generation.py
```

## 🔧 Technical Details

### XML Processing
- Handles large XML files (3.5MB+) efficiently
- Parses workspace-level domains before field processing
- Preserves original domain descriptions from geodatabase
- Supports both CodedValue and Range domains

### Output Optimization
- Multiple formats for different use cases
- Large domain handling (>50 values show samples)
- UTF-8 encoding for international characters
- Professional HTML styling with navigation

### Memory Management
- Streaming XML processing for large files
- Proper namespace handling
- Memory cleanup during processing

## 🤝 Contributing

This tool was developed for military GIS applications. For improvements or adaptations:

1. Follow the established workflow in `WORKFLOW_NOTES.md`
2. Run all validation tests before committing changes
3. Update documentation for any new features
4. Maintain compatibility with existing output formats

## 📞 Support

### For End Users
- Start with `CSV_READING_GUIDE.html`
- Use `building_a_complete_manual.html` for field reference
- Check `FILE_SUMMARY.md` for file descriptions

### For Developers
- Review `WORKFLOW_NOTES.md` for technical details
- See `GIS_XML_SCHEMA_EXTRACTION_MANUAL.md` for comprehensive guidance
- Run validation scripts for quality assurance

## 📈 Version History

### v1.0 (2025)
- Initial release with complete Building_A extraction
- Full HTML manual generation
- Comprehensive testing suite
- Multiple output format support

## 🏗️ Architecture

```
gis-schema-extraction/
├── DATABASE_EXPORT.XML          # Source geodatabase export
├── extract_*.py                 # Extraction scripts
├── generate_*.py                # Generation utilities  
├── test_*.py                    # Quality assurance
├── validate_*.py                # Validation tools
├── building_a_*.*              # Generated data files
├── docs/                       # Documentation
│   ├── CSV_READING_GUIDE.html  # User guide
│   ├── WORKFLOW_NOTES.md       # Technical workflow
│   └── *.md                    # Additional documentation
└── README.md                   # This file
```

## 🎯 Use Cases

### Primary Applications
- **Military GIS Systems**: Building attribute standardization
- **Data Collection**: Pick list generation for field teams
- **System Integration**: Domain validation for data pipelines
- **Documentation**: Field reference for GIS analysts

### Integration Targets
- Palantir Foundry data collection
- ArcGIS field validation
- Custom data entry systems
- Database constraint definition

---

**Developed by Maj Art Dietrich, 2025**  
*Supporting military GIS operations through automated schema extraction*