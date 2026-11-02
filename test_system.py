"""
Quick system test script.
Tests the system without needing full environment setup.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from helpdesk import config
        print("✓ config")
    except Exception as e:
        print(f"✗ config: {e}")
        return False
    
    try:
        from helpdesk import doc_meta
        print("✓ doc_meta")
    except Exception as e:
        print(f"✗ doc_meta: {e}")
        return False
    
    try:
        from helpdesk import entities
        print("✓ entities")
    except Exception as e:
        print(f"✗ entities: {e}")
        return False
    
    try:
        from helpdesk import ingest
        print("✓ ingest")
    except Exception as e:
        print(f"✗ ingest: {e}")
        return False
    
    try:
        from helpdesk import search
        print("✓ search")
    except Exception as e:
        print(f"✗ search: {e}")
        return False
    
    try:
        from helpdesk import sql_guard
        print("✓ sql_guard")
    except Exception as e:
        print(f"✗ sql_guard: {e}")
        return False
    
    try:
        from helpdesk import stations
        print("✓ stations")
    except Exception as e:
        print(f"✗ stations: {e}")
        return False
    
    try:
        from helpdesk import sql
        print("✓ sql")
    except Exception as e:
        print(f"✗ sql: {e}")
        return False
    
    try:
        from helpdesk import answer
        print("✓ answer")
    except Exception as e:
        print(f"✗ answer: {e}")
        return False
    
    try:
        from helpdesk import router
        print("✓ router")
    except Exception as e:
        print(f"✗ router: {e}")
        return False
    
    try:
        from helpdesk import pipeline
        print("✓ pipeline")
    except Exception as e:
        print(f"✗ pipeline: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True


def test_entity_extraction():
    """Test entity extraction."""
    print("Testing entity extraction...")
    
    from helpdesk.entities import extract_identifiers
    
    test_cases = [
        ("What is Rule 25?", ["Rule 25"], "rules"),
        ("Train 12002 schedule", ["12002"], "trains"),
        ("Circular CC08/2025", ["CC08/2025"], "circulars"),
        ("Refund is ₹240", ["₹240"], "amounts"),
    ]
    
    passed = 0
    for text, expected, key in test_cases:
        ids = extract_identifiers(text)
        if any(exp in str(ids[key]) for exp in expected):
            print(f"✓ {text}")
            passed += 1
        else:
            print(f"✗ {text} - Expected {expected}, got {ids[key]}")
    
    print(f"\nPassed {passed}/{len(test_cases)} entity extraction tests\n")
    return passed == len(test_cases)


def test_sql_guard():
    """Test SQL guard."""
    print("Testing SQL guard...")
    
    from helpdesk.sql_guard import guard_sql
    
    test_cases = [
        ("SELECT * FROM trains", True, "Valid SELECT"),
        ("INSERT INTO trains VALUES (1)", False, "Reject INSERT"),
        ("UPDATE trains SET name = 'x'", False, "Reject UPDATE"),
        ("DELETE FROM trains", False, "Reject DELETE"),
        ("DROP TABLE trains", False, "Reject DROP"),
    ]
    
    passed = 0
    for sql, expected_safe, desc in test_cases:
        is_safe, reason = guard_sql(sql)
        if is_safe == expected_safe:
            print(f"✓ {desc}")
            passed += 1
        else:
            print(f"✗ {desc} - Expected {expected_safe}, got {is_safe}")
    
    print(f"\nPassed {passed}/{len(test_cases)} SQL guard tests\n")
    return passed == len(test_cases)


def test_config():
    """Test configuration."""
    print("Testing configuration...")
    
    from helpdesk.config import config, validate_environment
    
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Index directory: {config.INDEX_DIR}")
    print(f"API key set: {'Yes' if config.GEMINI_API_KEY else 'No (needs .env)'}")
    
    is_valid, errors = validate_environment()
    if is_valid:
        print("✓ Environment valid")
    else:
        print("✗ Environment issues:")
        for error in errors:
            print(f"  - {error}")
    
    print()
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("SYSTEM TEST")
    print("="*60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Entity Extraction", test_entity_extraction()))
    results.append(("SQL Guard", test_sql_guard()))
    
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print()
    if all_passed:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Create .env with your GEMINI_API_KEY")
        print("2. Run: python build_index.py")
        print("3. Run: python ask.py 'test question'")
    else:
        print("❌ Some tests failed - check errors above")
    
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
