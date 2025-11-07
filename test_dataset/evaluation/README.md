# NER Model Evaluation Framework

## Overview

This framework evaluates Named Entity Recognition models against the gold standard annotations created from Saskatchewan historical documents.

---

## Evaluation Workflow

### Step 1: Create Gold Standard

Annotate at least 5-10 documents to establish a baseline:

```bash
cd test_dataset
python create_gold_standard.py BDM_1883042601
python create_gold_standard.py PTR_1883011001
# ... annotate more documents
```

Gold standard files saved to: `gold_standard/`

### Step 2: Generate Model Predictions

Run each NER model on the snippets and save predictions in the same format as gold standard.

**Prediction format:**
```json
{
  "document_id": "PTR_1883011001",
  "model": "spacy",
  "metadata": {...},
  "snippets": [
    {
      "snippet_id": "001",
      "text": "...",
      "entities": [
        {
          "text": "Fort Carlton",
          "start": 41,
          "end": 53,
          "type": "LOC",
          "confidence": 0.95
        }
      ]
    }
  ]
}
```

Save predictions to:
```
predictions/
├── spacy/
│   ├── PTR_1883011001_pred.json
│   └── ...
├── dell_harvard/
│   ├── PTR_1883011001_pred.json
│   └── ...
├── gliner/
│   └── ...
└── universalner/
    └── ...
```

### Step 3: Run Evaluation

```bash
cd test_dataset
python evaluation/evaluate_ner.py spacy
python evaluation/evaluate_ner.py dell_harvard
python evaluation/evaluate_ner.py gliner
python evaluation/evaluate_ner.py universalner
```

---

## Metrics Computed

### Overall Metrics

**Exact Match:**
- **Precision**: Correct predictions / Total predictions
- **Recall**: Correct predictions / Total gold entities
- **F1 Score**: Harmonic mean of precision and recall
- Entity boundaries and type must match exactly

**Partial Match:**
- Allows overlapping boundaries if type matches
- More lenient metric for practical applications

### Per-Entity-Type Metrics

Separate P/R/F1 for each entity type:
- LOC (critical for geoparsing)
- PER
- ORG
- MISC

### Error Analysis

**Error Categories:**
1. **False Positives**: Predicted but not in gold standard
   - Model hallucinating entities
   - Wrong entity type assigned

2. **False Negatives**: In gold standard but not predicted
   - Model missed entities
   - Low recall issues

3. **Boundary Errors**: Overlaps with gold but wrong span
   - `Saskatchewan` (pred) vs `Saskatchewan River` (gold)
   - Tokenization issues

4. **Type Errors**: Correct span but wrong type
   - `Hudson Bay` as ORG instead of LOC
   - Ambiguity in entity classification

---

## Example Evaluation Output

```
================================================================================
NER EVALUATION REPORT: dell_harvard
================================================================================

Overall Performance (Exact Match):
  Precision: 0.887
  Recall:    0.834
  F1 Score:  0.860

  True Positives:  167
  False Positives: 21
  False Negatives: 33
  Total Gold:      200
  Total Predicted: 188

--------------------------------------------------------------------------------
Per-Entity-Type Performance:
--------------------------------------------------------------------------------
Type     Precision    Recall       F1           Gold     Pred
----------------------------------------------------------------------
LOC      0.912        0.891        0.901        120      128
MISC     0.800        0.727        0.762        22       20
ORG      0.857        0.800        0.828        30       28
PER      0.875        0.750        0.808        28       24

--------------------------------------------------------------------------------
Per-Document Performance:
--------------------------------------------------------------------------------
Document                            Precision    Recall       F1
----------------------------------------------------------------------
BDM_1883042601                      0.950        0.900        0.924
PTR_1883011001                      0.880        0.850        0.865
PTR_1885081401                      0.870        0.820        0.844

================================================================================
```

---

## Comparing Models

### Generate Comparison Report

```python
import json
from pathlib import Path

models = ['spacy', 'dell_harvard', 'gliner', 'universalner']
results = {}

for model in models:
    eval_file = Path(f'evaluation/{model}_evaluation.json')
    if eval_file.exists():
        with open(eval_file) as f:
            data = json.load(f)
            # Extract overall F1
            total_tp = sum(r['overall_exact']['true_positives'] for r in data['results'])
            total_fp = sum(r['overall_exact']['false_positives'] for r in data['results'])
            total_fn = sum(r['overall_exact']['false_negatives'] for r in data['results'])
            total_gold = sum(r['overall_exact']['total_gold'] for r in data['results'])
            total_pred = sum(r['overall_exact']['total_pred'] for r in data['results'])

            precision = total_tp / total_pred if total_pred > 0 else 0
            recall = total_tp / total_gold if total_gold > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            results[model] = {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }

# Print comparison
print(f"{'Model':<20} {'Precision':<12} {'Recall':<12} {'F1':<12}")
print("-" * 60)
for model, metrics in sorted(results.items(), key=lambda x: x[1]['f1'], reverse=True):
    print(f"{model:<20} {metrics['precision']:<12.3f} {metrics['recall']:<12.3f} {metrics['f1']:<12.3f}")
```

---

## Model Selection Criteria

### For Geoparsing (LOC Focus)

**Priority Metrics:**
1. **LOC F1 Score** (primary)
2. **LOC Recall** (don't miss place names)
3. **Overall F1** (general quality)

**Decision Thresholds:**
- LOC F1 > 0.85: Excellent for geoparsing
- LOC F1 0.75-0.85: Good, acceptable
- LOC F1 < 0.75: Needs improvement

### For General NER

**Priority Metrics:**
1. **Overall F1** (balanced performance)
2. **Per-type F1** (consistency across types)
3. **Precision** (if false positives are costly)

### Cost-Benefit Analysis

Consider:
- **Inference speed** (docs/hour)
- **GPU requirements** (memory, compute)
- **Quality gain** (does higher F1 justify higher cost?)

Example decision matrix:

| Model | LOC F1 | Speed | GPU Memory | Verdict |
|-------|--------|-------|------------|---------|
| dell-harvard | 0.90 | 100 docs/hr | 4GB | ✅ **Best balance** |
| UniversalNER | 0.93 | 20 docs/hr | 16GB | Consider for high-value docs |
| GLiNER | 0.82 | 200 docs/hr | 2GB | Good for exploration |
| spaCy | 0.68 | 150 docs/hr | 2GB | Baseline only |

---

## Error Analysis Deep Dive

### Investigating False Negatives

Entities missed by model - potential causes:
1. **OCR quality**: Corrupted text prevents recognition
2. **Historical spelling**: Old spellings not in training data
3. **Context dependence**: Entity requires broader context
4. **Training data gap**: Entity type/pattern not seen during training

### Investigating False Positives

Entities incorrectly predicted:
1. **Generic terms**: Model tags "the river" as LOC
2. **Context confusion**: "Hudson Bay" (company) tagged as LOC
3. **Tokenization**: Model splits/merges tokens incorrectly
4. **Overfitting**: Model too aggressive in tagging

### Document-Specific Issues

Check per-document F1:
- **High variance**: Some doc types handled better than others
- **Language effects**: French vs English performance
- **OCR quality correlation**: Bad OCR → bad NER

---

## Iterative Improvement

### If Results Are Poor (F1 < 0.75)

1. **Annotate more documents**: Especially from low-performing types
2. **Add more snippets**: From documents with high error rates
3. **Review guidelines**: Ensure consistent annotation
4. **Try different models**: Some may handle historical text better

### If Results Are Good (F1 > 0.85)

1. **Proceed to full corpus**: Run on all 1,222 documents
2. **Spot check**: Manually review 50-100 random predictions
3. **Monitor edge cases**: Track entities in ambiguous contexts
4. **Integrate with geoparsing**: Feed LOC entities to gazetteer matching

---

## Reproducibility

### Save Evaluation Configuration

```json
{
  "evaluation_date": "2025-11-07",
  "gold_standard_version": "1.0",
  "models_evaluated": [
    {
      "name": "dell_harvard",
      "version": "historical_newspaper_ner",
      "huggingface_id": "dell-research-harvard/historical_newspaper_ner",
      "parameters": {
        "max_length": 512,
        "device": "cuda"
      }
    }
  ],
  "documents_annotated": 10,
  "total_entities": 350,
  "entity_distribution": {
    "LOC": 180,
    "PER": 80,
    "ORG": 60,
    "MISC": 30
  }
}
```

---

## Next Steps After Evaluation

1. **Select best model(s)** based on F1 scores and cost
2. **Run on full corpus** (1,222 documents)
3. **Extract LOC entities** for geoparsing pipeline
4. **Match to gazetteers** (GeoNames, Wikidata)
5. **Populate Neo4j graph** with extracted knowledge

See main NER research document for full pipeline architecture.
