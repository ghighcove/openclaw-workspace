#!/usr/bin/env python3
"""
Initialize Billy Byte's Recursive Improvement Tracker database.

Creates the SQLite database with all necessary tables, indexes, and views.
Safe to run multiple times - won't destroy existing data.
"""

import sqlite3
import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

DB_PATH = PROJECT_ROOT / "data" / "billy_feedback.db"
SCHEMA_PATH = PROJECT_ROOT / "data" / "schema.sql"


def init_database():
    """Initialize database from schema file."""
    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema file not found at {SCHEMA_PATH}")
        sys.exit(1)

    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Read schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Create database
    print(f"Initializing Billy's database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)

    try:
        # Execute schema (creates tables, indexes, views)
        conn.executescript(schema_sql)
        conn.commit()

        # Verify tables created
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n[OK] Database initialized successfully")
        print(f"[OK] Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} rows")

        # Verify views created
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view'
            ORDER BY name
        """)
        views = [row[0] for row in cursor.fetchall()]
        print(f"\n[OK] Created {len(views)} views:")
        for view in views:
            print(f"  - {view}")

        print(f"\nBilly's database ready at: {DB_PATH}")

    except Exception as e:
        print(f"\nERROR: Failed to initialize database")
        print(f"  {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
