#!/usr/bin/env python3
"""
Evaluate NER model predictions against gold standard.

Computes standard NER metrics:
- Precision, Recall, F1 (exact match and partial match)
- Per-entity-type breakdown
- Confusion matrix
- Error analysis

Usage:
    python evaluate_ner.py [gold_standard_dir] [predictions_dir] [model_name]
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import argparse


class Entity:
    """Represents a single entity annotation."""
    def __init__(self, text: str, start: int, end: int, etype: str, source: str = ""):
        self.text = text
        self.start = start
        self.end = end
        self.type = etype
        self.source = source  # For tracking which system predicted it

    def __repr__(self):
        return f"Entity('{self.text}', {self.start}:{self.end}, {self.type})"

    def __eq__(self, other):
        """Exact match: same boundaries and type."""
        return (self.start == other.start and
                self.end == other.end and
                self.type == other.type)

    def __hash__(self):
        return hash((self.start, self.end, self.type))

    def overlaps(self, other) -> bool:
        """Check if two entities overlap."""
        return not (self.end <= other.start or other.end <= self.start)

    def partial_match(self, other) -> bool:
        """Check if entities overlap and have same type."""
        return self.overlaps(other) and self.type == other.type


def load_gold_standard(gold_file: Path) -> Dict:
    """Load gold standard annotations."""
    with open(gold_file, 'r') as f:
        return json.load(f)


def load_predictions(pred_file: Path) -> Dict:
    """Load model predictions."""
    with open(pred_file, 'r') as f:
        return json.load(f)


def extract_entities(snippet_data: Dict, source: str = "") -> List[Entity]:
    """Extract Entity objects from snippet data."""
    entities = []
    for ent in snippet_data.get('entities', []):
        entities.append(Entity(
            text=ent['text'],
            start=ent['start'],
            end=ent['end'],
            etype=ent['type'],
            source=source
        ))
    return entities


def compute_metrics(gold_entities: List[Entity],
                   pred_entities: List[Entity],
                   match_type: str = 'exact') -> Dict:
    """
    Compute precision, recall, F1.

    Args:
        gold_entities: Ground truth entities
        pred_entities: Predicted entities
        match_type: 'exact' or 'partial'
    """
    if match_type == 'exact':
        true_positives = len(set(gold_entities) & set(pred_entities))
    else:  # partial
        true_positives = 0
        matched_gold = set()
        for pred in pred_entities:
            for gold in gold_entities:
                if gold not in matched_gold and pred.partial_match(gold):
                    true_positives += 1
                    matched_gold.add(gold)
                    break

    false_positives = len(pred_entities) - true_positives
    false_negatives = len(gold_entities) - true_positives

    precision = true_positives / len(pred_entities) if pred_entities else 0
    recall = true_positives / len(gold_entities) if gold_entities else 0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0)

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'total_gold': len(gold_entities),
        'total_pred': len(pred_entities)
    }


def compute_per_type_metrics(gold_entities: List[Entity],
                             pred_entities: List[Entity]) -> Dict:
    """Compute metrics broken down by entity type."""
    # Group by type
    gold_by_type = defaultdict(list)
    pred_by_type = defaultdict(list)

    for ent in gold_entities:
        gold_by_type[ent.type].append(ent)
    for ent in pred_entities:
        pred_by_type[ent.type].append(ent)

    # Get all types
    all_types = set(gold_by_type.keys()) | set(pred_by_type.keys())

    results = {}
    for etype in sorted(all_types):
        gold = gold_by_type[etype]
        pred = pred_by_type[etype]
        results[etype] = compute_metrics(gold, pred, match_type='exact')

    return results


def analyze_errors(gold_entities: List[Entity],
                   pred_entities: List[Entity]) -> Dict:
    """Detailed error analysis."""
    # Convert to sets for exact matching
    gold_set = set(gold_entities)
    pred_set = set(pred_entities)

    # False positives: predicted but not in gold
    false_positives = pred_set - gold_set

    # False negatives: in gold but not predicted
    false_negatives = gold_set - pred_set

    # Boundary errors: overlap with gold but different boundaries
    boundary_errors = []
    for pred in pred_entities:
        if pred not in gold_set:
            for gold in gold_entities:
                if pred.overlaps(gold) and pred.type == gold.type:
                    boundary_errors.append((pred, gold))
                    break

    # Type errors: same boundaries but wrong type
    type_errors = []
    for pred in pred_entities:
        for gold in gold_entities:
            if pred.start == gold.start and pred.end == gold.end and pred.type != gold.type:
                type_errors.append((pred, gold))
                break

    return {
        'false_positives': [
            {'text': e.text, 'start': e.start, 'end': e.end, 'type': e.type}
            for e in false_positives
        ],
        'false_negatives': [
            {'text': e.text, 'start': e.start, 'end': e.end, 'type': e.type}
            for e in false_negatives
        ],
        'boundary_errors': [
            {
                'predicted': {'text': p.text, 'start': p.start, 'end': p.end, 'type': p.type},
                'gold': {'text': g.text, 'start': g.start, 'end': g.end, 'type': g.type}
            }
            for p, g in boundary_errors
        ],
        'type_errors': [
            {
                'text': p.text,
                'predicted_type': p.type,
                'gold_type': g.type
            }
            for p, g in type_errors
        ]
    }


def evaluate_document(gold_data: Dict, pred_data: Dict) -> Dict:
    """Evaluate predictions for a single document."""
    doc_id = gold_data['document_id']

    # Match snippets
    gold_snippets = {s['snippet_id']: s for s in gold_data['snippets']}
    pred_snippets = {s['snippet_id']: s for s in pred_data.get('snippets', [])}

    # Collect all entities
    all_gold_entities = []
    all_pred_entities = []

    snippet_results = []

    for snippet_id in gold_snippets.keys():
        if snippet_id not in pred_snippets:
            print(f"  WARNING: No predictions for snippet {snippet_id}")
            continue

        gold_entities = extract_entities(gold_snippets[snippet_id], source='gold')
        pred_entities = extract_entities(pred_snippets[snippet_id], source='pred')

        all_gold_entities.extend(gold_entities)
        all_pred_entities.extend(pred_entities)

        # Per-snippet metrics
        snippet_metrics = compute_metrics(gold_entities, pred_entities, 'exact')
        snippet_results.append({
            'snippet_id': snippet_id,
            'metrics': snippet_metrics
        })

    # Overall metrics
    overall_exact = compute_metrics(all_gold_entities, all_pred_entities, 'exact')
    overall_partial = compute_metrics(all_gold_entities, all_pred_entities, 'partial')
    per_type = compute_per_type_metrics(all_gold_entities, all_pred_entities)
    errors = analyze_errors(all_gold_entities, all_pred_entities)

    return {
        'document_id': doc_id,
        'overall_exact': overall_exact,
        'overall_partial': overall_partial,
        'per_type': per_type,
        'snippet_results': snippet_results,
        'error_analysis': errors
    }


def print_metrics_report(results: List[Dict], model_name: str):
    """Print human-readable evaluation report."""
    print(f"\n{'='*80}")
    print(f"NER EVALUATION REPORT: {model_name}")
    print(f"{'='*80}\n")

    # Aggregate metrics
    total_gold = sum(r['overall_exact']['total_gold'] for r in results)
    total_pred = sum(r['overall_exact']['total_pred'] for r in results)
    total_tp = sum(r['overall_exact']['true_positives'] for r in results)
    total_fp = sum(r['overall_exact']['false_positives'] for r in results)
    total_fn = sum(r['overall_exact']['false_negatives'] for r in results)

    precision = total_tp / total_pred if total_pred > 0 else 0
    recall = total_tp / total_gold if total_gold > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"Overall Performance (Exact Match):")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    print(f"  F1 Score:  {f1:.3f}")
    print(f"\n  True Positives:  {total_tp}")
    print(f"  False Positives: {total_fp}")
    print(f"  False Negatives: {total_fn}")
    print(f"  Total Gold:      {total_gold}")
    print(f"  Total Predicted: {total_pred}")

    # Per-type metrics
    print(f"\n{'-'*80}")
    print(f"Per-Entity-Type Performance:")
    print(f"{'-'*80}")

    # Aggregate per-type metrics
    type_metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'gold': 0, 'pred': 0})

    for result in results:
        for etype, metrics in result['per_type'].items():
            type_metrics[etype]['tp'] += metrics['true_positives']
            type_metrics[etype]['fp'] += metrics['false_positives']
            type_metrics[etype]['fn'] += metrics['false_negatives']
            type_metrics[etype]['gold'] += metrics['total_gold']
            type_metrics[etype]['pred'] += metrics['total_pred']

    print(f"{'Type':<8} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Gold':<8} {'Pred':<8}")
    print(f"{'-'*70}")

    for etype in sorted(type_metrics.keys()):
        m = type_metrics[etype]
        p = m['tp'] / m['pred'] if m['pred'] > 0 else 0
        r = m['tp'] / m['gold'] if m['gold'] > 0 else 0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0

        print(f"{etype:<8} {p:<12.3f} {r:<12.3f} {f:<12.3f} {m['gold']:<8} {m['pred']:<8}")

    # Per-document summary
    print(f"\n{'-'*80}")
    print(f"Per-Document Performance:")
    print(f"{'-'*80}")
    print(f"{'Document':<35} {'Precision':<12} {'Recall':<12} {'F1':<12}")
    print(f"{'-'*70}")

    for result in results:
        doc_id = result['document_id']
        m = result['overall_exact']
        print(f"{doc_id:<35} {m['precision']:<12.3f} {m['recall']:<12.3f} {m['f1']:<12.3f}")

    print(f"\n{'='*80}\n")


def main():
    """Main evaluation workflow."""
    parser = argparse.ArgumentParser(description='Evaluate NER model predictions')
    parser.add_argument('model_name', help='Name of model (e.g., "spacy", "dell_harvard")')
    parser.add_argument('--gold-dir', default=None,
                        help='Directory with gold files (default: test_dataset/gold_standard relative to this script)')
    parser.add_argument('--pred-dir', default=None,
                        help='Directory with prediction files (default: test_dataset/predictions/{model_name} relative to this script)')
    parser.add_argument('--output', default=None,
                        help='Output JSON file for detailed results')

    args = parser.parse_args()

    # Resolve default paths relative to repository layout regardless of CWD
    script_dir = Path(__file__).parent
    test_dir = script_dir.parent
    gold_dir = Path(args.gold_dir) if args.gold_dir else (test_dir / 'gold_standard')
    pred_dir = Path(args.pred_dir) if args.pred_dir else (test_dir / 'predictions' / args.model_name)

    if not gold_dir.exists():
        print(f"ERROR: Gold standard directory not found: {gold_dir}")
        return 1

    if not pred_dir.exists():
        print(f"ERROR: Predictions directory not found: {pred_dir}")
        return 1

    # Find all gold standard files
    gold_files = list(gold_dir.glob('*_gold.json'))

    if not gold_files:
        print(f"ERROR: No gold standard files found in {gold_dir}")
        return 1

    print(f"Evaluating {args.model_name}...")
    print(f"Gold standard: {gold_dir}")
    print(f"Predictions:   {pred_dir}")
    print(f"Documents:     {len(gold_files)}\n")

    results = []

    for gold_file in sorted(gold_files):
        doc_id = gold_file.stem.replace('_gold', '')
        pred_file = pred_dir / f'{doc_id}_pred.json'

        if not pred_file.exists():
            print(f"WARNING: No predictions found for {doc_id}, skipping")
            continue

        print(f"Evaluating {doc_id}...")

        gold_data = load_gold_standard(gold_file)
        pred_data = load_predictions(pred_file)

        result = evaluate_document(gold_data, pred_data)
        results.append(result)

    if not results:
        print("ERROR: No documents were evaluated")
        return 1

    # Print report
    print_metrics_report(results, args.model_name)

    # Save detailed results
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = Path(f'test_dataset/evaluation/{args.model_name}_evaluation.json')

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'model_name': args.model_name,
            'evaluation_date': datetime.now().isoformat(),
            'total_documents': len(results),
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print(f"Detailed results saved to: {output_file}")

    return 0


if __name__ == '__main__':
    from datetime import datetime
    sys.exit(main())
