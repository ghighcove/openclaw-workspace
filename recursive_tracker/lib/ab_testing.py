"""
A/B Testing Framework - Test instruction variants.

Compare control vs variant instructions to determine which performs better.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import math


class ABTestFramework:
    """Manages A/B testing of instruction variants."""

    def __init__(self, db_path: Path = None):
        """Initialize framework."""
        if db_path is None:
            lib_dir = Path(__file__).parent
            db_path = lib_dir.parent / "data" / "billy_feedback.db"

        self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_experiment(
        self,
        experiment_name: str,
        decision_type: str,
        control_text: str,
        variant_text: str
    ) -> int:
        """
        Create a new A/B test experiment.

        Args:
            experiment_name: Unique name for the experiment
            decision_type: Type of decision being tested
            control_text: Current instruction (control)
            variant_text: New instruction to test (variant)

        Returns:
            Experiment ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Check if experiment already exists
            cursor.execute("""
                SELECT id FROM instruction_experiments
                WHERE experiment_name = ?
            """, (experiment_name,))

            if cursor.fetchone():
                raise ValueError(f"Experiment '{experiment_name}' already exists")

            # Create experiment
            cursor.execute("""
                INSERT INTO instruction_experiments (
                    experiment_name,
                    decision_type,
                    control_text,
                    variant_text,
                    status,
                    started_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                experiment_name,
                decision_type,
                control_text,
                variant_text,
                'running',
                datetime.now().isoformat()
            ))

            conn.commit()
            return cursor.lastrowid

        finally:
            conn.close()

    def record_decision(
        self,
        experiment_name: str,
        variant: str,
        outcome: str
    ) -> None:
        """
        Record a decision outcome for an experiment.

        Args:
            experiment_name: Name of the experiment
            variant: 'control' or 'variant'
            outcome: 'success', 'failure', or 'user_correction'
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get experiment
            cursor.execute("""
                SELECT id, status FROM instruction_experiments
                WHERE experiment_name = ?
            """, (experiment_name,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Experiment '{experiment_name}' not found")

            if row['status'] != 'running':
                raise ValueError(f"Experiment is not running (status: {row['status']})")

            experiment_id = row['id']

            # Update counts
            if variant == 'control':
                if outcome == 'success':
                    cursor.execute("""
                        UPDATE instruction_experiments
                        SET control_success_count = control_success_count + 1,
                            control_total_count = control_total_count + 1
                        WHERE id = ?
                    """, (experiment_id,))
                else:
                    cursor.execute("""
                        UPDATE instruction_experiments
                        SET control_total_count = control_total_count + 1
                        WHERE id = ?
                    """, (experiment_id,))
            elif variant == 'variant':
                if outcome == 'success':
                    cursor.execute("""
                        UPDATE instruction_experiments
                        SET variant_success_count = variant_success_count + 1,
                            variant_total_count = variant_total_count + 1
                        WHERE id = ?
                    """, (experiment_id,))
                else:
                    cursor.execute("""
                        UPDATE instruction_experiments
                        SET variant_total_count = variant_total_count + 1
                        WHERE id = ?
                    """, (experiment_id,))
            else:
                raise ValueError(f"Invalid variant: {variant}")

            conn.commit()

        finally:
            conn.close()

    def calculate_statistics(self, experiment_name: str) -> Dict[str, Any]:
        """
        Calculate statistics for an experiment.

        Args:
            experiment_name: Name of the experiment

        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM instruction_experiments
                WHERE experiment_name = ?
            """, (experiment_name,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Experiment '{experiment_name}' not found")

            experiment = dict(row)

            # Calculate success rates
            if experiment['control_total_count'] > 0:
                experiment['control_success_rate'] = (
                    experiment['control_success_count'] / experiment['control_total_count']
                )
            else:
                experiment['control_success_rate'] = None

            if experiment['variant_total_count'] > 0:
                experiment['variant_success_rate'] = (
                    experiment['variant_success_count'] / experiment['variant_total_count']
                )
            else:
                experiment['variant_success_rate'] = None

            # Calculate p-value using z-test
            if (experiment['control_success_rate'] is not None and
                experiment['variant_success_rate'] is not None and
                experiment['control_total_count'] >= 10 and
                experiment['variant_total_count'] >= 10):

                # Pooled proportion
                p1 = experiment['control_success_rate']
                p2 = experiment['variant_success_rate']
                n1 = experiment['control_total_count']
                n2 = experiment['variant_total_count']

                # Z-test for two proportions
                p_pooled = (p1 * n1 + p2 * n2) / (n1 + n2)
                se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

                if se > 0:
                    z = (p2 - p1) / se
                    # Two-tailed p-value
                    import scipy.stats as stats
                    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
                    experiment['p_value'] = p_value
                    experiment['confidence_level'] = 1 - p_value
                else:
                    experiment['p_value'] = None
                    experiment['confidence_level'] = None
            else:
                experiment['p_value'] = None
                experiment['confidence_level'] = None

            # Determine winner
            if experiment['control_success_rate'] is not None and experiment['variant_success_rate'] is not None:
                if experiment['p_value'] is not None and experiment['p_value'] < 0.05:
                    # Statistically significant
                    if experiment['variant_success_rate'] > experiment['control_success_rate']:
                        experiment['winner'] = 'variant'
                    else:
                        experiment['winner'] = 'control'
                else:
                    experiment['winner'] = 'inconclusive'
            else:
                experiment['winner'] = None

            return experiment

        finally:
            conn.close()

    def complete_experiment(
        self,
        experiment_name: str,
        recommendation: str = None
    ) -> Dict[str, Any]:
        """
        Mark an experiment as complete and generate report.

        Args:
            experiment_name: Name of the experiment
            recommendation: Optional recommendation text

        Returns:
            Final experiment report
        """
        conn = self._get_connection()
        try:
            # Calculate final statistics
            report = self.calculate_statistics(experiment_name)

            # Update experiment status
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE instruction_experiments
                SET status = 'completed',
                    completed_at = ?,
                    control_success_rate = ?,
                    variant_success_rate = ?,
                    p_value = ?,
                    confidence_level = ?,
                    winner = ?,
                    recommendation = ?
                WHERE experiment_name = ?
            """, (
                datetime.now().isoformat(),
                report.get('control_success_rate'),
                report.get('variant_success_rate'),
                report.get('p_value'),
                report.get('confidence_level'),
                report.get('winner'),
                recommendation,
                experiment_name
            ))

            conn.commit()
            return report

        finally:
            conn.close()

    def generate_report(self, experiment_name: str) -> str:
        """Generate a human-readable experiment report."""
        try:
            stats = self.calculate_statistics(experiment_name)

            report = []
            report.append("=" * 60)
            report.append(f"A/B Test Report: {experiment_name}")
            report.append("=" * 60)
            report.append(f"Decision Type: {stats['decision_type']}")
            report.append(f"Status: {stats['status']}")
            report.append("")

            report.append("Control:")
            report.append(f"  Text: {stats['control_text'][:60]}...")
            report.append(f"  Total: {stats['control_total_count']}")
            report.append(f"  Success: {stats['control_success_count']}")
            report.append(f"  Success Rate: {stats['control_success_rate']:.1%}" if stats['control_success_rate'] else "  Success Rate: N/A")
            report.append("")

            report.append("Variant:")
            report.append(f"  Text: {stats['variant_text'][:60]}...")
            report.append(f"  Total: {stats['variant_total_count']}")
            report.append(f"  Success: {stats['variant_success_count']}")
            report.append(f"  Success Rate: {stats['variant_success_rate']:.1%}" if stats['variant_success_rate'] else "  Success Rate: N/A")
            report.append("")

            if stats['p_value'] is not None:
                report.append(f"P-value: {stats['p_value']:.4f}")
                report.append(f"Confidence: {stats['confidence_level']:.1%}")
                report.append("")

            if stats['winner']:
                report.append(f"Winner: {stats['winner'].upper()}")

                if stats['winner'] == 'variant':
                    improvement = (stats['variant_success_rate'] - stats['control_success_rate']) / stats['control_success_rate']
                    report.append(f"Improvement: {improvement:.1%}")
            else:
                report.append("Winner: Inconclusive")

            if stats.get('recommendation'):
                report.append("")
                report.append(f"Recommendation: {stats['recommendation']}")

            report.append("=" * 60)

            return "\n".join(report)

        except Exception as e:
            return f"Error generating report: {e}"
