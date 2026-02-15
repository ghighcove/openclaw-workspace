#!/usr/bin/env python
# Verify health scores after Phase 2 cleanup
import sys
import os

# Add project-dashboard to path
dashboard_path = 'G:/ai/project-dashboard'
sys.path.insert(0, os.path.join(dashboard_path, 'src'))

os.chdir(dashboard_path)

from scanner import ProjectScanner

scanner = ProjectScanner()
projects_to_check = [
    'C:/ai/superlead',
    'G:/ai/dev_journal',
    'G:/ai/article-publisher',
    'G:/ai/essay_topic_explorer',
    'G:/ai/trading_bot',
    'G:/ai/project-dashboard',
    'G:/ai/recursive_proj'
]

print("Health Scores After Phase 2 Cleanup:")
print("-" * 50)

before_scores = {
    'superlead': 80,
    'dev_journal': 80,
    'article-publisher': 80,
    'essay_topic_explorer': 80,
    'Trading Bot': 80,
    'Project Dashboard': 80,
    'recursive_proj': 80
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
print(f"  Projects at 90+: {improved_to_90}/7")
print(f"  Average score: {sum(r['after'] for r in results) / len(results):.0f}/100")
