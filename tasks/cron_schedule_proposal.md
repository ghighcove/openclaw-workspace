# Cron Schedule Proposal - Proactive Monitoring

**Purpose:** Automated monitoring and work execution when Glenn is away from computer

---

## PROPOSED SCHEDULED TASKS

### 1. Trading Bot Health Check
**Schedule:** Every 2 hours
**Task:** Check trading bot status, detect anomalies
**Action on error:** Send Telegram alert immediately

### 2. Project Dashboard Scan
**Schedule:** Every 4 hours
**Task:** Scan 21 projects for health changes
**Action on issue:** Send Telegram alert with project name + issue

### 3. LinkedIn Metrics Check
**Schedule:** Daily at 6:00 AM
**Task:** Check profile views, search appearances, recruiter messages
**Action on change:** Send Telegram with delta from previous day

### 4. NFL Data Pipeline Check
**Schedule:** Daily at 3:00 AM
**Task:** Verify data pipeline ran successfully
**Action on failure:** Send Telegram alert

### 5. Whiteboard Ticket Scan
**Schedule:** Every 1 hour
**Task:** Check C:\ai\whiteboard for new high-priority tickets
**Action on new ticket:** Execute immediately if critical priority

---

## IMPLEMENTATION NOTES

**Cron tool available:** Yes (via `cron` command)
**Telegram alerts:** Already configured (bot connected, preferences set)

**Required setup:**
1. Define cron schedules for each task
2. Create error-detection logic for alerts
3. Test before activating

---

## PRE-DEPARTURE CHECKLIST

**Before Glenn goes out and is about his computer:**

1. **Review current state:**
   - Trading bot status
   - Projects in progress
   - Urgent tasks

2. **Create contingency whiteboard tickets:**
   - "If [condition], then [action]"
   - Examples: "If trading bot has 3 losses, pause", "If LinkedIn recruiter messages > 5, send summary"

3. **Set cron schedules active:**
   - Confirm all scheduled tasks running
   - Verify Telegram alerts configured

4. **Return checkpoint:**
   - Check this webchat for any sub-agent messages
   - Review cron job logs/summaries

---

**This gives Glenn intervention capability even when away.**

*Created: February 14, 2026*
*Status: Proposal - await Glenn's approval*
