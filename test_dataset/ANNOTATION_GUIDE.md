# Gold Standard Annotation Guide

## Quick Start

### 1. View Available Documents

```bash
cd test_dataset
python create_gold_standard.py
```

This will show you all 20 documents available for annotation.

### 2. Annotate a Document

```bash
python create_gold_standard.py PTR_1883011001
```

Follow the interactive prompts to annotate entities in each snippet.

### 3. Annotation Workflow

For each snippet, you'll:
1. Read the displayed text
2. Identify entities (LOC, PER, ORG, MISC)
3. Enter entity text exactly as it appears
4. Specify entity type
5. Add optional notes
6. Type 'done' when finished with the snippet

---

## Entity Types

### LOC (Location) - **PRIORITY FOR GEOPARSING**
Places, regions, natural features, historical settlements

**Examples:**
- `Fort Carlton`, `Prince Albert`, `Brandon`
- `Saskatchewan River`, `Hudson Bay`, `Qu'Appelle Valley`
- `North-West Territory`, `Rupert's Land`
- `Cumberland House`, `Fort Pitt` (trading posts)
- `Île-à-la-Crosse`, `Lac la Ronge` (French place names)

**Include:**
- Modern and historical place names
- Natural features (rivers, lakes, mountains)
- Indigenous place names
- Directional descriptors when part of name: `North Saskatchewan River`

**Exclude:**
- Generic references: "the river", "the prairie" (without specific name)
- Relative directions: "northward", "westward" (unless part of proper name)

### PER (Person)
Named individuals, including historical figures

**Examples:**
- `Louis Riel`, `Gabriel Dumont`
- `Sir John A. Macdonald`
- `Mgr Grandin`, `Father Lacombe` (include titles when part of name)
- `Big Bear`, `Poundmaker` (indigenous leaders)

**Include:**
- Titles when they're part of how the person is named: `Sir John`, `Chief Big Bear`

**Exclude:**
- Generic titles without names: "the chief", "the father"

### ORG (Organization)
Companies, government bodies, institutions

**Examples:**
- `Hudson's Bay Company`, `North West Company`
- `North-West Mounted Police`
- `Department of Indian Affairs`
- `Oblates of Mary Immaculate`
- `Prince Albert Times`

**Handle ambiguity:**
- `Hudson Bay` (water body) → LOC
- `Hudson's Bay Company` → ORG

### MISC (Miscellaneous)
Indigenous groups, treaties, events, other named entities

**Examples:**
- `Cree`, `Métis`, `Chipewyan`, `Blackfoot` (peoples/groups)
- `Treaty 6`, `Treaty 7`
- `North-West Rebellion`, `Battle of Batoche` (events)

---

## Annotation Tips

### Finding Entities

1. **Scan for capitalized words**: Most entities start with capitals
2. **Look for entity indicators**:
   - LOC: "at", "in", "near", "river", "fort", "settlement"
   - PER: "Mr.", "Sir", "Chief", "Father", "Mgr"
   - ORG: "Company", "Department", "Police", "Association"
3. **Check for compound names**: `Fort à la Corne`, `North West Company`

### Entity Boundaries

**Mark minimal spans** - include only the entity itself:

✅ Correct:
- Input: "at Fort Carlton"
- Annotate: `Fort Carlton`

❌ Incorrect:
- Input: "at Fort Carlton"
- Annotate: `at Fort Carlton` (includes preposition)

**Include articles/determiners only if part of proper name:**
- `The Pas` (city name includes "The") → Include
- `the fort` → Exclude

### Handling Multiple Occurrences

If an entity appears multiple times in a snippet:
- The tool will find all occurrences
- You can annotate all at once (type 'all') or select specific ones

### OCR Errors

**Do NOT correct OCR errors** - annotate as they appear:
- Text has: `Sascatchewan` → Annotate: `Sascatchewan` (LOC)
- Text has: `Pnnce Albert` → Annotate: `Pnnce Albert` (LOC)
- Add note: "OCR error, should be 'Prince Albert'"

### Ambiguous Cases

**Document your reasoning in notes:**
- `Carlton` alone → Note: "Assumed to refer to Fort Carlton based on context"
- `Hudson Bay` → Note: "Refers to water body, not company"

---

## Example Annotation Session

```
=== SNIPPET 1/5 ===
Text:
The North-West Mounted Police arrived at Fort Carlton on the Saskatchewan River
in the spring of 1875. Chief Big Bear was present at the negotiations.

--- Entity #1 ---
Entity text: North-West Mounted Police
Entity type: ORG
Notes: Full organization name

--- Entity #2 ---
Entity text: Fort Carlton
Entity type: LOC
Notes: HBC trading post

--- Entity #3 ---
Entity text: Saskatchewan River
Entity type: LOC
Notes: Major waterway

--- Entity #4 ---
Entity text: Chief Big Bear
Entity type: PER
Notes: Include title as part of name

--- Entity #5 ---
Entity text: done
```

---

## Quality Guidelines

### Target Metrics
- **Completeness**: Annotate ALL entities in each snippet
- **Consistency**: Apply same rules throughout
- **Accuracy**: Double-check entity boundaries

### Common Mistakes to Avoid

1. **Including prepositions**: ❌ `at Fort Carlton` → ✅ `Fort Carlton`
2. **Missing compound names**: ❌ `North` `West Company` → ✅ `North West Company`
3. **Wrong boundaries**: ❌ `Saskatchewan Riv` → ✅ `Saskatchewan River`
4. **Inconsistent types**: Same entity should have same type across snippets

### When to Skip a Snippet

Type `skip` if:
- Snippet is severely corrupted by OCR errors
- Text is in a language you don't understand
- No clear entities are present

---

## Suggested Annotation Strategy

### Phase 1: High-Priority Documents (Newspapers, small books)
Start with these for quick initial gold standard:

```bash
# Newspapers (small, high entity density)
python create_gold_standard.py BDM_1883042601
python create_gold_standard.py PTR_1883011001
python create_gold_standard.py PTR_1885081401

# Small French documents
python create_gold_standard.py P007493
python create_gold_standard.py P000644
```

**Estimated time**: ~1-2 hours for 5 documents

### Phase 2: Medium Books
```bash
python create_gold_standard.py P001454
python create_gold_standard.py P001415
python create_gold_standard.py cihm_29478
```

**Estimated time**: ~2-3 hours

### Phase 3: Large Documents (Sample snippets)
For very large documents (>100K words), the tool has already extracted high-density snippets:

```bash
python create_gold_standard.py P000045
python create_gold_standard.py P000151
python create_gold_standard.py School_Files_Series-RG10_c-7935
```

**Estimated time**: ~3-4 hours

### Total Annotation Time
- **Minimum viable gold standard** (5 docs): ~2 hours
- **Good coverage** (10 docs): ~5 hours
- **Full dataset** (20 docs): ~10-12 hours

---

## Checking Your Work

### View Your Annotations

```bash
cat gold_standard/PTR_1883011001_gold.json | python -m json.tool | less
```

### Count Entities by Type

```bash
python3 << 'EOF'
import json
from pathlib import Path
from collections import Counter

gold_dir = Path('gold_standard')
entity_counts = Counter()

for gold_file in gold_dir.glob('*_gold.json'):
    with open(gold_file) as f:
        data = json.load(f)
        for snippet in data['snippets']:
            for entity in snippet['entities']:
                entity_counts[entity['type']] += 1

print("Entity type distribution:")
for etype, count in entity_counts.most_common():
    print(f"  {etype}: {count}")
print(f"\nTotal: {sum(entity_counts.values())} entities")
EOF
```

---

## Inter-Annotator Agreement (if multiple annotators)

If you have multiple people annotating:

1. Have 2-3 people annotate the same document independently
2. Compare annotations
3. Compute Cohen's Kappa or F1 agreement
4. Resolve disagreements through discussion
5. Establish clear guidelines for ambiguous cases

**Target agreement**: > 0.85 Cohen's Kappa or > 0.90 F1

---

## Need Help?

### Common Questions

**Q: Should I annotate "Hudson Bay Company" or "Hudson's Bay Company"?**
A: Annotate exactly as written in the text. The OCR may have errors.

**Q: What if I'm not sure about an entity type?**
A: Add a note explaining your reasoning. When in doubt, prioritize LOC for geoparsing.

**Q: The text mentions "the fort" multiple times. Should I annotate it?**
A: No - only annotate when a specific fort name is mentioned.

**Q: How do I handle French accents in entity text?**
A: Copy exactly as shown in the snippet, including all diacritics.

---

## Next Steps

After creating gold standard:

1. **Run baseline NER models** on snippets
2. **Evaluate predictions** against your gold standard
3. **Analyze errors** to select best model
4. **Iterate** - add more documents if needed

See `evaluation/README.md` for model evaluation workflow.
