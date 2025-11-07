# Saskatchewan NER Test Dataset - Summary

**Created:** 2025-11-07
**Purpose:** Gold standard dataset for evaluating NER models on Saskatchewan historical documents (1808-1946)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Total Documents** | 20 |
| **Total Snippets** | 205 |
| **Total Words** | ~1.95 million |
| **Languages** | English (13), French (7), Bilingual (1) |
| **Time Period** | 1809-1890 |
| **Document Types** | Newspapers (3), Books (15), Government (2) |

---

## Dataset Composition

### By Document Type
- **Newspapers**: 3 documents, 11 snippets (~6,655 words)
  - Prince Albert Times and Saskatchewan Review (1883, 1885)
  - Brandon Daily Mail (1883)

- **Books**: 15 documents, 180 snippets (~1.9M words)
  - English: 8 books (exploration narratives, historical collections)
  - French: 7 books (mission letters, Riel-related documents, exploration reports)

- **Government Records**: 2 documents, 30 snippets (~680K words)
  - School Files Series (RG10)

### By Language
- **English**: 13 documents, 125 snippets
- **French**: 7 documents, 79 snippets
- **Bilingual (EN/FR)**: 1 document, 1 snippet

### By Time Period
- **Early (1809-1850)**: 5 documents
- **Mid (1851-1870)**: 3 documents
- **Late (1871-1890)**: 12 documents

---

## File Structure

```
test_dataset/
├── README.md                          # Comprehensive documentation
├── ANNOTATION_GUIDE.md                # Step-by-step annotation instructions
├── extract_snippets.py                # Automated snippet extraction tool
├── create_gold_standard.py            # Interactive annotation tool
│
├── snippets/                          # Extracted text snippets (205 total)
│   ├── SUMMARY.json                  # Metadata summary
│   ├── PTR_1883011001_snippets.json
│   ├── P000045_snippets.json
│   └── ...
│
├── gold_standard/                     # Human-annotated entities (create these!)
│   ├── PTR_1883011001_gold.json
│   └── ...
│
├── predictions/                       # Model predictions
│   ├── spacy/
│   ├── dell_harvard/
│   ├── biglam_toponym/
│   ├── gliner/
│   └── universalner/
│
└── evaluation/                        # Evaluation framework
    ├── README.md                     # Evaluation workflow guide
    ├── evaluate_ner.py               # Evaluation script
    └── [model_name]_evaluation.json  # Results (generated)
```

---

## Snippet Extraction Strategy

Documents were intelligently sampled based on:

1. **Entity density**: Passages with high concentration of places, people, organizations
2. **Representation**: Diverse contexts across the document
3. **Size-adaptive**: More snippets for larger documents

### Extraction Rules
- **Tiny docs (<500 words)**: Full text (1 snippet)
- **Small docs (500-2000 words)**: 1-3 snippets
- **Medium docs (2000-10K words)**: 5-10 snippets
- **Large docs (>10K words)**: 10-15 snippets

### Snippet Size
- **Target**: 800 characters
- **Range**: 300-1200 characters
- **Boundaries**: Sentence-aligned (not mid-word)

---

## Sample Documents

### High-Priority for Initial Annotation

**Quick start (1-2 hours):**
```bash
python create_gold_standard.py BDM_1883042601      # 1 snippet, newspaper
python create_gold_standard.py PTR_1883011001      # 5 snippets, newspaper
python create_gold_standard.py P007493             # 1 snippet, French
python create_gold_standard.py P000644             # 5 snippets, French
```

**Good coverage (5 hours):**
Add these medium-sized books:
```bash
python create_gold_standard.py P001454             # 5 snippets, French, Riel
python create_gold_standard.py P001415             # 7 snippets, French, Riel
python create_gold_standard.py cihm_29478          # 10 snippets, Prince Albert guide
```

### Document Highlights

| Document | Why Include | Entity Richness | Challenge |
|----------|-------------|-----------------|-----------|
| **PTR_1883011001** | Saskatchewan newspaper, 1883 | High LOC density | Standard entities |
| **P000045** | Classic exploration narrative | Indigenous places, routes | Historical spellings |
| **P001454** | Riel assemblée (French) | Political entities, places | French + OCR |
| **School_Files_RG10** | Government records | Indigenous schools, locations | Dense bureaucratic text |
| **bp_2820** | Bilingual map | Geographic names | Minimal text, high LOC |

---

## Expected Entity Distribution

Based on corpus analysis, anticipate:

| Entity Type | Estimated % | Primary Sources |
|-------------|-------------|-----------------|
| **LOC** | ~55-60% | All documents, esp. exploration narratives |
| **PER** | ~20-25% | Newspapers, political documents |
| **ORG** | ~10-15% | Newspapers, government records |
| **MISC** | ~5-10% | Various (indigenous groups, treaties, events) |

**Total estimated entities across 205 snippets**: 800-1200

---

## Annotation Workflow

### Step 1: Setup (Done ✓)
- ✅ 20 documents sampled
- ✅ 205 snippets extracted
- ✅ Annotation tool created
- ✅ Evaluation framework ready

### Step 2: Annotate (Your Task)
```bash
cd test_dataset
python create_gold_standard.py [document_id]
```

Follow interactive prompts. See `ANNOTATION_GUIDE.md` for detailed instructions.

**Time estimates:**
- Newspaper (1-5 snippets): 10-30 min
- Small book (5-7 snippets): 30-60 min
- Large book (15 snippets): 1-2 hours

### Step 3: Run Models on Snippets
Generate predictions from each model (dell-harvard, GLiNER, UniversalNER, etc.)

Save to: `predictions/[model_name]/[doc_id]_pred.json`

### Step 4: Evaluate
```bash
python evaluation/evaluate_ner.py dell_harvard
python evaluation/evaluate_ner.py gliner
python evaluation/evaluate_ner.py universalner
```

### Step 5: Select Best Model
Based on LOC F1 score and cost-benefit analysis.

---

## Key Features

### 1. Intelligent Snippet Selection
- Not random - prioritizes high entity density
- Uses heuristics: capitalized words, geographic terms, titles
- Sentence-aligned boundaries (clean, readable)

### 2. Metadata Preservation
Each snippet includes:
- Document ID and title
- Year, language, document type
- Position in original document (char offsets)
- Entity density score

### 3. Multi-Language Support
- English (13 docs): Standard modern English to archaic spellings
- French (7 docs): Mission letters, political documents
- Handles accents and diacritics correctly

### 4. OCR Quality Representation
Mix of:
- High-quality print (newspapers)
- Microform degradation (historical books)
- Gothic/Fraktur fonts (early period)
- Handwritten elements (government records)

### 5. Flexible Annotation
- Interactive terminal-based tool
- Handles multiple occurrences of same entity
- Notes field for ambiguous cases
- Skip option for corrupted snippets

---

## Evaluation Metrics

### Standard NER Metrics
- **Precision**: % of predicted entities that are correct
- **Recall**: % of gold entities that are found
- **F1 Score**: Harmonic mean (overall quality)
- **Per-type breakdown**: LOC, PER, ORG, MISC

### Geoparsing-Specific Metrics
- **LOC F1**: Critical for your use case
- **LOC Recall**: Don't miss place names
- **Toponym recognition rate**: % of geographic entities found

### Error Analysis
- False positives (hallucinations)
- False negatives (missed entities)
- Boundary errors (wrong span)
- Type errors (wrong classification)

---

## Usage for Nibi Setup

### On Your nibi Environment

1. **Transfer test dataset:**
```bash
# On your local machine
scp -r test_dataset/ user@nibi:/path/to/olmOCR_data/

# Or via git
git clone [repo] && cd olmOCR_data
```

2. **Install dependencies:**
```bash
# Minimal requirements for annotation
pip install json pathlib

# For running models (install as needed)
pip install transformers torch spacy gliner
pip install vllm  # For UniversalNER
```

3. **Start annotating:**
```bash
cd test_dataset
python create_gold_standard.py --help  # See options
python create_gold_standard.py BDM_1883042601  # Start with small doc
```

4. **Run models in parallel:**
```bash
# Example: Run dell-harvard on all snippets
python scripts/run_dell_harvard_predictions.py

# Example: Run GLiNER
python scripts/run_gliner_predictions.py

# Example: Run UniversalNER on DRAC cluster
sbatch scripts/run_universalner.slurm
```

5. **Evaluate and compare:**
```bash
python evaluation/evaluate_ner.py dell_harvard
python evaluation/evaluate_ner.py gliner
python evaluation/evaluate_ner.py universalner

# Compare results
python evaluation/compare_models.py
```

---

## Quality Assurance

### Inter-Annotator Agreement (if applicable)
If you have multiple annotators:
- Have 2-3 people annotate same document
- Compute Cohen's Kappa or F1 agreement
- Target: > 0.85 agreement
- Resolve disagreements through discussion

### Validation Checks
- **Completeness**: All snippets annotated
- **Consistency**: Same entities have same type
- **Boundary accuracy**: No trailing spaces, proper spans
- **Type accuracy**: Follow guidelines for LOC/PER/ORG/MISC

---

## Expected Outcomes

### Minimum Viable Gold Standard (5 documents)
- **Time**: ~2 hours of annotation
- **Entities**: ~150-200 entities
- **Coverage**: Basic evaluation of each model
- **Decision**: Can identify clearly best/worst models

### Good Coverage (10 documents)
- **Time**: ~5 hours of annotation
- **Entities**: ~350-500 entities
- **Coverage**: Statistical significance
- **Decision**: Confident model selection

### Full Dataset (20 documents)
- **Time**: ~10-12 hours of annotation
- **Entities**: ~800-1200 entities
- **Coverage**: Comprehensive, publication-quality
- **Decision**: Fine-grained analysis, error categorization

---

## Next Steps

1. **Annotate 5 documents** (start small):
   - 3 English newspapers
   - 2 French books

2. **Run 3 models** for comparison:
   - dell-harvard (baseline)
   - GLiNER (fast zero-shot)
   - UniversalNER (high-accuracy)

3. **Evaluate and select**:
   - Compare LOC F1 scores
   - Check cost (GPU hours)
   - Select best model

4. **Scale to full corpus** (1,222 documents):
   - Run selected model(s)
   - Extract all LOC entities
   - Feed to geoparsing pipeline

5. **Integrate with Neo4j**:
   - Match entities to GeoNames/Wikidata
   - Build knowledge graph
   - Enable geographic queries

---

## Support Files

All documentation included:
- ✅ `test_dataset/README.md` - Comprehensive overview
- ✅ `test_dataset/ANNOTATION_GUIDE.md` - Step-by-step instructions
- ✅ `test_dataset/evaluation/README.md` - Evaluation workflow
- ✅ `NER_RESEARCH_FINDINGS.md` - Model comparisons and recommendations

---

## Summary

You now have:
- **20 diverse documents** spanning 1809-1890
- **205 intelligently extracted snippets** ready for annotation
- **Interactive annotation tool** with clear guidelines
- **Automated evaluation framework** for model comparison
- **Complete documentation** for workflow

**Estimated total time to gold standard**: 10-12 hours of careful annotation

**Expected outcome**: High-confidence selection of best NER model for Saskatchewan historical documents, enabling large-scale knowledge extraction for your geoparsing pipeline.

**Ready to start**: Begin with `python create_gold_standard.py BDM_1883042601`
