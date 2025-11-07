#!/usr/bin/env python3
"""
Review Claude's draft annotations - Quick confirm/reject workflow.

This script loads Claude-AI generated draft annotations and allows human review
with a simple keyboard interface for fast confirmation.

Usage:
    python review_annotations.py [document_id]
"""

import json
import sys
from pathlib import Path
from datetime import datetime


ENTITY_TYPES = {
    'LOC': 'Location (places, regions, natural features)',
    'PER': 'Person (named individuals)',
    'ORG': 'Organization (companies, government bodies)',
    'MISC': 'Miscellaneous (indigenous groups, treaties, events)'
}


def load_draft(doc_id: str):
    """Load draft annotations for a document."""
    draft_file = Path('test_dataset/drafts') / f'{doc_id}_draft.json'
    if not draft_file.exists():
        print(f"ERROR: Draft file not found: {draft_file}")
        print(f"\nAsk Claude to create draft annotations for: {doc_id}")
        sys.exit(1)

    with open(draft_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def show_entity(text, entity, entity_num, total_entities, snippet_num):
    """Display entity with context."""
    start = entity['start']
    end = entity['end']

    # Context (60 chars before/after)
    ctx_start = max(0, start - 60)
    ctx_end = min(len(text), end + 60)

    before = text[ctx_start:start]
    ent_text = text[start:end]
    after = text[ctx_end:end]

    print(f"\n{'='*80}")
    print(f"Snippet {snippet_num} | Entity {entity_num}/{total_entities}")
    print(f"{'='*80}")
    print(f"\nContext: ...{before}[[[{ent_text}]]]{after}...")
    print(f"\nEntity: \"{entity['text']}\"")
    print(f"Type: {entity['type']} - {ENTITY_TYPES.get(entity['type'], 'Unknown')}")
    print(f"Confidence: {entity.get('confidence', 0):.2f}")
    if entity.get('notes'):
        print(f"Notes: {entity['notes']}")


def quick_review_entity(text, entity, entity_num, total_entities, snippet_num):
    """Quick review with single-key interface."""
    show_entity(text, entity, entity_num, total_entities, snippet_num)

    while True:
        choice = input("\n[y]es/[n]o/[m]odify/[s]kip snippet/[q]uit: ").strip().lower()

        if choice == 'y' or choice == '':
            entity['confidence'] = 1.0
            entity['reviewed'] = True
            print("✓ Accepted")
            return entity

        elif choice == 'n':
            print("✗ Rejected")
            return None

        elif choice == 'm':
            # Quick modify
            print(f"\nCurrent: {entity['text']} ({entity['type']})")
            new_type = input(f"New type [{entity['type']}]: ").strip().upper()
            if new_type and new_type in ENTITY_TYPES:
                entity['type'] = new_type
            notes = input("Add notes: ").strip()
            if notes:
                entity['notes'] = notes

            entity['confidence'] = 1.0
            entity['reviewed'] = True
            print("✓ Modified")
            return entity

        elif choice == 's':
            return 'SKIP'

        elif choice == 'q':
            return 'QUIT'

        else:
            print("Invalid. Use: y/n/m/s/q")


def add_missed_entities(text):
    """Add entities Claude missed."""
    print(f"\n{'='*80}")
    print("Add entities that Claude missed?")
    print(f"{'='*80}\n")

    new_entities = []

    while True:
        entity_text = input("\nEntity text (or Enter to skip): ").strip()
        if not entity_text:
            break

        # Find in text
        idx = text.find(entity_text)
        if idx == -1:
            print(f"  Not found: '{entity_text}'")
            continue

        # Get type
        print("  Types: LOC, PER, ORG, MISC")
        entity_type = input("  Type: ").strip().upper()
        if entity_type not in ENTITY_TYPES:
            print("  Invalid type")
            continue

        notes = input("  Notes (optional): ").strip()

        entity = {
            'text': entity_text,
            'start': idx,
            'end': idx + len(entity_text),
            'type': entity_type,
            'confidence': 1.0,
            'source': 'human_added',
            'reviewed': True,
            'notes': notes or 'Added during review'
        }

        new_entities.append(entity)
        print(f"  ✓ Added: {entity_text} ({entity_type})")

    return new_entities


def review_snippet(snippet, snippet_num, total_snippets):
    """Review all entities in a snippet."""
    print(f"\n\n{'#'*80}")
    print(f"# SNIPPET {snippet_num}/{total_snippets}")
    print(f"# Text length: {len(snippet['text'])} chars")
    print(f"# Entities found by Claude: {len(snippet['entities'])}")
    print(f"{'#'*80}")

    entities = snippet['entities']
    reviewed = []

    if not entities:
        print("\nClaude found no entities here.")
        add = input("Add entities manually? (y/n): ").strip().lower()
        if add == 'y':
            reviewed.extend(add_missed_entities(snippet['text']))
    else:
        for i, entity in enumerate(entities, 1):
            result = quick_review_entity(snippet['text'], entity, i, len(entities), snippet_num)

            if result == 'SKIP':
                print("Skipping rest of snippet...")
                return None
            elif result == 'QUIT':
                return 'QUIT'
            elif result is not None:
                reviewed.append(result)

        # Offer to add more
        add = input("\nAdd missed entities? (y/n): ").strip().lower()
        if add == 'y':
            reviewed.extend(add_missed_entities(snippet['text']))

    return {
        'snippet_id': snippet['snippet_id'],
        'text': snippet['text'],
        'char_start': snippet['char_start'],
        'char_end': snippet['char_end'],
        'entities': sorted(reviewed, key=lambda e: e['start'])
    }


def save_gold_standard(doc_id, metadata, reviewed_snippets):
    """Save reviewed annotations as gold standard."""
    output = {
        'document_id': doc_id,
        'metadata': metadata,
        'annotation_date': datetime.now().isoformat(),
        'annotator': 'human_reviewed',
        'annotation_method': 'claude_ai_assisted',
        'total_snippets': len(reviewed_snippets),
        'total_entities': sum(len(s['entities']) for s in reviewed_snippets),
        'snippets': reviewed_snippets
    }

    gold_dir = Path('test_dataset/gold_standard')
    gold_dir.mkdir(exist_ok=True)

    output_file = gold_dir / f'{doc_id}_gold.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✓ GOLD STANDARD SAVED")
    print(f"{'='*80}")
    print(f"File: {output_file}")
    print(f"Snippets: {len(reviewed_snippets)}")
    print(f"Entities: {output['total_entities']}")

    # Breakdown
    counts = {}
    for snippet in reviewed_snippets:
        for entity in snippet['entities']:
            t = entity['type']
            counts[t] = counts.get(t, 0) + 1

    if counts:
        print(f"\nEntity breakdown:")
        for etype in sorted(counts.keys()):
            print(f"  {etype}: {counts[etype]}")

    print(f"{'='*80}\n")


def list_drafts():
    """List available draft annotations."""
    draft_dir = Path('test_dataset/drafts')
    if not draft_dir.exists():
        print("No drafts directory found.")
        print("Ask Claude to create draft annotations.")
        return []

    drafts = list(draft_dir.glob('*_draft.json'))

    if not drafts:
        print("No draft annotations found.")
        print("Ask Claude to analyze snippets and create drafts.")
        return []

    print("\nAvailable drafts:\n")
    print(f"{'Document ID':<35} {'Entities':<10} {'Language':<10}")
    print("-" * 60)

    doc_ids = []
    for draft_file in sorted(drafts):
        with open(draft_file, 'r') as f:
            data = json.load(f)
            doc_id = data['document_id']
            entities = data.get('total_entities', 0)
            lang = data['metadata'].get('language', 'unknown')
            print(f"{doc_id:<35} {entities:<10} {lang:<10}")
            doc_ids.append(doc_id)

    print(f"\nTotal: {len(drafts)} drafts ready for review")
    return doc_ids


def main():
    """Main review workflow."""
    print(f"\n{'='*80}")
    print("CLAUDE-ASSISTED ANNOTATION REVIEW")
    print(f"{'='*80}\n")

    if len(sys.argv) < 2:
        list_drafts()
        print("\nUsage: python review_annotations.py [document_id]")
        return 0

    doc_id = sys.argv[1]

    # Load draft
    draft = load_draft(doc_id)

    print(f"Document: {draft['metadata'].get('title', 'Unknown')[:60]}")
    print(f"Year: {draft['metadata'].get('year', 'Unknown')}")
    print(f"Language: {draft['metadata'].get('language', 'Unknown')}")
    print(f"Snippets: {len(draft['snippets'])}")
    print(f"Claude found: {draft['total_entities']} entities")
    print(f"\nAnnotated by: {draft.get('annotator', 'unknown')}")
    print(f"Model: {draft.get('model', 'unknown')}")

    input("\nPress Enter to begin review...")

    # Review each snippet
    reviewed = []
    for i, snippet in enumerate(draft['snippets'], 1):
        result = review_snippet(snippet, i, len(draft['snippets']))

        if result == 'QUIT':
            print("\nQuitting... (progress not saved)")
            return 0
        elif result is not None:
            reviewed.append(result)

    if not reviewed:
        print("\nNo snippets reviewed. Exiting.")
        return 0

    # Save
    save_gold_standard(doc_id, draft['metadata'], reviewed)

    print("✓ Review complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
