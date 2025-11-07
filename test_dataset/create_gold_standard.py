#!/usr/bin/env python3
"""
Interactive annotation tool for creating gold standard NER labels.

Usage:
    python create_gold_standard.py [document_id]

If no document_id provided, shows list of available documents.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Resolve paths relative to this script directory so it works regardless of CWD
SCRIPT_DIR = Path(__file__).parent


ENTITY_TYPES = {
    'LOC': 'Location (places, regions, natural features)',
    'PER': 'Person (named individuals)',
    'ORG': 'Organization (companies, government bodies)',
    'MISC': 'Miscellaneous (indigenous groups, treaties, events)'
}


def load_snippets(doc_id: str) -> Dict:
    """Load snippets file for a document."""
    snippets_file = SCRIPT_DIR / 'snippets' / f'{doc_id}_snippets.json'
    if not snippets_file.exists():
        print(f"ERROR: Snippets file not found: {snippets_file}")
        sys.exit(1)

    with open(snippets_file, 'r') as f:
        return json.load(f)


def display_snippet(snippet: Dict, snippet_num: int, total: int):
    """Display a snippet for annotation."""
    print(f"\n{'='*80}")
    print(f"SNIPPET {snippet_num}/{total}")
    print(f"{'='*80}")
    print(f"Entity Density Score: {snippet['entity_density_score']}")
    print(f"Position: chars {snippet['char_start']}-{snippet['char_end']}")
    print(f"\n{'-'*80}")
    print(snippet['text'])
    print(f"{'-'*80}\n")


def highlight_entity(text: str, start: int, end: int) -> str:
    """Highlight an entity in text with markers."""
    return (text[:start] +
            f"<<<{text[start:end]}>>>" +
            text[end:])


def find_entity_in_text(text: str, entity_text: str, start_hint: int = 0) -> List[Tuple[int, int]]:
    """Find all occurrences of entity text in snippet."""
    matches = []
    pattern = re.escape(entity_text)
    for match in re.finditer(pattern, text, re.IGNORECASE):
        matches.append((match.start(), match.end()))
    return matches


def annotate_snippet_interactive(snippet: Dict, snippet_num: int, total: int) -> Dict:
    """Interactively annotate a single snippet."""
    display_snippet(snippet, snippet_num, total)

    entities = []

    print("Enter entities one at a time. Type 'done' when finished.\n")
    print("For each entity, you'll provide:")
    print("  1. Entity text (exact string from snippet)")
    print("  2. Entity type (LOC, PER, ORG, MISC)")
    print("  3. Optional notes\n")

    entity_num = 1
    while True:
        print(f"\n--- Entity #{entity_num} ---")
        entity_text = input("Entity text (or 'done' to finish, 'skip' to skip snippet): ").strip()

        if entity_text.lower() == 'done':
            break

        if entity_text.lower() == 'skip':
            return None

        if not entity_text:
            continue

        # Find entity in text
        matches = find_entity_in_text(snippet['text'], entity_text)

        if not matches:
            print(f"  WARNING: '{entity_text}' not found in snippet.")
            retry = input("  Try again? (y/n): ").strip().lower()
            if retry == 'y':
                continue
            else:
                # Allow manual entry
                print("  Enter character positions manually:")
                try:
                    start = int(input("    Start position: ").strip())
                    end = int(input("    End position: ").strip())
                    matches = [(start, end)]
                except ValueError:
                    print("  Invalid positions, skipping entity.")
                    continue

        if len(matches) > 1:
            print(f"  Found {len(matches)} matches:")
            for i, (s, e) in enumerate(matches, 1):
                context_start = max(0, s - 30)
                context_end = min(len(snippet['text']), e + 30)
                context = snippet['text'][context_start:context_end]
                print(f"    {i}. ...{context}...")
            choice = input(f"  Which one? (1-{len(matches)}, or 'all' for all): ").strip()

            if choice.lower() == 'all':
                selected_matches = matches
            else:
                try:
                    idx = int(choice) - 1
                    selected_matches = [matches[idx]]
                except (ValueError, IndexError):
                    print("  Invalid choice, skipping entity.")
                    continue
        else:
            selected_matches = matches

        # Show entity types
        print("\n  Entity types:")
        for code, desc in ENTITY_TYPES.items():
            print(f"    {code}: {desc}")

        entity_type = input("  Entity type: ").strip().upper()

        if entity_type not in ENTITY_TYPES:
            print(f"  WARNING: '{entity_type}' is not a standard type.")
            confirm = input(f"  Use anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue

        notes = input("  Notes (optional): ").strip()

        # Add entity (or entities if multiple matches)
        for start, end in selected_matches:
            entity = {
                'text': snippet['text'][start:end],
                'start': start,
                'end': end,
                'type': entity_type,
                'confidence': 1.0,
                'notes': notes if notes else ''
            }
            entities.append(entity)
            print(f"  ✓ Added: {entity['text']} ({entity_type})")

        entity_num += 1

    return {
        'snippet_id': f"{snippet['snippet_id']:03d}",
        'text': snippet['text'],
        'char_start': snippet['char_start'],
        'char_end': snippet['char_end'],
        'entities': sorted(entities, key=lambda e: e['start'])
    }


def save_gold_standard(doc_id: str, doc_metadata: Dict, annotated_snippets: List[Dict]):
    """Save annotated snippets as gold standard."""
    output = {
        'document_id': doc_id,
        'metadata': doc_metadata,
        'annotation_date': datetime.now().isoformat(),
        'annotator': 'human',
        'total_snippets': len(annotated_snippets),
        'total_entities': sum(len(s['entities']) for s in annotated_snippets),
        'snippets': annotated_snippets
    }

    output_file = SCRIPT_DIR / 'gold_standard' / f'{doc_id}_gold.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Gold standard saved to: {output_file}")
    print(f"  Total snippets: {len(annotated_snippets)}")
    print(f"  Total entities: {output['total_entities']}")

    # Print entity type breakdown
    entity_counts = {}
    for snippet in annotated_snippets:
        for entity in snippet['entities']:
            entity_type = entity['type']
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

    print(f"\n  Entity breakdown:")
    for etype, count in sorted(entity_counts.items()):
        print(f"    {etype}: {count}")


def list_available_documents():
    """List all documents with snippets available."""
    snippets_dir = SCRIPT_DIR / 'snippets'
    snippet_files = list(snippets_dir.glob('*_snippets.json'))

    print("Available documents for annotation:\n")
    print(f"{'Document ID':<35} {'Snippets':<10} {'Type':<12} {'Language':<10}")
    print("-" * 75)

    for snippet_file in sorted(snippet_files):
        with open(snippet_file, 'r') as f:
            data = json.load(f)
            doc_id = data['document_id']
            num_snippets = len(data['snippets'])
            doc_type = data['metadata'].get('doc_type', 'unknown')
            language = data['metadata'].get('language', 'unknown')
            print(f"{doc_id:<35} {num_snippets:<10} {doc_type:<12} {language:<10}")

    print(f"\nTotal: {len(snippet_files)} documents")


def main():
    """Main annotation workflow."""
    if len(sys.argv) < 2:
        list_available_documents()
        print("\nUsage: python create_gold_standard.py [document_id]")
        return 0

    doc_id = sys.argv[1]

    print(f"\n{'='*80}")
    print(f"GOLD STANDARD ANNOTATION")
    print(f"Document: {doc_id}")
    print(f"{'='*80}\n")

    # Load snippets
    data = load_snippets(doc_id)
    snippets = data['snippets']

    print(f"Document: {data['metadata'].get('title', 'Unknown')}")
    print(f"Year: {data['metadata'].get('year', 'Unknown')}")
    print(f"Language: {data['metadata'].get('language', 'Unknown')}")
    print(f"Total snippets: {len(snippets)}")

    input("\nPress Enter to begin annotation...")

    # Annotate each snippet
    annotated = []
    for i, snippet in enumerate(snippets, 1):
        result = annotate_snippet_interactive(snippet, i, len(snippets))
        if result is not None:
            annotated.append(result)

    if not annotated:
        print("\nNo snippets were annotated. Exiting.")
        return 0

    # Save gold standard
    save_gold_standard(doc_id, data['metadata'], annotated)

    print("\n✓ Annotation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
