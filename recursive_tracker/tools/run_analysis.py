#!/usr/bin/env python3
"""
Run comprehensive analysis of Billy's decisions and patterns.

This is the main automation tool that runs:
- Pattern detection
- Rule promotion analysis
- Conflict detection
- Cross-project transfer candidates
- A/B test status
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from pattern_detector import PatternDetector
from conflict_detector import ConflictDetector
from pattern_transfer import PatternTransfer
from ab_testing import ABTestFramework


def run_pattern_analysis():
    """Run pattern detection and analysis."""
    print("=" * 60)
    print("PATTERN ANALYSIS")
    print("=" * 60)

    detector = PatternDetector()

    # Detect patterns
    patterns = detector.detect_all_patterns(min_occurrences=2)
    print(f"\n[INFO] Detected {len(patterns)} patterns")

    # Save patterns
    if patterns:
        saved = detector.save_patterns(patterns)
        print(f"[OK] Saved {saved} patterns to database")

    # Get promotion candidates
    candidates = detector.get_promotion_candidates()
    print(f"[INFO] {len(candidates)} patterns ready for promotion")

    return len(patterns), len(candidates)


def run_conflict_analysis():
    """Run conflict detection."""
    print("\n" + "=" * 60)
    print("CONFLICT ANALYSIS")
    print("=" * 60)

    detector = ConflictDetector()

    # Scan workspace
    print("[INFO] Scanning workspace for rule conflicts...")
    results = detector.scan_workspace()

    print(f"[INFO] Scanned {results['files_scanned']} files")
    print(f"[INFO] Found {results['conflicts_found']} conflicts")
    print(f"[INFO] Files with conflicts: {len(results['files_with_conflicts'])}")

    return results['conflicts_found']


def run_transfer_analysis():
    """Run cross-project transfer analysis."""
    print("\n" + "=" * 60)
    print("CROSS-PROJECT TRANSFER ANALYSIS")
    print("=" * 60)

    transfer = PatternTransfer()

    # Find transfer candidates
    candidates = transfer.find_transfer_candidates(
        min_occurrences=3,
        success_threshold=0.8
    )

    print(f"[INFO] Found {len(candidates)} patterns ready for transfer")

    # Get proven transfers
    proven = transfer.get_successful_transfers()
    print(f"[INFO] {len(proven)} proven patterns available for reuse")

    return len(candidates), len(proven)


def run_ab_test_analysis():
    """Run A/B test status check."""
    print("\n" + "=" * 60)
    print("A/B TEST STATUS")
    print("=" * 60)

    ab_test = ABTestFramework()

    # Note: This would need to be integrated with actual A/B tests
    # For now, we just report that the framework is ready
    print("[INFO] A/B testing framework initialized")
    print("[INFO] No active experiments")
    print("[INFO] Run 'python tools/run_ab_test.py' to create experiments")

    return 0


def generate_comprehensive_report():
    """Generate a comprehensive analysis report."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE ANALYSIS REPORT")
    print("=" * 60)

    import sqlite3

    DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Overall stats
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_decisions,
            AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
            COUNT(DISTINCT project_path) as projects
        FROM decisions
    """)
    stats = dict(cursor.fetchone())

    # Pattern stats
    cursor.execute("""
        SELECT COUNT(*) as total_patterns,
               SUM(CASE WHEN promoted = 1 THEN 1 ELSE 0 END) as promoted_patterns
        FROM pattern_instances
    """)
    pattern_stats = dict(cursor.fetchone())

    # Rule promotion stats
    cursor.execute("""
        SELECT COUNT(*) as total_proposals,
               SUM(CASE WHEN status = 'deployed' THEN 1 ELSE 0 END) as deployed_rules
        FROM rule_promotions
    """)
    promotion_stats = dict(cursor.fetchone())

    # Conflict stats
    cursor.execute("""
        SELECT COUNT(*) as active_conflicts
        FROM rule_conflicts
        WHERE status = 'detected'
    """)
    conflict_stats = dict(cursor.fetchone())

    # Transfer stats
    cursor.execute("""
        SELECT COUNT(*) as total_transfers,
               SUM(CASE WHEN status = 'proven' THEN 1 ELSE 0 END) as proven_transfers
        FROM knowledge_transfers
    """)
    transfer_stats = dict(cursor.fetchone())

    conn.close()

    # Generate report
    report = []
    report.append("")
    report.append("OVERALL STATISTICS")
    report.append("-" * 40)
    report.append(f"Total Decisions: {stats['total_decisions']}")
    report.append(f"Success Rate: {stats['success_rate']:.1%}")
    report.append(f"Projects Tracked: {stats['projects']}")
    report.append("")

    report.append("PATTERNS")
    report.append("-" * 40)
    report.append(f"Total Patterns: {pattern_stats['total_patterns'] or 0}")
    report.append(f"Promoted Patterns: {pattern_stats['promoted_patterns'] or 0}")
    report.append("")

    report.append("RULES")
    report.append("-" * 40)
    report.append(f"Total Proposals: {promotion_stats['total_proposals'] or 0}")
    report.append(f"Deployed Rules: {promotion_stats['deployed_rules'] or 0}")
    report.append("")

    report.append("CONFLICTS")
    report.append("-" * 40)
    report.append(f"Active Conflicts: {conflict_stats['active_conflicts']}")
    report.append("")

    report.append("KNOWLEDGE TRANSFERS")
    report.append("-" * 40)
    report.append(f"Total Transfers: {transfer_stats['total_transfers'] or 0}")
    report.append(f"Proven Transfers: {transfer_stats['proven_transfers'] or 0}")
    report.append("")

    report.append("=" * 60)

    return "\n".join(report)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run comprehensive analysis')
    parser.add_argument('--patterns', action='store_true',
                        help='Run pattern analysis only')
    parser.add_argument('--conflicts', action='store_true',
                        help='Run conflict analysis only')
    parser.add_argument('--transfers', action='store_true',
                        help='Run transfer analysis only')
    parser.add_argument('--report-only', action='store_true',
                        help='Only generate report without running analysis')

    args = parser.parse_args()

    if args.report_only:
        print(generate_comprehensive_report())
        return

    if args.patterns or args.conflicts or args.transfers:
        # Run selected analyses
        if args.patterns:
            run_pattern_analysis()
        if args.conflicts:
            run_conflict_analysis()
        if args.transfers:
            run_transfer_analysis()
    else:
        # Run all analyses
        run_pattern_analysis()
        run_conflict_analysis()
        run_transfer_analysis()
        run_ab_test_analysis()

        # Generate comprehensive report
        print("\n")
        print(generate_comprehensive_report())


if __name__ == "__main__":
    main()
