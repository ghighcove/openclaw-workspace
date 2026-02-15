"""
Schedule Manager - Manages progressive analysis intervals.

Tracks system age and adjusts analysis frequency:
- First few days: Every 2 hours
- After a week: Every day
- After that: Re-calibrate based on data volume
"""

import json
from datetime import datetime
from pathlib import Path


class ScheduleManager:
    """Manages progressive scheduling for analysis."""

    def __init__(self, workspace_path: Path = None):
        """Initialize schedule manager."""
        if workspace_path is None:
            workspace_path = Path(__file__).parent.parent.parent

        self.workspace_path = workspace_path
        self.state_file = self.workspace_path / "recursive_tracker" / "schedule_state.json"

    def load_state(self) -> dict:
        """Load schedule state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Initialize new state
            return self._init_state()

    def save_state(self, state: dict) -> None:
        """Save schedule state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, default=str)

    def _init_state(self) -> dict:
        """Initialize new schedule state."""
        now = datetime.now()

        state = {
            'start_date': now.isoformat(),
            'last_analysis': None,
            'phase': 'initial',  # 'initial', 'weekly', 'calibrated'
            'analysis_count': 0,
            'phases': {
                'initial': {
                    'name': 'Initial',
                    'start': now.isoformat(),
                    'end': None,
                    'interval_hours': 2,
                    'description': 'First few days - every 2 hours'
                },
                'weekly': {
                    'name': 'Weekly',
                    'start': None,
                    'end': None,
                    'interval_hours': 24,
                    'description': 'After first week - every day'
                },
                'calibrated': {
                    'name': 'Calibrated',
                    'start': None,
                    'end': None,
                    'interval_hours': None,  # Will be calculated
                    'description': 'Based on data volume and patterns'
                }
            }
        }

        self.save_state(state)
        return state

    def get_system_age_hours(self) -> float:
        """Get system age in hours."""
        state = self.load_state()
        start = datetime.fromisoformat(state['start_date'])
        now = datetime.now()
        return (now - start).total_seconds() / 3600

    def get_current_phase(self) -> dict:
        """Get current phase information."""
        state = self.load_state()
        phase_name = state['phase']
        return state['phases'][phase_name]

    def update_phase_if_needed(self) -> bool:
        """
        Check if we need to move to next phase.

        Returns:
            True if phase changed, False otherwise
        """
        state = self.load_state()
        current_phase = state['phase']

        age_hours = self.get_system_age_hours()

        # Check if we need to move from initial to weekly
        if current_phase == 'initial' and age_hours >= 168:  # 7 days = 168 hours
            # Move to weekly phase
            now = datetime.now().isoformat()

            state['phases']['initial']['end'] = now
            state['phases']['weekly']['start'] = now
            state['phase'] = 'weekly'

            self.save_state(state)
            return True

        # Check if we need to calibrate (after 30 days)
        if current_phase == 'weekly' and age_hours >= 720:  # 30 days = 720 hours
            # Calculate optimal interval based on data
            optimal_hours = self._calculate_optimal_interval()

            now = datetime.now().isoformat()

            state['phases']['weekly']['end'] = now
            state['phases']['calibrated']['start'] = now
            state['phases']['calibrated']['interval_hours'] = optimal_hours
            state['phase'] = 'calibrated'

            self.save_state(state)
            return True

        return False

    def _calculate_optimal_interval(self) -> int:
        """
        Calculate optimal analysis interval based on data.

        Returns:
            Interval in hours
        """
        # Import here to avoid circular dependency
        import sys
        sys.path.insert(0, str(self.workspace_path / "recursive_tracker" / "lib"))
        from billy_tracker import BillyTracker

        try:
            tracker = BillyTracker()
            stats = tracker.get_global_stats()

            total_decisions = stats['total_decisions']

            # Heuristic: More decisions = longer interval
            # 0-50 decisions: every 12 hours
            # 50-100 decisions: every 24 hours
            # 100-200 decisions: every 48 hours
            # 200+ decisions: every 72 hours

            if total_decisions < 50:
                return 12
            elif total_decisions < 100:
                return 24
            elif total_decisions < 200:
                return 48
            else:
                return 72

        except Exception:
            # Default if tracker fails
            return 24

    def should_run_analysis(self) -> bool:
        """
        Check if analysis should run based on schedule.

        Returns:
            True if analysis should run, False otherwise
        """
        state = self.load_state()
        last_analysis = state.get('last_analysis')

        if not last_analysis:
            # Never run, so run now
            return True

        # Check for phase change
        phase_changed = self.update_phase_if_needed()

        # If phase just changed, run analysis
        if phase_changed:
            return True

        # Get current phase interval
        phase = self.get_current_phase()
        interval_hours = phase['interval_hours']

        if not interval_hours:
            # Shouldn't happen, but handle gracefully
            return True

        # Calculate hours since last analysis
        last = datetime.fromisoformat(last_analysis)
        now = datetime.now()
        hours_since = (now - last).total_seconds() / 3600

        return hours_since >= interval_hours

    def record_analysis(self) -> None:
        """Record that analysis was run."""
        state = self.load_state()
        state['last_analysis'] = datetime.now().isoformat()
        state['analysis_count'] += 1
        self.save_state(state)

    def get_status(self) -> str:
        """Get human-readable status."""
        state = self.load_state()
        phase = self.get_current_phase()
        age_hours = self.get_system_age_hours()
        age_days = age_hours / 24

        last_analysis = state.get('last_analysis')
        if last_analysis:
            last = datetime.fromisoformat(last_analysis)
            hours_since = (datetime.now() - last).total_seconds() / 3600
        else:
            hours_since = None

        status = []
        status.append(f"System Age: {age_days:.1f} days ({age_hours:.0f} hours)")
        status.append(f"Current Phase: {phase['name']}")
        status.append(f"Interval: Every {phase['interval_hours']} hours")
        status.append(f"Analysis Count: {state['analysis_count']}")

        if hours_since is not None:
            if hours_since >= phase['interval_hours']:
                status.append(f"Status: READY (last analysis {hours_since:.1f} hours ago)")
            else:
                hours_until = phase['interval_hours'] - hours_since
                status.append(f"Status: Wait {hours_until:.1f} hours (last {hours_since:.1f} hours ago)")
        else:
            status.append("Status: Never run")

        status.append(f"\n{phase['description']}")

        return "\n".join(status)


# Convenience function for quick usage
def check_schedule():
    """Check if analysis should run."""
    manager = ScheduleManager()
    should_run = manager.should_run_analysis()
    status = manager.get_status()

    return should_run, status


def record_analysis():
    """Record that analysis was run."""
    manager = ScheduleManager()
    manager.record_analysis()
