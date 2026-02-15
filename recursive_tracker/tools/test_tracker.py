#!/usr/bin/env python3
"""
Test BillyTracker integration.

Tests the core functionality of Billy's Recursive Improvement Tracker.
Run this after initializing the database to verify everything works.
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from billy_tracker import BillyTracker


def test_log_decision():
    """Test logging a decision."""
    print("[TEST] Logging decision...")
    tracker = BillyTracker()

    decision_id = tracker.log_decision(
        decision_type='file_modification',
        action_taken='Test: Created test file',
        rule_source='global_claude_md',
        rule_text='Always verify after file modifications'
    )

    if decision_id:
        print(f"[OK] Decision logged with ID: {decision_id}")
        return decision_id
    else:
        print("[ERROR] Failed to log decision")
        return None


def test_record_outcome(decision_id):
    """Test recording an outcome."""
    print("\n[TEST] Recording outcome...")
    tracker = BillyTracker()

    if decision_id is None:
        print("[SKIP] No decision ID provided")
        return False

    tracker.record_outcome(
        decision_id=decision_id,
        outcome='success',
        evidence='Test completed successfully',
        time_elapsed=5,
        user_frustration=False
    )

    print("[OK] Outcome recorded")
    return True


def test_get_recent_decisions():
    """Test retrieving recent decisions."""
    print("\n[TEST] Getting recent decisions...")
    tracker = BillyTracker()

    decisions = tracker.get_recent_decisions(limit=5)

    print(f"[OK] Retrieved {len(decisions)} recent decisions")
    for i, decision in enumerate(decisions[:3], 1):
        print(f"  {i}. {decision['action_taken']}: {decision['outcome']}")

    return len(decisions) > 0


def test_get_stats():
    """Test getting statistics."""
    print("\n[TEST] Getting statistics...")
    tracker = BillyTracker()

    stats = tracker.get_stats()

    print(f"[OK] Statistics retrieved:")
    print(f"  - Total decisions: {stats['total_decisions']}")
    print(f"  - Success rate: {stats['success_rate']:.1%}")
    print(f"  - Avg time to resolution: {stats['avg_time_to_resolution']:.1f}s")
    print(f"  - Frustration rate: {stats['frustration_rate']:.1%}")

    return stats['total_decisions'] >= 1


def test_get_global_stats():
    """Test getting global statistics."""
    print("\n[TEST] Getting global statistics...")
    tracker = BillyTracker()

    stats = tracker.get_global_stats()

    print(f"[OK] Global statistics:")
    print(f"  - Total decisions: {stats['total_decisions']}")
    print(f"  - Total projects: {stats['total_projects']}")
    print(f"  - Success rate: {stats['success_rate']:.1%}")

    return stats['total_decisions'] >= 1


def test_frustration_detection():
    """Test frustration detection."""
    print("\n[TEST] Detecting user frustration...")
    tracker = BillyTracker()

    test_messages = [
        ("Good job!", False),
        ("Why didn't you check the file?", True),
        ("You keep doing this wrong!", True),
        ("That worked perfectly.", False)
    ]

    all_passed = True
    for message, expected_frustrated in test_messages:
        result = tracker.detect_user_frustration(message)
        if result['frustrated'] == expected_frustrated:
            print(f"[OK] '{message[:40]}...' -> frustrated={result['frustrated']}")
        else:
            print(f"[FAIL] '{message[:40]}...' -> expected={expected_frustrated}, got={result['frustrated']}")
            all_passed = False

    return all_passed


def test_log_lesson():
    """Test logging a lesson."""
    print("\n[TEST] Logging lesson...")
    tracker = BillyTracker()

    lesson_id = tracker.log_lesson(
        source_file='test_lessons.md',
        source_type='lessons_md',
        lesson_text='Test: Always verify after file modifications',
        category='verification',
        severity='high'
    )

    if lesson_id:
        print(f"[OK] Lesson logged with ID: {lesson_id}")
        return True
    else:
        print("[ERROR] Failed to log lesson")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("BillyTracker Integration Tests")
    print("=" * 60)

    tests = [
        ("Log Decision", test_log_decision),
        ("Record Outcome", lambda: test_record_outcome(test_log_decision())),
        ("Get Recent Decisions", test_get_recent_decisions),
        ("Get Stats", test_get_stats),
        ("Get Global Stats", test_get_global_stats),
        ("Frustration Detection", test_frustration_detection),
        ("Log Lesson", test_log_lesson)
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
