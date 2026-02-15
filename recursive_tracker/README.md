# Billy Byte's Recursive Improvement Tracker

Billy Byte's personal learning and decision tracking system. Tracks decisions, detects patterns, and automatically promotes proven approaches to improve performance over time.

## What This Does

This system:
- Logs Billy's decisions during development sessions
- Records outcomes (success/failure/user correction)
- Detects patterns in successful vs failed approaches
- Promotes proven patterns to CLAUDE.md/AGENTS.md
- Generates visual dashboards for performance tracking

## Quick Start

```bash
# Initialize database
python tools/init_database.py

# Test integration
python tools/test_tracker.py

# Scrape existing lessons
python tools/scrape_lessons.py

# Generate dashboard
python tools/generate_dashboard.py
```

## Usage in Code

```python
from lib.billy_tracker import BillyTracker

tracker = BillyTracker()

# Log a decision
decision_id = tracker.log_decision(
    decision_type='file_modification',
    action_taken='Updated HTML tables in article',
    rule_source='global_claude_md',
    rule_text='Always verify after file modifications'
)

# Record outcome
tracker.record_outcome(
    decision_id=decision_id,
    outcome='success',
    evidence='Read file, verified tables render correctly',
    time_elapsed=45
)

# Get statistics
stats = tracker.get_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
```

## Database

- **Location:** `data/billy_feedback.db`
- **Format:** SQLite
- **Schema:** `data/schema.sql`

## Project Structure

```
recursive_tracker/
├── CLAUDE.md              # Project context and instructions
├── README.md              # This file
├── VERSION                # Version tracking
├── data/
│   ├── billy_feedback.db  # SQLite database (created by init)
│   └── schema.sql         # Database schema
├── lib/
│   └── billy_tracker.py   # Core tracking library
├── tools/
│   ├── init_database.py   # Initialize database
│   ├── test_tracker.py    # Test integration
│   ├── scrape_lessons.py  # Scrape existing lessons
│   └── generate_dashboard.py  # Generate HTML dashboard
└── docs/
    └── DESIGN.md          # Design decisions and architecture
```

## Version

Current: **0.3.0** (Complete with Automated Scheduling)

## Status

**PRODUCTION READY** - Running automatically with progressive scheduling:
- First few days: Every 2 hours
- After 1 week: Every day
- After 30 days: Calibrated based on data

## Automated Scheduling

The system runs automatically via cron job. See `IMPLEMENTATION_GUIDE.md` for details.

## License

Internal tool for Billy Byte's personal development.
