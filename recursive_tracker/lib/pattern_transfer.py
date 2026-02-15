"""
Cross-Project Pattern Transfer - Transfer proven patterns between projects.

Transfers successful patterns from one project to others and tracks effectiveness.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class PatternTransfer:
    """Manages cross-project pattern transfers."""

    def __init__(self, db_path: Path = None):
        """Initialize transfer system."""
        if db_path is None:
            lib_dir = Path(__file__).parent
            db_path = lib_dir.parent / "data" / "billy_feedback.db"

        self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def find_transfer_candidates(self, min_occurrences: int = 3, success_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find patterns that could be transferred to other projects.

        Args:
            min_occurrences: Minimum pattern occurrences
            success_threshold: Minimum success rate

        Returns:
            List of transfer candidates
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Find successful patterns (without JSON functions)
            cursor.execute("""
                SELECT
                    pi.id,
                    pi.pattern_name,
                    pi.pattern_type,
                    pi.decision_type,
                    pi.occurrence_count,
                    pi.projects_affected,
                    pi.description,
                    pi.occurrence_count as success_count,
                    pi.occurrence_count as total_count
                FROM pattern_instances pi
                WHERE pi.pattern_type = 'success_pattern'
                AND pi.occurrence_count >= ?
                AND pi.promoted = 0
                ORDER BY pi.occurrence_count DESC
            """, (min_occurrences,))

            candidates = []
            for row in cursor.fetchall():
                # Since these are success patterns, assume 100% success rate
                candidate = dict(row)
                if candidate['total_count'] >= min_occurrences:
                    candidates.append(candidate)

            return candidates

        finally:
            conn.close()

    def propose_transfer(
        self,
        pattern_id: int,
        source_project: str,
        target_projects: List[str],
        effectiveness_window_days: int = 14
    ) -> int:
        """
        Propose transferring a pattern to other projects.

        Args:
            pattern_id: ID of the pattern to transfer
            source_project: Project where pattern was discovered
            target_projects: List of target project paths
            effectiveness_window_days: Days to track effectiveness

        Returns:
            Transfer ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Check if transfer already exists
            cursor.execute("""
                SELECT id FROM knowledge_transfers
                WHERE pattern_id = ? AND status = 'deployed'
            """, (pattern_id,))

            if cursor.fetchone():
                raise ValueError(f"Pattern {pattern_id} already transferred")

            # Insert transfer proposal
            cursor.execute("""
                INSERT INTO knowledge_transfers (
                    pattern_id,
                    source_project,
                    target_projects,
                    transfer_date,
                    effectiveness_window_days,
                    status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                source_project,
                str(target_projects),
                datetime.now().isoformat(),
                effectiveness_window_days,
                'proposed'
            ))

            conn.commit()
            return cursor.lastrowid

        finally:
            conn.close()

    def approve_transfer(self, transfer_id: int) -> bool:
        """Mark a transfer as approved and deploy it."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE knowledge_transfers
                SET status = 'deployed'
                WHERE id = ?
            """, (transfer_id,))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def record_transfer_outcome(
        self,
        transfer_id: int,
        success: bool
    ) -> None:
        """
        Record the outcome of applying a transferred pattern.

        Args:
            transfer_id: ID of the transfer
            success: Whether the application was successful
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE knowledge_transfers
                SET success_count = success_count + ?,
                    total_count = total_count + 1,
                    transfer_success_rate = CAST(success_count AS REAL) / total_count
                WHERE id = ?
            """, (1 if success else 0, transfer_id))

            conn.commit()

        finally:
            conn.close()

    def evaluate_transfer_effectiveness(self, transfer_id: int) -> Dict[str, Any]:
        """
        Evaluate the effectiveness of a transfer.

        Args:
            transfer_id: ID of the transfer

        Returns:
            Dictionary with effectiveness metrics
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM knowledge_transfers
                WHERE id = ?
            """, (transfer_id,))

            transfer = dict(cursor.fetchone())

            # Determine status based on effectiveness
            if transfer['total_count'] >= 5:
                if transfer['transfer_success_rate'] >= 0.7:
                    transfer['evaluated_status'] = 'proven'
                else:
                    transfer['evaluated_status'] = 'ineffective'
            else:
                transfer['evaluated_status'] = transfer['status']

            return transfer

        finally:
            conn.close()

    def get_successful_transfers(self) -> List[Dict[str, Any]]:
        """Get all proven transfers that can be reused."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    kt.*,
                    pi.pattern_name,
                    pi.decision_type
                FROM knowledge_transfers kt
                JOIN pattern_instances pi ON kt.pattern_id = pi.id
                WHERE kt.status = 'proven'
                ORDER BY kt.transfer_success_rate DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def generate_transfer_report(self) -> str:
        """Generate a report of pattern transfers."""
        successful = self.get_successful_transfers()

        if not successful:
            return "No successful transfers recorded yet."

        report = []
        report.append("=" * 60)
        report.append("Cross-Project Pattern Transfer Report")
        report.append("=" * 60)
        report.append(f"Proven transfers: {len(successful)}")
        report.append("")

        for i, transfer in enumerate(successful, 1):
            report.append(f"{i}. {transfer['pattern_name']}")
            report.append(f"   Decision Type: {transfer['decision_type']}")
            report.append(f"   Success Rate: {transfer['transfer_success_rate']:.1%}")
            report.append(f"   Applications: {transfer['total_count']}")
            report.append(f"   Source: {transfer['source_project']}")
            report.append("")

        return "\n".join(report)
