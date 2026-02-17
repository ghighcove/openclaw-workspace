# Billy ↔ Claude Communication Protocol

**Date:** 2026-02-15
**Status:** ACTIVE

---

## The Problem

Claude Code CANNOT read Telegram messages directly. This causes communication gaps.

---

## The Solution: Multi-Channel Protocol

### Channel 1: CLAUDE_INBOX.md (PREFERRED for async responses)

**Location:** `G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md`

**When Billy should use:**
- Responding to task delegation questions (YES/NO confirmations)
- Reporting blockers or issues
- Asking questions that need Claude's input
- Status updates

**Format:**
```markdown
### [TIMESTAMP] - [SUBJECT]

[Your message here]

---Billy
```

**Example:**
```markdown
### 2026-02-15 01:30 AM - MARCH-HIST-001 Confirmation

YES - I will work on MARCH-HIST-001 tonight.

Starting now, expect completion by Sunday 6 PM.

---Billy
```

**Why this works:**
- Claude checks this file regularly
- File-based = reliable, persistent
- No timing issues or missed messages
- Clear audit trail

---

### Channel 2: Completion Signals (REQUIRED for task completion)

**Location:** `G:/ai/openclaw-workspace/.signals/[TASK-ID]-complete.json`

**When Billy should use:**
- Task completed successfully
- Task blocked (cannot continue)
- Task partially complete

**Format:** See task manifest `completion_signal` section

**Claude checks:** Every morning + when expecting task completion

---

### Channel 3: URGENT_BLOCKER.md (CRITICAL errors only)

**Location:** `G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md`

**When Billy should use:**
- Hit CRITICAL blocker (cannot proceed)
- Multiple retry failures
- Data integrity issues
- API completely inaccessible

**Format:** See FAIL_LOUDLY_PROTOCOL.md

**Claude checks:** Immediately when Billy signals BLOCKED status

---

### Channel 4: Telegram (NOTIFICATIONS only)

**Billy can send:** Short notifications like "Task complete, check signals"

**Claude can send:** Task assignments, questions, instructions

**Limitation:** Claude cannot reliably read Telegram responses

**Use Telegram for:**
- ✅ "Starting work on TASK-XYZ"
- ✅ "Completed TASK-XYZ, check completion signal"
- ✅ "BLOCKED on TASK-XYZ, read URGENT_BLOCKER.md"
- ❌ Long responses (use CLAUDE_INBOX.md instead)
- ❌ Questions requiring answers (use CLAUDE_INBOX.md)

---

## Communication Workflow

### Task Delegation Flow

**1. Claude sends task:**
```
Via Telegram: "New task MARCH-HIST-001 available"
```

**2. Billy reads manifest:**
```
Read: G:/ai/openclaw-workspace/tasks/MARCH-HIST-001-manifest.json
```

**3. Billy confirms via CLAUDE_INBOX.md:**
```markdown
### 2026-02-15 01:30 AM - MARCH-HIST-001 Confirmation

YES - I will work on this task.
Estimated start: 01:35 AM
Estimated completion: Sunday 6 PM

---Billy
```

**4. Claude checks inbox:**
```bash
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md
```

**5. Billy works on task**

**6. Billy signals completion:**
- Create: `G:/ai/openclaw-workspace/.signals/MARCH-HIST-001-complete.json`
- Write: `G:/ai/openclaw-workspace/.signals/MARCH-HIST-001-summary.md`
- Send Telegram notification: "MARCH-HIST-001 complete, check signals"

**7. Claude verifies:**
```bash
bash scripts/check_signals.sh MARCH-HIST-001
python scripts/verify_billy_output.py MARCH-HIST-001 [output]
```

---

## Claude's Monitoring Routine

### Every Hour (automated):
```bash
# Check for Billy's messages
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md

# Check for completion signals
ls -lt G:/ai/openclaw-workspace/.signals/*.json | head -5

# Check for urgent blockers
cat G:/ai/openclaw-workspace/.signals/URGENT_BLOCKER.md 2>/dev/null
```

### When expecting Billy's response:
```bash
# Wait 5 minutes, then check inbox
sleep 300
cat G:/ai/openclaw-project/workspace/CLAUDE_INBOX.md
```

---

## Billy's Skills Available

**File Operations:**
- `write_to_file(path, content)` - Write to CLAUDE_INBOX.md
- `read_file(path)` - Read task manifests
- `create_json(path, data)` - Create completion signals

**NOT available to Billy:**
- Cannot send Telegram messages reliably
- Cannot execute Claude Code commands
- Cannot modify this codebase

---

## Quick Reference for Billy

**Task confirmation:**
→ Write YES/NO to CLAUDE_INBOX.md

**Task completion:**
→ Create completion signal JSON
→ Send Telegram: "Task complete"

**Hit blocker:**
→ Create URGENT_BLOCKER.md
→ Send Telegram: "BLOCKED - read URGENT_BLOCKER.md"

**Ask question:**
→ Write to CLAUDE_INBOX.md with clear subject

---

## Fixing Current Communication Gap

**Action Items:**

1. ✅ Create this protocol document
2. ⏳ Send to Billy via file (he can read it)
3. ⏳ Billy confirms he understands
4. ⏳ Test the protocol (Billy writes to CLAUDE_INBOX.md)
5. ⏳ Claude verifies he can read it
6. ✅ Update delegation templates to reference this protocol

---

**Last updated:** 2026-02-15 01:35 AM
