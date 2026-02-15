#!/usr/bin/env python3
"""
Scheduled Analysis Runner - Runs analysis according to progressive schedule.

This script is called by cron every 2 hours but only actually runs
analysis when the schedule manager indicates it's time.

Progressive schedule:
- First few days: Every 2 hours
- After first week: Every day
- After 30 days: Calibrated based on data volume
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from schedule_manager import ScheduleManager


def main():
    """Main entry point."""
    print("=" * 60)
    print("Billy's Recursive Improvement Tracker - Scheduled Analysis")
    print("=" * 60)

    manager = ScheduleManager()

    # Check current status
    print("\n[SCHEDULE STATUS]")
    status = manager.get_status()
    print(status)

    # Check if we should run analysis
    print("\n[CHECKING SCHEDULE]")
    should_run = manager.should_run_analysis()

    if should_run:
        print("[INFO] Analysis is due - running now...\n")

        # Run the analysis using subprocess
        import subprocess

        print("[RUNNING ANALYSIS]")
        result = subprocess.run(
            [sys.executable, "tools/run_analysis.py"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("[ERROR]", result.stderr, file=sys.stderr)

        # Generate dashboard
        print("\n[UPDATING DASHBOARD]")
        result = subprocess.run(
            [sys.executable, "tools/generate_dashboard.py"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("[ERROR]", result.stderr, file=sys.stderr)

        # Record that we ran analysis
        manager.record_analysis()

        print("\n[OK] Analysis complete - recorded to schedule")

    else:
        print("\n[INFO] Analysis not due yet - skipping")
        print("[INFO] Next analysis will be scheduled automatically")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
