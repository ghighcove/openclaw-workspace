"""
Pattern Detector - Analyzes decisions to detect patterns.

Identifies success patterns, failure patterns, and correction patterns
across Billy's decisions.
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class PatternDetector:
    """Detects patterns in Billy's decisions."""

    def __init__(self, db_path: Path = None):
        """Initialize detector."""
        if db_path is None:
            lib_dir = Path(__file__).parent
            db_path = lib_dir.parent / "data" / "billy_feedback.db"

        self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common stop words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by']
        for word in stop_words:
            text = re.sub(r'\b' + word + r'\b', '', text)
        return text.strip()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0.0 to 1.0)."""
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)

        if not norm1 or not norm2:
            return 0.0

        words1 = set(norm1.split())
        words2 = set(norm2.split())

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union

    def detect_success_patterns(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """
        Detect patterns in successful decisions.

        Args:
            min_occurrences: Minimum times pattern must appear

        Returns:
            List of detected patterns
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get all successful decisions
            cursor.execute("""
                SELECT id, decision_type, action_taken, rule_source, rule_text
                FROM decisions
                WHERE outcome = 'success'
                ORDER BY timestamp
            """)

            decisions = [dict(row) for row in cursor.fetchall()]
            patterns = []

            # Group by decision type
            by_type = defaultdict(list)
            for decision in decisions:
                by_type[decision['decision_type']].append(decision)

            # Find patterns within each type
            for decision_type, type_decisions in by_type.items():
                if len(type_decisions) < min_occurrences:
                    continue

                # Find similar actions
                similar_groups = []
                processed = set()

                for i, d1 in enumerate(type_decisions):
                    if i in processed:
                        continue

                    group = [d1]
                    processed.add(i)

                    for j, d2 in enumerate(type_decisions):
                        if j in processed or j <= i:
                            continue

                        similarity = self._calculate_similarity(
                            d1['action_taken'],
                            d2['action_taken']
                        )

                        if similarity >= 0.5:  # 50% similarity threshold
                            group.append(d2)
                            processed.add(j)

                    if len(group) >= min_occurrences:
                        similar_groups.append(group)

                # Create patterns from groups
                for group in similar_groups:
                    # Extract common words
                    all_actions = [d['action_taken'] for d in group]
                    pattern_name = self._extract_pattern_name(all_actions)

                    # Determine rule prevalence
                    rules = [d['rule_source'] for d in group if d['rule_source']]
                    rule_source = max(set(rules), key=rules.count) if rules else 'none'

                    pattern = {
                        'pattern_name': pattern_name,
                        'pattern_type': 'success_pattern',
                        'decision_type': decision_type,
                        'occurrence_count': len(group),
                        'decision_ids': [d['id'] for d in group],
                        'rule_source': rule_source,
                        'examples': [d['action_taken'][:60] + '...' for d in group[:3]]
                    }

                    patterns.append(pattern)

            return patterns

        finally:
            conn.close()

    def detect_failure_patterns(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """
        Detect patterns in failed decisions.

        Args:
            min_occurrences: Minimum times pattern must appear

        Returns:
            List of detected patterns
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get all failed decisions
            cursor.execute("""
                SELECT id, decision_type, action_taken, outcome_evidence
                FROM decisions
                WHERE outcome = 'failure' OR outcome = 'user_correction'
                ORDER BY timestamp
            """)

            decisions = [dict(row) for row in cursor.fetchall()]
            patterns = []

            if len(decisions) < min_occurrences:
                return patterns

            # Group by decision type
            by_type = defaultdict(list)
            for decision in decisions:
                by_type[decision['decision_type']].append(decision)

            # Find patterns within each type
            for decision_type, type_decisions in by_type.items():
                if len(type_decisions) < min_occurrences:
                    continue

                # Find similar actions
                similar_groups = []
                processed = set()

                for i, d1 in enumerate(type_decisions):
                    if i in processed:
                        continue

                    group = [d1]
                    processed.add(i)

                    for j, d2 in enumerate(type_decisions):
                        if j in processed or j <= i:
                            continue

                        similarity = self._calculate_similarity(
                            d1['action_taken'],
                            d2['action_taken']
                        )

                        if similarity >= 0.5:
                            group.append(d2)
                            processed.add(j)

                    if len(group) >= min_occurrences:
                        similar_groups.append(group)

                # Create patterns from groups
                for group in similar_groups:
                    all_actions = [d['action_taken'] for d in group]
                    pattern_name = self._extract_pattern_name(all_actions)

                    # Calculate total time wasted
                    total_wasted = sum(
                        d.get('time_to_resolution_seconds', 0) or 0
                        for d in group
                    )

                    # Determine severity
                    severity = 'low'
                    if len(group) >= 3 or total_wasted > 600:
                        severity = 'high'
                    elif total_wasted > 300:
                        severity = 'medium'

                    pattern = {
                        'pattern_name': pattern_name,
                        'pattern_type': 'failure_pattern',
                        'decision_type': decision_type,
                        'occurrence_count': len(group),
                        'decision_ids': [d['id'] for d in group],
                        'total_time_wasted': total_wasted,
                        'severity': severity,
                        'examples': [d['action_taken'][:60] + '...' for d in group[:3]]
                    }

                    patterns.append(pattern)

            return patterns

        finally:
            conn.close()

    def _extract_pattern_name(self, actions: List[str]) -> str:
        """Extract a common pattern name from similar actions."""
        if not actions:
            return "Unknown Pattern"

        # Get first action as base
        base = actions[0]

        # Extract key words (verbs, nouns)
        words = self._normalize_text(base).split()

        # Keep first 3-4 meaningful words
        key_words = [w for w in words if len(w) > 3][:4]

        if key_words:
            return ' '.join(key_words).title()
        else:
            return base[:50] + '...'

    def detect_all_patterns(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """
        Detect all patterns (success and failure).

        Args:
            min_occurrences: Minimum times pattern must appear

        Returns:
            List of all detected patterns
        """
        success_patterns = self.detect_success_patterns(min_occurrences)
        failure_patterns = self.detect_failure_patterns(min_occurrences)

        return success_patterns + failure_patterns

    def save_patterns(self, patterns: List[Dict[str, Any]]) -> int:
        """
        Save detected patterns to database.

        Args:
            patterns: List of patterns to save

        Returns:
            Number of patterns saved
        """
        conn = self._get_connection()
        try:
            saved = 0

            for pattern in patterns:
                # Check if pattern already exists
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, occurrence_count
                    FROM pattern_instances
                    WHERE pattern_name = ? AND decision_type = ? AND pattern_type = ?
                """, (
                    pattern['pattern_name'],
                    pattern['decision_type'],
                    pattern['pattern_type']
                ))

                row = cursor.fetchone()

                now = datetime.now().isoformat()

                if row:
                    # Update existing pattern
                    pattern_id = row['id']
                    cursor.execute("""
                        UPDATE pattern_instances
                        SET occurrence_count = occurrence_count + ?,
                            last_seen = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (
                        pattern['occurrence_count'],
                        now,
                        now,
                        pattern_id
                    ))
                else:
                    # Insert new pattern
                    # Calculate projects affected
                    cursor.execute("""
                        SELECT DISTINCT project_path
                        FROM decisions
                        WHERE id IN ({})
                    """.format(','.join(map(str, pattern['decision_ids']))))

                    projects = [row['project_path'] for row in cursor.fetchall()]

                    cursor.execute("""
                        INSERT INTO pattern_instances (
                            pattern_name,
                            pattern_type,
                            description,
                            occurrence_count,
                            first_seen,
                            last_seen,
                            projects_affected,
                            decision_ids,
                            decision_type,
                            severity,
                            total_time_wasted_seconds,
                            promotion_candidate
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        pattern['pattern_name'],
                        pattern['pattern_type'],
                        f"{pattern['decision_type']}: {pattern['pattern_name']}",
                        pattern['occurrence_count'],
                        now,
                        now,
                        str(projects),
                        str(pattern['decision_ids']),
                        pattern['decision_type'],
                        pattern.get('severity', 'low'),
                        pattern.get('total_time_wasted', 0),
                        pattern['pattern_type'] == 'failure_pattern' or
                        pattern['occurrence_count'] >= 3
                    ))

                    pattern_id = cursor.lastrowid

                conn.commit()
                saved += 1

            return saved

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to save patterns: {e}", file=sys.stderr)
            return 0
        finally:
            conn.close()

    def get_promotion_candidates(self) -> List[Dict[str, Any]]:
        """
        Get patterns ready for promotion to CLAUDE.md.

        Returns:
            List of promotion candidates
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM v_promotion_candidates
                ORDER BY severity DESC, occurrence_count DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def promote_pattern(
        self,
        pattern_id: int,
        target_file: str,
        target_section: str = None,
        proposed_by: str = "Billy Byte"
    ) -> bool:
        """
        Promote a pattern to a rule proposal.

        Args:
            pattern_id: ID of pattern to promote
            target_file: Where the rule should be added
            target_section: Section within the target file
            proposed_by: Who is proposing this

        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get pattern details
            cursor.execute("""
                SELECT * FROM pattern_instances
                WHERE id = ?
            """, (pattern_id,))

            pattern = dict(cursor.fetchone())

            if not pattern:
                return False

            # Determine severity
            severity = pattern.get('severity', 'medium')

            # Generate rule text based on pattern type
            if pattern['pattern_type'] == 'failure_pattern':
                rule_text = f"AVOID: {pattern['pattern_name']} - This pattern has failed {pattern['occurrence_count']} times"
            else:
                rule_text = f"DO: {pattern['pattern_name']} - This pattern has succeeded {pattern['occurrence_count']} times"

            # Insert rule promotion
            cursor.execute("""
                INSERT INTO rule_promotions (
                    pattern_id,
                    promotion_date,
                    source_projects,
                    occurrence_count,
                    severity,
                    time_wasted_seconds,
                    rule_text,
                    target_file,
                    target_section,
                    status,
                    approved_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                datetime.now().isoformat(),
                pattern['projects_affected'],
                pattern['occurrence_count'],
                severity,
                pattern.get('total_time_wasted_seconds', 0),
                rule_text,
                target_file,
                target_section,
                'proposed',
                proposed_by
            ))

            # Update pattern
            cursor.execute("""
                UPDATE pattern_instances
                SET promotion_candidate = 0
                WHERE id = ?
            """, (pattern_id,))

            conn.commit()
            return True

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to promote pattern: {e}", file=sys.stderr)
            return False
        finally:
            conn.close()

    def generate_pattern_report(self) -> str:
        """Generate a text report of detected patterns."""
        patterns = self.get_promotion_candidates()

        if not patterns:
            return "No patterns detected yet."

        report = []
        report.append("=" * 60)
        report.append("Pattern Detection Report")
        report.append("=" * 60)
        report.append(f"Total patterns: {len(patterns)}")
        report.append("")

        for i, pattern in enumerate(patterns, 1):
            report.append(f"{i}. {pattern['pattern_name']}")
            report.append(f"   Type: {pattern['pattern_type']}")
            report.append(f"   Decision Type: {pattern['decision_type']}")
            report.append(f"   Occurrences: {pattern['occurrence_count']}")
            report.append(f"   Severity: {pattern['severity']}")
            if pattern.get('total_time_wasted_seconds'):
                mins = pattern['total_time_wasted_seconds'] / 60
                report.append(f"   Time Wasted: {mins:.1f} minutes")
            report.append("")

        return "\n".join(report)
