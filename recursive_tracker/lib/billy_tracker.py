"""
BillyTracker - Core library for logging Billy's decisions and outcomes.

Usage:
    from billy_tracker import BillyTracker

    tracker = BillyTracker()

    # Log a decision
    decision_id = tracker.log_decision(
        decision_type='file_modification',
        action_taken='Updated HTML tables in article',
        rule_source='global_claude_md',
        rule_text='Verification Protocol: Always read file after modification'
    )

    # Record the outcome
    tracker.record_outcome(
        decision_id=decision_id,
        outcome='success',
        evidence='Read file, verified tables render correctly',
        time_elapsed=45
    )
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid


class BillyTracker:
    """Tracks Billy's decisions and their outcomes."""

    def __init__(self, db_path: Optional[Path] = None, project_path: Optional[str] = None):
        """
        Initialize tracker.

        Args:
            db_path: Path to database (defaults to data/billy_feedback.db)
            project_path: Current project path (defaults to cwd)
        """
        if db_path is None:
            # Default to data/billy_feedback.db relative to this file
            lib_dir = Path(__file__).parent
            db_path = lib_dir.parent / "data" / "billy_feedback.db"

        self.db_path = Path(db_path)
        self.project_path = project_path or str(Path.cwd())

        # Generate session ID
        self.session_id = str(uuid.uuid4())[:8]

        # Ensure database exists
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {self.db_path}. "
                f"Run 'python tools/init_database.py' first."
            )

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def log_decision(
        self,
        decision_type: str,
        action_taken: str,
        rule_source: Optional[str] = None,
        rule_text: Optional[str] = None,
        project_path: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """
        Log a decision Billy makes.

        Args:
            decision_type: Type of decision ('file_operation', 'tool_choice', 'approach', 'verification', 'communication', 'research', 'automation')
            action_taken: Human-readable description of what was done
            rule_source: Where guidance came from ('global_claude_md', 'agents_md', 'lessons_md', 'none')
            rule_text: The specific rule that guided this decision
            project_path: Override default project path
            session_id: Override default session ID

        Returns:
            decision_id: ID for this decision (use with record_outcome)

        Example:
            decision_id = tracker.log_decision(
                decision_type='file_modification',
                action_taken='Updated medium_draft.md with table images',
                rule_source='global_claude_md',
                rule_text='Medium Publishing: Tables must be PNG images'
            )
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions (
                    timestamp,
                    project_path,
                    decision_type,
                    action_taken,
                    rule_source,
                    rule_text,
                    outcome,
                    session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                project_path or self.project_path,
                decision_type,
                action_taken,
                rule_source,
                rule_text,
                'success',  # Default to success, update with record_outcome if needed
                session_id or self.session_id
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            # Non-blocking: log to stderr but don't crash
            import sys
            print(f"[WARNING] Failed to log decision: {e}", file=sys.stderr)
            return None
        finally:
            conn.close()

    def record_outcome(
        self,
        decision_id: int,
        outcome: str,
        evidence: Optional[str] = None,
        time_elapsed: Optional[int] = None,
        user_frustration: bool = False,
        frustration_signals: Optional[List[str]] = None
    ) -> None:
        """
        Record the outcome of a decision.

        Args:
            decision_id: ID from log_decision()
            outcome: 'success', 'failure', or 'user_correction'
            evidence: Proof of outcome (error message, user quote, verification result)
            time_elapsed: Seconds from decision to resolution
            user_frustration: Whether frustration was detected
            frustration_signals: List of detected frustration patterns

        Example:
            tracker.record_outcome(
                decision_id=123,
                outcome='user_correction',
                evidence='User said: "Why didn\'t you verify the file?"',
                time_elapsed=120,
                user_frustration=True,
                frustration_signals=['repeated_correction', 'questioning_tone']
            )
        """
        if decision_id is None:
            # Can't record outcome if decision wasn't logged
            return

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE decisions
                SET outcome = ?,
                    outcome_evidence = ?,
                    time_to_resolution_seconds = ?,
                    user_frustration_detected = ?,
                    frustration_signals = ?
                WHERE id = ?
            """, (
                outcome,
                evidence,
                time_elapsed,
                1 if user_frustration else 0,
                json.dumps(frustration_signals) if frustration_signals else None,
                decision_id
            ))
            conn.commit()

            if cursor.rowcount == 0:
                import sys
                print(f"[WARNING] Decision ID {decision_id} not found", file=sys.stderr)

        except Exception as e:
            # Non-blocking: log to stderr but don't crash
            import sys
            print(f"[WARNING] Failed to record outcome: {e}", file=sys.stderr)
        finally:
            conn.close()

    def detect_user_frustration(self, user_message: str) -> Dict[str, Any]:
        """
        Detect frustration signals in user message.

        Args:
            user_message: User's message text

        Returns:
            {
                'frustrated': bool,
                'signals': List[str],
                'confidence': float
            }

        Example:
            result = tracker.detect_user_frustration("Why didn't you check the file?")
            # Returns: {'frustrated': True, 'signals': ['questioning_failure'], 'confidence': 0.8}
        """
        signals = []
        message_lower = user_message.lower()

        # Pattern matching for frustration signals
        patterns = {
            'repeated_correction': [
                r'still (not|wrong|broken|incorrect)',
                r'again[,\s]',
                r'i (told|said|asked) you',
                r'multiple times',
                r'keep (doing|making|saying)'
            ],
            'questioning_failure': [
                r'why (didn\'t|did not) you',
                r'why (aren\'t|are not) you',
                r'how is this',
                r'what happened to'
            ],
            'expressing_disappointment': [
                r'i thought you (would|could)',
                r'i expected',
                r'you (should have|should\'ve)',
                r'disappointed'
            ],
            'direct_frustration': [
                r'frustrat(ed|ing)',
                r'annoying',
                r'wast(e|ing) (my )?time',
                r'not helpful',
                r'giving up',
                r'wrong',
                r'incorrect'
            ],
            'emphatic_language': [
                r'!!!',
                r'PLEASE',
                r'JUST',
                r'STOP'
            ]
        }

        for signal_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, message_lower):
                    signals.append(signal_type)
                    break  # Only count each signal type once

        frustrated = len(signals) > 0
        confidence = min(len(signals) * 0.4, 1.0)  # 0.4 per signal, max 1.0

        return {
            'frustrated': frustrated,
            'signals': signals,
            'confidence': confidence
        }

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent decisions with outcomes.

        Args:
            limit: Number of decisions to return

        Returns:
            List of decision dictionaries

        Example:
            recent = tracker.get_recent_decisions(limit=5)
            for decision in recent:
                print(f"{decision['action_taken']}: {decision['outcome']}")
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM v_recent_decisions
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            import sys
            print(f"[WARNING] Failed to get recent decisions: {e}", file=sys.stderr)
            return []
        finally:
            conn.close()

    def get_stats(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a project.

        Args:
            project_path: Project to analyze (defaults to current)

        Returns:
            {
                'total_decisions': int,
                'success_rate': float,
                'avg_time_to_resolution': float,
                'frustration_rate': float,
                'decisions_by_type': Dict[str, int]
            }

        Example:
            stats = tracker.get_stats()
            print(f"Success rate: {stats['success_rate']:.1%}")
        """
        conn = self._get_connection()
        try:
            project = project_path or self.project_path
            cursor = conn.cursor()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(time_to_resolution_seconds) as avg_time,
                    AVG(CASE WHEN user_frustration_detected = 1 THEN 1.0 ELSE 0.0 END) as frustration_rate
                FROM decisions
                WHERE project_path = ?
            """, (project,))

            row = cursor.fetchone()
            stats = {
                'total_decisions': row['total'],
                'success_rate': row['success_rate'] or 0.0,
                'avg_time_to_resolution': row['avg_time'] or 0.0,
                'frustration_rate': row['frustration_rate'] or 0.0
            }

            # Decisions by type
            cursor.execute("""
                SELECT decision_type, COUNT(*) as count
                FROM decisions
                WHERE project_path = ?
                GROUP BY decision_type
            """, (project,))

            stats['decisions_by_type'] = {
                row['decision_type']: row['count']
                for row in cursor.fetchall()
            }

            return stats

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to get stats: {e}", file=sys.stderr)
            return {
                'total_decisions': 0,
                'success_rate': 0.0,
                'avg_time_to_resolution': 0.0,
                'frustration_rate': 0.0,
                'decisions_by_type': {}
            }
        finally:
            conn.close()

    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get statistics across all projects.

        Returns:
            {
                'total_decisions': int,
                'total_projects': int,
                'success_rate': float,
                'avg_time_to_resolution': float,
                'frustration_rate': float,
                'top_decision_types': List[Dict]
            }
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT project_path) as projects,
                    AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(time_to_resolution_seconds) as avg_time,
                    AVG(CASE WHEN user_frustration_detected = 1 THEN 1.0 ELSE 0.0 END) as frustration_rate
                FROM decisions
            """)

            row = cursor.fetchone()
            stats = {
                'total_decisions': row['total'],
                'total_projects': row['projects'],
                'success_rate': row['success_rate'] or 0.0,
                'avg_time_to_resolution': row['avg_time'] or 0.0,
                'frustration_rate': row['frustration_rate'] or 0.0
            }

            # Top decision types
            cursor.execute("""
                SELECT
                    decision_type,
                    COUNT(*) as count,
                    AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END) as success_rate
                FROM decisions
                GROUP BY decision_type
                ORDER BY count DESC
                LIMIT 5
            """)

            stats['top_decision_types'] = [
                {
                    'type': row['decision_type'],
                    'count': row['count'],
                    'success_rate': row['success_rate']
                }
                for row in cursor.fetchall()
            ]

            return stats

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to get global stats: {e}", file=sys.stderr)
            return {
                'total_decisions': 0,
                'total_projects': 0,
                'success_rate': 0.0,
                'avg_time_to_resolution': 0.0,
                'frustration_rate': 0.0,
                'top_decision_types': []
            }
        finally:
            conn.close()

    def log_lesson(
        self,
        source_file: str,
        source_type: str,
        lesson_text: str,
        category: Optional[str] = None,
        severity: str = 'medium'
    ) -> int:
        """
        Log a lesson scraped from existing files.

        Args:
            source_file: Path to the source file
            source_type: 'lessons_md', 'context_md', 'memory_md'
            lesson_text: The lesson content
            category: Category of the lesson
            severity: 'low', 'medium', 'high'

        Returns:
            lesson_id: ID for this lesson
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Check if lesson already exists
            cursor.execute("""
                SELECT id, occurrence_count, last_seen
                FROM lesson_records
                WHERE source_file = ? AND lesson_text = ?
            """, (source_file, lesson_text))

            row = cursor.fetchone()

            if row:
                # Update existing lesson
                cursor.execute("""
                    UPDATE lesson_records
                    SET occurrence_count = occurrence_count + 1,
                        last_seen = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (datetime.now().isoformat(), row['id']))
                conn.commit()
                return row['id']
            else:
                # Insert new lesson
                cursor.execute("""
                    INSERT INTO lesson_records (
                        source_file,
                        source_type,
                        lesson_text,
                        category,
                        severity,
                        first_seen,
                        last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    source_file,
                    source_type,
                    lesson_text,
                    category,
                    severity,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return cursor.lastrowid

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to log lesson: {e}", file=sys.stderr)
            return None
        finally:
            conn.close()


# Convenience functions for quick usage
def track_decision(
    decision_type: str,
    action_taken: str,
    rule_source: Optional[str] = None,
    rule_text: Optional[str] = None
) -> int:
    """
    Quick function to log a decision without creating tracker instance.

    Returns decision_id for use with track_outcome.
    """
    tracker = BillyTracker()
    return tracker.log_decision(decision_type, action_taken, rule_source, rule_text)


def track_outcome(
    decision_id: int,
    outcome: str,
    evidence: Optional[str] = None,
    time_elapsed: Optional[int] = None
) -> None:
    """
    Quick function to record outcome without creating tracker instance.
    """
    tracker = BillyTracker()
    tracker.record_outcome(decision_id, outcome, evidence, time_elapsed)
