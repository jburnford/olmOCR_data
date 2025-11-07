# NER Research Findings for Saskatchewan Historical OCR Data (1808-1946)

**Date:** 2025-11-07
**Purpose:** Evaluate NER approaches for knowledge extraction and geoparsing from historical Saskatchewan documents

---

## Executive Summary

Recent research (2024-2025) shows that **LLMs with proper prompting can now outperform traditional spaCy/BERT models** for historical NER, but **fine-tuned BERT models specifically trained on historical newspapers remain highly competitive** and are more cost-effective for large-scale processing. Several pre-trained models exist specifically for late 19th/early 20th century text. **UniversalNER (ICLR 2024)** represents a middle ground: a 7B model distilled from ChatGPT that outperforms it while being 10x smaller, trained on 13,020+ entity types.

### Key Recommendation
**Start with fine-tuned historical models (dell-research-harvard/historical_newspaper_ner or BigLAM models), then benchmark against zero-shot GLiNER and UniversalNER for your specific corpus. Use UniversalNER if you need broad entity coverage beyond standard LOC/PER/ORG.**

---

## Best Available Models for Saskatchewan Data (1808-1946)

### 1. **dell-research-harvard/historical_newspaper_ner** ⭐ TOP CHOICE
**Model:** Fine-tuned RoBERTa-large
**Hugging Face:** `dell-research-harvard/historical_newspaper_ner`

**Strengths:**
- Specifically designed for **OCR-corrupted historical newspaper text**
- Trained on American historical newspapers with OCR errors
- F1 score: **90.4%** for entity span detection (outperforms RoBERTa-large on CoNLL03)
- Recognizes: LOC, ORG, PER, MISC
- **Perfect fit for your Prince Albert Times, Brandon Daily Mail, etc.**

**Performance on OCR errors:**
- Maintains high accuracy even with noisy OCR input
- Research shows NER accuracy typically drops from 90% to 50% when word error rate increases from 8% to 50%
- This model was specifically trained to handle such degradation

**When to use:** First choice for newspaper content (353 docs in your collection)

---

### 2. **BigLAM Historic Language Models** ⭐ EXCELLENT FOR GEOPARSING
**Collection:** `biglam/historic-language-modeling`
**Hugging Face:** https://huggingface.co/collections/biglam/historic-language-modeling-64f9a0af6b021d61eee993e2

**Available Models:**
- **BERT models fine-tuned on 19th century books (1760-1900)**
  - Temporal subsets: 1760-1850, 1850-1875
  - ~5.1 billion tokens training data

- **Toponym detection model** (critical for your geoparsing pipeline!)
  - Specifically trained to detect place names in historical collections
  - Fine-tuned on 19th century text

- **hmBERT: Historical Multilingual BERT**
  - Languages: German, English, French, Swedish, Finnish
  - Multiple size variants (64k vocab)
  - Good for handling multilingual documents (you have 148 French docs)

**When to use:**
- For books/monographs (264 docs)
- **For geoparsing toponym extraction** (your stated use case)
- For French-language documents

---

### 3. **GLiNER: Zero-Shot NER** ⭐ BEST FOR FLEXIBILITY
**Model:** `urchade/gliner_multi-v2.1`
**GitHub:** https://github.com/urchade/GLiNER
**Paper:** NAACL 2024

**Strengths:**
- **Zero-shot**: No training required, define entities on the fly
- Outperforms ChatGPT on multiple NER benchmarks
- **Demonstrated success on 19th century historical text** (Dutch travel texts, Oct 2024)
- Multilingual support (even languages not in training data)
- Integrates with spaCy pipeline
- Lightweight and fast (bidirectional transformer, parallel extraction)

**Perfect for:**
- Custom entity types (e.g., "fur trading posts", "indigenous groups", "ships")
- Exploratory analysis where entity types aren't predefined
- Testing on small samples before committing to training

**Trade-offs:**
- "Far from perfect" on historical text (per 2024 evaluation)
- Good for generating silver-labeled data for domain-specific model training

**When to use:**
- Initial exploration phase
- Custom entity types beyond standard LOC/PER/ORG
- When you need flexibility without fine-tuning

---

### 4. **UniversalNER (LLaMA 2 7B Distilled)** ⭐ STRONG CONTENDER
**Models:** `Universal-NER/UniNER-7B-type`, `UniNER-7B-all`, `UniNER-7B-type-sup`
**Paper:** ICLR 2024 (Zhou et al., Microsoft/USC/UCLA)
**GitHub:** https://github.com/universal-ner/universal-ner

**Key Innovation:**
- **Distilled from ChatGPT** into much smaller LLaMA 2 7B model
- Uses "targeted distillation with mission-focused instruction tuning"
- Trained on **largest NER benchmark to date**: 43 datasets, 9 domains, 13,020 distinct entity types
- 45,889 training examples with 240,725 entities

**Performance:**
- **Outperforms ChatGPT by 7-9 absolute F1 points** while using a tiny fraction of parameters
- Beats general instruction-tuned models (Alpaca, Vicuna) by **over 30 F1 points**
- Surpasses InstructUIE (state-of-the-art multi-task system) by large margin
- **Open NER capability**: Can recognize arbitrary entity types without retraining

**Trade-offs vs GLiNER:**
- **Supervised setting:** UniversalNER > GLiNER
- **Zero-shot setting:** GLiNER > UniversalNER
- **Architecture:** Auto-regressive (slower, token-by-token) vs GLiNER's bidirectional (faster, parallel)
- **Size:** 7B parameters vs GLiNER's ~300M
- **Deployment:** Requires more resources but offers better accuracy on known domains

**When to use:**
- When you need **high accuracy across diverse entity types**
- For historical text with domain-specific entities (fur trading companies, indigenous groups, territorial designations)
- When you can afford 7B model inference costs
- For generating high-quality training labels for smaller models

**Available Variants:**
- `UniNER-7B-type`: Base model for open NER
- `UniNER-7B-all`: General-purpose variant
- `UniNER-7B-type-sup`: **Fine-tuned on 40 supervised datasets** (best performance)

**Practical Considerations:**
- Requires `vllm` library and CUDA 11.0-11.8
- Can run with tensor parallelization: `tensor_parallel_size=1` for single GPU
- Max input length: 512 tokens (may need chunking for long documents)
- Research-only license (same restrictions as LLaMA 2)

---

### 5. **LLM-Based NER (Mistral, LLaMA 3.2)**

**Recent Performance (2024-2025):**
- **With proper prompting**, LLMs can "significantly outperform state-of-the-art NLP tools such as spaCy and even flair in recall and precision using... 0-shot prompts"
- Key insight: "Rethinking prompting strategies and fundamentally reconceptualising NER from a linguistic task to a humanities-focused task with contextual information and appropriate persona modelling"

**Performance Benchmarks:**
- **Mixtral:** 66.67% vs GPT-4o's 33.33% and 63.64% vs LLaMA3's 36.36% (unique entity extraction)
- **8B parameter models** (Mistral, LLaMA): 2-8% higher F-scores than 300M encoder models (BERT, DeBERTa)
- **CyberLLaMA** (LLaMA-3.2-3B fine-tuned): 98.88% F1 (domain-specific)

**Computational Costs:**
- Decoder models require **2 GPUs** for training/evaluation vs 1 GPU for encoders
- Mistral 7B uses grouped-query attention (GQA) and sliding window attention (SWA) for efficiency

**Best Models for Your Use Case:**
- **Mistral 7B** (balanced performance/efficiency)
- **LLaMA 3.2 3B** (smaller, good for bulk processing on DRAC)
- **oss-120** (if you have cluster access)

**When to use:**
- When you need contextual understanding (e.g., disambiguating "Hudson Bay" as location vs company)
- For complex entities requiring reasoning
- When you can afford computational cost
- For generating high-quality training data

---

## Comparative Analysis: spaCy vs Fine-tuned Models vs LLMs

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **spaCy (out-of-box)** | Fast, easy, well-documented | Poor on historical text; trained on modern news | Baseline only |
| **spaCy + Historical BERT** | Fast, production-ready, integrates spacy-transformers | Requires GPU | Newspapers (dell-harvard) |
| **Fine-tuned BERT/RoBERTa** | Highest F1 on historical newspapers (90.4%) | Fixed entity types | Large-scale processing |
| **BigLAM Toponym Model** | **Specialized for place names** | Limited to LOC | **Your geoparsing pipeline** |
| **GLiNER** | Zero-shot, flexible, multilingual, fast | Lower accuracy than fine-tuned | Exploration, custom entities |
| **UniversalNER** | **Open NER, beats ChatGPT**, 13K+ entity types | 7B params, auto-regressive (slower) | Diverse entity types, high accuracy |
| **LLMs (Mistral/LLaMA)** | Best with proper prompting, contextual | High compute cost, slower | High-quality samples, disambiguation |

---

## Recommended Pipeline for Saskatchewan Geoparsing

### Phase 1: Baseline Evaluation (1-2 days)

```python
# Test these approaches on 50-100 sample documents:
1. spaCy (en_core_web_trf) - baseline
2. dell-research-harvard/historical_newspaper_ner - newspapers
3. BigLAM toponym model - all documents
4. GLiNER zero-shot with custom prompt
5. UniversalNER (UniNER-7B-type-sup) - sample of 20 docs for quality comparison
```

**Evaluation metrics:**
- Precision/Recall/F1 for LOC entities
- Character Error Rate (CER) tolerance
- Processing speed (docs/hour)
- Integration complexity with neo4j pipeline

### Phase 2: Fine-Tuning Decision (Week 2)

Based on Phase 1 results:

**Option A: Good enough (F1 > 85%)**
- Deploy best model to neo4j pipeline
- Focus on gazetteer matching (GeoNames/Wikidata)

**Option B: Needs improvement (F1 < 85%)**
- Use GLiNER or LLM to generate silver labels on 500-1000 docs
- Manual correction of 200-300 high-value docs (newspapers with known places)
- Fine-tune BigLAM or RoBERTa on corrected data

### Phase 3: LLM Augmentation (Optional)

For ambiguous cases:
```python
# Pseudo-code
if confidence < 0.7:
    llm_result = mistral_ner(text, context=historical_background)
    if high_consensus:
        use_llm_result
```

### Phase 4: Neo4j Integration

```python
# Recommended flow:
OCR Text → NER (dell-harvard) → Toponym List →
Gazetteer Matching (GeoNames/Wikidata) →
Disambiguation (if needed: LLM) → Neo4j Graph
```

---

## Specific Recommendations by Document Type

### Newspapers (353 docs, 1880s)
**Model:** `dell-research-harvard/historical_newspaper_ner`
- Highest reported accuracy for your exact use case
- Trained on American newspapers (similar to your Brandon Daily Mail, Prince Albert Times)
- Handles OCR errors robustly

### Books/Monographs (264 docs, 1760-1900)
**Model:** BigLAM BERT (1760-1850 or 1850-1875 depending on doc date)
- Temporal alignment critical (research shows models perform better when training data temporally overlaps with target)
- For geoparsing: Use BigLAM toponym detection model

### French Documents (148 docs)
**Model:** hmBERT (multilingual) or BigLAM French variant
- Handles diacritics properly (you have good OCR quality for French)
- Consider language-specific processing branch

### Government Records (School Files Series, RG10)
**Model:** Start with dell-harvard, evaluate GLiNER for custom entities
- These may have specialized terminology not in standard NER
- GLiNER useful for entities like "residential school names", "treaty numbers"

### Indigenous Language Materials (Cree, Chipewyan, 6 docs)
**Model:** Manual annotation or LLM with expert prompting
- Too few for training, too specialized for existing models
- Consider as Phase 2 special project

---

## OCR Quality Impact

Your Saskatchewan data shows **olmOCR v0.3.4** extraction quality:
- High quality on printed materials (newspapers, books)
- Proper handling of French diacritics
- Some degraded microform sources (flagged in metadata)

**OCR Error Research Findings:**
- Finnish historical newspapers (CER 6.96%, WER 16.67%): F1 dropped ~10 points vs clean text (72% vs 82%)
- General trend: 90% → 50% accuracy as word error rate goes 8% → 50%
- **dell-harvard model specifically designed to handle this**

**Recommendation:**
- Monitor `ocr_degraded` and `ocr_detected_lang_conf` fields in metadata
- Route low-confidence OCR docs through LLM post-correction before NER
- Recent research shows LLMs achieve **1% CER** on historical handwriting post-correction

---

## Cost Analysis for DRAC Cluster Deployment

### Model Size Comparison

| Model | Parameters | GPU Memory | Inference Speed | Cost Tier |
|-------|-----------|------------|-----------------|-----------|
| dell-harvard (RoBERTa-large) | 355M | ~4GB | ~100 docs/hr | Low |
| BigLAM BERT | 110M-340M | ~2-4GB | ~150 docs/hr | Low |
| GLiNER | ~300M | ~2GB | ~200 docs/hr | Very Low |
| **UniversalNER** | **7B** | **~16GB** | **~15-20 docs/hr** | **Medium** |
| Mistral 7B | 7B | ~16GB (2 GPUs) | ~10 docs/hr | Medium |
| LLaMA 3.2 3B | 3B | ~8GB | ~20 docs/hr | Low-Med |
| oss-120 | varies | check specs | varies | Cluster-dependent |

### Processing Estimates (1,222 docs)

**Conservative approach:**
- dell-harvard on all newspapers: 3-4 GPU hours
- BigLAM on all books/monographs: 2-3 GPU hours
- Total: ~1 day on single GPU for full corpus

**LLM approach:**
- Mistral 7B on full corpus: ~120 GPU hours (5 days)
- Cost: Likely overkill unless quality justifies

**Recommendation:** Use BERT models for bulk processing, reserve UniversalNER/LLM for:
- Ambiguous cases flagged by confidence scores
- Complex entity types (e.g., "Hudson's Bay Company" vs "Hudson Bay" location)
- Generating training data (if needed)
- Final validation on 10% sample

**UniversalNER Consideration:**
- If initial BERT results show gaps in entity coverage (missing specialized terms)
- Use `UniNER-7B-type-sup` on subset to assess if 7B model worth the cost
- Expected: ~60-80 GPU hours for full corpus (vs 5-6 for BERT)
- May be cost-effective if you need diverse entity types beyond standard LOC/PER/ORG

---

## Implementation Roadmap

### Week 1: Setup & Baseline
- [ ] Install spacy-transformers, transformers, GLiNER
- [ ] Download dell-research-harvard/historical_newspaper_ner
- [ ] Download BigLAM toponym detection model
- [ ] Create evaluation dataset (50 newspaper pages, 50 book pages, hand-annotated)
- [ ] Run baseline comparisons
- [ ] Generate performance report

### Week 2: Integration Testing
- [ ] Test best model(s) on full newspaper subcollection
- [ ] Extract toponyms, generate candidate list
- [ ] Test GeoNames/Wikidata matching
- [ ] Identify disambiguation challenges
- [ ] Document edge cases

### Week 3: Neo4j Pipeline
- [ ] Design graph schema (Document → Entity → Place → Coordinates)
- [ ] Build ETL pipeline (OCR JSON → NER → Neo4j)
- [ ] Implement confidence thresholding
- [ ] Add provenance tracking (which model, confidence, etc.)

### Week 4: Quality Assurance & LLM Augmentation
- [ ] Evaluate end-to-end pipeline on 100 docs
- [ ] Identify low-confidence cases
- [ ] If needed: Set up Mistral/LLaMA on DRAC
- [ ] Run LLM disambiguation on flagged entities
- [ ] Final validation

---

## Key Research Papers & Resources

### Must-Read Papers
1. **"UniversalNER: Targeted Distillation from Large Language Models for Open Named Entity Recognition"** (Zhou et al., ICLR 2024)
   - arXiv: 2308.03279
   - Demonstrates distilling ChatGPT into 7B model that outperforms it
   - Largest NER benchmark (43 datasets, 13K entity types)

2. **"Leveraging Open Large Language Models for Historical Named Entity Recognition"** (González-Gallardo et al., 2024)
   - Recent benchmark of LLMs on historical NER

3. **"Named Entity Recognition and Classification in Historical Documents: A Survey"** (ACM Computing Surveys, 2023)
   - Comprehensive overview of challenges and approaches

4. **"Early evidence of how LLMs outperform traditional systems on OCR/HTR tasks for historical records"** (arXiv 2025)
   - Shows LLMs achieving 1% CER on post-correction

5. **"Neural Language Models for Nineteenth-Century English"** (Journal of Open Humanities Data, 2021)
   - Foundation for BigLAM models

6. **"GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer"** (NAACL 2024)
   - Comparison point: GLiNER beats UniversalNER in zero-shot, UniversalNER wins in supervised

### Tools & Repositories
- **UniversalNER:** https://github.com/universal-ner/universal-ner
  - Models: https://huggingface.co/Universal-NER
  - Dataset: https://huggingface.co/datasets/universalner/universal_ner
- **dell-research-harvard:** https://huggingface.co/dell-research-harvard/historical_newspaper_ner
- **BigLAM Collection:** https://huggingface.co/collections/biglam/historic-language-modeling-64f9a0af6b021d61eee993e2
- **GLiNER:** https://github.com/urchade/GLiNER
- **Instruct-NER** (for fine-tuning LLaMA/Mistral): https://github.com/poteminr/instruct-ner
- **Historic-NER** (German, but good methods): https://github.com/dbmdz/historic-ner

### Tutorials
- **spaCy-transformers integration:** https://explosion.ai/blog/spacy-transformers
- **Fine-tuning Mistral for NER:** https://medium.com/ubiai-nlp/fine-tuning-mistral-7b-for-named-entity-recognition-ner-bbb96af918d3
- **GLiNER on historical text:** https://medium.com/@tess.dejaeghere/text-tales-basic-zero-shot-ner-with-gliner-for-dh-on-19th-century-dutch-travel-text-1828c62e3ef4

---

## Prompting Strategies for LLMs (If Using)

### General Structure (from 2024 research)

```
You are an expert historian specializing in 19th century Western Canadian history.
Your task is to identify named entities in historical newspaper text that may
contain OCR errors and archaic language.

Context: This text is from {newspaper_name} published in {location} on {date}.
The region discussed is primarily present-day Saskatchewan during the territorial period.

Text: {ocr_text}

Extract the following entities:
- LOCATION: Places, geographic features, territories (e.g., "Fort Carlton", "Saskatchewan River")
- PERSON: Names of individuals (e.g., "Louis Riel", "Mgr Vital Grandin")
- ORGANIZATION: Companies, government bodies, groups (e.g., "North West Company", "Hudson's Bay Company")

Consider:
- OCR errors may cause spelling variations
- Place names may differ from modern usage (e.g., "Prince Albert Settlement" vs "Prince Albert")
- Some entities may be in French or Indigenous languages

Output format: JSON with entity type, text span, and confidence (0-1)
```

### Domain-Specific Customization for Saskatchewan

```python
HISTORICAL_CONTEXT = """
Saskatchewan territorial period (1870s-1900s) key entities to watch for:
- Indigenous groups: Cree, Métis, Chipewyan, Dene
- Trading posts: Fort Carlton, Fort Pitt, Cumberland House
- Early settlements: Prince Albert, Battleford, Regina (Pile O'Bones)
- Organizations: North West Company, Hudson's Bay Company, NWMP
- Key figures: Louis Riel, Gabriel Dumont, Big Bear, Poundmaker
- Transportation: Saskatchewan River, Carlton Trail
"""
```

---

## Success Metrics

### NER Quality
- **F1 Score:** Target >85% for LOC entities (critical for geoparsing)
- **Precision:** >90% (minimize false positives for clean graph)
- **Recall:** >80% (capture most place mentions)

### Geoparsing Quality
- **Gazetteer Match Rate:** >70% of extracted toponyms resolve to GeoNames/Wikidata
- **Disambiguation Accuracy:** >85% correct for ambiguous place names
- **Coverage:** Capture >90% of significant place mentions in corpus

### Pipeline Efficiency
- **Processing Speed:** 1,222 docs in <24 hours on available compute
- **Cost:** Minimize GPU hours while maintaining quality
- **Maintainability:** Reproducible, version-controlled, documented

---

## Conclusion

**For your Saskatchewan geoparsing project, the optimal approach is:**

1. **Primary NER:** `dell-research-harvard/historical_newspaper_ner` (newspapers) + **BigLAM toponym model** (all docs)
   - Best accuracy for your use case
   - Efficient on standard GPU
   - Proven on OCR-corrupted text

2. **Exploratory:** `GLiNER` for custom entity types and quick experimentation

3. **Mid-tier option:** `UniversalNER (UniNER-7B-type-sup)`
   - **Consider if:** You need diverse entity types beyond standard categories (e.g., fur trading posts, treaties, indigenous confederacies)
   - **Advantage:** Outperforms ChatGPT, handles 13K+ entity types
   - **Trade-off:** 10x slower than BERT but potentially higher recall on domain-specific entities
   - **Cost:** ~60-80 GPU hours for full corpus vs 5-6 for BERT

4. **High-value enhancement:** LLM (Mistral 7B or LLaMA 3.2) for:
   - Disambiguating toponyms (Hudson Bay location vs company)
   - Resolving low-confidence cases
   - Generating training data if needed

5. **Recommended strategy:**
   - **Standard path:** BERT models for 95% of processing, LLM for 5% challenging cases (~1 day GPU)
   - **High-accuracy path:** UniversalNER for 100% of processing (~3-4 days GPU), may not need LLM backup
   - **Hybrid path:** BERT for newspapers (fast), UniversalNER for books/government records (better entity coverage), GLiNER for exploration

This tiered approach lets you balance quality, speed, and compute budget based on your specific needs and DRAC cluster availability.

---

**Next Steps:** See `NER_IMPLEMENTATION_PLAN.md` for detailed code examples and pipeline architecture.
