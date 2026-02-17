#!/usr/bin/env python3
"""
Billy Coordinated Batch Script - MARCH-HIST-001-REVISED
Uses wrapper to enforce protocols
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add workspace to path for wrapper
sys.path.insert(0, str(Path("G:/ai/openclaw-workspace")))
from BILLY_WRAPPER import BillyWrapper

class BatchCoordinator:
    def __init__(self, manifest_path):
        self.manifest_path = Path(manifest_path).expanduser()
        self.workspace = Path("~/openclaw-workspace").expanduser()
        self.signals = self.workspace / ".signals"
        self.results = self.workspace / "results"

        with open(self.manifest_path) as f:
            self.manifest = json.load(f)

        self.task_id = self.manifest['task_metadata']['task_id']
        self.batches = self.manifest['batch_specification']['batches']

    def create_trigger(self, batch_spec):
        """Create trigger file for Claude to process"""
        trigger_file = self.signals / batch_spec['trigger_file'].split('/')[-1]

        trigger_data = {
            'batch_id': batch_spec['batch_id'],
            'season': batch_spec['description'].split()[-1],  # Extract year from description
            'date_range': self._infer_date_range(batch_spec),
            'expected_rows_range': self._parse_expected_rows(batch_spec),
            'rate_limit_seconds': 1,
            'instructions': batch_spec['instructions'],
            'output_file': batch_spec['expected_output']['file_path'],
            'quality_checks': batch_spec['quality_checks'],
            'data_sources': batch_spec['data_sources']
        }

        self.signals.mkdir(parents=True, exist_ok=True)
        with open(trigger_file, 'w') as f:
            json.dump(trigger_data, f, indent=2)

        print(f"Created trigger: {trigger_file}")
        return trigger_file

    def _infer_date_range(self, batch_spec):
        """Infer date range from batch description"""
        # This is simplified - real implementation would parse properly
        season_year = int(batch_spec['description'].split()[-1])
        return {
            'start': f"{season_year-1}-11-01",
            'end': f"{season_year}-04-10"
        }

    def _parse_expected_rows(self, batch_spec):
        """Parse expected row count from quality checks"""
        for check in batch_spec['quality_checks']:
            if 'Row count' in check['check']:
                rule = check['rule']
                # Parse "500-1000 games" or similar
                if '-' in rule:
                    parts = rule.split('-')
                    min_val = int(''.join(filter(str.isdigit, parts[0])))
                    max_val = int(''.join(filter(str.isdigit, parts[1])))
                    return [min_val, max_val]
        return [500, 2000]  # Default

    def wait_for_completion(self, batch_id, timeout=7200):
        """Wait for Claude to complete batch (max 2 hours)"""
        completion_file = self.signals / f"CLAUDE-BATCH-{batch_id:03d}-complete.json"

        print(f"Waiting for completion signal: {completion_file}")
        start_time = time.time()

        while time.time() - start_time < timeout:
            if completion_file.exists():
                with open(completion_file) as f:
                    signal = json.load(f)
                print(f"Batch {batch_id} completed: {signal['status']}")
                return signal

            time.sleep(30)  # Check every 30 seconds

        raise TimeoutError(f"Batch {batch_id} did not complete within {timeout/3600:.1f} hours")

    def verify_output(self, batch_spec, completion_signal):
        """Verify batch output exists and looks reasonable"""
        output_file = Path(completion_signal['output_file']).expanduser()

        if not output_file.exists():
            raise RuntimeError(f"Output file not found: {output_file}")

        file_size = output_file.stat().st_size
        rows = completion_signal['rows_processed']

        print(f"Verified output: {output_file}")
        print(f"  Size: {file_size / 1024 / 1024:.2f} MB")
        print(f"  Rows: {rows}")

        if file_size < 1000:
            raise RuntimeError(f"Output file suspiciously small: {file_size} bytes")

        return True

    def coordinate(self):
        """Main coordination loop"""
        print(f"Starting coordination for {self.task_id}")
        print(f"Total batches: {len(self.batches)}")

        completed = []
        failed = []

        for batch_spec in self.batches:
            batch_id = batch_spec['batch_id']
            print(f"\n{'='*60}")
            print(f"BATCH {batch_id}: {batch_spec['description']}")
            print(f"{'='*60}")

            try:
                # Create trigger for Claude
                trigger_file = self.create_trigger(batch_spec)

                # Wait for Claude to complete
                completion_signal = self.wait_for_completion(batch_id)

                # Verify output
                self.verify_output(batch_spec, completion_signal)

                completed.append(batch_id)
                print(f"✓ Batch {batch_id} SUCCESS")

            except Exception as e:
                print(f"✗ Batch {batch_id} FAILED: {str(e)}")
                failed.append((batch_id, str(e)))

                # Decide whether to continue or stop
                if len(failed) >= 2:
                    print(f"\nToo many failures ({len(failed)}), stopping coordination")
                    break

        # Final report
        print(f"\n{'='*60}")
        print(f"COORDINATION COMPLETE")
        print(f"{'='*60}")
        print(f"Completed: {len(completed)}/{len(self.batches)}")
        print(f"Failed: {len(failed)}")

        if failed:
            print("\nFailures:")
            for batch_id, error in failed:
                print(f"  Batch {batch_id}: {error}")

        return len(completed), len(failed)


def main():
    if len(sys.argv) < 2:
        print("Usage: python billy_coordination_script.py <manifest_path>")
        sys.exit(1)

    manifest_path = sys.argv[1]

    # Use wrapper to enforce protocols
    wrapper = BillyWrapper()

    def coordination_task():
        coordinator = BatchCoordinator(manifest_path)
        completed, failed = coordinator.coordinate()

        if failed > 0:
            raise RuntimeError(f"{failed} batches failed")

        return f"All {completed} batches completed"

    # Wrap with full enforcement
    wrapper.wrap_task("MARCH-HIST-001-REVISED", coordination_task)


if __name__ == '__main__':
    main()
