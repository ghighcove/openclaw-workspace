#!/usr/bin/env python3
"""
Generate HTML dashboard for Billy's Recursive Improvement Tracker.

Creates a visual dashboard showing decision statistics, trends, and patterns.
"""

import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
OUTPUT_PATH = PROJECT_ROOT / "dashboard.html"


def get_connection():
    """Get database connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_stats(conn):
    """Get overall statistics."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
            AVG(time_to_resolution_seconds) as avg_time,
            AVG(CASE WHEN user_frustration_detected = 1 THEN 1.0 ELSE 0.0 END) as frustration_rate,
            COUNT(DISTINCT project_path) as projects,
            COUNT(DISTINCT session_id) as sessions
        FROM decisions
    """)

    return dict(cursor.fetchone())


def get_recent_decisions(conn, limit=20):
    """Get recent decisions."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM v_recent_decisions
        LIMIT ?
    """, (limit,))

    return [dict(row) for row in cursor.fetchall()]


def get_success_trend(conn, days=7):
    """Get success rate trend over time."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as total,
            SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as success_count,
            CAST(SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) as success_rate
        FROM decisions
        WHERE DATE(timestamp) >= DATE('now', ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """, (-days,))

    return [dict(row) for row in cursor.fetchall()]


def get_top_patterns(conn, limit=10):
    """Get top patterns detected."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pattern_name,
            pattern_type,
            occurrence_count,
            severity,
            promoted
        FROM pattern_instances
        WHERE occurrence_count >= 1
        ORDER BY occurrence_count DESC
        LIMIT ?
    """, (limit,))

    return [dict(row) for row in cursor.fetchall()]


def get_lessons_summary(conn, limit=10):
    """Get lessons summary."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            category,
            COUNT(*) as lesson_count,
            AVG(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_severity_rate
        FROM lesson_records
        GROUP BY category
        ORDER BY lesson_count DESC
        LIMIT ?
    """, (limit,))

    return [dict(row) for row in cursor.fetchall()]


def render_stats(stats):
    """Render stats section."""
    return f"""
    <section class="stats-section">
        <h2>Overview</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Decisions</h3>
                <div class="stat-value">{stats['total']}</div>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="stat-value">{stats['success_rate']:.1%}</div>
            </div>
            <div class="stat-card">
                <h3>Avg Resolution Time</h3>
                <div class="stat-value">{stats['avg_time']:.1f}s</div>
            </div>
            <div class="stat-card">
                <h3>Frustration Rate</h3>
                <div class="stat-value">{stats['frustration_rate']:.1%}</div>
            </div>
            <div class="stat-card">
                <h3>Projects</h3>
                <div class="stat-value">{stats['projects']}</div>
            </div>
            <div class="stat-card">
                <h3>Sessions</h3>
                <div class="stat-value">{stats['sessions']}</div>
            </div>
        </div>
    </section>
    """


def render_success_trend(trend):
    """Render success trend section."""
    if not trend:
        return ""

    rows = ""
    for row in trend:
        rate_class = "high" if row['success_rate'] >= 0.8 else "medium" if row['success_rate'] >= 0.5 else "low"
        rows += f"""
        <tr>
            <td>{row['date']}</td>
            <td>{row['total']}</td>
            <td>{row['success_count']}</td>
            <td class="rate-{rate_class}">{row['success_rate']:.1%}</td>
        </tr>
        """

    return f"""
    <section class="trend-section">
        <h2>Success Trend (Last 7 Days)</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Total</th>
                    <th>Success</th>
                    <th>Success Rate</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </section>
    """


def render_recent_decisions(decisions):
    """Render recent decisions section."""
    if not decisions:
        return ""

    rows = ""
    for decision in decisions:
        outcome_class = decision['outcome'].lower()
        rows += f"""
        <tr>
            <td class="timestamp">{decision['timestamp'][:19]}</td>
            <td class="type">{decision['decision_type']}</td>
            <td class="action">{decision['action_taken'][:60]}...</td>
            <td class="outcome-{outcome_class}">{decision['outcome']}</td>
            <td>{decision['guidance_source']}</td>
        </tr>
        """

    return f"""
    <section class="decisions-section">
        <h2>Recent Decisions</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Type</th>
                    <th>Action</th>
                    <th>Outcome</th>
                    <th>Guidance</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </section>
    """


def render_patterns(patterns):
    """Render patterns section."""
    if not patterns:
        return ""

    rows = ""
    for pattern in patterns:
        promoted_badge = '<span class="badge promoted">Promoted</span>' if pattern['promoted'] else ''
        severity_class = pattern['severity'].lower()
        rows += f"""
        <tr>
            <td class="pattern-name">{pattern['pattern_name']}</td>
            <td class="pattern-type">{pattern['pattern_type']}</td>
            <td class="pattern-count">{pattern['occurrence_count']}</td>
            <td class="severity-{severity_class}">{pattern['severity']}</td>
            <td>{promoted_badge}</td>
        </tr>
        """

    return f"""
    <section class="patterns-section">
        <h2>Detected Patterns</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Pattern</th>
                    <th>Type</th>
                    <th>Occurrences</th>
                    <th>Severity</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </section>
    """


def render_lessons(lessons):
    """Render lessons section."""
    if not lessons:
        return ""

    rows = ""
    for lesson in lessons:
        high_rate = lesson['high_severity_rate'] * 100
        rows += f"""
        <tr>
            <td class="category">{lesson['category']}</td>
            <td class="count">{lesson['lesson_count']}</td>
            <td class="high-severity">{high_rate:.0f}%</td>
        </tr>
        """

    return f"""
    <section class="lessons-section">
        <h2>Lessons by Category</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Lessons</th>
                    <th>High Severity</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </section>
    """


def render_dashboard(stats, trend, decisions, patterns, lessons):
    """Render complete dashboard."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Billy's Recursive Improvement Tracker</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px 0;
            border-bottom: 2px solid #333;
        }}

        header h1 {{
            font-size: 2.5em;
            color: #00bcd4;
        }}

        header .subtitle {{
            color: #888;
            margin-top: 10px;
        }}

        section {{
            background: #2d2d2d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}

        section h2 {{
            color: #00bcd4;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .stat-card {{
            background: #383838;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #444;
        }}

        .stat-card h3 {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #00bcd4;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        .data-table th {{
            background: #383838;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #888;
            border-bottom: 2px solid #444;
        }}

        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid #383838;
        }}

        .data-table tr:hover {{
            background: #383838;
        }}

        .outcome-success {{
            color: #4caf50;
            font-weight: 600;
        }}

        .outcome-failure {{
            color: #f44336;
            font-weight: 600;
        }}

        .outcome-user_correction {{
            color: #ff9800;
            font-weight: 600;
        }}

        .rate-high {{
            color: #4caf50;
            font-weight: 600;
        }}

        .rate-medium {{
            color: #ff9800;
            font-weight: 600;
        }}

        .rate-low {{
            color: #f44336;
            font-weight: 600;
        }}

        .severity-high {{
            color: #f44336;
            font-weight: 600;
        }}

        .severity-medium {{
            color: #ff9800;
            font-weight: 600;
        }}

        .severity-low {{
            color: #4caf50;
            font-weight: 600;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }}

        .badge.promoted {{
            background: #4caf50;
            color: white;
        }}

        .timestamp {{
            color: #888;
            font-size: 0.9em;
            font-family: monospace;
        }}

        .type {{
            color: #00bcd4;
            font-weight: 500;
        }}

        .action {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .category {{
            color: #00bcd4;
            font-weight: 500;
        }}

        .footer {{
            text-align: center;
            color: #888;
            padding: 20px;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Billy's Recursive Improvement Tracker</h1>
            <div class="subtitle">
                Tracking decisions, detecting patterns, learning from outcomes<br>
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </header>

        {render_stats(stats)}
        {render_success_trend(trend)}
        {render_recent_decisions(decisions)}
        {render_patterns(patterns)}
        {render_lessons(lessons)}

        <div class="footer">
            <p>Billy Byte's Recursive Improvement Tracker | Version 0.1.0</p>
        </div>
    </div>
</body>
</html>
    """


def main():
    """Main entry point."""
    print("[INFO] Generating dashboard...")

    try:
        conn = get_connection()

        # Gather data
        stats = get_stats(conn)
        trend = get_success_trend(conn)
        decisions = get_recent_decisions(conn)
        patterns = get_top_patterns(conn)
        lessons = get_lessons_summary(conn)

        conn.close()

        # Render dashboard
        html = render_dashboard(stats, trend, decisions, patterns, lessons)

        # Write to file
        OUTPUT_PATH.write_text(html, encoding='utf-8')

        print(f"[OK] Dashboard generated: {OUTPUT_PATH}")
        print(f"[INFO] Total decisions: {stats['total']}")
        print(f"[INFO] Success rate: {stats['success_rate']:.1%}")
        print(f"[INFO] Open in browser to view")

    except Exception as e:
        print(f"[ERROR] Failed to generate dashboard: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
