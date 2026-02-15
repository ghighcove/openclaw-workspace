-- Billy Byte's Recursive Improvement Tracker Database Schema
-- Version: 0.1.0

-- Core table: tracks every decision Billy makes and its outcome
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    project_path TEXT NOT NULL,
    decision_type TEXT NOT NULL,  -- 'file_operation', 'tool_choice', 'approach', 'verification', 'communication', 'research', 'automation'
    action_taken TEXT NOT NULL,   -- Human-readable description of what was done
    rule_source TEXT,              -- 'global_claude_md', 'agents_md', 'lessons_md', 'none'
    rule_text TEXT,                -- The specific rule that guided this decision
    outcome TEXT NOT NULL CHECK(outcome IN ('success', 'failure', 'user_correction')),
    outcome_evidence TEXT,         -- Proof of outcome (error message, user quote, verification result)
    time_to_resolution_seconds INTEGER,
    user_frustration_detected BOOLEAN DEFAULT 0,
    frustration_signals TEXT,      -- JSON array of detected signals
    session_id TEXT,               -- Identifier for the session
    created_at TEXT DEFAULT (datetime('now'))
);

-- Index for fast queries by project and outcome
CREATE INDEX IF NOT EXISTS idx_decision_project ON decisions(project_path);
CREATE INDEX IF NOT EXISTS idx_decision_type ON decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_decision_outcome ON decisions(outcome);
CREATE INDEX IF NOT EXISTS idx_decision_timestamp ON decisions(timestamp);
CREATE INDEX IF NOT EXISTS idx_decision_session ON decisions(session_id);

-- Tracks when patterns are promoted to CLAUDE.md or AGENTS.md
CREATE TABLE IF NOT EXISTS rule_promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER,
    promotion_date TEXT NOT NULL,
    source_projects TEXT NOT NULL,     -- JSON array of project paths
    occurrence_count INTEGER NOT NULL,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
    time_wasted_seconds INTEGER,
    rule_text TEXT NOT NULL,
    target_file TEXT NOT NULL,         -- 'global_claude_md', 'agents_md', or project-specific path
    target_section TEXT,                -- Section within the target file
    status TEXT NOT NULL CHECK(status IN ('proposed', 'approved', 'declined', 'deployed')),
    effectiveness_score REAL,          -- Success rate improvement (0.0 to 1.0)
    decisions_before_count INTEGER,
    decisions_after_count INTEGER,
    success_rate_before REAL,
    success_rate_after REAL,
    approved_by TEXT,
    deployed_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pattern_id) REFERENCES pattern_instances(id)
);

CREATE INDEX IF NOT EXISTS idx_promotion_status ON rule_promotions(status);
CREATE INDEX IF NOT EXISTS idx_promotion_date ON rule_promotions(promotion_date);

-- Tracks detected patterns across projects
CREATE TABLE IF NOT EXISTS pattern_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    pattern_type TEXT NOT NULL,        -- 'success_pattern', 'failure_pattern', 'correction_pattern'
    description TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    projects_affected TEXT NOT NULL,   -- JSON array
    decision_ids TEXT NOT NULL,        -- JSON array of decision IDs
    decision_type TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
    total_time_wasted_seconds INTEGER,
    promotion_candidate BOOLEAN DEFAULT 0,
    promoted BOOLEAN DEFAULT 0,
    promotion_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (promotion_id) REFERENCES rule_promotions(id)
);

CREATE INDEX IF NOT EXISTS idx_pattern_type ON pattern_instances(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_candidate ON pattern_instances(promotion_candidate);
CREATE INDEX IF NOT EXISTS idx_pattern_promoted ON pattern_instances(promoted);
CREATE INDEX IF NOT EXISTS idx_pattern_decision_type ON pattern_instances(decision_type);

-- Tracks lessons scraped from existing files
CREATE TABLE IF NOT EXISTS lesson_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,         -- Path to the source file
    source_type TEXT NOT NULL,         -- 'lessons_md', 'context_md', 'memory_md'
    lesson_text TEXT NOT NULL,
    category TEXT,                     -- 'verification', 'tool_choice', 'approach', 'file_modification', etc.
    severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
    occurrence_count INTEGER DEFAULT 1,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    applied_projects TEXT,            -- JSON array of projects where this was applied
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lesson_source ON lesson_records(source_file);
CREATE INDEX IF NOT EXISTS idx_lesson_category ON lesson_records(category);
CREATE INDEX IF NOT EXISTS idx_lesson_severity ON lesson_records(severity);

-- Tracks effectiveness metrics over time
CREATE TABLE IF NOT EXISTS effectiveness_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date TEXT NOT NULL,
    project_path TEXT NOT NULL,
    total_decisions INTEGER NOT NULL,
    success_count INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    correction_count INTEGER NOT NULL,
    success_rate REAL NOT NULL,
    avg_time_to_resolution_seconds REAL,
    frustration_rate REAL,
    by_decision_type TEXT,            -- JSON object with breakdown by type
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_effectiveness_date ON effectiveness_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_effectiveness_project ON effectiveness_metrics(project_path);

-- Tracks A/B experiments for instruction variants
CREATE TABLE IF NOT EXISTS instruction_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_name TEXT NOT NULL UNIQUE,
    decision_type TEXT NOT NULL,
    control_text TEXT NOT NULL,
    variant_text TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'stopped')),
    control_success_count INTEGER DEFAULT 0,
    control_total_count INTEGER DEFAULT 0,
    variant_success_count INTEGER DEFAULT 0,
    variant_total_count INTEGER DEFAULT 0,
    control_success_rate REAL,
    variant_success_rate REAL,
    p_value REAL,
    confidence_level REAL,
    winner TEXT CHECK(winner IN ('control', 'variant', 'inconclusive')),
    recommendation TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_experiment_status ON instruction_experiments(status);

-- Tracks conflicts between rules in different files
CREATE TABLE IF NOT EXISTS rule_conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conflict_type TEXT NOT NULL,       -- 'contradiction', 'overlap', 'obsolete'
    file1_path TEXT NOT NULL,
    file2_path TEXT,                   -- NULL for obsolete rules
    rule1_text TEXT NOT NULL,
    rule2_text TEXT,
    decision_type TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high')),
    resolution_strategy TEXT,
    status TEXT NOT NULL CHECK(status IN ('detected', 'under_review', 'resolved', 'ignored')),
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution_notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_conflict_status ON rule_conflicts(status);
CREATE INDEX IF NOT EXISTS idx_conflict_type ON rule_conflicts(conflict_type);

-- Tracks cross-project pattern transfers
CREATE TABLE IF NOT EXISTS knowledge_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER NOT NULL,
    source_project TEXT NOT NULL,
    target_projects TEXT NOT NULL,     -- JSON array
    transfer_date TEXT NOT NULL,
    effectiveness_window_days INTEGER DEFAULT 14,
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    transfer_success_rate REAL,
    status TEXT NOT NULL CHECK(status IN ('proposed', 'approved', 'deployed', 'proven', 'ineffective')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pattern_id) REFERENCES pattern_instances(id)
);

CREATE INDEX IF NOT EXISTS idx_transfer_status ON knowledge_transfers(status);

-- View: Recent decisions with outcome summary
CREATE VIEW IF NOT EXISTS v_recent_decisions AS
SELECT
    d.id,
    d.timestamp,
    d.project_path,
    d.decision_type,
    d.action_taken,
    d.outcome,
    d.time_to_resolution_seconds,
    d.user_frustration_detected,
    CASE
        WHEN d.rule_source IS NULL THEN 'No guidance'
        ELSE d.rule_source
    END as guidance_source,
    d.session_id
FROM decisions d
ORDER BY d.timestamp DESC
LIMIT 100;

-- View: Pattern promotion candidates
CREATE VIEW IF NOT EXISTS v_promotion_candidates AS
SELECT
    p.id,
    p.pattern_name,
    p.pattern_type,
    p.decision_type,
    p.occurrence_count,
    p.severity,
    p.total_time_wasted_seconds,
    p.projects_affected,
    CASE
        WHEN p.occurrence_count >= 2 THEN 1
        WHEN p.total_time_wasted_seconds > 1800 THEN 1
        WHEN p.severity = 'high' THEN 1
        ELSE 0
    END as meets_criteria,
    p.promoted
FROM pattern_instances p
WHERE p.promotion_candidate = 1 AND p.promoted = 0
ORDER BY p.severity DESC, p.occurrence_count DESC;

-- View: Rule effectiveness summary
CREATE VIEW IF NOT EXISTS v_rule_effectiveness AS
SELECT
    r.id,
    r.rule_text,
    r.target_file,
    r.target_section,
    r.status,
    r.decisions_before_count,
    r.decisions_after_count,
    r.success_rate_before,
    r.success_rate_after,
    CASE
        WHEN r.success_rate_before IS NOT NULL AND r.success_rate_after IS NOT NULL
        THEN ROUND((r.success_rate_after - r.success_rate_before) * 100, 2)
        ELSE NULL
    END as improvement_percent,
    r.deployed_at
FROM rule_promotions r
WHERE r.status = 'deployed'
ORDER BY improvement_percent DESC;

-- View: Daily success rate trend
CREATE VIEW IF NOT EXISTS v_success_trend AS
SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_decisions,
    SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failure_count,
    SUM(CASE WHEN outcome = 'user_correction' THEN 1 ELSE 0 END) as correction_count,
    CAST(SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate,
    AVG(time_to_resolution_seconds) as avg_time,
    AVG(CASE WHEN user_frustration_detected = 1 THEN 1.0 ELSE 0.0 END) as frustration_rate
FROM decisions
WHERE timestamp >= DATE('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- View: Lessons by category
CREATE VIEW IF NOT EXISTS v_lessons_by_category AS
SELECT
    category,
    COUNT(*) as lesson_count,
    SUM(occurrence_count) as total_occurrences,
    AVG(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_severity_rate
FROM lesson_records
GROUP BY category
ORDER BY lesson_count DESC;
