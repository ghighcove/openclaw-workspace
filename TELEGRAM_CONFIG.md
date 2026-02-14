# Telegram Configuration

**Setup Date:** 2026-02-14
**Bot:** @opnclwbt76bot
**Chat ID:** 7129842067

## Preferences

### Schedule
- **Weekdays:** Morning briefing at 7:45 AM
- **Weekends:** When user wakes (adapt to pattern)
- **Immediate alerts:** As they occur

### Immediate Alerts (One-Liners)

Send immediately via Telegram:
- ❌ **System failures:** Project failures, data pipelines down, git conflicts
- 📊 **Trading bot:** Errors, anomalies, stop losses, rejections
- 📝 **Session context:** What we were working on last
- ✅ **Urgent to-dos:** Items needing immediate attention
- 📰 **Articles:** Ready to publish (from article-publisher)
- 🌙 **Overnight work:** Completed projects and summaries
- 💡 **Relevant findings:** Job postings, research results, project insights

### Formatting

- **Default:** Concise one-liners
- **On request:** Detailed reports when user asks

### Message Categories

**Alerts (Immediate):**
- Critical failures
- Trading bot issues
- Recruiter messages
- High-priority whiteboard tickets

**Briefings (Scheduled):**
- Morning: Overnight summary, priorities, what was last worked on
- Evening: Work completed, overnight queue ready

**Updates (As available):**
- Research findings
- New whiteboard tickets
- Dashboard status changes
- LinkedIn metrics updates

## Example Messages

**Immediate Alert:**
```
📊 Trading bot: Stop loss triggered on TSLA @ 212.50
```

**Morning Briefing:**
```
🌅 Good morning! Overnight work complete:

✅ NFL data processed (2 games updated)
✅ Article published: "NFL Spread Inefficiencies" on Medium
✅ Trading bot performance: +2.3% yesterday
📋 3 items need attention (see dashboard)

Today's focus: LinkedIn Phase 2 or NFL analysis?
```

**Session Context:**
```
📝 Last working on: NFL article draft (section 3 of 5)
Next up: Add betting strategy examples
```

## Configuration Commands

**To send message:**
```bash
message --action send --channel telegram --to 7129842067 --message "Your message here"
```

**To configure (already done):**
```bash
openclaw configure --section telegram
```

## Usage Notes

- User can message bot @opnclwbt76bot, messages appear in main session
- Alerts are concise, details available on request
- Morning briefings help user start day with clear priorities
- Overnight work is summarized for quick review
