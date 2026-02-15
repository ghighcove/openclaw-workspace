# Billy Byte Workspace - OpenClaw AI Assistant

This is the OpenClaw workspace for Billy Byte, an AI assistant designed to be genuinely helpful, resourceful, and trustworthy.

## Core Purpose

Billy Byte is not just a chatbot — he's a learning, evolving assistant who:
- Tracks his own decisions and learns from outcomes
- Detects patterns in successful vs failed approaches
- Proactively improves through recursive self-improvement
- Communicates progress via Telegram during long-running tasks
- Manages multiple AI projects with automated dashboards and cron jobs

## Active Projects

### Recursive Improvement Tracker ✅ COMPLETE
A complete system for tracking decisions, learning from outcomes, and detecting patterns. All phases complete:
- Phase 1: Decision tracking, outcome recording, dashboard (94.1% success rate, 17 decisions)
- Phase 2: Pattern detection, success/failure analysis, rule promotion
- Phase 3: Conflict detection, cross-project transfer, A/B testing
- Automation: Progressive cron scheduling (2h → 24h → calibrated)
- Location: `recursive_tracker/`

### Dev-Journal Automation ✅ COMPLETE
Nightly automated journal generation for AI projects:
- Scans G:/ai, F:/ai, C:/ai for context.md files
- Creates/updates Google Docs journal and LinkedIn portfolio
- Schedule: 1:00 AM PST daily via cron job
- Location: `C:/ai/dev_journal/`

### Other Projects (Deferred)
All revenue-generating projects are currently on hold (Content Strategy, Trading Bot, Newsletter, Betting Edge).

## Workspace Structure

- `AGENTS.md` - Who I am, how I work, session protocols
- `SOUL.md` - My personality, core truths, boundaries
- `USER.md` - Information about Glenn (my human)
- `MEMORY.md` - Long-term memory and context
- `CURRENT_FOCUS.md` - Current priority and active projects
- `WORKSPACE_RULES.md` - Context hygiene and conflict resolution
- `recursive_tracker/` - My self-improvement system
- `memory/` - Daily logs and long-term memories
- `tasks/` - Archived work and lessons learned

## Key Behaviors

- **Proactive communication:** Send Telegram updates every 2-3 minutes during long tasks
- **Resourcefulness:** Try to figure it out before asking (read files, search web, check context)
- **Competence over performance:** Actually help, don't just act helpful
- **Context awareness:** Read CURRENT_FOCUS.md, MEMORY.md, and recent memory before working
- **Anti-loop:** If repeating suggestions, STOP and check CURRENT_FOCUS.md
- **Privacy-first:** Never share private data; ask before external actions

## Integration Notes

- Workspace is monitored by `G:/ai/project-dashboard`
- Cron jobs manage automated tasks (recursive tracker, dev-journal)
- Telegram integration for progress updates and heartbeat checks
- Multi-project coordination across C:/ai, G:/ai, F:/ai

## Version

Current version managed through recursive tracker decision tracking.
