# Simple Telegram Bot - Quick Start Guide

**Version:** 1.0.0
**Date:** February 14, 2026

---

## 🚀 READY TO TEST!

### Current State
- ✅ Bot code created: `G:\z.ai\workspace\bot\simple_telegram_bot.py`
- ✅ Command queue created: `G:\z.ai\workspace\commands_queue.json`
- ✅ Documentation created: `G:\z.ai\workspace\bot\README.md`
- ✅ Global CLAUDE.md updated with 12 new rules

---

## 📋 SETUP CHECKLIST

### Required (5 minutes)
- [ ] Set `TELEGRAM_BOT_TOKEN` environment variable
- [ ] Verify bot token is correct (from @BotFather)
- [ ] Run bot locally to test connection
- [ ] Send `/help` command to verify responses
- [ ] Check that bot is polling correctly

### Optional (For Production Deployment)
- [ ] Set up Task Scheduler (Windows) for background running
- [ ] Configure startup trigger (at system boot or specific time)
- [ ] Set up logging to file for debugging
- [ ] Configure restart-on-failure mechanism

---

## 🚀 QUICK TEST COMMANDS

### Step 1: Interactive Test (Now)
```bash
# Run bot in terminal (you can see all output)
cd G:\z.ai\workspace
python bot/simple_telegram_bot.py
```

**Expected Output:**
```
[START] Simple Telegram Bot starting...
[CONFIG] Polling every 15 seconds
[CONFIG] Chat ID: 7129842067
[CONFIG] Queue file: G:\z.ai\workspace\commands_queue.json
[CONFIG] Telegram Bot Token: [your-token-hidden]
[IDLE] Waiting 15 seconds before next poll...
```

**To Stop:** Press `Ctrl+C` in terminal

---

### Step 2: Test Help Command (After Bot Starts)
Once bot starts, send this in Telegram:
```
/help
```

**Expected Response:**
Bot will send back:
```
🤖 Simple Telegram Bot - Available Commands

📊 Monitoring Commands:
• /status - Overall system status
• /dashboard_scan - Scan all projects
• /linkedin_metrics - LinkedIn profile metrics

🤖 Trading Bot Commands:
• /tradingbot_pause - Pause trading bot
• /tradingbot_resume - Resume operations
• /tradingbot_status - Detailed status

📈 Reporting Commands:
• /overnight_report - Generate overnight work summary

❓ System Commands:
• /help - Show this message

Usage:
1. Send a command to this bot
2. Bot executes it and sends back result
3. Commands are processed in order received
```

---

## 🎯 TEST SCENARIOS

### Scenario 1: Status Check
**Command:** `/status`

**Expected Result:**
```
✅ CMD_001: status

Overall Status:
• Trading Bot: ACTIVE (Positions: 3, P&L: $12,345, Risk: LOW)
• Project Dashboard: HEALTHY (21 projects scanned)
• LinkedIn Metrics: VIEWS: 142 (Week), APPEARANCES: 28
• Recruiter Messages: 3 (VP level: 2, Director: 1)

System Status:
• All systems operational
• No critical issues detected
• Queue: 0 pending commands
```

---

### Scenario 2: Dashboard Scan
**Command:** `/dashboard_scan`

**Expected Result:**
```
✅ CMD_005: dashboard_scan

Dashboard scan complete:
• 21 projects scanned
• Projects needing attention: 5 (NFL Spread2, OpenClaw, Essay Helper, Science Template, LinkedIn)
• Health scores calculated
• Report: [scan output 500 chars]
```

---

### Scenario 3: Trading Bot Pause (Emergency)
**Command:** `/tradingbot_pause`

**Expected Result:**
```
✅ CMD_002: tradingbot_pause

Trading Bot PAUSED (Emergency halt).
No new positions will be opened.
Normal trading operations halted immediately.
```

---

## 🔧 PRODUCTION DEPLOYMENT (Tomorrow)

### Background Service Setup

**Option A: Windows Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task: "Start Telegram Bot"
3. Action: "Start a program: `python G:\z.ai\workspace\bot\simple_telegram_bot.py`"
4. Trigger: "At startup" or "At 7:45 AM daily"
5. Settings: Run whether user is logged in or not

**Option B: Cron Job (Linux/Mac)**
```bash
# Add to crontab
crontab -e | python G:/z.ai/workspace/bot/simple_telegram_bot.py >> /tmp/telegram_bot.log 2>&1
```

---

## 📊 MONITORING & LOGGING

### Where Logs Go
Bot prints to console, but for background service, you want logs in file:

```bash
# Redirect bot output to log file
python G:/z.ai/workspace/bot/simple_telegram_bot.py >> G:/z.ai/workspace/bot/telegram_bot.log 2>&1
```

### Log File Locations
- `G:\z.ai\workspace\bot\telegram_bot.log` - Main bot log
- `G:\z.ai\workspace\commands_queue.json` - Command execution history
- `G:\z.ai\workspace\bot\history.json` - Long-term command history (for analytics)

---

## ❓ SUPPORT & TROUBLESHOOTING

### Bot Not Responding
**Symptoms:** Bot starts but doesn't respond to commands

**Diagnosis Steps:**
1. Check if bot is actually running (look for "START" message)
2. Check your Telegram messages - did you receive confirmation?
3. Check bot's output for errors
4. Verify `TELEGRAM_BOT_TOKEN` is set correctly

**Common Fixes:**
- Token incorrect (from wrong bot or old message)
- Bot script crashed (restart it)
- Command queue file has syntax error (delete and recreate)
- Polling interval too long (increase to 30 seconds)

### Commands Not Executing
**Symptoms:** Bot says "Executing CMD_XXX" but doesn't return result

**Diagnosis Steps:**
1. Check if command category/action is implemented
2. Review bot output for error messages
3. Test command manually using Python shell
4. Check `commands_queue.json` for failed commands

**Common Fixes:**
- Command syntax typo in `commands_queue.json` (add manually and mark completed)
- Implementation function returns error or crashes
- Command not recognized (wrong category/action combo)

---

## 🎯 SUCCESS CRITERIA

Bot is **production-ready** when:

1. ✅ Starts successfully (shows "START" message)
2. ✅ Polls queue file regularly (every 15 seconds)
3. ✅ Executes commands and sends Telegram replies
4. ✅ Marks commands as completed
5. ✅ Saves command history
6. ✅ Sends `/help` when asked
7. ✅ No console errors

---

## 📋 YOUR DECISION

**Option A: Test Now (Interactive Mode)**
- Run bot in terminal
- Test `/help`, `/status`, `/dashboard_scan`
- Verify all responses work
- Stop bot with `Ctrl+C`
- Review logs for issues

**Option B: Deploy Tomorrow (Background Service)**
- Set up Task Scheduler for automatic startup
- Configure logging to file
- Monitor logs for 24 hours
- Adjust polling interval based on CPU/memory usage

**Option C: Review First**
- Read full documentation at `G:\z.ai\workspace\bot\README.md`
- Review bot code at `G:\z.ai\workspace\bot\simple_telegram_bot.py`
- Ask questions about functionality

---

## 🚀 LET'S TEST NOW!

**Your Next Steps:**
1. Set `TELEGRAM_BOT_TOKEN` environment variable
2. Run: `python G:\z.ai\workspace\bot\simple_telegram_bot.py`
3. Send: `/help` in Telegram
4. Send: `/status` in Telegram
5. Verify you receive correct responses
6. Stop bot with `Ctrl+C` when done

**I'll be monitoring for any issues!** 🤖

---
