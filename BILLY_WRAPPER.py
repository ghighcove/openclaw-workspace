#!/usr/bin/env python3
"""
Billy Wrapper - ENFORCES all protocols before Billy can work
This wrapper MUST be used for all Billy tasks - no bypass allowed
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class BillyWrapper:
    def __init__(self):
        self.workspace = Path(__file__).parent.resolve()
        self.inbox = self.workspace.parent / "openclaw-project" / "workspace" / "CLAUDE_INBOX.md"
        self.signals = self.workspace / ".signals"
        self.heartbeat = self.workspace / ".heartbeat"

    def enforce_startup_protocol(self):
        """Run mandatory startup checks - BLOCKS if failed"""
        print("=" * 60)
        print("BILLY WRAPPER - ENFORCING PROTOCOLS")
        print("=" * 60)

        # Check 1: Inbox exists
        if not self.inbox.exists():
            raise RuntimeError("FATAL: CLAUDE_INBOX.md not found")

        # Check 2: Count acknowledgments
        content = self.inbox.read_text(encoding='utf-8')
        claude_count = content.count("---Claude")
        ack_count = content.count("ACKNOWLEDGED")

        if claude_count > ack_count:
            unacked = claude_count - ack_count
            raise RuntimeError(
                f"BLOCKED: {unacked} unacknowledged message(s)\n"
                f"You must acknowledge ALL messages before working.\n"
                f"Read {self.inbox} and acknowledge each message."
            )

        # Check 3: STOP commands
        if "STOP" in content or "DO NOT" in content:
            raise RuntimeError(
                "BLOCKED: STOP command found in inbox\n"
                "Handle STOP commands before working."
            )

        # Check 4: Send heartbeat
        self.heartbeat.mkdir(parents=True, exist_ok=True)
        heartbeat_file = self.heartbeat / "log.txt"
        with open(heartbeat_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Billy session started\n")

        print("\nAll protocol checks passed")
        print("=" * 60)
        return True

    def verify_file_io_mode(self):
        """Verify Billy will use APPEND mode, not WRITE mode"""
        # This is a reminder - actual enforcement happens in Billy's code
        print("\nREMINDER: When writing to CLAUDE_INBOX.md:")
        print("  - ALWAYS use append mode: open(file, 'a')")
        print("  - NEVER use write mode: open(file, 'w')")
        print("  - Overwriting deletes all messages!")

    def log_task_start(self, task_id):
        """Log that Billy is starting a task"""
        log_file = self.signals / "billy_task_log.jsonl"
        self.signals.mkdir(parents=True, exist_ok=True)

        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'task_start',
            'task_id': task_id,
            'status': 'started'
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def wrap_task(self, task_id, task_function):
        """Wrap a task with full protocol enforcement"""
        try:
            # Enforce protocols FIRST
            self.enforce_startup_protocol()
            self.verify_file_io_mode()
            self.log_task_start(task_id)

            print(f"\nStarting task: {task_id}")
            print("-" * 60)

            # Run the actual task
            result = task_function()

            print("-" * 60)
            print(f"Task {task_id} completed")
            return result

        except RuntimeError as e:
            print(f"\nBLOCKED: {str(e)}")
            print("\nFix the issues above, then try again.")
            sys.exit(1)
        except Exception as e:
            print(f"\nTask failed: {str(e)}")
            sys.exit(1)


def example_usage():
    """Example: How Billy should use this wrapper"""
    wrapper = BillyWrapper()

    def my_task():
        # Billy's actual task code goes here
        print("Doing coordination work...")
        print("Creating trigger files...")
        print("Monitoring completion signals...")
        return "success"

    # Wrap the task with enforcement
    wrapper.wrap_task("EXAMPLE-TASK-001", my_task)


if __name__ == '__main__':
    print("Billy Wrapper - Protocol Enforcement System")
    print("\nThis wrapper ensures Billy follows all protocols.")
    print("Billy's tasks must use this wrapper - no bypass allowed.")
    print("\nExample usage:")
    print("  wrapper = BillyWrapper()")
    print("  wrapper.wrap_task('TASK-ID', my_function)")
