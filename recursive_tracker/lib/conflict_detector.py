"""
Conflict Detector - Detects conflicts between rules.

Identifies contradictory, overlapping, or obsolete rules in CLAUDE.md files.
"""

import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict


class ConflictDetector:
    """Detects conflicts between rules."""

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

    def _extract_rules_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from a markdown file."""
        rules = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for rule patterns
            # Pattern 1: ## Rule: or ### Rule:
            rule_pattern = r'#{2,4}\s*(?:Rule|DO|AVOID|CRITICAL)[:\s]+(.+?)(?:\n|$)'
            matches = re.finditer(rule_pattern, content, re.IGNORECASE)

            for match in matches:
                rule_text = match.group(1).strip()
                if len(rule_text) > 10:  # Minimum meaningful length
                    rules.append({
                        'text': rule_text,
                        'line': content[:match.start()].count('\n') + 1
                    })

            # Pattern 2: Bullet points that look like rules
            bullet_pattern = r'^-\s*(?:Always|Never|Must|Should|Avoid|Do|Don\'t)\s+(.+)$'
            matches = re.finditer(bullet_pattern, content, re.MULTILINE)

            for match in matches:
                rule_text = match.group(1).strip()
                if len(rule_text) > 10:
                    rules.append({
                        'text': rule_text,
                        'line': content[:match.start()].count('\n') + 1
                    })

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to read {file_path}: {e}", file=sys.stderr)

        return rules

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        norm1 = text1.lower().strip()
        norm2 = text2.lower().strip()

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

    def detect_contradictions(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect contradictory rules.

        Args:
            rules: List of rules to analyze

        Returns:
            List of contradictions found
        """
        contradictions = []

        # Contradiction keywords
        contradiction_pairs = [
            ('always', 'never'),
            ('must', 'must not'),
            ('should', 'should not'),
            ('do', 'don\'t'),
            ('avoid', 'prefer'),
            ('enable', 'disable'),
            ('include', 'exclude')
        ]

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                text1 = rule1['text'].lower()
                text2 = rule2['text'].lower()

                # Check for direct contradictions
                for word1, word2 in contradiction_pairs:
                    if word1 in text1 and word2 in text2:
                        contradictions.append({
                            'type': 'contradiction',
                            'rule1': rule1,
                            'rule2': rule2,
                            'evidence': f"'{word1}' vs '{word2}'"
                        })
                        break

        return contradictions

    def detect_overlaps(self, rules: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Detect overlapping/similar rules.

        Args:
            rules: List of rules to analyze
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of overlaps found
        """
        overlaps = []

        for i in range(len(rules)):
            for j in range(i + 1, len(rules)):
                rule1 = rules[i]
                rule2 = rules[j]

                similarity = self._calculate_similarity(rule1['text'], rule2['text'])

                if similarity >= threshold:
                    overlaps.append({
                        'type': 'overlap',
                        'rule1': rule1,
                        'rule2': rule2,
                        'similarity': similarity
                    })

        return overlaps

    def scan_workspace(self, workspace_path: Path = None) -> Dict[str, Any]:
        """
        Scan workspace for rule conflicts.

        Args:
            workspace_path: Root directory to scan

        Returns:
            Dictionary with scan results
        """
        if workspace_path is None:
            workspace_path = Path(__file__).parent.parent.parent

        results = {
            'files_scanned': 0,
            'conflicts_found': 0,
            'conflicts': [],
            'files_with_conflicts': []
        }

        # Look for CLAUDE.md files
        claude_md_files = list(workspace_path.rglob('CLAUDE.md'))

        for file_path in claude_md_files:
            # Skip recursive_tracker's own CLAUDE.md
            if 'recursive_tracker' in str(file_path):
                continue

            results['files_scanned'] += 1

            # Extract rules
            rules = self._extract_rules_from_file(file_path)

            if len(rules) < 2:
                continue

            # Detect contradictions
            contradictions = self.detect_contradictions(rules)

            # Detect overlaps
            overlaps = self.detect_overlaps(rules)

            # Combine all conflicts
            all_conflicts = contradictions + overlaps

            if all_conflicts:
                results['conflicts_found'] += len(all_conflicts)
                results['files_with_conflicts'].append({
                    'file': str(file_path.relative_to(workspace_path)),
                    'conflicts': all_conflicts
                })

                # Save to database
                self._save_conflicts(file_path, all_conflicts)

        return results

    def _save_conflicts(self, file_path: Path, conflicts: List[Dict[str, Any]]) -> None:
        """Save conflicts to database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            for conflict in conflicts:
                cursor.execute("""
                    INSERT INTO rule_conflicts (
                        conflict_type,
                        file1_path,
                        rule1_text,
                        rule2_text,
                        decision_type,
                        severity,
                        status,
                        detected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conflict['type'],
                    str(file_path),
                    conflict['rule1']['text'][:500],  # Truncate if too long
                    conflict['rule2'].get('text', '')[:500],
                    'general',  # Generic decision type for conflicts
                    'medium',   # Default severity
                    'detected',
                    datetime.now().isoformat()
                ))

            conn.commit()

        except Exception as e:
            import sys
            print(f"[WARNING] Failed to save conflicts: {e}", file=sys.stderr)
        finally:
            conn.close()

    def get_active_conflicts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) conflicts."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM rule_conflicts
                WHERE status = 'detected'
                ORDER BY severity DESC, detected_at DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def resolve_conflict(self, conflict_id: int, resolution_strategy: str, notes: str = None) -> bool:
        """
        Mark a conflict as resolved.

        Args:
            conflict_id: ID of the conflict
            resolution_strategy: How it was resolved
            notes: Optional resolution notes

        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE rule_conflicts
                SET status = 'resolved',
                    resolution_strategy = ?,
                    resolution_notes = ?,
                    resolved_at = ?
                WHERE id = ?
            """, (
                resolution_strategy,
                notes,
                datetime.now().isoformat(),
                conflict_id
            ))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def generate_conflict_report(self) -> str:
        """Generate a text report of conflicts."""
        conflicts = self.get_active_conflicts()

        if not conflicts:
            return "No active conflicts detected."

        report = []
        report.append("=" * 60)
        report.append("Rule Conflict Report")
        report.append("=" * 60)
        report.append(f"Active conflicts: {len(conflicts)}")
        report.append("")

        for i, conflict in enumerate(conflicts, 1):
            report.append(f"{i}. {conflict['conflict_type'].upper()}")
            report.append(f"   File: {conflict['file1_path']}")
            report.append(f"   Severity: {conflict['severity']}")
            report.append(f"   Rule 1: {conflict['rule1_text'][:60]}...")
            if conflict['rule2_text']:
                report.append(f"   Rule 2: {conflict['rule2_text'][:60]}...")
            report.append(f"   Detected: {conflict['detected_at']}")
            report.append("")

        return "\n".join(report)
