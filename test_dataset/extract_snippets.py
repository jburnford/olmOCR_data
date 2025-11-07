#!/usr/bin/env python3
"""
Extract representative text snippets from OCR JSON files for NER annotation.

Strategy:
- Small docs (<1000 words): Use full text
- Medium docs (1000-5000 words): Extract 5-10 snippets
- Large docs (>5000 words): Extract 10-15 snippets
- Focus on high entity density passages (mentions of places, people, orgs)
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import random
import argparse

# Set random seed for reproducibility
random.seed(42)

# Snippet configuration
MIN_SNIPPET_LENGTH = 300  # characters
MAX_SNIPPET_LENGTH = 1200  # characters
TARGET_SNIPPET_LENGTH = 800  # characters


def load_ocr_document(ocr_path: Path) -> Tuple[str, dict]:
    """Load OCR JSON and return full text and metadata."""
    with open(ocr_path, 'r') as f:
        data = json.load(f)

    if not data or len(data) == 0:
        return "", {}

    # Concatenate all page texts
    full_text = ""
    for page in data:
        if 'text' in page:
            full_text += page['text'] + "\n\n"

    # Get metadata from first page
    metadata = data[0].get('metadata', {}) if data else {}
    attributes = data[0].get('attributes', {}) if data else {}

    return full_text, {
        'metadata': metadata,
        'attributes': attributes,
        'total_pages': metadata.get('pdf-total-pages', len(data))
    }


def estimate_entity_density(text: str) -> float:
    """
    Estimate entity density in text using heuristics.
    Returns score 0-1 indicating likely entity richness.
    """
    score = 0.0

    # Capitalized words (potential entities)
    cap_words = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text))
    score += min(cap_words / 50, 0.3)

    # Geographic indicators
    geo_terms = ['river', 'lake', 'fort', 'mountain', 'prairie', 'settlement',
                 'territory', 'district', 'creek', 'hill', 'bay', 'island',
                 'rivière', 'lac', 'montagne', 'territoire']
    geo_count = sum(text.lower().count(term) for term in geo_terms)
    score += min(geo_count / 10, 0.3)

    # Proper name patterns (e.g., "Mr. Smith", "Sir John")
    titles = len(re.findall(r'\b(Mr\.|Mrs\.|Dr\.|Sir|Lady|Chief|Father|Mgr|Rev\.)\s+[A-Z]', text))
    score += min(titles / 10, 0.2)

    # Organization indicators
    org_terms = ['Company', 'Association', 'Department', 'Commission', 'Police',
                 'Compagnie', 'Société']
    org_count = sum(text.count(term) for term in org_terms)
    score += min(org_count / 5, 0.2)

    return min(score, 1.0)


def extract_sentence_boundaries(text: str) -> List[int]:
    """Find sentence boundaries in text (approximate)."""
    # Simple sentence boundary detection
    boundaries = [0]
    for match in re.finditer(r'[.!?]\s+[A-Z]', text):
        boundaries.append(match.start() + 2)
    boundaries.append(len(text))
    return boundaries


def extract_snippets(text: str, num_snippets: int) -> List[Dict]:
    """
    Extract representative snippets from text.
    Prioritizes passages with high estimated entity density.
    """
    if len(text) < MIN_SNIPPET_LENGTH:
        # Document too short, return entire text
        return [{
            'snippet_id': 1,
            'text': text.strip(),
            'char_start': 0,
            'char_end': len(text),
            'entity_density_score': estimate_entity_density(text)
        }]

    # If text is small enough, just return it
    if len(text) < TARGET_SNIPPET_LENGTH * 1.5:
        return [{
            'snippet_id': 1,
            'text': text.strip(),
            'char_start': 0,
            'char_end': len(text),
            'entity_density_score': estimate_entity_density(text)
        }]

    # Split into potential snippets with overlap
    sentence_boundaries = extract_sentence_boundaries(text)

    # Create candidate snippets
    candidates = []
    for i, start_boundary in enumerate(sentence_boundaries[:-1]):
        # Build snippet of approximately TARGET_SNIPPET_LENGTH
        char_start = start_boundary
        char_end = start_boundary

        # Extend to target length
        for end_boundary in sentence_boundaries[i+1:]:
            if end_boundary - start_boundary >= MIN_SNIPPET_LENGTH:
                char_end = end_boundary
                if end_boundary - start_boundary >= TARGET_SNIPPET_LENGTH:
                    break

        if char_end - char_start < MIN_SNIPPET_LENGTH:
            continue

        snippet_text = text[char_start:char_end].strip()
        if len(snippet_text) < MIN_SNIPPET_LENGTH:
            continue

        density = estimate_entity_density(snippet_text)

        candidates.append({
            'char_start': char_start,
            'char_end': char_end,
            'text': snippet_text,
            'density': density,
            'length': len(snippet_text)
        })

    if not candidates:
        # Fallback: just split into chunks
        chunk_size = TARGET_SNIPPET_LENGTH
        candidates = []
        for i in range(0, len(text), chunk_size // 2):
            end = min(i + chunk_size, len(text))
            snippet_text = text[i:end].strip()
            if len(snippet_text) >= MIN_SNIPPET_LENGTH:
                candidates.append({
                    'char_start': i,
                    'char_end': end,
                    'text': snippet_text,
                    'density': estimate_entity_density(snippet_text),
                    'length': len(snippet_text)
                })

    # Sort by entity density (descending)
    candidates.sort(key=lambda x: x['density'], reverse=True)

    # Select top N non-overlapping snippets
    selected = []
    for candidate in candidates:
        # Check for overlap with already selected
        overlap = False
        for sel in selected:
            if not (candidate['char_end'] <= sel['char_start'] or
                    candidate['char_start'] >= sel['char_end']):
                overlap = True
                break

        if not overlap:
            selected.append(candidate)

        if len(selected) >= num_snippets:
            break

    # Sort selected by position in document
    selected.sort(key=lambda x: x['char_start'])

    # Format output
    snippets = []
    for i, snip in enumerate(selected, 1):
        snippets.append({
            'snippet_id': i,
            'text': snip['text'],
            'char_start': snip['char_start'],
            'char_end': snip['char_end'],
            'entity_density_score': round(snip['density'], 3)
        })

    return snippets


def process_document(doc_id: str, ocr_path: Path, doc_metadata: Dict) -> Dict:
    """Process a single document and extract snippets."""
    print(f"Processing {doc_id}...", file=sys.stderr)

    # Load document
    full_text, ocr_metadata = load_ocr_document(ocr_path)

    if not full_text or len(full_text.strip()) < 50:
        print(f"  WARNING: Document {doc_id} has insufficient text", file=sys.stderr)
        return None

    word_count = len(full_text.split())
    print(f"  Text length: {len(full_text)} chars, ~{word_count} words", file=sys.stderr)

    # Determine number of snippets based on document size
    if word_count < 500:
        num_snippets = 1
        strategy = "full_text"
    elif word_count < 2000:
        num_snippets = min(3, max(1, word_count // 500))
        strategy = "small_doc"
    elif word_count < 10000:
        num_snippets = min(10, max(5, word_count // 1000))
        strategy = "medium_doc"
    else:
        num_snippets = min(15, max(10, word_count // 2000))
        strategy = "large_doc"

    print(f"  Strategy: {strategy}, extracting {num_snippets} snippet(s)", file=sys.stderr)

    # Extract snippets
    snippets = extract_snippets(full_text, num_snippets)

    print(f"  Extracted {len(snippets)} snippet(s)", file=sys.stderr)

    # Build output
    output = {
        'document_id': doc_id,
        'metadata': {
            **doc_metadata,
            'word_count': word_count,
            'char_count': len(full_text),
            'total_pages': ocr_metadata.get('total_pages', 0),
            'extraction_strategy': strategy,
            'num_snippets': len(snippets)
        },
        'snippets': snippets
    }

    return output


def main():
    """Main extraction process."""
    parser = argparse.ArgumentParser(description='Extract representative OCR snippets for NER annotation')
    parser.add_argument('--ids-file', default=None,
                        help='File with one identifier per line (default: test_dataset/ids.txt relative to this script)')
    parser.add_argument('--subcollection', default='saskatchewan_1808_1946',
                        help='Subcollection to read OCR from (default: saskatchewan_1808_1946)')
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent  # export_bundle
    test_dir = base_dir / 'test_dataset'

    # Load sample IDs
    default_ids = test_dir / 'ids.txt'
    ids_path = Path(args.ids_file) if args.ids_file else default_ids
    if not ids_path.exists():
        print(f"ERROR: IDs file not found: {ids_path}", file=sys.stderr)
        return 1

    with open(ids_path, 'r') as f:
        sample_ids = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(sample_ids)} documents...\n", file=sys.stderr)

    # Load document metadata from documents.jsonl
    doc_metadata_map = {}
    with open(base_dir / 'documents.jsonl', 'r') as f:
        for line in f:
            doc = json.loads(line)
            if doc.get('subcollection') == 'saskatchewan_1808_1946':
                doc_metadata_map[doc['identifier']] = {
                    'title': doc.get('title', ''),
                    'year': doc.get('year'),
                    'language': doc.get('language', ''),
                    'collection': doc.get('collection', ''),
                    'doc_type': 'unknown'  # Will be inferred
                }

    # Ensure output dir exists
    (test_dir / 'snippets').mkdir(parents=True, exist_ok=True)

    # Process each document
    results = []
    for doc_id in sample_ids:
        if doc_id not in doc_metadata_map:
            print(f"WARNING: No metadata found for {doc_id}", file=sys.stderr)
            continue

        ocr_path = base_dir / f'ocr/{args.subcollection}/{doc_id}.json'
        if not ocr_path.exists():
            print(f"WARNING: OCR file not found: {ocr_path}", file=sys.stderr)
            continue

        doc_metadata = doc_metadata_map[doc_id]

        # Infer document type
        if any(x in doc_id.lower() for x in ['ptr_', 'bdm_', 'brm_', 'lmt_', 'mja_', 'mtm_']):
            doc_metadata['doc_type'] = 'newspaper'
        elif 'school_files' in doc_id.lower() or 'rg10' in doc_id.lower():
            doc_metadata['doc_type'] = 'government'
        else:
            doc_metadata['doc_type'] = 'book'

        result = process_document(doc_id, ocr_path, doc_metadata)
        if result:
            results.append(result)

            # Save individual snippet file
            output_file = test_dir / 'snippets' / f'{doc_id}_snippets.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Saved to {output_file}\n", file=sys.stderr)

    # Save summary
    summary = {
        'total_documents': len(results),
        'total_snippets': sum(r['metadata']['num_snippets'] for r in results),
        'documents': [
            {
                'doc_id': r['document_id'],
                'title': r['metadata']['title'][:80],
                'year': r['metadata']['year'],
                'language': r['metadata']['language'],
                'type': r['metadata']['doc_type'],
                'num_snippets': r['metadata']['num_snippets'],
                'word_count': r['metadata']['word_count']
            }
            for r in results
        ]
    }

    summary_file = test_dir / 'snippets/SUMMARY.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"EXTRACTION COMPLETE", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Documents processed: {len(results)}", file=sys.stderr)
    print(f"Total snippets: {summary['total_snippets']}", file=sys.stderr)
    print(f"Summary saved to: {summary_file}", file=sys.stderr)
    print(f"Individual files in: {test_dir}/snippets/", file=sys.stderr)

    # Print summary table
    print(f"\nDocument Summary:", file=sys.stderr)
    print(f"{'Document':<30} {'Type':<12} {'Lang':<6} {'Snippets':<10} {'Words':<10}", file=sys.stderr)
    print(f"{'-'*70}", file=sys.stderr)
    for doc in summary['documents']:
        print(f"{doc['doc_id']:<30} {doc['type']:<12} {doc['language']:<6} "
              f"{doc['num_snippets']:<10} {doc['word_count']:<10}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
