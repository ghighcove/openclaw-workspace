import json
import sys

# Read the JSON - handle UTF-16-LE encoding with BOM
content = open(r'G:\z.ai\workspace\all_projects_scan.json', 'rb').read()
# Check for UTF-16-LE BOM
if content.startswith(b'\xff\xfe'):
    content = content[2:]  # Remove BOM
data = json.loads(content.decode('utf-16-le'))

projects = data['projects']

# Categorize health scores
health_90_plus = []
health_70_89 = []
health_50_69 = []
health_below_50 = []

projects_needing_attention = []

for project in projects:
    score = project['health_score']
    name = project['name']
    path = project['path']
    git = project['git']
    context = project['context']

    # Categorize by health score
    if score >= 90:
        health_90_plus.append((name, score))
    elif score >= 70:
        health_70_89.append((name, score))
    elif score >= 50:
        health_50_69.append((name, score))
    else:
        health_below_50.append((name, score))

    # Check for issues needing attention
    issues = []
    if not git['clean']:
        issues.append(f"{git['uncommitted']} uncommitted")
    if git['unpushed'] > 0:
        issues.append(f"{git['unpushed']} unpushed")
    if not context['exists']:
        issues.append("No context file")
    elif context['is_stale']:
        issues.append("Stale context")

    if issues:
        projects_needing_attention.append({
            'name': name,
            'score': score,
            'issues': ', '.join(issues)
        })

# Sort and get top/bottom
health_90_plus.sort(key=lambda x: -x[1])
health_70_89.sort(key=lambda x: -x[1])
health_50_69.sort(key=lambda x: -x[1])
health_below_50.sort(key=lambda x: -x[1])

top_3 = health_90_plus[:3] or health_70_89[:3] or health_50_69[:3]
bottom_3 = health_below_50[:3] or (health_50_69[:3] if not health_below_50 else health_50_69[-3:])

# Generate report
report = f"""# Dashboard Health Analysis Report

**Generated:** {data['scan_date']}

## Summary

- **Total Projects Found:** {len(projects)}
- **Health Score Distribution:**
  - 90+ (Excellent): {len(health_90_plus)} projects
  - 70-89 (Good): {len(health_70_89)} projects
  - 50-69 (Needs Work): {len(health_50_69)} projects
  - <50 (Critical): {len(health_below_50)} projects

## Health Score Breakdown

### 90+ (Excellent)
{chr(10).join([f"  - {name}: {score}/100" for name, score in health_90_plus]) if health_90_plus else "  None"}

### 70-89 (Good)
{chr(10).join([f"  - {name}: {score}/100" for name, score in health_70_89]) if health_70_89 else "  None"}

### 50-69 (Needs Work)
{chr(10).join([f"  - {name}: {score}/100" for name, score in health_50_69]) if health_50_69 else "  None"}

### <50 (Critical)
{chr(10).join([f"  - {name}: {score}/100" for name, score in health_below_50]) if health_below_50 else "  None"}

## Top 3 Healthiest Projects
{chr(10).join([f"{i+1}. {name} - {score}/100" for i, (name, score) in enumerate(top_3)])}

## Bottom 3 Projects Needing Work
{chr(10).join([f"{i+1}. {name} - {score}/100" for i, (name, score) in enumerate(bottom_3)])}

## Projects Needing Attention ({len(projects_needing_attention)})
{chr(10).join([f"  - {name} ({score}/100): {info['issues']}" for name, score, info in [(p['name'], p['score'], p) for p in projects_needing_attention]]) if projects_needing_attention else "  None"}

## Recommendations

### Immediate Actions
1. **Address uncommitted changes** - {len([p for p in projects if not p['git']['clean']])} projects have uncommitted changes
2. **Add context.md to projects** - {len([p for p in projects if not p['context']['exists']])} projects missing context files

### Medium Priority
1. Review projects with health scores 50-69
2. Push uncommitted commits to remote repositories

### Notes
- All projects with 80+ scores have fresh context and are in good shape
- Projects < 50 score should be reviewed for archival or cleanup
"""

print(report)

# Save to file
with open(r'G:\z.ai\workspace\dashboard_analysis.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("\nReport saved to: G:/z.ai/workspace/dashboard_analysis.md")
