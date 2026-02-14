#!/usr/bin/env python3
"""
Archive Custom Bot Files - Python Script (Cross-Platform)
Author: Billy Byte (OpenClaw)
Date: February 14, 2026
Version: 1.0.3

Description:
- Archive custom bot files (they were good learning exercises, but native OpenClaw integration is better)
- Cross-platform compatible (Windows, Linux, Mac)
- Safe path handling for Windows backslashes

Usage:
python archive_custom_bot.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Paths - Using raw strings to avoid Windows path issues
WORKSPACE = r"G:\z.ai\workspace\bot"
ARCHIVE_DIR = os.path.join(WORKSPACE, "archive")

# Files to archive
FILES_TO_ARCHIVE = [
    os.path.join(WORKSPACE, "simple_telegram_bot.py"),
    os.path.join(WORKSPACE, "commands_queue.json"),
    os.path.join(WORKSPACE, "README.md"),
    os.path.join(WORKSPACE, "START_GUIDE.md")
]

def main():
    """Main entry point - archiving custom bot files"""
    print(f"[START] Archiving custom bot files at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create archive directory if it doesn't exist
        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            print(f"[CREATE] Archive directory: {ARCHIVE_DIR}")
        
        # Archive each file
        archived_count = 0
        
        for file_path in FILES_TO_ARCHIVE:
            if os.path.exists(file_path):
                # Get filename only
                filename = os.path.basename(file_path)
                
                # Archive path
                archive_path = os.path.join(ARCHIVE_DIR, filename)
                
                # Move file to archive
                shutil.move(file_path, archive_path)
                print(f"[ARCHIVE] Moved: {filename} -> archive/{filename}")
                archived_count += 1
            else:
                print(f"[SKIP] File doesn't exist: {file_path}")
        
        print(f"[COMPLETE] Archived {archived_count} files to {ARCHIVE_DIR}")
        print(f"[INFO] Archive directory: {ARCHIVE_DIR}")
        print(f"[INFO] See START_GUIDE.md for next steps to configure OpenClaw native integration")
        print(f"[SUCCESS] Custom bot archived. Ready for OpenClaw native integration setup")
        
    except Exception as e:
        print(f"\n[FATAL] Archive script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
