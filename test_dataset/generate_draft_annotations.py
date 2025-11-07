#!/usr/bin/env python3
"""
AI-assisted annotation: Generate draft entity annotations using NER.

This script uses spaCy to pre-annotate entities, which can then be
reviewed and corrected by a human annotator.

Usage:
    python generate_draft_annotations.py [document_id]

If no document_id provided, processes all documents.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")
    print("         Then download model: python -m spacy download en_core_web_sm")


ENTITY_TYPE_MAP = {
    'GPE': 'LOC',      # Geopolitical entity -> Location
    'LOC': 'LOC',      # Location
    'FAC': 'LOC',      # Facility -> Location
    'PERSON': 'PER',   # Person
    'ORG': 'ORG',      # Organization
    'NORP': 'MISC',    # Nationalities/religious/political groups
    'EVENT': 'MISC',   # Named events
    'LAW': 'MISC',     # Named documents/laws/treaties
}


def load_spacy_model():
    """Load spaCy model for entity recognition."""
    if not SPACY_AVAILABLE:
        return None

    try:
        # Try to load English model
        nlp = spacy.load("en_core_web_sm")
        print("✓ Loaded spaCy model: en_core_web_sm")
        return nlp
    except OSError:
        print("ERROR: spaCy model not found.")
        print("Install with: python -m spacy download en_core_web_sm")
        return None


def annotate_with_spacy(text: str, nlp) -> List[Dict]:
    """Use spaCy to detect entities in text."""
    if nlp is None:
        return []

    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        # Map spaCy entity type to our taxonomy
        entity_type = ENTITY_TYPE_MAP.get(ent.label_, None)

        if entity_type:
            entity = {
                'text': ent.text,
                'start': ent.start_char,
                'end': ent.end_char,
                'type': entity_type,
                'confidence': 0.8,  # Draft confidence
                'source': 'spacy',
                'original_type': ent.label_,
                'notes': f'Auto-detected by spaCy as {ent.label_}'
            }
            entities.append(entity)

    return entities


def load_snippets(doc_id: str) -> Dict:
    """Load snippets file for a document."""
    snippets_file = Path('test_dataset/snippets') / f'{doc_id}_snippets.json'
    if not snippets_file.exists():
        print(f"ERROR: Snippets file not found: {snippets_file}")
        return None

    with open(snippets_file, 'r') as f:
        return json.load(f)


def generate_draft_for_document(doc_id: str, nlp) -> bool:
    """Generate draft annotations for a single document."""
    print(f"\nProcessing: {doc_id}")

    # Load snippets
    data = load_snippets(doc_id)
    if data is None:
        return False

    snippets = data['snippets']
    print(f"  {len(snippets)} snippets to annotate")

    # Annotate each snippet
    draft_snippets = []
    total_entities = 0

    for snippet in snippets:
        entities = annotate_with_spacy(snippet['text'], nlp)

        draft_snippet = {
            'snippet_id': f"{snippet['snippet_id']:03d}",
            'text': snippet['text'],
            'char_start': snippet['char_start'],
            'char_end': snippet['char_end'],
            'entities': sorted(entities, key=lambda e: e['start'])
        }

        draft_snippets.append(draft_snippet)
        total_entities += len(entities)

    # Create draft annotation file
    output = {
        'document_id': doc_id,
        'metadata': data['metadata'],
        'annotation_date': datetime.now().isoformat(),
        'annotator': 'ai_draft',
        'model': 'spacy_en_core_web_sm',
        'status': 'draft',
        'total_snippets': len(draft_snippets),
        'total_entities': total_entities,
        'snippets': draft_snippets
    }

    # Save draft
    draft_dir = Path('test_dataset/drafts')
    draft_dir.mkdir(exist_ok=True)

    output_file = draft_dir / f'{doc_id}_draft.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Draft saved: {output_file}")
    print(f"    Entities detected: {total_entities}")

    # Print entity type breakdown
    entity_counts = {}
    for snippet in draft_snippets:
        for entity in snippet['entities']:
            entity_type = entity['type']
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

    if entity_counts:
        print(f"    Breakdown: ", end="")
        print(", ".join(f"{k}:{v}" for k, v in sorted(entity_counts.items())))

    return True


def list_available_documents():
    """List all documents with snippets available."""
    snippets_dir = Path('test_dataset/snippets')
    snippet_files = list(snippets_dir.glob('*_snippets.json'))

    if snippet_files:
        snippet_files = [f for f in snippet_files if f.name != 'SUMMARY.json']

    return [f.stem.replace('_snippets', '') for f in sorted(snippet_files)]


def main():
    """Main draft generation workflow."""
    print(f"\n{'='*80}")
    print("AI-ASSISTED ANNOTATION: Draft Generation")
    print(f"{'='*80}\n")

    # Load NER model
    nlp = load_spacy_model()
    if nlp is None:
        print("\nERROR: Cannot generate drafts without NER model.")
        print("Install spaCy and model, then try again.")
        return 1

    # Get document list
    if len(sys.argv) > 1:
        doc_ids = [sys.argv[1]]
    else:
        doc_ids = list_available_documents()
        print(f"Found {len(doc_ids)} documents to process")
        proceed = input("\nGenerate drafts for all documents? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Cancelled.")
            return 0

    # Process documents
    success_count = 0
    for doc_id in doc_ids:
        if generate_draft_for_document(doc_id, nlp):
            success_count += 1

    print(f"\n{'='*80}")
    print(f"✓ Draft generation complete!")
    print(f"  Successfully processed: {success_count}/{len(doc_ids)} documents")
    print(f"\nNext step: Review drafts using:")
    print(f"  python review_draft_annotations.py [document_id]")
    print(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
