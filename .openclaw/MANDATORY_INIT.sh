#!/bin/bash
# MANDATORY INITIALIZATION - Billy CANNOT work without this
# This runs AUTOMATICALLY when Billy starts any task

set -e  # Exit on any error

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="$(dirname "$WORKSPACE")/openclaw-project/workspace/CLAUDE_INBOX.md"
SIGNALS="$WORKSPACE/.signals"
HEARTBEAT="$WORKSPACE/.heartbeat"

echo "========================================"
echo "BILLY MANDATORY INITIALIZATION"
echo "========================================"

# Step 1: Verify inbox exists
if [ ! -f "$INBOX" ]; then
    echo "FATAL: CLAUDE_INBOX.md not found!"
    exit 1
fi

# Step 2: Count unacknowledged messages
CLAUDE_COUNT=$(grep -c "---Claude" "$INBOX" || echo "0")
BILLY_ACK_COUNT=$(grep -c "✅ ACKNOWLEDGED" "$INBOX" || echo "0")

if [ "$CLAUDE_COUNT" -gt "$BILLY_ACK_COUNT" ]; then
    UNACKED=$((CLAUDE_COUNT - BILLY_ACK_COUNT))
    echo "BLOCKED: $UNACKED unacknowledged messages"
    echo ""
    echo "You must acknowledge ALL messages before working."
    echo "Read $INBOX and acknowledge each message."
    exit 1
fi

# Step 3: Check for STOP commands
if grep -q "STOP\|🚨.*STOP\|DO NOT" "$INBOX"; then
    echo "BLOCKED: STOP command found in inbox"
    echo ""
    echo "You must handle STOP commands before working."
    grep -n "STOP\|🚨.*STOP\|DO NOT" "$INBOX" || true
    exit 1
fi

# Step 4: Send heartbeat
mkdir -p "$HEARTBEAT"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Billy session started" >> "$HEARTBEAT/log.txt"

# Step 5: Verify no stale context
LAST_MSG=$(grep -n "---Billy" "$INBOX" | tail -1 | cut -d: -f1 || echo "0")
if [ "$LAST_MSG" -gt 0 ]; then
    # Check if last Billy message is older than 4 hours
    # (This is approximate - actual implementation would parse timestamps)
    echo "Last Billy message at line $LAST_MSG"
fi

echo ""
echo "✓ Initialization complete"
echo "✓ All messages acknowledged"
echo "✓ No STOP commands"
echo "✓ Heartbeat sent"
echo ""
echo "You may now proceed with work."
echo "========================================"

exit 0
