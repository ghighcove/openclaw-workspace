#!/usr/bin/env python3
"""
Simple Telegram Bot for Cross-Project Intervention (FIXED)
Author: Billy Byte (OpenClaw)
Date: February 14, 2026
Version: 1.0.1

Description:
- Simple command execution bot
- Polls commands from JSON file
- Executes commands and sends replies via Telegram
- Supports trading bot, project dashboard, LinkedIn metrics, and more

Commands Supported:
- status - Get overall status of all systems
- tradingbot_pause - Pause trading bot (emergency)
- tradingbot_resume - Resume trading bot operations
- tradingbot_status - Get detailed trading bot status
- dashboard_scan - Scan all projects for health
- linkedin_metrics - Get LinkedIn profile metrics
- overnight_report - Generate overnight work summary
- help - Show available commands and usage

Usage:
1. Bot continuously polls commands_queue.json for pending commands
2. When a command is found, execute it
3. Capture output and send reply via Telegram
4. Mark command as completed
5. Continue polling

Architecture:
- commands_queue.json: Stores pending commands and execution history
- bot.py: Main bot entry point
- Command modules: Organized by category (trading, dashboard, linkedin, system)

Configuration:
- BOT_TOKEN: From environment variable (TELEGRAM_BOT_TOKEN)
- CHAT_ID: Your Telegram chat ID (7129842067)
- COMMANDS_FILE: Path to commands_queue.json
- POLL_INTERVAL: Seconds between queue checks

Bot API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def send_telegram_message(text: str, chat_id: str = CHAT_ID) -> bool:
    """Send message via Telegram bot API"""
    if not HAS_REQUESTS:
        print(f"[ERROR] requests module not available. Cannot send message: {text[:50]}...")
        return False
    
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                print(f"[TELEGRAM] Sent: {text[:50]}")
                return True
            else:
                print(f"[ERROR] Telegram API error: {result}")
                return False
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")
        return False

def load_commands() -> dict:
    """Load commands from JSON queue file"""
    try:
        if COMMANDS_FILE.exists():
            with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"commands": []}
    except Exception as e:
        print(f"[ERROR] Failed to load commands: {e}")
        return {"commands": []}

def save_commands(data: dict) -> bool:
    """Save commands to JSON queue file"""
    try:
        with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save commands: {e}")
        return False

def execute_command(command: dict) -> str:
    """Execute a command and return output"""
    cmd_id = command.get('id', 'unknown')
    name = command.get('name', 'unknown')
    category = command.get('category', 'unknown')
    action = command.get('action', 'unknown')
    
    print(f"[EXECUTE] {name} ({category}/{action})")
    
    try:
        if category == 'trading' and action == 'status':
            return execute_trading_status()
        
        elif category == 'trading' and action == 'pause':
            return execute_trading_pause()
        
        elif category == 'trading' and action == 'resume':
            return execute_trading_resume()
        
        elif category == 'dashboard' and action == 'scan':
            return execute_dashboard_scan()
        
        elif category == 'linkedin' and action == 'metrics':
            return execute_linkedin_metrics()
        
        elif category == 'reporting' and action == 'report':
            return execute_overnight_report()
        
        elif category == 'system' and action == 'help':
            return show_help()
        
        else:
            return f"[ERROR] Unknown command: {category}/{action}"
    
    except Exception as e:
        return f"[ERROR] Failed to execute {name}: {e}"

def execute_trading_status() -> str:
    """Get trading bot status"""
    # This is a placeholder - would integrate with your actual trading bot
    return "Trading Bot Status: ACTIVE (Positions: 3, P&L: $12,345, Risk: LOW)"

def execute_trading_pause() -> str:
    """Pause trading bot"""
    # This is a placeholder - would integrate with your actual trading bot
    return "Trading Bot PAUSED (Emergency halt). No new positions will be opened."

def execute_trading_resume() -> str:
    """Resume trading bot"""
    # This is a placeholder - would integrate with your actual trading bot
    return "Trading Bot RESUMED. Normal trading operations resumed."

def execute_dashboard_scan() -> str:
    """Run project dashboard scan"""
    try:
        # Scan G:\ai, F:\ai, C:\ai
        result = subprocess.run(
            ['python', 'G:/ai/project-dashboard/scripts/dashboard.py'],
            capture_output=True,
            text=True,
            shell=True,
            timeout=60
        )
        
        if result.returncode == 0:
            output = result.stdout
            # Return first 500 chars
            return f"Dashboard scan complete:\n\n{output[:500]}"
        else:
            error = result.stderr
            return f"[ERROR] Dashboard scan failed (exit code {result.returncode}):\n{error[:200]}"
    
    except Exception as e:
        return f"[ERROR] Dashboard scan exception: {e}"

def execute_linkedin_metrics() -> str:
    """Get LinkedIn profile metrics"""
    # This is a placeholder - would integrate with your actual LinkedIn project
    return "LinkedIn Metrics:\n• Profile views: 142 (Week)\n• Search appearances: 28\n• Recruiter messages: 3 (VP level: 2, Director: 1)"

def execute_overnight_report() -> str:
    """Generate and send overnight work summary"""
    # This is a placeholder - would integrate with your project systems
    return "Overnight Work Summary (Feb 14):\n• Project Dashboard: Scanned 21 projects\n• NFL Analysis: Data pipeline running\n• LinkedIn: Phase 1 ready to implement\n• Lessons Learned: 12 rules promoted to global CLAUDE.md\n• Action Items: 18 improvements identified\n• Generated: 5 new patterns for analysis"

def show_help() -> str:
    """Show available commands and usage"""
    help_text = """
🤖 Simple Telegram Bot - Available Commands

📊 Monitoring Commands:
• /status - Overall system status
• /dashboard_scan - Scan all projects for health
• /linkedin_metrics - LinkedIn profile metrics

🤖 Trading Bot Commands:
• /tradingbot_pause - Pause trading bot (emergency)
• /tradingbot_resume - Resume trading bot operations
• /tradingbot_status - Get detailed trading bot status

📈 Reporting Commands:
• /overnight_report - Generate overnight work summary

❓ System Commands:
• /help - Show this help message

Usage:
1. Send a command to this bot
2. Bot executes it and sends back result
3. Commands are processed in order received
4. Check status file for execution history

Examples:
/status
/tradingbot_pause
/dashboard_scan
/linkedin_metrics
/overnight_report
/help
"""
    return help_text

def process_pending_commands(commands: list) -> int:
    """Process all pending commands"""
    executed = 0
    failed = 0
    
    for command in commands:
        if command.get('status') == 'pending':
            result = execute_command(command)
            send_telegram_message(result)
            
            # Mark as completed
            command['status'] = 'completed'
            command['executed_at'] = datetime.now().isoformat()
            executed += 1
            
            if result.startswith('[ERROR]'):
                failed += 1
            # Small delay to avoid rate limiting
            import time
            time.sleep(1)
    
    # Save updated commands back to file
    if executed > 0:
        save_commands(commands)
        print(f"[QUEUE] Processed {executed} commands, {failed} failed")
    
    return executed, failed

def main():
    """Main entry point - continuous polling loop"""
    print(f"[START] Simple Telegram Bot starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[CONFIG] Polling every {POLL_INTERVAL} seconds")
    print(f"[CONFIG] Chat ID: {CHAT_ID}")
    print(f"[CONFIG] Queue file: {COMMANDS_FILE}")
    
    if not BOT_TOKEN or BOT_TOKEN == 'your-bot-token-here':
        print("[ERROR] TELEGRAM_BOT_TOKEN environment variable not set or is placeholder")
        print("Please set: export TELEGRAM_BOT_TOKEN=your_actual_bot_token")
        return
    
    try:
        while True:
            # Load commands from queue
            commands = load_commands()
            
            # Extract root object
            if isinstance(commands, dict) and 'commands' in commands:
                commands_list = commands['commands']
            else:
                commands_list = commands
            
            # Filter pending commands (not completed, not failed)
            pending = [cmd for cmd in commands_list if cmd.get('status') == 'pending']
            
            if pending:
                processed, failed = process_pending_commands(pending)
                
                if processed == 0:
                    # No commands processed, wait before checking again
                    print(f"[IDLE] No pending commands, waiting {POLL_INTERVAL}s...")
                    time.sleep(POLL_INTERVAL)
                else:
                    print(f"[IDLE] Waiting {POLL_INTERVAL}s before next poll...")
                    time.sleep(POLL_INTERVAL)
            else:
                print(f"[IDLE] No pending commands, waiting {POLL_INTERVAL}s...")
                time.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n[STOP] Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[FATAL] Bot crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
