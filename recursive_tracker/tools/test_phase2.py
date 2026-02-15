#!/usr/bin/env python3
"""
Test Phase 2 components: Pattern detection and rule promotion.
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from pattern_detector import PatternDetector


def test_pattern_detection():
    """Test pattern detection."""
    print("[TEST] Pattern Detection...")
    detector = PatternDetector()

    # Detect patterns
    patterns = detector.detect_all_patterns(min_occurrences=2)

    if patterns:
        print(f"[OK] Detected {len(patterns)} patterns")
        for pattern in patterns:
            print(f"  - {pattern['pattern_name']} ({pattern['pattern_type']})")
        return True
    else:
        print("[FAIL] No patterns detected")
        return False


def test_save_patterns():
    """Test saving patterns to database."""
    print("\n[TEST] Save Patterns...")
    detector = PatternDetector()

    patterns = detector.detect_all_patterns(min_occurrences=2)

    if not patterns:
        print("[SKIP] No patterns to save")
        return False

    saved = detector.save_patterns(patterns)

    if saved > 0:
        print(f"[OK] Saved {saved} patterns to database")
        return True
    else:
        print("[FAIL] Failed to save patterns")
        return False


def test_promotion_candidates():
    """Test getting promotion candidates."""
    print("\n[TEST] Promotion Candidates...")
    detector = PatternDetector()

    candidates = detector.get_promotion_candidates()

    if candidates:
        print(f"[OK] Found {len(candidates)} promotion candidates")
        for candidate in candidates[:3]:
            print(f"  - {candidate['pattern_name']} (severity: {candidate['severity']})")
        return True
    else:
        print("[INFO] No promotion candidates yet")
        return True


def test_pattern_report():
    """Test pattern report generation."""
    print("\n[TEST] Pattern Report...")
    detector = PatternDetector()

    report = detector.generate_pattern_report()

    if "Pattern Detection Report" in report:
        print(f"[OK] Report generated ({len(report)} characters)")
        return True
    else:
        print("[FAIL] Report generation failed")
        return False


def run_all_tests():
    """Run all Phase 2 tests."""
    print("=" * 60)
    print("Phase 2 Integration Tests")
    print("=" * 60)

    tests = [
        ("Pattern Detection", test_pattern_detection),
        ("Save Patterns", test_save_patterns),
        ("Promotion Candidates", test_promotion_candidates),
        ("Pattern Report", test_pattern_report)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n[OK] {test_name}: PASSED\n")
            else:
                failed += 1
                print(f"\n[FAIL] {test_name}: FAILED\n")
        except Exception as e:
            failed += 1
            print(f"\n[ERROR] {test_name}: {e}\n")

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
