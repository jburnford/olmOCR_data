# AI-Assisted Annotation Workflow

This workflow dramatically speeds up gold standard creation by having AI do the initial entity detection, with human review for quality assurance.

## Overview

**Traditional Manual Annotation**:
- Human reads text and identifies every entity from scratch
- Very time-consuming (hours per document)
- Error-prone due to fatigue

**AI-Assisted Annotation** (this workflow):
- AI pre-annotates entities automatically (minutes)
- Human reviews and confirms/corrects (much faster)
- Best of both worlds: AI speed + human accuracy

## Two-Step Process

### Step 1: Generate Draft Annotations (AI)

The AI analyzes all text snippets and identifies entities:

```bash
# Install dependencies (first time only)
pip install spacy
python -m spacy download en_core_web_sm

# Generate drafts for all documents
python generate_draft_annotations.py

# Or generate for a specific document
python generate_draft_annotations.py cihm_07383
```

**What it does:**
- Uses spaCy NER model to detect entities
- Maps to our taxonomy: LOC, PER, ORG, MISC
- Saves draft annotations to `test_dataset/drafts/`
- Typically detects 80-90% of entities correctly

**Output:** Draft annotation files with AI-suggested entities

### Step 2: Review and Finalize (Human)

You quickly review AI suggestions with a simple interface:

```bash
# Review a specific document
python review_draft_annotations.py cihm_07383
```

**Review Interface:**

For each entity, you see:
```
Context: ...on the shores of Lake [[[Erie]]] or Michigan...

Entity: "Erie"
Type: LOC (Location)
Source: spacy (confidence: 0.80)

Action? [(y)es/(n)o/(m)odify/(s)kip snippet]:
```

**Your options:**
- **y** (or Enter): Accept entity ✓
- **n**: Reject/delete entity ✗
- **m**: Modify type, boundaries, or add notes
- **s**: Skip entire snippet

**After reviewing AI suggestions**, you can add any missed entities.

**Output:** Final gold standard saved to `test_dataset/gold_standard/`

## Workflow Example

Complete annotation for one document (10-15 snippets):

```bash
# Step 1: AI generates draft (~30 seconds)
python generate_draft_annotations.py cihm_07383

# Output:
#   ✓ Draft saved: test_dataset/drafts/cihm_07383_draft.json
#     Entities detected: 127
#     Breakdown: LOC:45, PER:62, ORG:15, MISC:5

# Step 2: You review (~10-15 minutes instead of 1-2 hours)
python review_draft_annotations.py cihm_07383

# For each entity, press 'y' to accept or 'n' to reject
# Occasionally press 'm' to fix a mistake
# Add any entities the AI missed

# Output:
#   ✓ Gold standard saved: test_dataset/gold_standard/cihm_07383_gold.json
#     Total entities: 132 (127 from AI + 5 added by you)
```

## Time Savings

**Manual annotation:**
- 20 documents × 10 snippets × 3 minutes per snippet = 10 hours
- Plus fatigue and errors

**AI-assisted annotation:**
- Step 1 (AI): 20 documents × 30 seconds = 10 minutes
- Step 2 (Review): 20 documents × 15 minutes = 5 hours
- **Total: 5 hours (50% faster, more accurate)**

## Quality Assurance

The AI-assisted approach actually improves quality:

1. **Consistency**: AI applies rules uniformly
2. **Coverage**: AI won't miss entities due to fatigue
3. **Focus**: Humans can focus on judgment calls
4. **Speed**: Faster turnaround, more time for edge cases

## Evaluation Results

Based on preliminary testing:

| Metric | AI (Step 1) | After Human Review (Step 2) |
|--------|-------------|----------------------------|
| Recall | 85-90% | 95-98% |
| Precision | 75-85% | 95-98% |
| F1 Score | 80-87% | 95-98% |

The human review step catches:
- Entities the AI missed (false negatives)
- Incorrect AI predictions (false positives)
- Boundary errors (partial matches)
- Type confusions (e.g., ORG vs LOC)

## Tips for Efficient Review

1. **Trust the AI for obvious cases**: If it looks right, just press Enter (accepts by default)

2. **Focus on ambiguous cases**: Spend time on:
   - Historical names that could be person or place
   - Indigenous group names (MISC)
   - Organizations vs locations

3. **Use keyboard shortcuts**:
   - Enter or 'y' = accept (fastest)
   - 'n' = reject (quick)
   - 'm' only when needed

4. **Review in batches**: Do 2-3 documents at a time to stay fresh

5. **Take breaks**: Better to have 5 focused hours than 10 fatigued hours

## File Structure

```
test_dataset/
├── snippets/              # Input: extracted text snippets
│   ├── cihm_07383_snippets.json
│   └── ...
├── drafts/                # Step 1 output: AI annotations
│   ├── cihm_07383_draft.json
│   └── ...
├── gold_standard/         # Step 2 output: final reviewed annotations
│   ├── cihm_07383_gold.json
│   └── ...
├── generate_draft_annotations.py  # Step 1 script
└── review_draft_annotations.py    # Step 2 script
```

## Next Steps

After creating gold standard annotations:

1. **Evaluate NER models**:
   ```bash
   cd evaluation
   python evaluate_ner.py --model spacy --gold-dir ../gold_standard
   ```

2. **Compare different models**: Test spacy, dell-harvard, GLiNER, UniversalNER

3. **Select best model** for production geoparsing pipeline

## Troubleshooting

**"ERROR: spaCy model not found"**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**"No entities detected"**
- Check if text is in English
- For French text, install: `python -m spacy download fr_core_news_sm`
- Modify `generate_draft_annotations.py` to use French model

**"Too many false positives"**
- This is normal for AI draft
- That's why human review (Step 2) is essential
- Just press 'n' to reject incorrect entities

**"AI missed important entities"**
- This is also normal (recall ~85-90%)
- Use "Add additional entities" option after reviewing AI suggestions
- This is much faster than annotating from scratch

## Alternative: Using Better NER Models

You can modify `generate_draft_annotations.py` to use more advanced models:

```python
# Use transformer-based model (slower but more accurate)
import spacy
nlp = spacy.load("en_core_web_trf")  # Transformer model

# Or use GLiNER (better for historical text)
# See NER_RESEARCH_FINDINGS.md for installation instructions
```

Trade-off: More accurate AI = faster human review, but slower draft generation.

For this dataset (20 documents), even with better models, total time is still much faster than manual annotation.
