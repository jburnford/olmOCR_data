# Saskatchewan OCR Data Overview

## Repository Context

This repository contains OCR (Optical Character Recognition) data exported from an archive tracking database. The export includes metadata and OCR results for multiple subcollections, with **Saskatchewan (1808-1946)** being one of the primary collections.

### Repository Structure
```
olmOCR_data/
├── manifest.csv                    # Master index of all documents
├── documents.jsonl                 # Combined metadata + OCR info (4,360 documents)
├── metadata/                       # Archive.org metadata by subcollection
│   ├── saskatchewan_1808_1946/    # 1,222 metadata files
│   └── [4 other subcollections]
└── ocr/                           # OCR results by subcollection
    ├── saskatchewan_1808_1946/    # 1,222 OCR files (921 MB)
    └── [4 other subcollections]
```

### All Subcollections in Repository
- **saskatchewan_1808_1946**: 1,222 documents (FOCUS OF THIS OVERVIEW)
- **pioneer_questionnaires**: 1,231 documents
- **main**: 1,088 documents
- **india**: 676 documents
- **jacob**: 100 documents

---

## Saskatchewan Collection (1808-1946): Detailed Analysis

### Collection Statistics

| Metric | Value |
|--------|-------|
| **Total Documents** | 1,222 files |
| **Total OCR Data Size** | ~920 MB |
| **Average File Size** | ~750 KB |
| **Metadata Files** | 1,222 JSON files (matching 1:1 with OCR) |
| **Date Range** | 1808 - 1890 |
| **Primary Coverage** | Early Canadian/Saskatchewan history |

### Document Page Counts

Sample analysis shows significant variation in document length:

| Document Type | Example File | Pages |
|---------------|--------------|-------|
| Small (Newspaper page) | BDM_1883042601.json | 4 pages |
| Medium (Book) | P000045.json | 340 pages |
| Large (Manuscript) | cihm_38161.json | 1,101 pages |
| Very Large (School Files) | School_Files_Series-RG10_c-8760.json | 1,715 pages |

**File Size Distribution:**
- Smallest files: ~1 KB (single-page documents, maps)
- Largest files: Up to 8.5 MB (multi-volume works, extensive government records)
- Most common: 10-500 KB (newspapers, pamphlets, short books)

### Temporal Coverage

**Date Range:** 1808-1890 (with some entries having null dates)

**Earliest Documents (1808-1820s):**
- The British treaty (1808)
- Travels and adventures in Canada and the Indian territories (1809)
- The idler series (1810)
- Early exploration narratives and government documents

**Peak Period:** 1880s
- Significant concentration of newspaper issues
- Prince Albert Times and Saskatchewan Review (weekly issues)
- Various regional newspapers and official publications

### Language Distribution

| Language | Document Count | Notes |
|----------|---------------|-------|
| English ("eng" + "English") | ~1,097 | Dominant language |
| French ("fre" + "French") | ~148 | Significant minority |
| Mixed (French; English) | ~5 | Bilingual documents |
| Cree | ~6 | Indigenous language materials |
| Swedish | 1 | |
| German | 1 | |
| Chipewyan/Hare/Loucheux | 1 | Northern Athapaskan languages |
| English-handwritten | 2 | Manuscript materials |

### Content Types & Subjects

**Primary Source Collections:**

1. **Peel Newspapers** (353 documents)
   - Brandon Daily Mail
   - Prince Albert Times and Saskatchewan Review
   - Other Western Canadian newspapers
   - Collection: `peel_newspapers;peel;university_of_alberta_libraries;toronto`

2. **Peel Print Collection** (264 documents)
   - Books, pamphlets, monographs
   - Historical narratives
   - Government documents
   - Collection: `peel_print;peel;university_of_alberta_libraries;toronto`

3. **Microfilm Archives** (211 documents)
   - CIHM (Canadian Institute for Historical Microreproductions) materials
   - Collection: `university_of_alberta_libraries_microfilm;university_of_alberta_libraries;toronto;microfilm;additional_collections`

4. **Internet Archive Open Source** (347 documents)
   - Community-contributed materials
   - Collection: `opensource;community`

5. **Specialized Collections:**
   - Americana (16 documents)
   - Thomas Fisher Rare Book Library, U of Toronto (13 documents)
   - Cornell/Biodiversity (7 documents)
   - University of Ottawa (6 documents)
   - European Libraries (6 documents)

**Major Subject Areas:**

- **Indigenous Peoples & History**
  - Indians of North America
  - North West Company
  - Métis history
  - Cree language materials

- **Exploration & Travel**
  - Saskatchewan description and travel
  - Overland journeys to the Pacific
  - Arctic expeditions
  - Franklin expedition materials

- **Religious History**
  - Catholic Church missions
  - Moravian Church
  - United Church of England and Ireland
  - Missionary accounts

- **Political & Social History**
  - Democratic Party (U.S.)
  - Public finance
  - Canadian constitutional matters
  - 1837 Rebellion materials

- **Natural History & Geography**
  - Physical sciences
  - Natural history
  - Maps and cartography
  - Western Canada geography

### Document Genres

**Newspapers** (Major portion)
- Daily newspapers (Daily Mail series)
- Weekly newspapers (Prince Albert Times and Saskatchewan Review)
- Various regional publications from 1880s

**Books & Monographs**
- Historical narratives
- Travel accounts
- Religious texts
- Educational materials

**Government Documents**
- School Files Series (RG10 records)
- Parliamentary papers
- Official correspondence
- Administrative records

**Maps & Cartographic Materials**
- Early territorial maps
- Harbor charts
- Regional surveys

**Manuscripts**
- Handwritten questionnaires
- Personal correspondence
- Official records

### Publishers & Sources

**Geographic Distribution:**
- Montreal publishers (multiple houses)
- Toronto publishers
- Winnipeg publishers (Bishop Engraving, Call Printing Co.)
- Ottawa (government printers)
- European publishers (Paris, London, Edinburgh, Switzerland)
- American publishers (Boston, New York, Buffalo, Baltimore)

**Sample Publishers:**
- C. Cliffe (Brandon)
- "Witness" Printing House (Montreal)
- Brown Chamberlin, Queen's Printer (Ottawa)
- A.S. Woodburn (Ottawa)
- Various religious presses

### OCR Data Format & Quality

**JSON Structure:**
Each OCR file contains an array with the following structure:

```json
[{
  "id": "unique-hash-identifier",
  "text": "Full extracted text content...",
  "source": "olmocr",
  "added": "2025-10-06",
  "created": "2025-10-06",
  "metadata": {
    "Source-File": "original-pdf-path",
    "olmocr-version": "0.3.4",
    "pdf-total-pages": 4,
    "total-input-tokens": 6456,
    "total-output-tokens": 814,
    "total-fallback-pages": 0
  },
  "attributes": {
    "pdf_page_numbers": [[start, end, page_num]],
    "primary_language": ["en", "en"],
    "is_rotation_valid": [true, true],
    "rotation_correction": [0, 0],
    "is_table": [false, false],
    "is_diagram": [false, false]
  }
}]
```

**OCR Engine:** olmOCR v0.3.4
- Modern AI-based OCR system
- Handles multi-language documents
- Supports rotation correction
- Table and diagram detection
- Language identification per page

**Quality Indicators:**
- Rotation validation status
- Language detection confidence
- Token counts (input/output)
- Fallback page tracking (pages requiring special processing)

**Text Extraction Quality:**

*High Quality* (Modern print, clear text):
```
Example from BDM_1883042601.json (1883 newspaper):
"NO SMALL POX HERE.
STABLES, STABLES, STABLES.
JUST OPENED.
ON
Tenth Street Between Rosser and Pacific Avenues,
Livery, Sale and Feed Stables..."
```
Clean, accurate extraction of classified ads and newspaper content.

*Good Quality* (French text):
```
Example from P007493.json:
"FAITS DIVERS.
Le 25 avril, se sont embarqués à Brest, se rendant au vicariat de la Saskatchewan :
Mgr Vital Grandin, évêque de Satala et vicaire de la Saskatchewan ;
Le R. P. Dupin ;
Le F. Doucet, scolastique..."
```
Proper handling of French diacritics and formatting.

**Challenges:**
- Very large files (8+ MB) may indicate complex layouts or extensive documents
- Handwritten materials flagged separately
- Some degraded microform sources
- Mixed-language documents require careful handling

### Metadata Companion Files

Each OCR file has a corresponding metadata JSON in `metadata/saskatchewan_1808_1946/` containing:

- **Archive.org identifiers** and URLs
- **Bibliographic data**: title, creator, publisher, date
- **Collection affiliations**
- **Subject headings** (Library of Congress, local classifications)
- **Technical metadata**: scanner info, OCR engine versions, page counts
- **Upload/publication dates**
- **Language codes**
- **Physical descriptions** (extent, format)

Example fields:
```json
{
  "identifier": "BDM_1883042601",
  "collective_title": "Daily mail",
  "coverage": "Canada;Manitoba;Brandon",
  "date": "1883-04-26",
  "genre": "Newspaper",
  "publisher": "C. Cliffe.",
  "imagecount": "4",
  "ocr": "tesseract 5.3.0-1-gd3a4",
  "identifier-access": "http://archive.org/details/BDM_1883042601"
}
```

### Research Use Cases

This Saskatchewan OCR dataset is valuable for:

1. **Historical Text Analysis**
   - Linguistic patterns in 19th century Canadian English/French
   - Evolution of newspaper language
   - Indigenous language documentation

2. **Content Mining**
   - Place name extraction (Saskatchewan settlement history)
   - Person name identification (pioneers, officials, explorers)
   - Event tracking (1837 Rebellion, exploration expeditions)

3. **Digital Humanities**
   - Newspaper corpus studies
   - Comparative analysis of French/English publications
   - Mission and religious history research

4. **Archival Research**
   - Government records (School Files Series)
   - Early territorial history
   - North-West Company and fur trade

5. **Indigenous Studies**
   - Cree language materials
   - Indigenous-European contact documentation
   - Missionary perspectives on Indigenous peoples

### Data Quality Considerations

**Strengths:**
- Consistent JSON format across all files
- Rich metadata linking to source materials
- Language identification at page level
- Source provenance tracked
- Multiple source collections represented

**Limitations:**
- No PDF files included (metadata only references original paths)
- Some documents have null/missing dates
- OCR quality varies with source material condition
- Large files may be challenging to process
- Original PDF paths reference specific system locations (not portable)

**Recommended Validation:**
- Cross-reference with Archive.org URLs in metadata
- Check language codes against actual text content
- Verify page counts match text segmentation
- Sample quality across different document types

### Access & Attribution

**Archive.org Links:**
All documents can be accessed via Internet Archive using the identifier:
```
https://archive.org/details/{identifier}
```

**Primary Contributing Institutions:**
- University of Alberta Libraries (Peel's Prairie Provinces collection)
- University of Toronto Libraries
- Canadian Institute for Historical Microreproductions (CIHM)
- Internet Archive Community

**OCR Processing:**
- Engine: olmOCR v0.3.4
- Processing date: October 2025
- Export date: 2025-11-07

---

## Technical Specifications

### File Paths
- OCR Data: `ocr/saskatchewan_1808_1946/{identifier}.json`
- Metadata: `metadata/saskatchewan_1808_1946/{identifier}.json`
- Manifest Entry: Row in `manifest.csv` with `subcollection = "saskatchewan_1808_1946"`

### Identifier Patterns
- Archive.org IDs: `P000045`, `cihm_38163`, etc.
- Newspaper codes: `BDM_1883042601` (Brandon Daily Mail, date-coded)
- Series codes: `School_Files_Series-RG10_c-8760`
- Custom IDs: Various institutional patterns

### JSON Processing Notes
- All OCR files are valid JSON arrays
- Text fields may contain Unicode characters (French, Cree, etc.)
- Metadata fields are optional; use `.field // empty` in jq queries
- Large files (>1 MB) may require streaming parsers

### Integration with Manifest

The `manifest.csv` provides the master index:
```csv
identifier,title,year,publisher,subject,subcollection,pdf_file_id,pdf_filename,
pdf_original_path,pdf_export_relpath,ocr_id,ocr_completed_date,
ocr_export_relpath,metadata_export_relpath
```

Saskatchewan entries: 1,265 rows (slightly more than OCR files, indicating some processing variations)

---

## Conclusion

The Saskatchewan (1808-1946) subcollection represents a rich corpus of 1,222 digitized documents spanning the early settlement and territorial period of Saskatchewan and Western Canada. With nearly 1 GB of OCR text data, comprehensive metadata, and coverage across newspapers, books, government records, and multilingual materials, this collection provides substantial resources for historical, linguistic, and cultural research.

The high-quality OCR extraction (using modern AI-based olmOCR), combined with detailed provenance metadata and Archive.org integration, makes this dataset well-suited for computational text analysis, digital humanities research, and archival discovery applications.

**Key Strengths:**
- Temporal depth (1808-1890)
- Multilingual content (English, French, Cree, others)
- Diverse source types (newspapers, books, manuscripts, government records)
- Rich metadata and provenance
- Clean, structured JSON format

**Recommended Next Steps:**
- Sample quality validation across document types
- Language-specific text analysis
- Named entity extraction (places, people, organizations)
- Temporal analysis of newspaper content
- Cross-collection comparisons with other subcollections in this repository
