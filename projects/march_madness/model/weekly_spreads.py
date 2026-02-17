"""
Weekly spread generation for Billy (Category B - Batch Processing).

Generates point spreads for all games involving featured schools for the
upcoming week. Designed to run autonomously via cron every Monday 3 AM.

Output: JSON file with spreads, confidence intervals, and upset alerts
Location: ~/openclaw-workspace/projects/march_madness/spreads/week_XX.json

Billy Execution:
    cd ~/openclaw-workspace/projects/march_madness/model
    python weekly_spreads.py --week 15 --season 2026
"""

import sys
from pathlib import Path
import yaml
import json
import pandas as pd
from datetime import datetime, timedelta

# Add bracket-picker to path
sys.path.insert(0, str(Path.home() / 'openclaw-workspace' / 'projects' / 'march_madness' / 'bracket-picker' / 'src'))

# Import from main project
bracket_picker_scripts = Path.home() / 'openclaw-workspace' / 'projects' / 'march_madness' / 'bracket-picker' / 'scripts'
sys.path.insert(0, str(bracket_picker_scripts))


def load_featured_schools():
    """Load featured schools from config."""
    config_path = Path.home() / 'openclaw-workspace' / 'projects' / 'march_madness' / 'config' / 'featured_schools.yaml'

    if not config_path.exists():
        # Fallback to main project location
        config_path = Path('G:/ai/march_madness/config/featured_schools.yaml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    featured = [school['name'] for school in config['featured_schools']]
    return featured


def get_upcoming_games(featured_schools, week_start_date):
    """
    Get upcoming games involving featured schools.

    For Billy: This would fetch from ESPN API or current season data.
    For now, generates sample matchups for testing.
    """
    # Sample matchups for testing
    # In production, Billy would fetch actual scheduled games from ESPN API
    sample_games = []

    # Generate some sample matchups involving featured schools
    matchups = [
        ('Duke', 'North Carolina'),
        ('Kansas', 'Baylor'),
        ('Houston', 'Texas Tech'),
        ('Purdue', 'Michigan St.'),
        ('Kentucky', 'Tennessee'),
        ('Gonzaga', 'Saint Mary\'s'),
        ('UCLA', 'Arizona'),
        ('Marquette', 'Creighton'),
        ('San Diego St.', 'New Mexico'),
    ]

    for team1, team2 in matchups:
        if team1 in featured_schools or team2 in featured_schools:
            sample_games.append({
                'team_1': team1,
                'team_2': team2,
                'date': (week_start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '19:00',
                'location': 'TBD'
            })

    return sample_games


def generate_weekly_spreads(week_number, season):
    """Generate spreads for upcoming week."""
    print("=" * 70)
    print(f"WEEKLY SPREAD GENERATION - Week {week_number}, {season}")
    print("=" * 70)

    # Calculate week start date
    week_start_date = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    print(f"\nWeek start: {week_start_date.strftime('%Y-%m-%d')}")

    # Load featured schools
    print("\nLoading featured schools...")
    featured_schools = load_featured_schools()
    print(f"  Featured schools: {len(featured_schools)}")

    # Get upcoming games
    print("\nFetching upcoming games...")
    games = get_upcoming_games(featured_schools, week_start_date)
    print(f"  Games found: {len(games)}")

    if len(games) == 0:
        print("\n[WARN] No games found for featured schools this week")
        return

    # Create input CSV for predict_spreads.py
    games_df = pd.DataFrame(games)
    temp_input = Path.home() / 'openclaw-workspace' / 'projects' / 'march_madness' / 'spreads' / f'week_{week_number}_input.csv'
    temp_input.parent.mkdir(parents=True, exist_ok=True)
    games_df[['team_1', 'team_2']].to_csv(temp_input, index=False)

    # Generate spreads using predict_spreads.py
    print(f"\nGenerating spreads...")

    import subprocess
    # Use main project path (not Billy workspace)
    script_path = Path('G:/ai/march_madness/bracket-picker/scripts/predict_spreads.py')
    output_path = Path.home() / 'openclaw-workspace' / 'projects' / 'march_madness' / 'spreads' / f'week_{week_number}.json'

    # Run prediction script
    result = subprocess.run([
        'python',
        str(script_path),
        '--input', str(temp_input),
        '--output', str(output_path),
        '--season', str(season)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"\n[ERROR] Spread generation failed:")
        print(result.stderr)
        return

    print(f"\n[OK] Spreads generated: {output_path}")

    # Load results for summary
    with open(output_path, 'r') as f:
        spreads = json.load(f)

    # Generate summary
    print("\n" + "=" * 70)
    print("WEEKLY SPREAD SUMMARY")
    print("=" * 70)

    print(f"\nTotal games: {len(spreads)}")

    # Top picks (highest confidence)
    print("\nTop 5 picks (by confidence):")
    sorted_spreads = sorted(spreads, key=lambda x: x['confidence'], reverse=True)
    for i, s in enumerate(sorted_spreads[:5], 1):
        print(f"  {i}. {s['spread_text']} - {s['win_probability']}% ({s['confidence']}% confidence)")

    # Upset alerts
    upset_alerts = [s for s in spreads if s['upset_alert']]
    print(f"\nUpset alerts: {len(upset_alerts)}")
    for alert in upset_alerts:
        print(f"  - {alert['matchup']} (Spread: {alert['spread']}, Confidence: {alert['confidence']}%)")

    # Create completion signal for Claude
    signal = {
        'task_id': f'WEEK_{week_number}_SPREADS',
        'status': 'success',
        'completion_time': datetime.now().isoformat(),
        'deliverables_created': [str(output_path)],
        'statistics': {
            'total_games': len(spreads),
            'upset_alerts': len(upset_alerts),
            'avg_confidence': round(sum(s['confidence'] for s in spreads) / len(spreads), 1)
        },
        'next_steps_for_claude': [
            f"Review spreads at: {output_path}",
            "Spot-check top 5 picks against Vegas lines (if available)",
            "Flag any anomalies or unexpected spreads",
            f"Consider creating content highlights for Article #{week_number // 4 + 1}"
        ]
    }

    signal_path = Path.home() / 'openclaw-workspace' / '.signals' / f'WEEK_{week_number}_SPREADS-complete.json'
    signal_path.parent.mkdir(parents=True, exist_ok=True)

    with open(signal_path, 'w') as f:
        json.dump(signal, f, indent=2)

    print(f"\n[OK] Signal created: {signal_path}")

    print("\n" + "=" * 70)
    print("WEEKLY SPREAD GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate weekly point spreads for featured schools"
    )
    parser.add_argument(
        '--week',
        type=int,
        required=True,
        help='Week number (e.g., 15 for week 15 of season)'
    )
    parser.add_argument(
        '--season',
        type=int,
        default=2026,
        help='Season year'
    )

    args = parser.parse_args()

    generate_weekly_spreads(args.week, args.season)
