# Git Cleanup Plan - Prioritized by Health Impact

**Generated:** 2026-02-14 20:58
**Total Projects with Uncommitted Changes:** 18

## Strategy

Prioritize projects where committing changes will:
1. Move them to a higher health category (70-89 → 90+)
2. Require minimal effort (fewer files to commit)
3. Have high strategic value

**Health Score Impact Calculation:**
- Projects with only uncommitted changes: +20 potential points
- Projects with both uncommitted AND unpushed: No gain (both issues)

---

## Priority 1: Quick Wins (70-89 → 90+)

These projects can reach "Excellent" (90+) with just a commit:

| Project | Current Score | Uncommitted | Projected Score | Impact |
|---------|--------------|-------------|-----------------|---------|
| NFL Salary Analysis | 80 | 1 | 90 | ✅ Excellent |
| superbowl_seat_prices | 80 | 1 | 90 | ✅ Excellent |
| ratings | 80 | 1 | 90 | ✅ Excellent |
| stock_photo1 | 80 | 1 | 90 | ✅ Excellent |
| linkedin | 70 | 1 | 80+ | ⬆️ Good |
| artmaster | 70 | 2 | 90 | ✅ Excellent |
| Billy Byte Workspace | 70 | 1 | 90 | ✅ Excellent |

**Effort:** 7 files total across 7 projects
**Impact:** 4 projects reach 90+ category

---

## Priority 2: Medium Impact (70-89 maintain)

High-value projects that will stay in good category but look cleaner:

| Project | Current Score | Uncommitted | Projected Score | Impact |
|---------|--------------|-------------|-----------------|---------|
| superlead | 80 | 2 | 90 | ✅ Excellent |
| dev_journal | 80 | 6 | 90 | ✅ Excellent |
| article-publisher | 80 | 4 | 90 | ✅ Excellent |
| essay_topic_explorer | 80 | 4 | 90 | ✅ Excellent |
| Trading Bot | 80 | 4 | 90 | ✅ Excellent |
| Project Dashboard | 80 | 8 | 90 | ✅ Excellent |
| agent-improvement-tracker | 80 | 7 | 90 | ✅ Excellent |

**Effort:** 35 files total across 7 projects
**Impact:** All reach 90+ category

---

## Priority 3: High Effort / Strategic

Projects with many uncommitted files:

| Project | Current Score | Uncommitted | Projected Score | Impact |
|---------|--------------|-------------|-----------------|---------|
| whiteboard | 80 | 11 | 90 | ✅ Excellent |
| NFL Spread Analysis | 70 | 4 | 90 | ✅ Excellent |

**Effort:** 15 files total across 2 projects
**Impact:** Both reach 90+ category

---

## Priority 4: Low Impact (Multiple Issues)

Projects with both uncommitted AND unpushed (git score already at 0, cleanup won't improve score):

| Project | Current Score | Uncommitted | Unpushed | Notes |
|---------|--------------|-------------|----------|-------|
| recursive_proj | 60 | 5 | 7 | Will stay at 60-80 even after commit |

**Effort:** 5 files
**Impact:** Minimal (will improve git hygiene but not health score)

---

## Recommended Execution Order

### Phase 1: Quick Wins (7 projects, ~10 minutes)
```bash
cd G:/ai/nfl; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/superbowl_seat_prices; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/entertainment_metrics/ratings; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd F:/ai/stock_photo1; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/artmaster; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/z.ai/workspace; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/linkedin; git add .; git commit -m 'Cleanup uncommitted changes'; git push
```

**Expected Result:** 4 projects reach 90+, 3 projects improve to 80+

### Phase 2: Medium Impact (7 projects, ~30 minutes)
```bash
cd C:/ai/superlead; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/dev_journal; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/article-publisher; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/essay_topic_explorer; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/trading_bot; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/project-dashboard; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd G:/ai/recursive_proj/agent-improvement-tracker; git add .; git commit -m 'Cleanup uncommitted changes'; git push
```

**Expected Result:** 7 projects reach 90+

### Phase 3: High Effort (2 projects, ~15 minutes)
```bash
cd C:/ai/whiteboard; git add .; git commit -m 'Cleanup uncommitted changes'; git push
cd C:/ai/NFL_Spread2; git add .; git commit -m 'Cleanup uncommitted changes'; git push
```

**Expected Result:** 2 projects reach 90+

### Phase 4: Low Impact (1 project, ~5 minutes)
```bash
cd G:/ai/recursive_proj; git add .; git commit -m 'Cleanup uncommitted changes'
# Note: Still need to push 7 unpushed commits
```

**Expected Result:** Git hygiene improved, score unchanged

---

## Summary

| Phase | Projects | Files | Time | Health Impact |
|-------|----------|-------|------|---------------|
| 1 (Quick Wins) | 7 | 7 | 10 min | 4 → 90+, 3 → 80+ |
| 2 (Medium) | 7 | 35 | 30 min | 7 → 90+ |
| 3 (High Effort) | 2 | 15 | 15 min | 2 → 90+ |
| 4 (Low Impact) | 1 | 5 | 5 min | Git hygiene only |
| **Total** | **17** | **62** | **60 min** | **13 → 90+, 3 → 80+** |

**Before Cleanup:**
- 90+ (Excellent): 3 projects (12%)
- 70-89 (Good): 16 projects (62%)
- 50-69 (Needs Work): 6 projects (23%)
- <50 (Critical): 1 project (4%)

**After Phase 1-3 Cleanup:**
- 90+ (Excellent): 16 projects (62%) 🎯
- 70-89 (Good): 6 projects (23%)
- 50-69 (Needs Work): 3 projects (12%)
- <50 (Critical): 1 project (4%)

**Net Improvement:** +13 projects in Excellent category (50% increase)

---

## Notes

- `openclaw-project` was already cleaned up (50 → 90)
- Some projects may not have git remotes configured; skip `git push` for those
- Review commit messages before running for accuracy
- Consider committing changes incrementally (logical groupings)
