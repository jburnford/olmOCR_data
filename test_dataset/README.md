# Saskatchewan Historical Documents - NER Test Dataset

**Created:** 2025-11-07
**Purpose:** Gold standard evaluation dataset for Named Entity Recognition on historical Saskatchewan documents

---

## 🚀 Quick Start: Create Gold Standard Annotations

### Recommended: Claude-Assisted Workflow (Fast & Accurate!)

**Step 1:** Ask Claude to create draft annotations
```
"Claude, please analyze the snippets and create draft annotations for [document_id]"
```

**Step 2:** Review Claude's work (5-10 min per document)
```bash
python test_dataset/review_annotations.py [document_id]
```

**See full guide**: [CLAUDE_ASSISTED_WORKFLOW.md](CLAUDE_ASSISTED_WORKFLOW.md)

**Time savings**: 80% faster than manual annotation!

### Alternative: Manual Annotation
```bash
python test_dataset/create_gold_standard.py [document_id]
```
See: [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md)

---

## Dataset Overview

This test dataset contains **20 carefully selected documents** representing the diversity of the Saskatchewan 1808-1946 OCR collection:

### Document Distribution

| Type | Count | Examples |
|------|-------|----------|
| **Newspapers** | 3 | Prince Albert Times (1883-1885), Brandon Daily Mail (1883) |
| **Books (English)** | 7 | Travel narratives, historical collections, exploration accounts |
| **Books (French)** | 7 | Mission letters, Riel-related documents, exploration reports |
| **Government Records** | 2 | School Files Series (RG10) |
| **Maps** | 1 | North-West Territory map (1814, bilingual) |

### Temporal Distribution
- **Early Period (1808-1850)**: 5 documents
- **Mid Period (1851-1870)**: 3 documents
- **Late Period (1871-1890)**: 12 documents

### Language Distribution
- **English**: 12 documents
- **French**: 7 documents
- **Bilingual (English/French)**: 1 document

---

## Sampling Strategy

Documents were selected using stratified random sampling to ensure diversity across:

1. **Document type**: Newspapers, books, government records
2. **Time period**: Early (1808-1850), Mid (1851-1870), Late (1871-1890)
3. **Language**: English and French representation
4. **OCR quality**: Mix of print quality and microform sources
5. **Content relevance**: High geographic content for geoparsing evaluation

### Random seed: 42 (reproducible)

---

## Document Inventory

| ID | Title (abbreviated) | Year | Lang | Type | Pages | Size |
|----|---------------------|------|------|------|-------|------|
| PTR_1883011001 | Prince Albert times (1883-01-10) | 1883 | EN | Newspaper | 4 | Small |
| PTR_1885081401 | Prince Albert times (1885-08-14) | 1885 | EN | Newspaper | 4 | Small |
| BDM_1883042601 | Daily mail (1883-04-26) | 1883 | EN | Newspaper | 4 | Small |
| P000045 | Travels and adventures in Canada... | 1809 | EN | Book | 340 | Large |
| P000151 | Narrative of a journey to polar sea | 1823 | EN | Book | ~300 | Large |
| P001454 | Louis Riel: assemblée de Lachine | 1885 | FR | Book | ~50 | Medium |
| P001415 | La mort de Riel et la voix du sang | 1885 | FR | Book | ~30 | Small |
| P007493 | Faits Divers (Mgr Grandin) | 1868 | FR | Book | 1 | Tiny |
| P000644 | Lettre du Père Lacombe | 1872 | FR | Book | ~10 | Small |
| P000081 | Relation d'un voyage (1810-14) | 1820 | FR | Book | ~200 | Large |
| P000342 | Rapport exploration lac Supérieur | 1859 | FR | Book | ~100 | Medium |
| cihm_29478 | Prince Albert and North Saskatchewan | 1890 | EN | Book | ~50 | Medium |
| cihm_07383 | Tecumseh and Shawnee prophet | 1878 | EN | Book | ~200 | Large |
| cihm_21045 | Brief description of Nova Scotia | 1818 | EN | Book | ~100 | Medium |
| cihm_50569 | Historical collections NY state | 1841 | EN | Book | ~400 | Large |
| cihm_38152 | Bracebridge Hall | 1850 | EN | Book | ~200 | Large |
| cihm_41970 | Letter from James Stuart | 1831 | EN | Book | ~50 | Small |
| School_Files_Series-RG10_c-7935 | School Files Series (RG10) | 1879 | EN | Govt | 1715 | Huge |
| School_Files_Series-RG10_c-8670 | School Files Series (RG10) | 1879 | EN | Govt | ~1500 | Huge |
| bp_2820 | Map of North-West Territory | 1814 | EN/FR | Map | 1 | Tiny |

---

## Entity Types for Annotation

Following standard NER conventions with geoparsing focus:

### Primary Entity Types (Required)

1. **LOC** (Location) - **PRIORITY FOR GEOPARSING**
   - Geographic places: cities, towns, villages, settlements
   - Natural features: rivers, lakes, mountains, prairies
   - Regions: territories, provinces, districts
   - Historical place names: forts, trading posts
   - Indigenous territories and traditional lands

   Examples:
   - `Fort Carlton`, `Prince Albert`, `Saskatchewan River`
   - `Hudson Bay`, `Athabasca`, `Red River Colony`
   - `North-West Territory`, `Rupert's Land`

2. **PER** (Person)
   - Named individuals
   - Titles with names: `Mgr Grandin`, `Sir John A. Macdonald`
   - Indigenous leaders: `Big Bear`, `Poundmaker`, `Louis Riel`

3. **ORG** (Organization)
   - Companies: `Hudson's Bay Company`, `North West Company`
   - Government bodies: `North-West Mounted Police`, `Department of Indian Affairs`
   - Religious organizations: `Oblates of Mary Immaculate`
   - Newspapers: `Prince Albert Times`

### Secondary Entity Types (Optional, for advanced evaluation)

4. **MISC** (Miscellaneous)
   - Indigenous groups: `Cree`, `Métis`, `Chipewyan`, `Blackfoot`
   - Treaties: `Treaty 6`, `Treaty 7`
   - Events: `North-West Rebellion`, `Battle of Batoche`
   - Ships, expeditions

---

## Annotation Guidelines

### General Principles

1. **Mark minimal spans**: Include only the entity itself, not determiners/modifiers
   - ✅ `Fort Carlton`
   - ❌ `the Fort Carlton`

2. **Include titles/honorifics when part of proper name**
   - ✅ `Sir John A. Macdonald`
   - ✅ `Mgr Grandin`
   - ❌ `Mister Smith` (generic title)

3. **Handle nested entities by priority**: LOC > ORG > PER
   - `Hudson Bay Company` → ORG (not LOC for "Hudson Bay")
   - `Saskatchewan River District` → LOC

4. **Mark historical place names even if no longer in use**
   - `Carlton House`, `Cumberland House`, `Rocky Mountain House`
   - `Red River Settlement`, `Selkirk Colony`

5. **Include alternate spellings and archaic forms**
   - `Sascatchewan` (historical spelling)
   - `Saskachewine` (archaic)

### LOC-Specific Guidelines (Critical for Geoparsing)

#### Include:
- **Modern place names**: `Prince Albert`, `Regina`, `Saskatoon`
- **Historical settlements**: `Fort à la Corne`, `Fort Pitt`, `Frog Lake`
- **Natural features**: `Saskatchewan River`, `Qu'Appelle Valley`, `Touchwood Hills`
- **Directional descriptors when part of name**: `North Saskatchewan River`
- **Indigenous place names**: `Manitou Stone`, `Buffalo Pound`
- **French place names**: `Lac la Ronge`, `Île-à-la-Crosse`

#### Exclude:
- **Generic descriptors**: `the river`, `the prairie`, `the territory` (without specific name)
- **Relative directions**: `northward`, `in the west` (unless part of proper name)

#### Ambiguous Cases:
- **`Hudson Bay` vs `Hudson's Bay Company`**:
  - Mark as LOC if referring to body of water
  - Mark as ORG if referring to company (context-dependent)

- **`Carlton` alone**:
  - If clearly refers to `Fort Carlton` → LOC
  - If ambiguous → annotate based on context

### OCR Error Handling

**Do NOT correct OCR errors** in the text. Annotate entities as they appear, even with errors:
- Original text: `Sascatchewan` → Annotate as LOC
- Original text: `Pnnce Albert` → Annotate as LOC
- Document the error in notes for quality assessment

---

## File Structure

```
test_dataset/
├── README.md (this file)
├── documents/                  # Raw OCR JSON files
│   ├── PTR_1883011001.json
│   ├── P000045.json
│   └── ...
├── snippets/                   # Extracted text snippets for annotation
│   ├── PTR_1883011001_snippets.json
│   ├── P000045_snippets.json
│   └── ...
├── gold_standard/              # Human-annotated entities
│   ├── PTR_1883011001_gold.json
│   ├── P000045_gold.json
│   └── ...
├── predictions/                # Model predictions for comparison
│   ├── spacy/
│   ├── dell_harvard/
│   ├── biglam_toponym/
│   ├── gliner/
│   └── universalner/
└── evaluation/                 # Evaluation scripts and results
    ├── evaluate_ner.py
    ├── results_summary.json
    └── per_model_analysis.json
```

---

## Snippet Extraction Strategy

For each document:

1. **Newspapers (4 pages)**: Extract full text (already small)
2. **Books (<100 pages)**: Extract 5-10 representative snippets (500-1000 tokens each)
3. **Books (>100 pages)**: Extract 10-15 snippets (500-1000 tokens each)
4. **Government records**: Extract 20 snippets (high entity density sections)

### Snippet Selection Criteria:
- High geographic content (mentions of places)
- Varied contexts (urban, rural, natural features)
- Mix of English and French
- Representative of document style

---

## Annotation Format

### JSON Structure

```json
{
  "document_id": "PTR_1883011001",
  "snippet_id": "PTR_1883011001_001",
  "text": "The North-West Mounted Police arrived at Fort Carlton on the Saskatchewan River...",
  "metadata": {
    "year": 1883,
    "language": "en",
    "doc_type": "newspaper",
    "page": 2,
    "char_start": 1024,
    "char_end": 1524
  },
  "entities": [
    {
      "text": "North-West Mounted Police",
      "start": 4,
      "end": 29,
      "type": "ORG",
      "confidence": 1.0,
      "notes": "Full organization name"
    },
    {
      "text": "Fort Carlton",
      "start": 41,
      "end": 53,
      "type": "LOC",
      "confidence": 1.0,
      "notes": "Historical Hudson's Bay Company post"
    },
    {
      "text": "Saskatchewan River",
      "start": 61,
      "end": 79,
      "type": "LOC",
      "confidence": 1.0,
      "notes": "Major waterway"
    }
  ],
  "annotator": "human",
  "annotation_date": "2025-11-07",
  "quality_notes": "Clear text, no OCR errors"
}
```

---

## Evaluation Metrics

### Primary Metrics (Standard NER)
- **Precision**: Correct predictions / Total predictions
- **Recall**: Correct predictions / Total gold entities
- **F1 Score**: Harmonic mean of precision and recall
- **Exact match**: Entity boundaries and type must match exactly
- **Partial match**: Overlapping spans with correct type

### Geoparsing-Specific Metrics
- **LOC F1**: F1 score for location entities only
- **Toponym recognition rate**: % of place names identified
- **Disambiguation potential**: % of LOCs resolvable to GeoNames/Wikidata

### Error Analysis Categories
- **False positives**: Predicted entities not in gold standard
- **False negatives**: Missed gold standard entities
- **Boundary errors**: Correct type, wrong span
- **Type errors**: Correct span, wrong type
- **OCR-induced errors**: Errors due to OCR quality

---

## Usage Workflow

### Phase 1: Gold Standard Creation (Week 1)
1. Extract snippets from 20 documents → `snippets/`
2. Manual annotation using guidelines → `gold_standard/`
3. Inter-annotator agreement check (if multiple annotators)
4. Finalize gold standard

### Phase 2: Model Evaluation (Week 1-2)
1. Run each NER model on snippets
2. Save predictions → `predictions/[model_name]/`
3. Compare against gold standard
4. Generate evaluation reports

### Phase 3: Analysis & Selection (Week 2)
1. Analyze per-document, per-type performance
2. Identify strengths/weaknesses of each model
3. Select best model(s) for full corpus
4. Document findings

---

## Expected Inter-Annotator Agreement

Target metrics for quality assurance:
- **Cohen's Kappa**: > 0.85 (substantial agreement)
- **Entity F1 between annotators**: > 0.90
- **LOC-specific agreement**: > 0.92 (critical for geoparsing)

---

## Known Challenges

### 1. Historical Place Name Variation
- Multiple spellings: `Sascatchewan`, `Saskachawine`, `Saskatchewan`
- Name changes: `Pile O'Bones` → `Regina`
- French/English variants: `Lac la Ronge` / `Lac Ronge` / `Reindeer Lake`

### 2. OCR Quality Issues
- Gothic/Fraktur fonts in some documents
- Microform degradation
- Mixed languages causing OCR confusion

### 3. Entity Ambiguity
- `Hudson Bay` (location) vs `Hudson's Bay Company` (organization)
- `Carlton` alone (could be Fort Carlton, person name, etc.)
- Generic terms: `the river`, `the settlement`

### 4. Indigenous Names
- Multiple transliterations: `Piapot` / `Payipwat`
- Descriptive vs proper names
- Colonial vs indigenous place names

---

## Citation

If using this dataset, please cite:

```
Saskatchewan Historical Documents NER Test Dataset (2025)
Repository: olmOCR_data
Created for geoparsing and knowledge extraction from historical Saskatchewan documents (1808-1946)
Annotation guidelines follow CoNLL-2003 conventions with extensions for historical toponymy
```

---

## Contact & Contribution

For questions, corrections, or to contribute additional annotations, see repository documentation.

**Version**: 1.0
**Last Updated**: 2025-11-07
