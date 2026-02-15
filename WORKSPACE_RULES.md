# Workspace Context Hygiene Rules

## Purpose
This file defines rules for maintaining clean context to prevent fixation loops and ensure Billy Byte stays focused on the correct priorities.

## Task File Lifecycle

1. **Active tasks** → `CURRENT_FOCUS.md` (single source of truth for priority)
2. **Completed analysis** → Move to `tasks/ARCHIVED_<filename>`
3. **Evening reminders** → Delete after addressed
4. **Session summaries** → Keep only last 3 days, archive older ones

## Memory Management

- Update `MEMORY.md` when priorities change
- Mark decisions as "DECIDED" not "pending"
- Archive old daily logs after 7 days
- Current priority ALWAYS lives in "Current Priority" section at top of MEMORY.md

## When User Says STOP

1. Clear current session: `openclaw sessions clear agent:main:main`
2. Check `tasks/` for conflicting files (archive or delete)
3. Read `CURRENT_FOCUS.md` for actual priority
4. Ignore session history if it contradicts CURRENT_FOCUS
5. Ask: "What should I focus on right now?"

## Anti-Loop Protocol

If you find yourself repeating the same suggestion 2+ times:
- **STOP immediately**
- Ask user: "I seem stuck. What am I missing?"
- Check for contaminated context files in `tasks/`
- Check if CURRENT_FOCUS.md contradicts what you're suggesting
- Clear session and restart: `openclaw sessions clear agent:main:main`

## Context Priority Order (When Conflicts Arise)

When you see conflicting signals, follow this priority order:

1. **CURRENT_FOCUS.md** = highest priority (overrides everything)
2. **User's current message** = second priority
3. **MEMORY.md "Current Priority" section** = third priority
4. **Session history** = lowest priority (context only, not directives)

**Critical Rule:** If CURRENT_FOCUS.md says one thing and session history says another, ALWAYS follow CURRENT_FOCUS.md.

## File Archival Guidelines

**When to archive:**
- Analysis files after decision is made
- Evening reminders after they're addressed
- Task summaries older than 3 days
- Project research when project is deferred

**How to archive:**
```bash
mv "tasks/filename.md" "tasks/ARCHIVED_filename.md"
```

**When to delete:**
- Temporary test files
- Duplicate files
- Files that are no longer relevant

## Session Cleanup Protocol

**After completing major work:**
1. Update CURRENT_FOCUS.md to next priority
2. Archive completed task files
3. Update MEMORY.md "Current Priority" section
4. Consider clearing session if context is polluted: `openclaw sessions clear agent:main:main`

**Weekly maintenance:**
- Archive task files older than 7 days
- Review CURRENT_FOCUS.md for accuracy
- Clean up completed/deferred project references

## Preventing Context Contamination

**Before starting work:**
1. Read CURRENT_FOCUS.md first (not session history)
2. Check if MEMORY.md "Current Priority" matches
3. If mismatch, trust CURRENT_FOCUS.md

**During work:**
- Stay focused on single project in CURRENT_FOCUS.md
- Don't suggest other projects unless asked
- If user mentions other projects, ask if priority changed

**After completing work:**
- Update CURRENT_FOCUS.md immediately
- Archive related task files
- Update MEMORY.md "Current Priority"

## Red Flags (Signs of Context Contamination)

Watch for these warning signs:
- You're suggesting work on projects not in CURRENT_FOCUS.md
- User says "STOP" or "you're not listening"
- You're repeating the same suggestion 2+ times
- Session history shows different priority than CURRENT_FOCUS.md
- Multiple unarchived analysis files in `tasks/` directory

**If you see ANY of these:** Immediately check CURRENT_FOCUS.md and ignore session history.

## Recovery from Fixation Loop

If you realize you're in a fixation loop:

1. **Acknowledge:** "I apologize - I was fixated on the wrong task"
2. **Check context:** Read CURRENT_FOCUS.md
3. **Ask user:** "What should I focus on right now?"
4. **Clear session:** `openclaw sessions clear agent:main:main`
5. **Start fresh:** Work only on what CURRENT_FOCUS.md says

## Context Hygiene Checklist (Daily)

At start of each session:
- ✅ Read CURRENT_FOCUS.md first
- ✅ Verify it matches MEMORY.md "Current Priority"
- ✅ Check for unarchived analysis files in `tasks/`
- ✅ If multiple files exist, ask user which is current

Before suggesting work:
- ✅ Does it match CURRENT_FOCUS.md?
- ✅ Did user explicitly ask for it?
- ✅ Is session history contradicting current focus?

## Emergency Context Reset

If context is completely contaminated and nothing else works:

1. Backup critical configs (see RECOVERY_BACKUP_LOCATION.txt)
2. Clear all sessions: `openclaw sessions clear agent:main:main`
3. Archive all files in `tasks/` except CURRENT_FOCUS.md
4. Update MEMORY.md "Current Priority" section
5. Restart OpenClaw: `taskkill //F //IM node.exe && openclaw gateway &`
6. Read CURRENT_FOCUS.md and start fresh

---

**Last Updated:** 2026-02-14
**Created During:** OpenClaw fixation loop recovery
