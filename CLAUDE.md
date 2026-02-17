# OpenClaw Workspace - Project Instructions

**Project:** Multi-agent coordination workspace for Billy (OpenClaw) and Claude
**Purpose:** Coordinated batch processing with enforced protocols

## Path Consistency Rules (CRITICAL)

**ALL scripts in this workspace MUST use these exact paths:**

```python
# Correct paths
signals_dir = Path("~/openclaw-workspace/.signals").expanduser()
results_dir = Path("~/openclaw-workspace/results").expanduser()
workspace_dir = Path("~/openclaw-workspace").expanduser()

# NEVER use these paths
# ❌ Path("~/.signals")  # Wrong - outside workspace
# ❌ Path("~/results")   # Wrong - outside workspace
```

**Why this matters:**
- Billy's coordination script expects signals at `~/openclaw-workspace/.signals`
- Path mismatches cause Billy to wait indefinitely for signals that exist in wrong location
- Integration bugs waste hours of debugging time

**Verification checklist before creating ANY new script:**
1. Read ALL scripts that will interact with your new script
2. Identify their path expectations (signals_dir, results_dir, workspace paths)
3. Match those paths exactly in your new code
4. Test end-to-end: trigger → process → signal → verify receiver can find it

## Integration Point Verification (MANDATORY)

Before claiming any code "works" or is "fixed":

1. **Read dependent code** - What files/scripts will interact with yours?
2. **Verify interfaces match** - Paths, file formats, signal schemas
3. **Test end-to-end** - Don't just test your component, test the full workflow
4. **Check from receiver's perspective** - Can Billy/Claude actually find the output?

**Example: Creating a batch processor**
```python
# Step 1: Read billy_coordination_script.py
# Found: self.signals = self.workspace / ".signals"
#        self.workspace = Path("~/openclaw-workspace")
# Therefore: signals go to ~/openclaw-workspace/.signals

# Step 2: Match that path in batch processor
self.signals_dir = Path("~/openclaw-workspace/.signals").expanduser()

# Step 3: Test end-to-end
# - Create trigger file
# - Run processor
# - Verify signal appears at ~/openclaw-workspace/.signals
# - Verify coordination script can read it
```

## File I/O Rules

**APPEND mode for shared files:**
```python
# Correct - append to CLAUDE_INBOX.md
with open(inbox, 'a', encoding='utf-8') as f:
    f.write(message)

# NEVER use write mode on shared files
# ❌ with open(inbox, 'w') as f:  # Deletes all messages!
```

## Enforcement System

**Billy MUST use BILLY_WRAPPER.py for all tasks:**
```python
from BILLY_WRAPPER import BillyWrapper

wrapper = BillyWrapper()
wrapper.wrap_task("TASK-ID", task_function)
```

The wrapper enforces:
- All messages acknowledged before work starts
- No STOP commands in inbox
- Heartbeat logging
- Append mode reminders

**Cannot be bypassed** - raises RuntimeError if non-compliant

## Signal Schema

**Completion signals format:**
```json
{
  "batch_id": 1,
  "season": 2020,
  "status": "success|partial|failed",
  "completion_time": "2026-02-15T12:22:15.303635",
  "output_file": "C:\\Users\\ghigh\\openclaw-workspace\\results\\season_2020.parquet",
  "rows_processed": 856,
  "quality_checks_passed": 3,
  "quality_checks_failed": 0,
  "warnings": [],
  "errors": [],
  "duration_seconds": 191,
  "api_calls_made": 152,
  "retry_count": 0
}
```

**Location:** `~/openclaw-workspace/.signals/CLAUDE-BATCH-{batch_id:03d}-complete.json`

## Common Pitfalls (Lessons Learned)

### Path Mismatch Bug (2026-02-15)
- **Problem:** Batch processor wrote to `~/.signals`, coordination script expected `~/openclaw-workspace/.signals`
- **Result:** Billy stuck waiting 45+ minutes for signal in wrong location
- **Root cause:** Didn't read coordination script before creating processor
- **Fix:** All paths now standardized in this CLAUDE.md
- **Logged:** Outcome tracker decision_id=570

### Unicode Encoding Issues (2026-02-15)
- **Problem:** Emoji characters (✓ ✗ ❌) fail on Windows cp1252 encoding
- **Solution:** Never use emoji in Python output, use plain text
- **Force UTF-8:** Add this to all scripts:
```python
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

## Testing Before Deployment

**Minimum viable test for any component:**
1. Create test input (trigger file, manifest, etc.)
2. Run the component
3. Verify output appears in expected location
4. Verify downstream component can read/find it
5. Check error handling (what if input is missing/invalid?)

**Don't claim it works until all 5 steps pass.**

---

## Automatic Aggregation (Batch Processing)

**RULE: When all batches in a coordinated batch task complete successfully, automatically run aggregation.**

**Conditions for automatic aggregation:**
1. All batch completion signals exist (no missing batches)
2. All batches have `status: "success"` (not "partial" or "failed")
3. No critical quality check failures

**How to implement:**
```python
# After last batch completes, check all signals
all_complete = all(
    (signals_dir / f"CLAUDE-BATCH-{i:03d}-complete.json").exists()
    for i in range(1, num_batches + 1)
)

if all_complete:
    # Check all are successful
    all_success = True
    for i in range(1, num_batches + 1):
        signal = json.load(open(signals_dir / f"CLAUDE-BATCH-{i:03d}-complete.json"))
        if signal['status'] != 'success':
            all_success = False
            break

    if all_success:
        # Run aggregation automatically
        subprocess.run(['python', 'scripts/aggregate_seasons.py'])
```

**Why this matters:**
- Manual aggregation adds unnecessary wait time
- User shouldn't have to remember to run aggregation
- Batches are useless until aggregated
- Automation = fewer steps = less chance of forgetting

**Applied to:** NCAA historical data collection (batches 1-6 → combined dataset)
