# Billy's Recursive Improvement Tracker - Implementation Guide

**Date:** February 14, 2026
**Status:** ✅ FULLY IMPLEMENTED WITH AUTOMATED SCHEDULING

---

## Overview

Billy Byte's Recursive Improvement Tracker is now **fully automated** with progressive scheduling:
- **First few days:** Analysis runs every 2 hours
- **After 1 week:** Analysis runs every day (24 hours)
- **After 30 days:** Calibrated based on data volume (12-72 hours)

---

## Implementation Summary

### Components Added

1. **Schedule Manager** (`lib/schedule_manager.py`)
   - Tracks system age
   - Manages progressive phases (initial → weekly → calibrated)
   - Calculates optimal intervals based on data
   - 8,410 bytes of code

2. **Scheduled Analysis Runner** (`tools/run_scheduled_analysis.py`)
   - Checks if analysis is due
   - Runs comprehensive analysis when scheduled
   - Updates dashboard automatically
   - Records analysis completion
   - 1,979 bytes of code

3. **Cron Job** (`billy_recursive_tracker_analysis`)
   - Runs every 2 hours
   - Delegates to scheduled_analysis.py for smart scheduling
   - Announces results to Telegram
   - ID: `35ecc764-e7d1-48f9-997e-466d1a7579be`

### Schedule State File

**Location:** `G:/z.ai/workspace/recursive_tracker/schedule_state.json`

Tracks:
- `start_date` - When the system was first initialized
- `last_analysis` - Timestamp of last analysis run
- `phase` - Current phase (initial, weekly, calibrated)
- `analysis_count` - Total number of analyses run
- `phases` - Details of each phase

---

## Progressive Schedule Details

### Phase 1: Initial (First 7 Days)
- **Interval:** Every 2 hours
- **Total Runs:** ~84 analyses (168 hours / 2)
- **Description:** "First few days - every 2 hours"
- **Purpose:** Rapid pattern detection during early learning

**Transition to Phase 2:** After 168 hours (7 days)

### Phase 2: Weekly (Days 8-30)
- **Interval:** Every 24 hours (daily)
- **Total Runs:** ~23 analyses (672 hours - 168 hours) / 24
- **Description:** "After first week - every day"
- **Purpose:** Regular daily analysis with sufficient data

**Transition to Phase 3:** After 720 hours (30 days)

### Phase 3: Calibrated (Day 30+)
- **Interval:** Dynamic, based on data volume
  - 0-50 decisions: Every 12 hours
  - 50-100 decisions: Every 24 hours
  - 100-200 decisions: Every 48 hours
  - 200+ decisions: Every 72 hours
- **Description:** "Based on data volume and patterns"
- **Purpose:** Optimal frequency based on learning rate

---

## How It Works

### Cron Job Flow

```
Every 2 hours (cron triggers)
    ↓
run_scheduled_analysis.py runs
    ↓
ScheduleManager checks if analysis is due
    ↓
If due:
    - Run pattern analysis
    - Run conflict analysis
    - Run transfer analysis
    - Run A/B test status check
    - Generate comprehensive report
    - Update dashboard
    - Record analysis completion
    ↓
If not due:
    - Skip analysis
    - Wait for next scheduled run
```

### Schedule State Management

```python
from lib.schedule_manager import ScheduleManager

manager = ScheduleManager()

# Check if analysis should run
should_run, status = manager.check_schedule()

if should_run:
    # Run analysis
    python tools/run_analysis.py
    python tools/generate_dashboard.py

    # Record completion
    manager.record_analysis()
```

---

## Usage

### Check Schedule Status

```bash
cd G:/z.ai/workspace/recursive_tracker
python -c "from lib.schedule_manager import ScheduleManager; print(ScheduleManager().get_status())"
```

**Example Output:**
```
System Age: 0.0 days (0 hours)
Current Phase: Initial
Interval: Every 2 hours
Analysis Count: 1
Status: Wait 2.0 hours (last 0.0 hours ago)

First few days - every 2 hours
```

### Force Analysis Run

To run analysis immediately (ignoring schedule):

```bash
cd G:/z.ai/workspace/recursive_tracker
python tools/run_analysis.py
python tools/generate_dashboard.py
```

### Reset Schedule

To reset the schedule (start fresh):

```bash
rm G:/z.ai/workspace/recursive_tracker/schedule_state.json
# Next run will reinitialize
```

---

## Cron Job Details

### Job Configuration

```json
{
  "id": "35ecc764-e7d1-48f9-997e-466d1a7579be",
  "name": "billy_recursive_tracker_analysis",
  "enabled": true,
  "schedule": {
    "kind": "every",
    "everyMs": 7200000  // 2 hours in milliseconds
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "cd G:/z.ai/workspace/recursive_tracker && python tools/run_scheduled_analysis.py",
    "model": "zai/glm-4.7",
    "thinking": "low",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram"
  }
}
```

### Next Scheduled Run

The cron job runs every 2 hours, but the scheduled_analysis.py script checks if the analysis interval has elapsed. This means:

- **Cron triggers:** Every 2 hours (7,200,000 ms)
- **Actual analysis:** Runs only when interval has elapsed (2 hours / 24 hours / calibrated)

### Managing the Cron Job

**List cron jobs:**
```bash
openclaw cron list
```

**View job details:**
```bash
openclaw cron list | grep billy_recursive_tracker_analysis
```

**Disable job temporarily:**
```bash
openclaw cron remove billy_recursive_tracker_analysis
# Re-enable with same command used to create it
```

---

## Monitoring

### What You'll See on Telegram

When the analysis runs and completes, you'll receive an announcement with:
- Schedule status (current phase, interval, analysis count)
- Pattern analysis results
- Conflict analysis results
- Cross-project transfer status
- A/B test status
- Comprehensive report
- Dashboard update confirmation

**Example Announcement:**
```
============================================================
Billy's Recursive Improvement Tracker - Scheduled Analysis
============================================================

[OK] Analysis complete - recorded to schedule

OVERALL STATISTICS
----------------------------------------
Total Decisions: 17
Success Rate: 94.1%
...

Dashboard updated: dashboard.html
```

### Checking Locally

To see what the scheduler will do without running:

```bash
cd G:/z.ai/workspace/recursive_tracker
python -c "from lib.schedule_manager import ScheduleManager; should, status = ScheduleManager().check_schedule(); print(f'Should run: {should}\n\n{status}')"
```

---

## Calibration Algorithm

The calibrated phase interval is calculated based on the volume of decisions:

```python
def _calculate_optimal_interval(self):
    stats = tracker.get_global_stats()
    total_decisions = stats['total_decisions']

    if total_decisions < 50:
        return 12   # Every 12 hours (2x/day)
    elif total_decisions < 100:
        return 24   # Every 24 hours (1x/day)
    elif total_decisions < 200:
        return 48   # Every 48 hours (1x/2 days)
    else:
        return 72   # Every 72 hours (1x/3 days)
```

**Rationale:**
- Low data volume → Frequent analysis (more learning opportunities)
- High data volume → Less frequent analysis (patterns stabilize)
- Balances learning rate with computational cost

---

## Expected Timeline

### Week 1 (Days 1-7)
- **Runs:** ~84 analyses (every 2 hours)
- **Purpose:** Rapid learning from initial decisions
- **Transition:** To Phase 2 after 168 hours

### Weeks 2-4 (Days 8-30)
- **Runs:** ~23 analyses (every 24 hours)
- **Purpose:** Daily analysis with growing data
- **Transition:** To Phase 3 after 720 hours

### Week 5+ (Days 31+)
- **Runs:** Varies based on data (every 12-72 hours)
- **Purpose:** Optimized frequency based on learning rate
- **Adjustment:** Interval recalculates each run

---

## Manual Override

If you need to run analysis immediately:

```bash
cd G:/z.ai/workspace/recursive_tracker
python tools/run_analysis.py
python tools/generate_dashboard.py
```

This does NOT update the schedule state, so the next scheduled run will still happen as planned.

To reset the timer and run immediately:

```bash
cd G:/z.ai/workspace/recursive_tracker
python -c "from lib.schedule_manager import ScheduleManager; manager = ScheduleManager(); manager.record_analysis(); print('Schedule reset')"
python tools/run_analysis.py
python tools/generate_dashboard.py
```

---

## Troubleshooting

### Analysis Not Running

**Check 1:** Is the cron job enabled?
```bash
openclaw cron list
```

**Check 2:** Check schedule state
```bash
cat G:/z.ai/workspace/recursive_tracker/schedule_state.json
```

**Check 3:** Verify script runs manually
```bash
cd G:/z.ai/workspace/recursive_tracker
python tools/run_scheduled_analysis.py
```

### Phase Not Transitioning

The phase transitions automatically based on system age. To force a transition (for testing):

```python
from lib.schedule_manager import ScheduleManager
manager = ScheduleManager()
state = manager.load_state()
state['start_date'] = '2026-01-01T00:00:00'  # 44 days ago
manager.save_state(state)
print('System age reset for testing')
```

**⚠️ Warning:** Only use this for testing! It will reset your timeline.

---

## Files Added/Modified

### New Files
- `lib/schedule_manager.py` (8,410 bytes)
- `tools/run_scheduled_analysis.py` (1,979 bytes)
- `IMPLEMENTATION_GUIDE.md` (this file)

### Cron Job
- `billy_recursive_tracker_analysis` (ID: 35ecc764-e7d1-48f9-997e-466d1a7579be)

### State File (Created on First Run)
- `schedule_state.json` (JSON schedule state)

---

## Summary

✅ **Fully implemented with automated scheduling**
✅ **Progressive intervals: 2h → 24h → calibrated**
✅ **Cron job running every 2 hours**
✅ **Smart scheduling checks interval before running**
✅ **Telegram announcements for analysis results**
✅ **Automatic dashboard updates**
✅ **Phase transitions automatic after 7 days and 30 days**
✅ **Calibration based on data volume**

**Status:** PRODUCTION READY ✅

**Next Scheduled Analysis:** In approximately 2 hours (at ~19:46 PST on Feb 14, 2026)

---

**Version:** 0.3.0
**Last Updated:** February 14, 2026
**Implementation Time:** ~30 minutes
