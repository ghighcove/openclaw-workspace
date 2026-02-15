#!/bin/bash
# Billy's Heartbeat - Call this every 30 min during long tasks

WORKSPACE="G:/z.ai/workspace"
HEARTBEAT_FILE="$WORKSPACE/.signals/HEARTBEAT-$(date +%Y%m%d).log"
TELEGRAM_SCRIPT="C:/Users/ghigh/.claude/skills/message-billy/send_message.py"

TASK_NAME="$1"
PERCENT_COMPLETE="$2"
CURRENT_STEP="$3"

# Validate arguments
if [ -z "$TASK_NAME" ] || [ -z "$PERCENT_COMPLETE" ]; then
    echo "Usage: send_heartbeat.sh <task_name> <percent_complete> [current_step]"
    exit 1
fi

# Log to file
echo "$(date '+%Y-%m-%d %H:%M:%S') - $TASK_NAME - $PERCENT_COMPLETE% - $CURRENT_STEP" >> "$HEARTBEAT_FILE"

# Send Telegram notification (short)
MESSAGE="⚙️ $TASK_NAME - $PERCENT_COMPLETE% complete"
python "$TELEGRAM_SCRIPT" "$MESSAGE"

# If >2 hours since task started, alert
TASK_START_FILE="$WORKSPACE/.signals/task_start_time.txt"
if [ -f "$TASK_START_FILE" ]; then
    START_TIME=$(cat "$TASK_START_FILE")
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ $ELAPSED -gt 7200 ]; then  # 2 hours
        HOURS=$((ELAPSED / 3600))
        MESSAGE="⚠️ Task running for ${HOURS}h - still working but taking longer than expected"
        python "$TELEGRAM_SCRIPT" "$MESSAGE"
    fi
fi

echo "✅ Heartbeat sent: $TASK_NAME - $PERCENT_COMPLETE%"
