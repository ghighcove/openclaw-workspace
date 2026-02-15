# Billy's Recursive Improvement Tracker - Design Document

## Overview

This is Billy Byte's personal learning and decision tracking system, inspired by Claude's recursive_proj but implemented as a completely separate system for Billy's own development and learning.

## Architecture

### Core Components

1. **Database Layer** (SQLite)
   - `data/billy_feedback.db` - Billy's personal database
   - Schema: `data/schema.sql`
   - Tables: decisions, pattern_instances, rule_promotions, lesson_records, etc.

2. **Tracking Library** (Python)
   - `lib/billy_tracker.py` - Core BillyTracker class
   - Non-blocking design (never crashes main tasks)
   - Handles connection management and error recovery

3. **CLI Tools**
   - `tools/init_database.py` - Initialize database
   - `tools/test_tracker.py` - Integration tests
   - `tools/scrape_lessons.py` - Extract lessons from existing files
   - `tools/generate_dashboard.py` - Generate HTML dashboard

4. **Views and Analysis**
   - Database views for common queries
   - Success rate trends
   - Pattern detection
   - Rule effectiveness tracking

## Design Decisions

### 1. Separate Database from Claude's Tracker

**Decision:** Billy uses `billy_feedback.db` in the recursive_tracker directory, not Claude's `feedback.db` in G:/ai/recursive_proj.

**Rationale:**
- Billy needs to learn independently
- Separate databases prevent contamination
- Allows different schemas tailored to each AI's needs
- Enables A/B testing of different tracking approaches

### 2. Non-Blocking Integration

**Decision:** All database operations have graceful error handling. Logging failures should never crash the main task.

**Rationale:**
- Billy's primary job is to help the user, not track himself
- Database errors are informational, not critical
- Warnings go to stderr, errors don't stop execution

### 3. SQLite Over Other Databases

**Decision:** Use SQLite with file-based storage instead of Postgres, MySQL, etc.

**Rationale:**
- Zero external dependencies
- Version control friendly (database is a file)
- Simple setup and maintenance
- More than sufficient for Billy's tracking volume
- Easy to backup and migrate

### 4. Custom Template Renderer

**Decision:** Simple string-based template rendering instead of Jinja2, Django templates, etc.

**Rationale:**
- No external dependencies
- Simple, predictable behavior
- Easy to debug
- Sufficient for dashboard needs

### 5. Decision Types

**Decision:** Track 7 decision types specific to Billy's work:
- file_operation - Reading, writing, editing files
- tool_choice - Selecting which tool to use
- approach - Choosing implementation strategy
- verification - Checking work is correct
- communication - Responding to user messages
- research - Looking up information
- automation - Creating tools/workflows

**Rationale:**
- Captures Billy's actual decision-making patterns
- Differentiates between different kinds of work
- Enables targeted improvement for each type
- More specific than Claude's 4 types

### 6. Session Tracking

**Decision:** Each Billy session gets a unique session_id (8-character UUID).

**Rationale:**
- Enables per-session analysis
- Tracks decision chains within a session
- Helps identify session-specific patterns
- Useful for debugging and retrospective analysis

## Data Flow

### 1. Decision Logging

```
User Request
    ↓
Billy makes a decision
    ↓
tracker.log_decision()
    ↓
INSERT INTO decisions
    ↓
Returns decision_id
```

### 2. Outcome Recording

```
Task completes
    ↓
tracker.record_outcome(decision_id, outcome, evidence)
    ↓
UPDATE decisions SET outcome = ...
    ↓
Pattern detection (future phase)
```

### 3. Pattern Detection (Future)

```
Analyze decisions
    ↓
Group by similarity
    ↓
INSERT INTO pattern_instances
    ↓
Promote to CLAUDE.md if criteria met
```

### 4. Dashboard Generation

```
Query database views
    ↓
Render HTML template
    ↓
Write to dashboard.html
    ↓
Open in browser
```

## Database Schema

### Core Tables

**decisions** - Main tracking table
- Every decision Billy makes
- Timestamp, project, type, action
- Outcome and evidence
- Frustration detection
- Session tracking

**pattern_instances** - Detected patterns
- Patterns across decisions
- Occurrence counts
- Severity and time wasted
- Promotion status

**rule_promotions** - Pattern promotions
- When patterns are promoted to CLAUDE.md
- Effectiveness tracking
- Before/after metrics

**lesson_records** - Scraped lessons
- Lessons from existing files
- Categorized by type
- Severity tracking

### Views

**v_recent_decisions** - Last 100 decisions
**v_promotion_candidates** - Patterns ready for promotion
**v_rule_effectiveness** - Impact of promoted rules
**v_success_trend** - Daily success rates
**v_lessons_by_category** - Lessons summary

## Success Metrics (Phase 1)

### Technical Metrics
- Database initialized without errors
- 50+ decision outcomes logged in first week
- Dashboard renders correctly
- All integration tests pass
- Zero critical errors in BillyTracker

### Learning Metrics
- Lesson scraper finds patterns across 3+ projects
- Pattern analysis report generated
- Success rate baseline established
- Frustration patterns identified

## Future Phases

### Phase 2: Pattern Detection
- Automated pattern detection algorithms
- Similarity clustering for decisions
- Rule promotion workflow
- Cross-project pattern transfer

### Phase 3: Automation
- A/B testing framework
- Semantic similarity analysis
- Conflict detection
- Automated proposal generation

## Testing Strategy

### Unit Tests (Future)
- Test individual functions
- Mock database connections
- Edge case coverage

### Integration Tests
- End-to-end workflow
- Database operations
- File I/O operations

### Manual Testing
- Dashboard rendering
- Lesson scraping accuracy
- Pattern detection quality

## Known Limitations

### Phase 1
- Pattern detection is manual (needs automated algorithms)
- No semantic similarity analysis
- No cross-project pattern transfer
- Limited to 7 decision types

### Future Enhancements
- Add more decision types as needed
- Implement pattern detection algorithms
- Add A/B testing framework
- Integrate with Claude's tracker for comparison

## Maintenance

### Regular Tasks
- Weekly dashboard review during heartbeats
- Monthly pattern analysis
- Quarterly effectiveness review
- Annual database cleanup

### Backup Strategy
- Database is version-controlled (git-annex or similar)
- Export to CSV for analysis
- Snapshot before major changes

## Security & Privacy

### Data Handling
- No external API calls
- All data stays on local machine
- No personally identifiable information logged
- User messages may be logged as evidence

### Access Control
- Database file permissions
- No remote access
- Local-only operation

---

**Version:** 0.1.0
**Last Updated:** February 14, 2026
**Status:** Phase 1 Implementation Complete
