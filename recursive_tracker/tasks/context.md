# Context - Recursive Improvement Tracker

## TLDR

Billy Byte's personal learning and decision tracking system. Logs decisions, records outcomes, detects patterns, and promotes proven approaches to improve performance over time.

## Status

**PRODUCTION READY** - Fully automated with progressive scheduling (2h → 24h → calibrated). Current version: 0.3.0

## Key Metrics

- **Decisions Tracked:** 17
- **Success Rate:** 94.1%
- **Patterns Detected:** 1
- **Tests Passing:** 11/11 (7 Phase 1 + 4 Phase 2)

## What This Does

1. **Decision Tracking** - Logs Billy's decisions during development sessions
2. **Outcome Recording** - Records success/failure/user correction for each decision
3. **Pattern Detection** - Detects patterns in successful vs failed approaches
4. **Rule Promotion** - Promotes proven patterns to CLAUDE.md/AGENTS.md
5. **Dashboard Generation** - Visual dashboards for performance tracking

## Quick Commands

```bash
# Initialize database
python tools/init_database.py

# Run scheduled analysis
python tools/run_scheduled_analysis.py

# Generate dashboard
python tools/generate_dashboard.py

# Test integration
python tools/test_tracker.py
```

## Location

`G:/z.ai/workspace/recursive_tracker/`

## Up Next

- Monitor automated scheduling performance
- Analyze accumulated decision patterns
- A/B test promoted rules for effectiveness
- Calibrate schedule based on data after 30 days
