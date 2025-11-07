#!/usr/bin/env python3
"""
AI-assisted annotation: Review and finalize draft annotations.

This script loads AI-generated draft annotations and allows human review
with quick accept/reject/modify workflow.

Usage:
    python review_draft_annotations.py [document_id]
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict
from datetime import datetime


ENTITY_TYPES = {
    'LOC': 'Location (places, regions, natural features)',
    'PER': 'Person (named individuals)',
    'ORG': 'Organization (companies, government bodies)',
    'MISC': 'Miscellaneous (indigenous groups, treaties, events)'
}


def load_draft(doc_id: str) -> Dict:
    """Load draft annotations for a document."""
    draft_file = Path('test_dataset/drafts') / f'{doc_id}_draft.json'
    if not draft_file.exists():
        print(f"ERROR: Draft file not found: {draft_file}")
        print(f"\nGenerate draft first using:")
        print(f"  python generate_draft_annotations.py {doc_id}")
        sys.exit(1)

    with open(draft_file, 'r') as f:
        return json.load(f)


def display_entity_in_context(text: str, entity: Dict, snippet_num: int, entity_num: int, total_entities: int):
    """Display an entity with surrounding context for review."""
    start = entity['start']
    end = entity['end']

    # Get context (50 chars before/after)
    context_start = max(0, start - 50)
    context_end = min(len(text), end + 50)

    before = text[context_start:start]
    entity_text = text[start:end]
    after = text[context_end:end]

    print(f"\n{'='*80}")
    print(f"Snippet {snippet_num} | Entity {entity_num}/{total_entities}")
    print(f"{'='*80}")
    print(f"\nContext: ...{before}[[[{entity_text}]]]{after}...")
    print(f"\nEntity: \"{entity_text}\"")
    print(f"Type: {entity['type']} ({ENTITY_TYPES.get(entity['type'], 'Unknown')})")
    print(f"Source: {entity.get('source', 'unknown')} (confidence: {entity.get('confidence', 0):.2f})")
    if entity.get('notes'):
        print(f"Notes: {entity['notes']}")


def review_entity(text: str, entity: Dict, snippet_num: int, entity_num: int, total_entities: int) -> Dict:
    """Review a single entity with human in the loop."""
    display_entity_in_context(text, entity, snippet_num, entity_num, total_entities)

    while True:
        print(f"\n{'─'*80}")
        choice = input("Action? [(y)es/(n)o/(m)odify/(s)kip snippet]: ").strip().lower()

        if choice == 'y' or choice == '':
            # Accept entity
            entity['confidence'] = 1.0
            entity['reviewed'] = True
            print("  ✓ Accepted")
            return entity

        elif choice == 'n':
            # Reject entity
            print("  ✗ Rejected")
            return None

        elif choice == 'm':
            # Modify entity
            print("\nModify entity:")

            # Modify type
            print(f"Current type: {entity['type']}")
            print("Entity types:")
            for code, desc in ENTITY_TYPES.items():
                print(f"  {code}: {desc}")
            new_type = input(f"New type (Enter to keep '{entity['type']}'): ").strip().upper()
            if new_type and new_type in ENTITY_TYPES:
                entity['type'] = new_type
                print(f"  Updated type to: {new_type}")

            # Modify boundaries
            modify_bounds = input("Modify boundaries? (y/n): ").strip().lower()
            if modify_bounds == 'y':
                try:
                    new_start = int(input(f"  Start position (current {entity['start']}): ").strip())
                    new_end = int(input(f"  End position (current {entity['end']}): ").strip())
                    entity['start'] = new_start
                    entity['end'] = new_end
                    entity['text'] = text[new_start:new_end]
                    print(f"  Updated boundaries: {entity['text']}")
                except ValueError:
                    print("  Invalid input, keeping original boundaries")

            # Add notes
            notes = input("Notes (optional): ").strip()
            if notes:
                entity['notes'] = notes

            entity['confidence'] = 1.0
            entity['reviewed'] = True
            print("  ✓ Modified and accepted")
            return entity

        elif choice == 's':
            # Skip entire snippet
            return 'SKIP_SNIPPET'

        else:
            print("Invalid choice. Use: y (yes), n (no), m (modify), s (skip snippet)")


def add_additional_entities(text: str, existing_entities: List[Dict]) -> List[Dict]:
    """Allow user to add entities that were missed by AI."""
    print(f"\n{'='*80}")
    print("Add additional entities that were missed?")
    print(f"{'='*80}")
    print(f"\nText:\n{text}\n")

    print("Current entities:")
    for i, ent in enumerate(existing_entities, 1):
        print(f"  {i}. \"{ent['text']}\" ({ent['type']})")

    new_entities = []

    while True:
        entity_text = input("\nEntity text (or Enter to finish): ").strip()
        if not entity_text:
            break

        # Find entity in text
        matches = []
        pattern = re.escape(entity_text)
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append((match.start(), match.end()))

        if not matches:
            print(f"  WARNING: '{entity_text}' not found in snippet.")
            continue

        if len(matches) > 1:
            print(f"  Found {len(matches)} matches. Using all occurrences.")

        # Get entity type
        print("  Entity types:")
        for code, desc in ENTITY_TYPES.items():
            print(f"    {code}: {desc}")
        entity_type = input("  Entity type: ").strip().upper()

        if entity_type not in ENTITY_TYPES:
            print(f"  Invalid type, skipping.")
            continue

        notes = input("  Notes (optional): ").strip()

        # Add all matches
        for start, end in matches:
            entity = {
                'text': text[start:end],
                'start': start,
                'end': end,
                'type': entity_type,
                'confidence': 1.0,
                'source': 'human_added',
                'reviewed': True,
                'notes': notes if notes else 'Added during review'
            }
            new_entities.append(entity)
            print(f"  ✓ Added: {entity['text']} ({entity_type})")

    return new_entities


def review_snippet(snippet: Dict, snippet_num: int, total_snippets: int) -> Dict:
    """Review all entities in a snippet."""
    print(f"\n\n{'#'*80}")
    print(f"# SNIPPET {snippet_num}/{total_snippets}")
    print(f"{'#'*80}")

    entities = snippet['entities']
    reviewed_entities = []

    if not entities:
        print("\nNo entities detected by AI.")
        add_more = input("Add entities manually? (y/n): ").strip().lower()
        if add_more == 'y':
            new_entities = add_additional_entities(snippet['text'], [])
            reviewed_entities.extend(new_entities)
    else:
        # Review each entity
        for i, entity in enumerate(entities, 1):
            result = review_entity(snippet['text'], entity, snippet_num, i, len(entities))

            if result == 'SKIP_SNIPPET':
                return None

            if result is not None:
                reviewed_entities.append(result)

        # Allow adding more entities
        add_more = input("\nAdd additional entities? (y/n): ").strip().lower()
        if add_more == 'y':
            new_entities = add_additional_entities(snippet['text'], reviewed_entities)
            reviewed_entities.extend(new_entities)

    return {
        'snippet_id': snippet['snippet_id'],
        'text': snippet['text'],
        'char_start': snippet['char_start'],
        'char_end': snippet['char_end'],
        'entities': sorted(reviewed_entities, key=lambda e: e['start'])
    }


def save_gold_standard(doc_id: str, doc_metadata: Dict, reviewed_snippets: List[Dict]):
    """Save reviewed annotations as gold standard."""
    output = {
        'document_id': doc_id,
        'metadata': doc_metadata,
        'annotation_date': datetime.now().isoformat(),
        'annotator': 'human_reviewed',
        'annotation_method': 'ai_assisted',
        'total_snippets': len(reviewed_snippets),
        'total_entities': sum(len(s['entities']) for s in reviewed_snippets),
        'snippets': reviewed_snippets
    }

    # Create gold_standard directory
    gold_dir = Path('test_dataset/gold_standard')
    gold_dir.mkdir(exist_ok=True)

    output_file = gold_dir / f'{doc_id}_gold.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✓ Gold standard saved to: {output_file}")
    print(f"  Total snippets: {len(reviewed_snippets)}")
    print(f"  Total entities: {output['total_entities']}")

    # Print entity type breakdown
    entity_counts = {}
    for snippet in reviewed_snippets:
        for entity in snippet['entities']:
            entity_type = entity['type']
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

    print(f"\n  Entity breakdown:")
    for etype, count in sorted(entity_counts.items()):
        print(f"    {etype}: {count}")
    print(f"{'='*80}\n")


def list_available_drafts():
    """List all documents with draft annotations available."""
    draft_dir = Path('test_dataset/drafts')
    if not draft_dir.exists():
        print("ERROR: No drafts directory found.")
        print("\nGenerate drafts first using:")
        print("  python generate_draft_annotations.py")
        return []

    draft_files = list(draft_dir.glob('*_draft.json'))

    print("Available drafts for review:\n")
    print(f"{'Document ID':<35} {'Entities':<10}")
    print("-" * 50)

    for draft_file in sorted(draft_files):
        with open(draft_file, 'r') as f:
            data = json.load(f)
            doc_id = data['document_id']
            num_entities = data.get('total_entities', 0)
            print(f"{doc_id:<35} {num_entities:<10}")

    print(f"\nTotal: {len(draft_files)} drafts")
    return [f.stem.replace('_draft', '') for f in sorted(draft_files)]


def main():
    """Main review workflow."""
    if len(sys.argv) < 2:
        list_available_drafts()
        print("\nUsage: python review_draft_annotations.py [document_id]")
        return 0

    doc_id = sys.argv[1]

    print(f"\n{'='*80}")
    print(f"AI-ASSISTED ANNOTATION: Human Review")
    print(f"Document: {doc_id}")
    print(f"{'='*80}\n")

    # Load draft
    draft = load_draft(doc_id)

    print(f"Document: {draft['metadata'].get('title', 'Unknown')}")
    print(f"Year: {draft['metadata'].get('year', 'Unknown')}")
    print(f"Language: {draft['metadata'].get('language', 'Unknown')}")
    print(f"Total snippets: {len(draft['snippets'])}")
    print(f"AI-detected entities: {draft['total_entities']}")

    input("\nPress Enter to begin review...")

    # Review each snippet
    reviewed_snippets = []
    for i, snippet in enumerate(draft['snippets'], 1):
        result = review_snippet(snippet, i, len(draft['snippets']))
        if result is not None:
            reviewed_snippets.append(result)

    if not reviewed_snippets:
        print("\nNo snippets were reviewed. Exiting.")
        return 0

    # Save gold standard
    save_gold_standard(doc_id, draft['metadata'], reviewed_snippets)

    print("✓ Review complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
