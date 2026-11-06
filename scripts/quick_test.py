#!/usr/bin/env python3
"""
Quick system test - Run this after build_index.py to verify everything works.
Tests 3 questions: doc, db, and out-of-scope.
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from helpdesk.pipeline import ask


def test_question(question, expected_type):
    """Test a single question."""
    print(f"\n{'='*60}")
    print(f"Q: {question}")
    print(f"{'='*60}")
    
    try:
        result = ask(question)
        
        print(f"\nAnswer: {result['answer'][:200]}...")
        print(f"\nSources: {result['sources']}")
        print(f"SQL: {result['sql']}")
        print(f"Don't Know: {result['dont_know']}")
        
        # Basic validation
        assert isinstance(result, dict), "Result must be a dict"
        assert "answer" in result, "Missing 'answer' key"
        assert "sources" in result, "Missing 'sources' key"
        assert "sql" in result, "Missing 'sql' key"
        assert "dont_know" in result, "Missing 'dont_know' key"
        
        print(f"\n✓ PASS - Contract validated")
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run quick tests."""
    print("\n" + "="*60)
    print("QUICK SYSTEM TEST")
    print("="*60)
    
    tests = [
        ("What is the Tatkal cancellation charge?", "docs"),
        ("Which trains run from Delhi to Mumbai?", "db"),
        ("What is my PNR status?", "out_of_scope"),
    ]
    
    results = []
    for question, qtype in tests:
        passed = test_question(question, qtype)
        results.append((question, passed))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for question, passed_flag in results:
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {question[:50]}...")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n✓ All tests passed! System is working.")
        return 0
    else:
        print(f"\n✗ {total - passed} tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
