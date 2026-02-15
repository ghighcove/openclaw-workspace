#!/usr/bin/env python3
"""
Promote patterns to rules in CLAUDE.md files.

Generates rule proposals and can apply them to target files.
"""

import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from pattern_detector import PatternDetector


def list_proposals():
    """List all rule proposals."""
    print("=" * 60)
    print("Rule Proposals")
    print("=" * 60)

    import sqlite3

    DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        SELECT rp.*, pi.pattern_name
        FROM rule_promotions rp
        JOIN pattern_instances pi ON rp.pattern_id = pi.id
        WHERE rp.status = 'proposed'
        ORDER BY rp.severity DESC, rp.occurrence_count DESC
    """)

    proposals = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not proposals:
        print("[INFO] No rule proposals pending.")
        return []

    print(f"\nFound {len(proposals)} proposals:\n")

    for i, proposal in enumerate(proposals, 1):
        print(f"{i}. {proposal['pattern_name']}")
        print(f"   Rule: {proposal['rule_text']}")
        print(f"   Target: {proposal['target_file']}")
        if proposal['target_section']:
            print(f"   Section: {proposal['target_section']}")
        print(f"   Severity: {proposal['severity']}")
        print(f"   Occurrences: {proposal['occurrence_count']}")
        print(f"   Proposed by: {proposal['approved_by']}")
        print("")

    return proposals


def generate_rule_suggestion(pattern_id):
    """Generate a human-readable rule suggestion."""
    import sqlite3

    DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        SELECT pi.*, rp.rule_text
        FROM pattern_instances pi
        LEFT JOIN rule_promotions rp ON pi.id = rp.pattern_id
        WHERE pi.id = ?
    """, (pattern_id,))

    pattern = dict(cursor.fetchone())
    conn.close()

    if pattern['pattern_type'] == 'failure_pattern':
        # Generate anti-pattern rule
        suggestion = f"""
## Avoid: {pattern['pattern_name']}

**Pattern Type:** {pattern['pattern_type']}
**Decision Type:** {pattern['decision_type']}
**Occurrences:** {pattern['occurrence_count']}
**Severity:** {pattern.get('severity', 'medium')}
**Time Wasted:** {pattern.get('total_time_wasted_seconds', 0)} seconds

### Description
This pattern has failed {pattern['occurrence_count']} times. Avoid this approach.

### Evidence
{pattern.get('rule_text', 'See pattern details')}

### Alternative
Consider alternative approaches for {pattern['decision_type']} decisions.
"""
    else:
        # Generate success pattern rule
        suggestion = f"""
## Recommended: {pattern['pattern_name']}

**Pattern Type:** {pattern['pattern_type']}
**Decision Type:** {pattern['decision_type']}
**Occurrences:** {pattern['occurrence_count']}

### Description
This pattern has succeeded {pattern['occurrence_count']} times. Use this approach when possible.

### Evidence
{pattern.get('rule_text', 'See pattern details')}
"""
    return suggestion


def propose_rule(pattern_id, target_file, target_section=None, approved_by="Billy Byte"):
    """Create a rule proposal."""
    detector = PatternDetector()

    success = detector.promote_pattern(
        pattern_id=pattern_id,
        target_file=target_file,
        target_section=target_section,
        proposed_by=approved_by
    )

    if success:
        print(f"[OK] Created rule proposal for pattern {pattern_id}")
        print(f"[INFO] Target: {target_file}")
        if target_section:
            print(f"[INFO] Section: {target_section}")

        # Show suggestion
        suggestion = generate_rule_suggestion(pattern_id)
        print("\n[INFO] Suggested rule:")
        print("-" * 60)
        print(suggestion)
        print("-" * 60)
    else:
        print(f"[ERROR] Failed to create rule proposal")

    return success


def apply_rule(proposal_id, dry_run=True):
    """
    Apply a proposed rule to target file.

    Args:
        proposal_id: ID of the proposal to apply
        dry_run: If True, show what would be done without applying
    """
    import sqlite3

    DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        SELECT rp.*, pi.pattern_name, pi.decision_type
        FROM rule_promotions rp
        JOIN pattern_instances pi ON rp.pattern_id = pi.id
        WHERE rp.id = ?
    """, (proposal_id,))

    proposal = dict(cursor.fetchone())

    if not proposal:
        print(f"[ERROR] Proposal {proposal_id} not found")
        conn.close()
        return False

    if proposal['status'] != 'proposed':
        print(f"[INFO] Proposal already {proposal['status']}")
        conn.close()
        return False

    # Generate rule text
    rule_text = f"""
### Pattern-Based Rule: {proposal['pattern_name']}

**Source:** Pattern detection (occurrences: {proposal['occurrence_count']})
**Severity:** {proposal['severity']}

{proposal['rule_text']}

---

"""

    if dry_run:
        print("[DRY RUN] Would add this rule to:", proposal['target_file'])
        print("")
        print(rule_text)
        print("[DRY RUN] Use --apply to actually add the rule")
    else:
        # Find target file
        if proposal['target_file'] == 'global_claude_md':
            target_path = PROJECT_ROOT.parent / "CLAUDE.md"
        elif proposal['target_file'] == 'agents_md':
            target_path = PROJECT_ROOT.parent / "AGENTS.md"
        else:
            target_path = Path(proposal['target_file'])

        if not target_path.exists():
            print(f"[ERROR] Target file not found: {target_path}")
            conn.close()
            return False

        # Read existing content
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find insertion point
        if proposal['target_section']:
            # Try to find the section
            section_pattern = f"##\\s*{proposal['target_section']}"
            import re
            match = re.search(section_pattern, content, re.IGNORECASE)

            if match:
                # Insert after the section header
                insert_pos = match.end()
                content = content[:insert_pos] + "\n" + rule_text + "\n" + content[insert_pos:]
            else:
                # Append to end of file
                content += "\n" + rule_text + "\n"
        else:
            # Append to end of file
            content += "\n" + rule_text + "\n"

        # Write back
        if not dry_run:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] Applied rule to: {target_path}")

            # Update proposal status
            cursor.execute("""
                UPDATE rule_promotions
                SET status = 'deployed',
                    deployed_at = datetime('now')
                WHERE id = ?
            """, (proposal_id,))
            conn.commit()

    conn.close()
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Promote patterns to rules')
    subparsers = parser.add_subparsers(dest='command', help='Command')

    # List proposals
    subparsers.add_parser('list', help='List pending proposals')

    # Propose rule
    propose_parser = subparsers.add_parser('propose', help='Create a rule proposal')
    propose_parser.add_argument('--pattern-id', type=int, required=True,
                                help='Pattern ID to promote')
    propose_parser.add_argument('--target', type=str, required=True,
                                help='Target file (global_claude_md, agents_md, or path)')
    propose_parser.add_argument('--section', type=str,
                                help='Target section within file')

    # Apply rule
    apply_parser = subparsers.add_parser('apply', help='Apply a proposed rule')
    apply_parser.add_argument('--proposal-id', type=int, required=True,
                             help='Proposal ID to apply')
    apply_parser.add_argument('--dry-run', action='store_true',
                             help='Show what would be done without applying')

    args = parser.parse_args()

    if args.command == 'list':
        list_proposals()
    elif args.command == 'propose':
        propose_rule(
            pattern_id=args.pattern_id,
            target_file=args.target,
            target_section=args.section
        )
    elif args.command == 'apply':
        apply_rule(
            proposal_id=args.proposal_id,
            dry_run=args.dry_run
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
