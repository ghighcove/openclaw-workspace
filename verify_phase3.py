#!/usr/bin/env python
# Verify health scores after Phase 3 cleanup
import sys
import os

# Add project-dashboard to path
dashboard_path = 'G:/ai/project-dashboard'
sys.path.insert(0, os.path.join(dashboard_path, 'src'))

os.chdir(dashboard_path)

from scanner import ProjectScanner

scanner = ProjectScanner()
projects_to_check = [
    'C:/ai/whiteboard',
    'C:/ai/NFL_Spread2'
]

print("Health Scores After Phase 3 Cleanup:")
print("-" * 50)

before_scores = {
    'whiteboard': 80,
    'NFL Spread Analysis': 70
}

results = []
for path in projects_to_check:
    scan = scanner.scan_project(path)
    name = scan.metadata.name
    score = scan.health_score
    before = before_scores.get(name, '?')
    change = score - before if before != '?' else '?'
    status = 'Excellent' if score >= 90 else 'Good' if score >= 70 else 'Needs Work'

    results.append({
        'name': name,
        'before': before,
        'after': score,
        'change': change,
        'status': status
    })

for r in results:
    print(f"[{r['status']}] {r['name']}")
    print(f"    Before: {r['before']}/100 -> After: {r['after']}/100 ({'+' if r['change'] > 0 else ''}{r['change']})")

print("\nSummary:")
improved_to_90 = len([r for r in results if r['after'] >= 90])
print(f"  Projects at 90+: {improved_to_90}/2")
print(f"  Average score: {sum(r['after'] for r in results) / len(results):.0f}/100")

# Now let's verify all cleaned projects
all_cleaned = [
    'G:/ai/nfl',
    'G:/ai/superbowl_seat_prices',
    'G:/ai/entertainment_metrics/ratings',
    'F:/ai/stock_photo1',
    'G:/ai/linkedin',
    'G:/ai/artmaster',
    'G:/z.ai/workspace',
    'C:/ai/superlead',
    'G:/ai/dev_journal',
    'G:/ai/article-publisher',
    'G:/ai/essay_topic_explorer',
    'G:/ai/trading_bot',
    'G:/ai/project-dashboard',
    'G:/ai/recursive_proj',
    'C:/ai/whiteboard',
    'C:/ai/NFL_Spread2'
]

print("\n" + "=" * 50)
print("OVERALL CLEANUP SUMMARY (All Phases)")
print("=" * 50)

all_results = []
for path in all_cleaned:
    try:
        scan = scanner.scan_project(path)
        all_results.append(scan)
    except Exception as e:
        pass

excellent_count = len([s for s in all_results if s.health_score >= 90])
good_count = len([s for s in all_results if 70 <= s.health_score < 90])
needs_work_count = len([s for s in all_results if 50 <= s.health_score < 70])
critical_count = len([s for s in all_results if s.health_score < 50])

total_projects = len(all_results)
average_score = sum(s.health_score for s in all_results) / total_projects if total_projects > 0 else 0

print(f"\nHealth Score Distribution:")
print(f"  90+ (Excellent): {excellent_count} projects ({excellent_count/total_projects*100:.0f}%)")
print(f"  70-89 (Good): {good_count} projects ({good_count/total_projects*100:.0f}%)")
print(f"  50-69 (Needs Work): {needs_work_count} projects ({needs_work_count/total_projects*100:.0f}%)")
print(f"  <50 (Critical): {critical_count} projects ({critical_count/total_projects*100:.0f}%)")
print(f"\nTotal Projects: {total_projects}")
print(f"Average Health Score: {average_score:.0f}/100")
