#!/usr/bin/env python3
"""
Scrape lessons from existing files in the workspace.

Searches for lessons_md, context_md, and memory_md files and extracts lessons.
"""

import sys
import re
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from billy_tracker import BillyTracker


# Pattern for detecting lessons in markdown files
LESSON_PATTERNS = [
    # Match lessons in lessons.md files
    r'#{2,4}\s+Lesson:\s+(.+?)(?:\n|$)',
    r'#{2,4}\s+(.+(?:lesson|Lesson|LESSON).+?)(?:\n|$)',
    # Match items in bullet lists that look like lessons
    r'^-\s+(.+?(?:should|must|always|never|avoid|ensure|verify).+)$',
    # Match specific lesson formats
    r'^#{2,4}\s+(.+?)(?:\n-+\n)',
]


def detect_severity(text):
    """Detect severity of a lesson based on keywords."""
    text_lower = text.lower()

    high_keywords = ['critical', 'severe', 'blocker', 'failure', 'error', 'break', 'destroy']
    low_keywords = ['suggestion', 'consider', 'optional', 'nice to have', 'improvement']

    for keyword in high_keywords:
        if keyword in text_lower:
            return 'high'

    for keyword in low_keywords:
        if keyword in text_lower:
            return 'low'

    return 'medium'


def categorize_lesson(text):
    """Categorize a lesson based on keywords."""
    text_lower = text.lower()

    categories = {
        'verification': ['verify', 'check', 'validate', 'confirm', 'test', 'ensure'],
        'file_modification': ['file', 'modify', 'edit', 'write', 'create', 'update'],
        'tool_choice': ['tool', 'use', 'choose', 'select', 'prefer'],
        'approach': ['approach', 'strategy', 'method', 'way to'],
        'communication': ['respond', 'reply', 'message', 'tell', 'ask'],
        'automation': ['automate', 'script', 'workflow', 'tool', 'system']
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category

    return 'general'


def extract_lessons_from_file(file_path, source_type):
    """Extract lessons from a markdown file."""
    lessons = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split content into lines
        lines = content.split('\n')

        current_section = None
        lesson_buffer = []

        for line in lines:
            # Track current section
            if line.strip().startswith('#'):
                current_section = line.strip()

            # Look for lesson patterns
            for pattern in LESSON_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    lesson_text = match.group(1).strip()

                    # Skip if too short or generic
                    if len(lesson_text) < 10:
                        continue

                    # Add context from current section
                    if current_section and current_section not in lesson_text:
                        lesson_text = f"{current_section}: {lesson_text}"

                    lessons.append({
                        'text': lesson_text,
                        'severity': detect_severity(lesson_text),
                        'category': categorize_lesson(lesson_text)
                    })

    except Exception as e:
        print(f"[WARNING] Failed to read {file_path}: {e}", file=sys.stderr)

    return lessons


def scrape_workspace(workspace_path=None, max_files=50):
    """
    Scrape the workspace for lesson files.

    Args:
        workspace_path: Root directory to search (defaults to parent of recursive_tracker)
        max_files: Maximum number of files to process

    Returns:
        Dict with scraping results
    """
    if workspace_path is None:
        workspace_path = PROJECT_ROOT.parent

    workspace = Path(workspace_path)
    tracker = BillyTracker()

    # File patterns to search for
    file_patterns = [
        '**/lessons.md',
        '**/tasks/lessons.md',
        '**/tasks/context.md',
        '**/tasks/todo.md',
        '**/MEMORY.md',
        '**/memory/*.md',
        '**/CLAUDE.md'
    ]

    results = {
        'files_processed': 0,
        'lessons_found': 0,
        'lessons_added': 0,
        'files_skipped': 0
    }

    print(f"[INFO] Scraping workspace: {workspace}")
    print(f"[INFO] Looking for lessons in: lessons.md, context.md, todo.md, MEMORY.md, CLAUDE.md")

    for pattern in file_patterns:
        for file_path in workspace.glob(pattern):
            # Skip our own recursive_tracker directory
            if 'recursive_tracker' in str(file_path):
                continue

            if results['files_processed'] >= max_files:
                break

            # Determine source type
            if 'lessons.md' in str(file_path):
                source_type = 'lessons_md'
            elif 'context.md' in str(file_path):
                source_type = 'context_md'
            elif 'MEMORY.md' in str(file_path):
                source_type = 'memory_md'
            else:
                source_type = 'other'

            print(f"\n[INFO] Processing: {file_path.relative_to(workspace)}")

            lessons = extract_lessons_from_file(file_path, source_type)
            results['files_processed'] += 1
            results['lessons_found'] += len(lessons)

            if not lessons:
                print(f"[INFO] No lessons found")
                continue

            # Log each lesson
            for lesson in lessons:
                lesson_id = tracker.log_lesson(
                    source_file=str(file_path.relative_to(workspace)),
                    source_type=source_type,
                    lesson_text=lesson['text'],
                    category=lesson['category'],
                    severity=lesson['severity']
                )

                if lesson_id:
                    results['lessons_added'] += 1
                    print(f"[OK] Added lesson: {lesson['text'][:60]}...")

    return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("Lesson Scraper")
    print("=" * 60)

    results = scrape_workspace(max_files=50)

    print("\n" + "=" * 60)
    print("Scraping Complete")
    print("=" * 60)
    print(f"Files processed: {results['files_processed']}")
    print(f"Lessons found: {results['lessons_found']}")
    print(f"Lessons added: {results['lessons_added']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
