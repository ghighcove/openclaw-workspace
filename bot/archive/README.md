# Simple Telegram Bot - Solution 1

**Version:** 1.0.0
**Author:** Billy Byte (OpenClaw)
**Date:** February 14, 2026

---

## Overview

Simple command execution bot for cross-project intervention from anywhere via Telegram.

**Purpose:**
- Execute commands on your behalf (trading bot pause/resume, dashboard scans, LinkedIn metrics)
- Send back results and confirmations via Telegram
- Provide intervention capability while you're away from your computer
- Reduce frustration and improve response times for urgent actions

---

## Quick Start

### Prerequisites
1. **Python 3.7+** installed
2. **Telegram Bot Token** - Set as environment variable
3. **Telegram Chat ID** - Your chat ID (7129842067)
4. **Commands Queue File** - `G:\z.ai\workspace\commands_queue.json` (auto-created)

### Setup Environment Variable
```bash
# On Windows (PowerShell)
setx TELEGRAM_BOT_TOKEN "8385256909:AAGPH7QQkuEkIDICYrrfVGrgT4zPUdJfp5o"

# On Windows (CMD)
set TELEGRAM_BOT_TOKEN=8385256909:AAGPH7QQkuEkIDICYrrfVGrgT4zPUdJfp5o

# On Linux/Mac
export TELEGRAM_BOT_TOKEN="8385256909:AAGPH7QQkuEkIDICYrrfVGrgT4zPUdJfp5o"
```

### Verify Installation
```bash
python G:/z.ai/workspace/bot/simple_telegram_bot.py
```

Should see:
```
[START] Simple Telegram Bot starting...
[CONFIG] Polling every 15 seconds
[CONFIG] Chat ID: 7129842067
[CONFIG] Queue file: G:\z.ai\workspace\commands_queue.json
[CONFIG] Telegram Bot Token: [your-token-hidden]
[START] Simple Telegram Bot starting...
```

If it starts successfully and says "waiting for pending commands", you're ready!

---

## Running the Bot

### Option A: Interactive (For Testing)
```bash
# Bot will run in current terminal
python G:/z.ai/workspace/bot/simple_telegram_bot.py
```

**To stop:** Press `Ctrl+C` in terminal

### Option B: Background Service (For Production)
**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Task: "Start Telegram Bot"
3. Trigger: "At startup" or "At specific time"
4. Action: `python G:/z.ai/workspace/bot/simple_telegram_bot.py`
5. Settings: Run whether user is logged in or not

**Linux/Mac (cron):**
```bash
# Add to crontab
crontab -e | python G:/z.ai/workspace/bot/simple_telegram_bot.py >> /tmp/telegram_bot.log 2>&1
```

---

## Available Commands

### Monitoring Commands
- **status** - Get overall status of all systems
- **dashboard_scan** - Scan all projects for health
- **linkedin_metrics** - Get LinkedIn profile metrics

### Trading Bot Commands
- **tradingbot_pause** - Pause trading bot (emergency halt)
- **tradingbot_resume** - Resume trading bot operations
- **tradingbot_status** - Get detailed trading bot status

### Reporting Commands
- **overnight_report** - Generate overnight work summary

### System Commands
- **help** - Show available commands and usage instructions

---

## Commands Queue Format

Commands are stored in `commands_queue.json`:

```json
{
  "commands": [
    {
      "id": "CMD_001",
      "name": "status",
      "description": "Get overall status",
      "category": "monitoring",
      "priority": "high",
      "action": "health_check",
      "status": "pending"
    },
    {
      "id": "CMD_002",
      "name": "tradingbot_pause",
      "description": "Pause trading bot",
      "category": "trading",
      "priority": "critical",
      "action": "pause",
      "status": "pending"
    }
  ]
}
```

### Adding Commands via CLI
The bot will automatically add commands to the queue, but you can also add them manually via the bot:

1. Send any message to bot (your Telegram chat ID must be 7129842067)
2. Bot will parse commands and add to queue
3. Supported command syntax:

   **Simple:**
   - `/status`
   - `/dashboard_scan`
   - `/tradingbot_pause`
   - `/tradingbot_resume`
   - `/tradingbot_status`
   - `/linkedin_metrics`
   - `/overnight_report`
   - `/help`

   **With Arguments:**
   - `/tradingbot_pause emergency`
   - `/dashboard_scan priority:high`

---

## Command Execution Flow

1. **Bot polls** `commands_queue.json` every 15 seconds
2. Finds **pending** commands
3. Executes command (if category supported)
4. Sends result back to Telegram
5. Marks command as **completed**
6. Writes updated history to JSON file

---

## Response Format

Bot will send formatted responses:

### Success Response
```
✅ CMD_001: status

Overall Status:
• Trading Bot: ACTIVE (Positions: 3, P&L: $12,345, Risk: LOW)
• Project Dashboard: HEALTHY (21 projects scanned)
• LinkedIn Metrics: VIEWS: 142 (Week), APPEARANCES: 28

System Status:
• All systems operational
• No critical issues detected
• Queue: 0 pending commands
```

### Error Response
```
❌ CMD_002: tradingbot_pause

ERROR: Failed to execute tradingbot_pause
Reason: Trading bot integration not yet implemented
Status: Command marked as pending for retry
```

### Help Response
```
📖 Simple Telegram Bot - Help

📊 Monitoring Commands:
• /status - Overall system status
• /dashboard_scan - Scan all projects
• /linkedin_metrics - LinkedIn metrics

🤖 Trading Bot Commands:
• /tradingbot_pause - Pause trading bot (emergency)
• /tradingbot_resume - Resume operations
• /tradingbot_status - Detailed status
• /help - Show this message
```

---

## Integration Points

### Future Integrations

**Trading Bot:**
- Placeholder functions `execute_trading_status()`, `execute_trading_pause()`, `execute_trading_resume()` should call your actual trading bot scripts
- File: `G:\ai\trading_bot\src\trading_bot.py`

**Project Dashboard:**
- Already integrated via subprocess call to `G:\ai\project-dashboard\scripts\dashboard.py`

**LinkedIn Metrics:**
- Placeholder function `execute_linkedin_metrics()` should integrate with your LinkedIn project
- File: `G:\ai\linkedin\src\linkedin_metrics.py`

---

## Troubleshooting

### Bot Not Responding
**Possible causes:**
- Bot script not running
- TELEGRAM_BOT_TOKEN not set correctly
- Your chat ID is incorrect (must be 7129842067)
- Commands queue file not accessible

**Solutions:**
1. Check if bot is running (look for "Simple Telegram Bot starting..." in output)
2. Verify environment variable: `echo %TELEGRAM_BOT_TOKEN%`
3. Test connection: Send `/help` command
4. Check logs for errors

### Commands Not Executing
**Possible causes:**
- Command not recognized (typo in command name)
- Command not supported (category/action combination not valid)
- Command implementation returns error

**Solutions:**
1. Check `/help` for available commands
2. Verify command syntax in documentation
3. Check bot logs for error messages

---

## Security & Privacy

- Bot token is stored in environment variable (not in code)
- Commands queue file contains no sensitive data
- Bot executes commands on your behalf (no password required)
- All commands are logged with timestamps

---

## Next Steps

### Immediate (Testing Tonight)
1. ✅ Set `TELEGRAM_BOT_TOKEN` environment variable
2. ✅ Run bot in interactive mode to test commands
3. ✅ Send `/help` command to verify connection
4. ✅ Test `/status` command to check all systems
5. ✅ Test `/dashboard_scan` command to verify project monitoring

### This Week
1. Implement actual trading bot integration
2. Implement actual LinkedIn metrics integration
3. Add more commands as needed
4. Set up background service for production deployment

---

## Questions & Support

For issues or feature requests:
- Check this README file for troubleshooting
- Review available commands and usage
- Test bot responses first
- Check environment variables

---

**Ready to test?** 🚀
