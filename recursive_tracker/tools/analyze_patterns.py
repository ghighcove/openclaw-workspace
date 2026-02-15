#!/usr/bin/env python3
"""
Analyze patterns in Billy's decisions.

Detects success patterns, failure patterns, and suggests rule promotions.
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from pattern_detector import PatternDetector


def analyze_patterns(min_occurrences=2):
    """
    Analyze decisions for patterns.

    Args:
        min_occurrences: Minimum times pattern must appear
    """
    print("=" * 60)
    print("Pattern Analysis")
    print("=" * 60)

    detector = PatternDetector()

    # Detect all patterns
    print(f"\n[INFO] Detecting patterns (min occurrences: {min_occurrences})...")
    patterns = detector.detect_all_patterns(min_occurrences=min_occurrences)

    if not patterns:
        print("[INFO] No patterns detected yet. Need more decision data.")
        return

    print(f"[OK] Found {len(patterns)} patterns")

    # Group by type
    success_patterns = [p for p in patterns if p['pattern_type'] == 'success_pattern']
    failure_patterns = [p for p in patterns if p['pattern_type'] == 'failure_pattern']

    print(f"\n  - Success patterns: {len(success_patterns)}")
    print(f"  - Failure patterns: {len(failure_patterns)}")

    # Save patterns to database
    print(f"\n[INFO] Saving patterns to database...")
    saved = detector.save_patterns(patterns)
    print(f"[OK] Saved {saved} patterns")

    # Generate report
    print("\n" + "=" * 60)
    print("Pattern Report")
    print("=" * 60)

    for i, pattern in enumerate(patterns, 1):
        type_emoji = "[+]" if pattern['pattern_type'] == 'success_pattern' else "[!]"
        print(f"\n{type_emoji} {i}. {pattern['pattern_name']}")
        print(f"    Type: {pattern['pattern_type']}")
        print(f"    Decision Type: {pattern['decision_type']}")
        print(f"    Occurrences: {pattern['occurrence_count']}")

        if pattern['pattern_type'] == 'failure_pattern':
            mins = pattern.get('total_time_wasted', 0) / 60
            print(f"    Time Wasted: {mins:.1f} minutes")
            print(f"    Severity: {pattern.get('severity', 'low')}")

        print(f"    Examples:")
        for example in pattern.get('examples', [])[:3]:
            print(f"      - {example}")

    # Show promotion candidates
    print("\n" + "=" * 60)
    print("Promotion Candidates")
    print("=" * 60)

    candidates = detector.get_promotion_candidates()

    if not candidates:
        print("[INFO] No patterns ready for promotion.")
    else:
        print(f"[INFO] Found {len(candidates)} promotion candidates:")
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate['pattern_name']}")
            print(f"   Occurrences: {candidate['occurrence_count']}")
            print(f"   Severity: {candidate['severity']}")
            print(f"   Meets criteria: {'Yes' if candidate['meets_criteria'] else 'No'}")

    print("\n" + "=" * 60)


def auto_promote_patterns():
    """Auto-promote high-priority failure patterns."""
    print("\n[INFO] Auto-promoting high-priority failure patterns...")

    detector = PatternDetector()
    candidates = detector.get_promotion_candidates()

    promoted = 0

    for candidate in candidates:
        # Auto-promote high-severity failure patterns
        if (candidate['pattern_type'] == 'failure_pattern' and
            candidate['severity'] == 'high' and
            candidate['meets_criteria']):

            # Generate target file
            if candidate['decision_type'] == 'file_modification':
                target_file = 'global_claude_md'
                target_section = 'File Operations'
            elif candidate['decision_type'] == 'verification':
                target_file = 'global_claude_md'
                target_section = 'Verification'
            else:
                target_file = 'global_claude_md'
                target_section = None

            success = detector.promote_pattern(
                pattern_id=candidate['id'],
                target_file=target_file,
                target_section=target_section
            )

            if success:
                promoted += 1
                print(f"[OK] Promoted: {candidate['pattern_name']}")
            else:
                print(f"[FAIL] Failed to promote: {candidate['pattern_name']}")

    print(f"\n[OK] Auto-promoted {promoted} patterns")
    return promoted


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze patterns in Billy decisions')
    parser.add_argument('--min-occurrences', type=int, default=2,
                        help='Minimum pattern occurrences (default: 2)')
    parser.add_argument('--auto-promote', action='store_true',
                        help='Auto-promote high-priority patterns')

    args = parser.parse_args()

    analyze_patterns(min_occurrences=args.min_occurrences)

    if args.auto_promote:
        auto_promote_patterns()


if __name__ == "__main__":
    main()
