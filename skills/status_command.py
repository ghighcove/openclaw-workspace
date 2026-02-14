# Status Check Command - OpenClaw Native Skill

**Author:** Billy Byte (OpenClaw)
**Version:** 1.0.0
**Category:** Monitoring / System Check
**Trigger:** User sends `/status` in Telegram
**Priority:** High

---

## Overview

This skill provides a comprehensive status check across all major systems:
- Trading Bot Status (ACTIVE/PAUSED, positions, P&L, risk metrics)
- Project Dashboard Health (scan results, issues found, project counts)
- LinkedIn Metrics (profile views, search appearances, recruiter engagement)
- Overall System Status (critical issues, maintenance mode, operational status)

---

## Implementation

### Function: `execute()`

**Parameters:**
- `message_data`: OpenClaw message data (chat context, user ID)
- `config`: OpenClaw configuration

**Returns:**
- Formatted markdown report with system status
- Error handling for missing integrations

---

## System Checks

### Trading Bot Status
**File to Check:** `G:\ai\trading_bot\src\trading_bot.py` (placeholder)
**What to Check:**
- Does trading bot script exist?
- Is bot process running?
- What's current status (ACTIVE/PAUSED)?
- Current positions count?
- Current P&L (profit/loss)?
- Current risk level (LOW/MEDIUM/HIGH)?

**Fallback Behavior:**
- If script doesn't exist: Return "Not Configured - See System Admin"
- If process not running: Return "Status Unknown - Check Trading Bot Service"

**Output Example:**
```
🤖 Trading Bot

Status: ACTIVE
• Positions: 3
• P&L: +$1,245.30 (session), -$15.67 (total)
• Risk Level: MEDIUM
• Last Trade: 2026-02-14 11:30 AM PST

📊 Performance Today
• Trades Executed: 127
• Win Rate: 68.3%
• Average Win per Trade: +$12.75

⚠️ Alerts
• Drawdown Threshold: 15% (current drawdown)
• Risk Level Increased: LOW → MEDIUM
```

### Project Dashboard Status
**File to Check:** `G:\ai\project-dashboard\scripts\dashboard.py`
**What to Check:**
- Is dashboard script accessible?
- When was last scan run?
- How many projects monitored?
- Health score distribution (healthy/needs attention/stale)?

**Output Example:**
```
📈 Project Dashboard

Last Scan: 2026-02-14 10:15 AM PST
Projects Monitored: 21

Health Distribution:
• Healthy: 15 (71.4%)
• Needs Attention: 5 (23.8%)
• Stale: 1 (4.8%)

⚠️ Issues Found: 3
• NFL Spread2: No commits in 7 days
• Science Project Template: Missing CLAUDE.md
• OpenClaw: Uncommitted changes in workspace

Critical Issues: 0
```

### LinkedIn Metrics
**File to Check:** `G:\ai\linkedin\src\linkedin_metrics.py` (placeholder)
**What to Check:**
- Does LinkedIn scraper exist?
- When was last data update?
- What's current profile view count?
- Weekly view trends?
- Recruiter engagement (VP connections, Director messages)?

**Output Example:**
```
👔 LinkedIn Profile

Last Updated: 2026-02-13 08:00 AM PST

Metrics (Current Week: Feb 08-14):
• Profile Views: 142 (week total)
• Search Appearances: 28
• Recruiter Messages: 3
  – 1 VP connection request (ACCEPTED)
  – 1 Director message (REJECTED)
  – 1 Director profile view (VIEWED)

Weekly Trend (vs previous week):
• Views: +12 (↑ 9.2%)
• Search Appearances: +5 (↑ 21.7%)
• Recruiter Engagement: +2 (↑ 50%)

Engagement Level: MEDIUM-HIGH

⚠️ Data Freshness: 48 hours old (acceptable)
```

---

## Format

**Response Template:**

```
📊 SYSTEM STATUS REPORT
🤖 Trading Bot
[status and metrics]

📈 Project Dashboard
[scan results and issues]

👔 LinkedIn Metrics
[profile views and engagement]

📋 Overall System
[critical issues and status]

---
Generated at: 2026-02-14 12:12 PM PST
```

---

## Error Handling

### Missing Integration

**Scenario:** Integration file doesn't exist (e.g., `trading_bot.py` not found)

**Action:**
- Return graceful status: "Not Currently Configured - See System Admin"
- Add recommendation to enable integration
- Don't fail entire command

**Scenario:** All integration files missing

**Action:**
- Provide comprehensive system status
- List all available systems (Trading Bot, Dashboard, LinkedIn)
- Offer to set up integrations

---

## Notes

- This skill is designed to be called by OpenClaw's native `/status` command
- Integrations should be added to OpenClaw configuration when systems are ready
- Status is cached for 5 minutes to reduce system load
- Markdown formatting uses OpenClaw's message formatting standards

---

## Future Enhancements

1. **Real-time status updates** — Connect to actual APIs for live data
2. **Alert thresholds** — Send alerts when metrics cross critical thresholds
3. **Trend analysis** — Compare current status with historical data
4. **Multi-system correlation** — Identify patterns across trading bot, dashboard, LinkedIn