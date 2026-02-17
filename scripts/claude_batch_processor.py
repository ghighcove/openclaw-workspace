#!/usr/bin/env python3
"""
Claude Batch Processor for NCAA Historical Data Collection
Part of MARCH-HIST-001-REVISED coordinated batch pattern

Claude runs this when triggered by Billy for each season batch.
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
import pandas as pd

class NCAABatchProcessor:
    def __init__(self, trigger_file_path):
        self.trigger_file = Path(trigger_file_path).expanduser()
        self.signals_dir = Path("~/.signals").expanduser()
        self.results_dir = Path("~/openclaw-workspace/results").expanduser()

        # Load trigger file
        with open(self.trigger_file) as f:
            self.trigger = json.load(f)

        self.batch_id = self.trigger['batch_id']
        self.season = self.trigger['season']
        self.date_range = self.trigger['date_range']
        self.rate_limit = self.trigger.get('rate_limit_seconds', 1)

        print(f"=== Claude Batch Processor: Batch {self.batch_id} - Season {self.season} ===")

    def fetch_games(self):
        """Fetch all games for the season from ESPN API"""
        games = []
        api_calls = 0
        errors = []

        start_date = datetime.strptime(self.date_range['start'], '%Y-%m-%d')
        end_date = datetime.strptime(self.date_range['end'], '%Y-%m-%d')

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={date_str}"

            try:
                response = requests.get(url, timeout=30)
                api_calls += 1

                if response.status_code == 200:
                    data = response.json()
                    if 'events' in data:
                        for event in data['events']:
                            game = self._parse_game(event, self.season)
                            if game:
                                games.append(game)

                elif response.status_code == 429:
                    # Rate limit hit
                    print(f"Rate limit hit, waiting 5 seconds...")
                    time.sleep(5)
                    continue

                elif response.status_code >= 500:
                    errors.append(f"ESPN API {response.status_code} on {date_str}")

            except Exception as e:
                errors.append(f"Error fetching {date_str}: {str(e)}")

            # Rate limiting
            time.sleep(self.rate_limit)
            current_date += timedelta(days=1)

            # Progress indicator
            if api_calls % 50 == 0:
                print(f"  Fetched {api_calls} days, found {len(games)} games so far...")

        return games, api_calls, errors

    def _parse_game(self, event, season):
        """Parse a single game from ESPN API response"""
        try:
            game_id = event.get('id')
            date = event.get('date', '').split('T')[0]

            competitions = event.get('competitions', [])
            if not competitions:
                return None

            comp = competitions[0]
            competitors = comp.get('competitors', [])

            if len(competitors) < 2:
                return None

            # Determine home/away
            home = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away = next((c for c in competitors if c.get('homeAway') == 'away'), None)

            if not home or not away:
                return None

            # Check if game is complete
            status = comp.get('status', {}).get('type', {}).get('name', '')
            if status != 'STATUS_FINAL':
                return None  # Skip in-progress or scheduled games

            return {
                'game_id': game_id,
                'date': date,
                'home_team': home.get('team', {}).get('displayName', ''),
                'away_team': away.get('team', {}).get('displayName', ''),
                'home_score': int(home.get('score', 0)),
                'away_score': int(away.get('score', 0)),
                'season': season,
                'tournament_game': comp.get('notes', [{}])[0].get('headline', '').lower().find('ncaa tournament') >= 0
            }
        except Exception as e:
            print(f"Error parsing game {event.get('id')}: {str(e)}")
            return None

    def quality_checks(self, df, expected_rows_range):
        """Run quality checks on the data"""
        checks_passed = 0
        checks_failed = 0
        warnings = []

        # Check 1: Row count
        min_rows, max_rows = expected_rows_range
        if min_rows <= len(df) <= max_rows:
            checks_passed += 1
        else:
            warnings.append(f"Row count {len(df)} outside expected range {min_rows}-{max_rows}")
            checks_failed += 1

        # Check 2: No missing scores
        missing_scores = df[['home_score', 'away_score']].isnull().sum().sum()
        if missing_scores == 0:
            checks_passed += 1
        else:
            warnings.append(f"{missing_scores} missing scores found")
            checks_failed += 1

        # Check 3: No duplicate game IDs
        duplicates = df['game_id'].duplicated().sum()
        if duplicates == 0:
            checks_passed += 1
        else:
            warnings.append(f"{duplicates} duplicate game IDs found")
            checks_failed += 1

        return checks_passed, checks_failed, warnings

    def save_output(self, games):
        """Save games to Parquet file"""
        df = pd.DataFrame(games)
        output_file = self.results_dir / f"season_{self.season}.parquet"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_file, index=False)
        return output_file, len(df)

    def write_completion_signal(self, status, output_file, rows, api_calls, errors, checks_passed, checks_failed, warnings, duration):
        """Write completion signal for Billy to monitor"""
        completion_file = self.signals_dir / f"CLAUDE-BATCH-{self.batch_id:03d}-complete.json"

        signal = {
            'batch_id': self.batch_id,
            'season': self.season,
            'status': status,
            'completion_time': datetime.now().isoformat(),
            'output_file': str(output_file),
            'rows_processed': rows,
            'quality_checks_passed': checks_passed,
            'quality_checks_failed': checks_failed,
            'warnings': warnings,
            'errors': errors,
            'duration_seconds': duration,
            'api_calls_made': api_calls,
            'retry_count': 0
        }

        self.signals_dir.mkdir(parents=True, exist_ok=True)
        with open(completion_file, 'w') as f:
            json.dump(signal, f, indent=2)

        print(f"\n✓ Completion signal written: {completion_file}")
        return completion_file

    def process(self):
        """Main processing flow"""
        start_time = time.time()

        try:
            # Fetch games from ESPN
            print(f"\nFetching games for {self.season} ({self.date_range['start']} to {self.date_range['end']})...")
            games, api_calls, errors = self.fetch_games()
            print(f"✓ Fetched {len(games)} games with {api_calls} API calls")

            if not games:
                raise Exception("No games found")

            # Save to Parquet
            print(f"\nSaving to Parquet...")
            output_file, rows = self.save_output(games)
            print(f"✓ Saved {rows} games to {output_file}")

            # Quality checks
            print(f"\nRunning quality checks...")
            df = pd.read_parquet(output_file)
            expected_range = self.trigger.get('expected_rows_range', [500, 2000])
            checks_passed, checks_failed, warnings = self.quality_checks(df, expected_range)
            print(f"✓ Quality checks: {checks_passed} passed, {checks_failed} failed")

            if warnings:
                print(f"⚠️  Warnings:")
                for w in warnings:
                    print(f"   - {w}")

            # Write completion signal
            duration = int(time.time() - start_time)
            status = 'success' if checks_failed == 0 else 'partial'
            self.write_completion_signal(status, output_file, rows, api_calls, errors,
                                         checks_passed, checks_failed, warnings, duration)

            print(f"\n✅ Batch {self.batch_id} ({self.season}) completed successfully")
            print(f"   Duration: {duration//60} minutes {duration%60} seconds")
            print(f"   Output: {output_file}")

            return 0

        except Exception as e:
            # Write failure completion signal
            duration = int(time.time() - start_time)
            error_msg = str(e)
            print(f"\n❌ Batch {self.batch_id} ({self.season}) FAILED: {error_msg}")

            self.write_completion_signal('failed', '', 0, api_calls if 'api_calls' in locals() else 0,
                                         [error_msg], 0, 1, [], duration)
            return 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python claude_batch_processor.py <trigger_file_path>")
        sys.exit(1)

    processor = NCAABatchProcessor(sys.argv[1])
    exit_code = processor.process()
    sys.exit(exit_code)
