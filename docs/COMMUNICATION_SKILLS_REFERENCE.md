# Communication Skills Reference - Billy ↔ Claude

**Purpose:** Document what communication tools each side has available

---

## Claude's Skills (What Claude Can Do)

### To Send Messages to Billy:
```bash
# Send one-way message via Telegram
openclaw message send --channel telegram --target 7129842067 --message "text"

# Send message and get Billy's response (interactive)
openclaw agent --channel telegram --to 7129842067 --message "question" --deliver
```

### To Read Billy's Responses:
```bash
# Read Billy's inbox file (PREFERRED METHOD)
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md

# Check completion signals
cat G:/ai/openclaw-workspace/.signals/[TASK-ID]-complete.json

# Check for blockers
cat G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md

# List recent signal files
ls -lt G:/ai/openclaw-workspace/.signals/
```

### Monitoring Schedule:
- **Every hour:** Check CLAUDE_INBOX.md for new messages
- **When expecting response:** Check inbox after 5-10 minutes
- **Morning routine:** Check all signals and inbox
- **When Billy says "check signals":** Immediately check .signals/ directory

---

## Billy's Skills (What Billy Can Do)

### To Send Messages to Claude:

**Method 1: Write to CLAUDE_INBOX.md (BEST for responses)**
```
File: G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md

Use your write_file skill:
1. Read current file
2. Add new message under "## Messages (Newest First)"
3. Follow format:

### YYYY-MM-DD HH:MM AM/PM - Subject
Your message here
---Billy
```

**Method 2: Create Completion Signals (For task completion)**
```
File: G:/ai/openclaw-workspace/.signals/[TASK-ID]-complete.json

Use your create_json skill:
1. Follow format from task manifest
2. Include all required fields
3. Set status: success/partial/failed/BLOCKED
```

**Method 3: Create URGENT_BLOCKER.md (For critical issues)**
```
File: G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md

Use your write_file skill:
1. Follow template from FAIL_LOUDLY_PROTOCOL.md
2. Include: what happened, error message, what you tried
3. Be specific about what Claude needs to do
```

**Method 4: Telegram (For notifications only)**
```
Send via OpenClaw's Telegram integration:
- "Task [TASK-ID] complete, check signals"
- "BLOCKED on [TASK-ID], read URGENT_BLOCKER.md"
- "Started work on [TASK-ID]"

DO NOT use for: Long responses, questions, confirmations
USE CLAUDE_INBOX.md instead for those
```

---

## Communication Patterns

### Pattern 1: Task Confirmation

**Claude asks:**
```
Telegram: "Will you work on MARCH-HIST-001? Reply to CLAUDE_INBOX.md"
```

**Billy responds:**
```
Write to: G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md

### 2026-02-15 01:45 AM - MARCH-HIST-001 Confirmation

YES - I will work on this task.
Start time: 02:00 AM
Expected completion: Sunday 6 PM
Confidence: High (18 hours available, API seems stable)

---Billy
```

**Claude checks:**
```bash
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md
# Sees Billy's YES, marks task as delegated
```

---

### Pattern 2: Task Completion

**Billy finishes work:**
```
1. Create: G:/ai/openclaw-workspace/.signals/MARCH-HIST-001-complete.json
2. Create: G:/ai/openclaw-workspace/.signals/MARCH-HIST-001-summary.md
3. Send Telegram: "MARCH-HIST-001 complete. Check signals directory."
```

**Claude checks:**
```bash
bash scripts/check_signals.sh MARCH-HIST-001
python scripts/verify_billy_output.py MARCH-HIST-001 [output]
```

---

### Pattern 3: Hit Blocker

**Billy encounters blocker:**
```
1. Create: G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md
2. Update completion signal: status = "BLOCKED"
3. Send Telegram: "🚨 BLOCKED on MARCH-HIST-001. Read URGENT_BLOCKER.md immediately."
```

**Claude responds:**
```bash
cat G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md
# Diagnose issue, fix root cause
# Update task manifest or environment
# Re-delegate or handle manually
```

---

### Pattern 4: Ask Question Mid-Task

**Billy needs help:**
```
Write to: G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md

### 2026-02-15 03:15 AM - MARCH-HIST-001 Question

ESPN API returning different structure than expected.

Expected: response['events'][0]['competitions']
Actual: response['games'][0]['matchups']

Should I:
A) Adapt to new structure?
B) Stop and wait for your guidance?
C) Use fallback data source?

Current status: 2024 season 50% complete, others not started.

---Billy
```

**Claude checks inbox, responds:**
```
Telegram: "Saw your question in CLAUDE_INBOX.md. Adapt to new structure (option A). Update manifest after completion to document the change."
```

---

## Testing the Protocol

**Step 1: Billy writes test message**
```
Write to CLAUDE_INBOX.md:

### 2026-02-15 01:50 AM - Communication Test

Testing CLAUDE_INBOX.md communication.
Can you read this, Claude?

---Billy
```

**Step 2: Claude checks**
```bash
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md
```

**Step 3: Claude confirms**
```
Telegram: "✅ Received your test message in CLAUDE_INBOX.md. Communication working!"
```

**Step 4: Archive old messages**
```
Move old messages to Archive section to keep inbox clean
```

---

## Why This Protocol Exists

### The Problem:
- Claude cannot read Telegram messages directly
- `openclaw agent --deliver` times out or is unreliable
- Billy responds via Telegram, but Claude misses the responses
- Communication gaps cause confusion and wasted effort

### The Solution:
- **File-based communication** (CLAUDE_INBOX.md) = reliable, persistent
- **Completion signals** = structured, programmatically verifiable
- **Telegram** = notifications only, not for critical responses
- **Clear protocols** = both sides know what to expect

---

## Current Status

**Confirmed working:**
- ✅ Claude → Billy (Telegram message send)
- ✅ Billy → Claude (Completion signals for GIT-MONITOR-001)

**Needs testing:**
- ⏳ Billy → Claude (CLAUDE_INBOX.md write)
- ⏳ Claude monitoring (hourly inbox checks)
- ⏳ URGENT_BLOCKER workflow

**Action: Billy - please write a test message to CLAUDE_INBOX.md NOW to verify the protocol works!**

---

**Last updated:** 2026-02-15 01:50 AM
