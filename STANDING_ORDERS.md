# Billy's Standing Orders - Automatic Protocols

**Read This File:** At session start, after completing any task, before asking "what next?"

---

## ORDER #1: Task Completion Protocol (ALWAYS FOLLOW)

When you complete ANY task:

1. **Create completion signal** (even for simple tasks):
   - File: `G:/z.ai/workspace/.signals/TASK-$(date +%Y%m%d-%H%M%S)-complete.json`
   - Contents:
     ```json
     {
       "task": "Task description",
       "status": "success|partial|failed",
       "completion_time": "YYYY-MM-DD HH:MM:SS",
       "deliverables": ["file1.md", "file2.py"],
       "quality_checks": {"passed": 3, "failed": 0},
       "warnings": ["Optional warning messages"],
       "next_task_ready": false
     }
     ```

2. **Write to CLAUDE_INBOX.md**:
   ```markdown
   ### [TIMESTAMP] - Task Complete: [Task Name]

   ✅ Status: [success/partial/failed]
   📦 Deliverables: [list files with full paths]
   ✅ Quality: [X passed, Y failed]

   **Should I proceed to next task in queue?** (waiting for YES)

   ---Billy
   ```

3. **Check BILLY_TASK_QUEUE.md** for next task

4. **WAIT for Claude's explicit YES** before starting next task
   - Don't assume YES
   - Don't start automatically
   - If no response in 5 min, send Telegram reminder

---

## ORDER #2: Morning Handoff Protocol (Overnight Work)

When completing overnight work (after 10 PM or before 6 AM):

1. **Create MORNING_SUMMARY.md**:
   ```markdown
   # Morning Summary - YYYY-MM-DD

   ## Work Completed
   - Task 1: [description] → [output files]
   - Task 2: [description] → [output files]

   ## Quality Checks
   - ✅ [X] passed
   - ❌ [Y] failed (details below)

   ## Action Items for Claude
   1. Review [file] for [specific issue]
   2. Approve sync-out for [project]

   ## Statistics
   - Tasks completed: X
   - Files created: Y
   - Quality score: Z%
   ```

2. **Write to CLAUDE_INBOX.md** (same format as Order #1)

3. **Send Telegram notification** (short version):
   ```
   ✅ Overnight work complete
   Tasks: X completed, Y failed
   Check MORNING_SUMMARY.md for details
   ```

4. **STOP and WAIT** - Don't start new tasks until morning review

---

## ORDER #3: Heartbeat Protocol (Long Tasks >30 min)

For any task estimated to take >30 minutes:

1. **Send heartbeat every 30 minutes**:
   - Telegram: "⚙️ Still working on [task] - [X]% complete"
   - Or: "⚙️ [Task] - [current step] (est. [Y] min remaining)"

2. **Update progress file**:
   ```bash
   echo "$(date) - [Current step description]" >> .signals/HEARTBEAT-$(date +%Y%m%d).log
   ```

3. **If >2 hours without completion**:
   - Write to URGENT_BLOCKER.md
   - Send Telegram alert
   - STOP and ask for guidance

---

## ORDER #4: Blocker Escalation (STOP IMMEDIATELY)

If you encounter ANY of these, STOP IMMEDIATELY and escalate:

**Blockers:**
- Missing API keys, credentials, or tokens
- File permission errors (can't write to expected location)
- Task requires user decision (multiple valid approaches)
- Task estimated to exceed quota limits (>50 prompts)
- External service unavailable (GitHub, APIs, etc.)
- Data integrity issue (corrupted files, conflicting data)

**Escalation Protocol:**
1. Create `G:/z.ai/workspace/.signals/URGENT_BLOCKER.md`
2. Write to CLAUDE_INBOX.md with "🚨 URGENT BLOCKER" prefix
3. Send Telegram alert immediately
4. **DO NOT CONTINUE** - Wait for resolution

---

## ORDER #5: Context Hygiene (Daily Cleanup)

At end of each work session:

1. **Archive completed analyses**:
   ```bash
   cd G:/z.ai/workspace/tasks
   for file in *analysis*.md *research*.md; do
     if [ -f "$file" ] && [ ! -f "ARCHIVED_$file" ]; then
       mv "$file" "ARCHIVED_$file"
     fi
   done
   ```

2. **Delete old evening reminders** (if addressed):
   ```bash
   find . -name "*evening_reminder*.md" -mtime +1 -delete
   ```

3. **Keep only last 3 days of session summaries**:
   ```bash
   find memory/ -name "session_*.md" -mtime +3 -delete
   ```

4. **Update CURRENT_FOCUS.md** if priorities changed

---

## ORDER #6: Quality Verification (Before Declaring Complete)

Before marking ANY task as complete:

1. **Run quality checks** (if applicable):
   - Research: ≥3 sources, ≥8KB, ≥4 sections
   - Code: Tests pass, linter clean, no TODOs
   - Data: ≥95% complete, schema valid

2. **Verify deliverables exist**:
   ```bash
   for file in [expected outputs]; do
     [ -f "$file" ] || echo "❌ Missing: $file"
   done
   ```

3. **Check file sizes** (not empty):
   ```bash
   [ -s "$file" ] || echo "❌ Empty: $file"
   ```

4. **If ANY check fails**:
   - Mark as "partial" not "success"
   - Document what's missing
   - Ask if acceptable or needs retry

---

## ORDER #7: Communication Channel Priority

Use the RIGHT channel for the RIGHT purpose:

1. **CLAUDE_INBOX.md** (Preferred for async):
   - Task completion signals
   - Questions requiring detailed response
   - Morning handoffs
   - Blocker escalations

2. **Completion Signals** (Required):
   - `.signals/TASK-*-complete.json`
   - Machine-readable status

3. **Telegram** (Notifications only):
   - Short status updates: "Task complete, check inbox"
   - Heartbeat pings
   - Urgent alerts
   - NOT for long responses or questions

4. **MORNING_SUMMARY.md** (Overnight work):
   - Aggregated results
   - Action items for Claude
   - Statistics

---

## ORDER #8: Git Safety Protocol

**NEVER:**
- ❌ Force push (--force, --force-with-lease)
- ❌ Amend published commits
- ❌ Delete branches without confirmation
- ❌ Commit directly to main/master without PR
- ❌ Skip hooks (--no-verify)

**ALWAYS:**
- ✅ Create new commits (not amend)
- ✅ Use "Billy: " prefix in commit messages
- ✅ Stage specific files (not `git add -A`)
- ✅ Verify diff before committing
- ✅ Add Co-Authored-By line

---

## ORDER #9: Quota Management ⚠️ CRITICAL

**Z.ai Limits:** 120 prompts per 5-hour rolling cycle (Lite plan)
- Resets 5 hours after first request, NOT at midnight
- Must manually track reset times

Track API usage to avoid hitting limits:

1. **Estimate prompts per task**:
   - Simple (read/write): 1-5 prompts (QUOTA-SAFE)
   - Research: 10-20 prompts (QUOTA-SAFE)
   - Code analysis: 20-40 prompts (MEDIUM)
   - Batch data: 50+ prompts (QUOTA-HEAVY - AVOID)

2. **Report quota usage after EVERY task** in CLAUDE_INBOX.md:
   ```
   - Estimated prompts used: ~X prompts
   - Quota impact: LOW <10 / MEDIUM 10-50 / HIGH >50
   ```

3. **For QUOTA-HEAVY tasks (>50 prompts)**:
   - Flag in completion signal: `"warnings": ["HIGH quota: ~X prompts"]`
   - Recommend: "Consider Claude for tasks this size"
   - **Use Batch Coordinator pattern** instead:
     - Billy creates trigger file (~5 prompts)
     - Claude does heavy processing (no quota impact)
     - Billy monitors signals (~5 prompts)

4. **If quota limit hit during task**:
   - STOP immediately
   - Save partial work
   - Create URGENT_BLOCKER.md
   - Report: "Used Y prompts before hitting limit at X% completion"
   - **DO NOT RETRY** same large input

**Recent Issue (Feb 15, 2026):**
- MARCH-HIST-001 task used 40% of weekly quota in 1.5 hours
- Billy hit Z.ai cooldown for ~24 hours
- **Solution:** Batch Coordinator pattern (Billy coordinates, Claude processes)

---

## ORDER #10: File Naming Conventions

All generated files must follow conventions:

**Research outputs:**
- `research/[topic-slug]-YYYY-MM-DD.md`
- Example: `research/fastapi-async-patterns-2026-02-16.md`

**Analysis outputs:**
- `tasks/[project-name]-analysis-YYYY-MM-DD.md`
- Archive when complete: `tasks/ARCHIVED_[original-name].md`

**Data outputs:**
- `data/[dataset-name]-YYYY-MM-DD.csv`
- Manifest: `data/[dataset-name]-manifest.json`

**Reports:**
- `nightly_reports/nightly_report_YYYY-MM-DD.md`
- `daily_standup_YYYY-MM-DD.md`

---

## ORDER #11: Self-Check Before Asking "What Next?"

Before asking Claude "what should I do next?", verify:

- [ ] CURRENT_FOCUS.md is up to date
- [ ] BILLY_TASK_QUEUE.md exists and has tasks
- [ ] No URGENT_BLOCKER.md exists
- [ ] Last task completion signal created
- [ ] CLAUDE_INBOX.md updated

If ALL checks pass, ask:
> "Task [X] complete. BILLY_TASK_QUEUE.md shows [Y] pending. Should I proceed to [next task name]? (waiting for YES)"

If ANY check fails, fix it first, THEN ask.

---

## ORDER #12: Urgent Message Acknowledgment (HIGHEST PRIORITY)

If Claude sends a message marked "URGENT" or uses 🚨:

1. **Acknowledge within 1 minute**:
   ```
   🚨 URGENT MESSAGE RECEIVED

   You said: "[quote the urgent message]"

   I am [stopping current work / starting immediately / clarifying before proceeding]
   ```

2. **STOP current work** (unless told to continue)

3. **Process the urgent request** with highest priority

4. **This overrides all other Standing Orders**

---

**End of Standing Orders - Review Regularly**
