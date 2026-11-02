"""
Evaluation script for Railway Passenger Help Desk.
Computes metrics on test results.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
import re


def load_json(file_path: Path) -> List[Dict]:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def evaluate_answer_correctness(result: Dict, test_case: Dict) -> bool:
    """
    Check if answer is correct based on test case expectations.
    
    Args:
        result: Actual result from system
        test_case: Test case with expected values
        
    Returns:
        True if correct
    """
    answer = result.get('answer', '').lower()
    dont_know = result.get('dont_know', False)
    
    # Check dont_know expectations
    if test_case.get('expected_dont_know'):
        return dont_know
    
    # If expected to answer but said don't know - wrong
    if dont_know:
        return False
    
    # Check for expected text
    if 'expected_has_text' in test_case:
        for text in test_case['expected_has_text']:
            if text.lower() not in answer:
                return False
    
    # Check for expected amounts (₹ or %)
    if test_case.get('expected_has_amount'):
        if not re.search(r'[₹₹%]|\d+%|\d+\s*rupees?', answer):
            return False
    
    return True


def evaluate_sources(result: Dict, test_case: Dict) -> Dict:
    """
    Evaluate source citations.
    
    Returns:
        Dictionary with precision, recall, correct_doc
    """
    actual_sources = result.get('sources', [])
    
    if not actual_sources:
        if test_case.get('type') == 'db':
            return {'precision': 1.0, 'recall': 1.0, 'correct_doc': True}
        return {'precision': 0.0, 'recall': 0.0, 'correct_doc': False}
    
    # Check expected doc
    correct_doc = False
    if 'expected_doc' in test_case:
        for source in actual_sources:
            if test_case['expected_doc'] in source.get('doc', ''):
                correct_doc = True
                break
    elif 'expected_docs' in test_case:
        # Multiple expected docs
        correct_doc = any(
            any(exp_doc in src.get('doc', '') for src in actual_sources)
            for exp_doc in test_case['expected_docs']
        )
    else:
        # No expected doc specified
        correct_doc = True
    
    # For now, simple precision/recall
    precision = 1.0 if correct_doc else 0.5
    recall = 1.0 if correct_doc else 0.5
    
    return {
        'precision': precision,
        'recall': recall,
        'correct_doc': correct_doc
    }


def evaluate_sql(result: Dict, test_case: Dict) -> bool:
    """
    Evaluate SQL query correctness.
    
    Returns:
        True if SQL is reasonable
    """
    sql = result.get('sql')
    
    if test_case.get('type') == 'db' or test_case.get('expected_sql'):
        if not sql:
            return False
        
        sql_lower = sql.lower()
        
        # Check expected SQL components
        if 'expected_sql_has' in test_case:
            for component in test_case['expected_sql_has']:
                if component.lower() not in sql_lower:
                    return False
        
        return True
    
    # Non-SQL question
    return True


def compute_metrics(results: List[Dict], test_cases: List[Dict]) -> Dict:
    """
    Compute evaluation metrics.
    
    Returns:
        Dictionary of metrics
    """
    # Build test case map
    test_map = {tc['id']: tc for tc in test_cases}
    
    metrics = {
        'total_questions': len(results),
        'answer_correct': 0,
        'source_correct': 0,
        'sql_correct': 0,
        'dont_know_correct': 0,
        'dont_know_incorrect': 0,
        'false_refusal': 0,
        'false_answer': 0,
        'source_precision_sum': 0.0,
        'source_recall_sum': 0.0,
    }
    
    for result in results:
        qid = result.get('id')
        if qid not in test_map:
            continue
        
        test_case = test_map[qid]
        
        # Answer correctness
        if evaluate_answer_correctness(result, test_case):
            metrics['answer_correct'] += 1
        
        # Source correctness
        source_eval = evaluate_sources(result, test_case)
        if source_eval['correct_doc']:
            metrics['source_correct'] += 1
        metrics['source_precision_sum'] += source_eval['precision']
        metrics['source_recall_sum'] += source_eval['recall']
        
        # SQL correctness
        if evaluate_sql(result, test_case):
            metrics['sql_correct'] += 1
        
        # Don't know correctness
        dont_know = result.get('dont_know', False)
        expected_dont_know = test_case.get('expected_dont_know', False)
        
        if dont_know == expected_dont_know:
            metrics['dont_know_correct'] += 1
        else:
            metrics['dont_know_incorrect'] += 1
            if dont_know and not expected_dont_know:
                metrics['false_refusal'] += 1
            if not dont_know and expected_dont_know:
                metrics['false_answer'] += 1
    
    # Compute percentages
    total = metrics['total_questions']
    if total > 0:
        metrics['answer_accuracy'] = metrics['answer_correct'] / total
        metrics['source_accuracy'] = metrics['source_correct'] / total
        metrics['sql_accuracy'] = metrics['sql_correct'] / total
        metrics['dont_know_accuracy'] = metrics['dont_know_correct'] / total
        metrics['source_precision'] = metrics['source_precision_sum'] / total
        metrics['source_recall'] = metrics['source_recall_sum'] / total
        metrics['false_refusal_rate'] = metrics['false_refusal'] / total
        metrics['false_answer_rate'] = metrics['false_answer'] / total
    
    return metrics


def print_metrics(metrics: Dict):
    """Print metrics in a nice format."""
    print("\n" + "="*60)
    print("EVALUATION METRICS")
    print("="*60)
    print(f"Total Questions: {metrics['total_questions']}")
    print()
    
    print("ANSWER CORRECTNESS:")
    print(f"  Correct: {metrics['answer_correct']}/{metrics['total_questions']} ({metrics.get('answer_accuracy', 0)*100:.1f}%)")
    print()
    
    print("SOURCE ACCURACY:")
    print(f"  Correct Doc: {metrics['source_correct']}/{metrics['total_questions']} ({metrics.get('source_accuracy', 0)*100:.1f}%)")
    print(f"  Precision: {metrics.get('source_precision', 0):.3f}")
    print(f"  Recall: {metrics.get('source_recall', 0):.3f}")
    print()
    
    print("SQL CORRECTNESS:")
    print(f"  Correct: {metrics['sql_correct']}/{metrics['total_questions']} ({metrics.get('sql_accuracy', 0)*100:.1f}%)")
    print()
    
    print("DON'T KNOW HANDLING:")
    print(f"  Correct: {metrics['dont_know_correct']}/{metrics['total_questions']} ({metrics.get('dont_know_accuracy', 0)*100:.1f}%)")
    print(f"  False Refusals: {metrics['false_refusal']} ({metrics.get('false_refusal_rate', 0)*100:.1f}%)")
    print(f"  False Answers: {metrics['false_answer']} ({metrics.get('false_answer_rate', 0)*100:.1f}%)")
    print()
    
    # Estimated score
    answer_score = min(30, metrics.get('answer_accuracy', 0) * 30)
    source_score = min(10, metrics.get('source_accuracy', 0) * 10)
    dont_know_score = min(10, metrics.get('dont_know_accuracy', 0) * 10)
    estimated_total = answer_score + source_score + dont_know_score
    
    print("ESTIMATED HIDDEN QUESTION SCORE:")
    print(f"  Answer Correctness: {answer_score:.1f}/30")
    print(f"  Source Accuracy: {source_score:.1f}/10")
    print(f"  Don't Know: {dont_know_score:.1f}/10")
    print(f"  TOTAL: {estimated_total:.1f}/50")
    print("="*60)


def main():
    """Main evaluation function."""
    if len(sys.argv) != 3:
        print("Usage: python evaluate.py <results.json> <test_set.json>")
        sys.exit(1)
    
    results_file = Path(sys.argv[1])
    test_file = Path(sys.argv[2])
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)
    
    if not test_file.exists():
        print(f"Error: Test file not found: {test_file}")
        sys.exit(1)
    
    # Load data
    results = load_json(results_file)
    test_cases = load_json(test_file)
    
    print(f"Loaded {len(results)} results and {len(test_cases)} test cases")
    
    # Compute metrics
    metrics = compute_metrics(results, test_cases)
    
    # Print metrics
    print_metrics(metrics)
    
    # Save metrics
    metrics_file = results_file.parent / f"metrics_{results_file.stem}.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nMetrics saved to: {metrics_file}")


if __name__ == "__main__":
    main()
