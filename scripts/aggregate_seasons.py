#!/usr/bin/env python3
"""
Aggregate all season Parquet files into combined historical dataset
Run by Billy after all batches complete
"""

import sys
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def aggregate_seasons():
    results_dir = Path('~/openclaw-workspace/results').expanduser()
    signals_dir = Path('~/openclaw-workspace/.signals').expanduser()

    season_files = sorted(results_dir.glob('season_*.parquet'))

    print(f"=== Aggregating NCAA Seasons ===")
    print(f"Found {len(season_files)} season files:")
    for f in season_files:
        print(f"  - {f.name}")

    if len(season_files) == 0:
        print("ERROR: No season files found!")
        return 1

    # Load and concatenate
    dfs = []
    for f in season_files:
        df = pd.read_parquet(f)
        print(f"  {f.name}: {len(df)} games")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\n Combined: {len(combined)} games across {combined['season'].nunique()} seasons")

    # Quality checks
    duplicates = combined['game_id'].duplicated().sum()
    if duplicates > 0:
        print(f"WARNING:  WARNING: {duplicates} duplicate game IDs found")

    seasons_present = sorted(combined['season'].unique())
    print(f" Seasons present: {seasons_present}")

    # Save combined dataset
    output_file = results_dir / 'historical_2020_2025_combined.parquet'
    combined.to_parquet(output_file, index=False)
    print(f"\n✅ Saved combined dataset: {output_file}")
    print(f"   Total games: {len(combined)}")
    print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    # Write aggregation completion signal
    signal_file = signals_dir / 'AGGREGATION-complete.json'
    signal = {
        'status': 'success',
        'completion_time': datetime.now().isoformat(),
        'total_games': len(combined),
        'seasons_count': len(seasons_present),
        'seasons_present': seasons_present,
        'duplicates': int(duplicates),
        'output_file': str(output_file)
    }

    signals_dir.mkdir(parents=True, exist_ok=True)
    with open(signal_file, 'w') as f:
        json.dump(signal, f, indent=2)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(aggregate_seasons())
