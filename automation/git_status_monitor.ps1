# Git Status Monitor - PowerShell Script
# Runs daily at 6 AM to track uncommitted changes and unpushed commits
# Generates morning summary for Claude

$ErrorActionPreference = "Stop"

# Configuration
$WORKSPACE = $PSScriptRoot | Split-Path -Parent
$PYTHON_SCRIPT = Join-Path (Split-Path $WORKSPACE -Parent) "git-status-all.py"
$SIGNAL_DIR = "$WORKSPACE/.signals"
$TEMPLATE_DIR = "$WORKSPACE/templates"
$MORNING_SUMMARY_FILE = "$SIGNAL_DIR/morning_summary.md"
$COMPLETION_FILE = "$SIGNAL_DIR/GIT-MONITOR-001-complete.json"

# Create directories if they don't exist
if (-not (Test-Path $SIGNAL_DIR)) {
    New-Item -ItemType Directory -Path $SIGNAL_DIR -Force | Out-Null
}
if (-not (Test-Path $TEMPLATE_DIR)) {
    New-Item -ItemType Directory -Path $TEMPLATE_DIR -Force | Out-Null
}

# Function to write status updates to log
function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $message"
}

Write-Log "Starting Git Status Monitor..."

# Run git-status-all.py with --json flag for cleaner parsing
Write-Log "Running git-status-all.py --json..."
$gitOutput = python $PYTHON_SCRIPT --json 2>&1
$gitExitCode = $LASTEXITCODE

if ($gitExitCode -ne 0) {
    Write-Log "ERROR: git-status-all.py failed with exit code $gitExitCode"
    Write-Log "Output: $gitOutput"
    exit 1
}

Write-Log "Git status check completed"

# Parse JSON output
try {
    $data = $gitOutput | ConvertFrom-Json
    $projects = $data.projects
    $totalProjects = $projects.Count
    Write-Log "Found $totalProjects projects"
} catch {
    Write-Log "ERROR: Failed to parse JSON output: $_"
    exit 1
}

# Initialize counters
$cleanProjects = 0
$uncommittedProjects = 0
$unpushedProjects = 0
$staleProjects = 0
$dirtyProjectList = @()
$staleProjectList = @()

# Get current date for staleness checking (3 days ago)
$threeDaysAgo = (Get-Date).AddDays(-3)
$sevenDaysAgo = (Get-Date).AddDays(-7)

# Analyze each project
foreach ($project in $projects) {
    if ($project.status -eq "not_git") {
        # Skip non-git repos
        continue
    }

    $projectName = $project.name
    $projectPath = $project.path

    if ($project.uncommitted_count -gt 0) {
        $uncommittedProjects++
        $dirtyProjectList += $projectName

        # Check if uncommitted changes are stale (>3 days)
        # Get last commit timestamp for this project
        if ($projectPath -and (Test-Path (Join-Path $projectPath ".git"))) {
            try {
                $gitLogOutput = git -C $projectPath log -1 --format=%at 2>&1
                if ($LASTEXITCODE -eq 0 -and $gitLogOutput -match '^\d+$') {
                    $lastCommitTime = [DateTimeOffset]::FromUnixTimeSeconds([int]$gitLogOutput).DateTime
                    if ($lastCommitTime -lt $threeDaysAgo) {
                        $staleProjects++
                        $lastCommitDate = $lastCommitTime.ToString("yyyy-MM-dd")
                        $staleProjectList += "$projectName (last commit: $lastCommitDate)"

                        # Check if critical (>7 days)
                        if ($lastCommitTime -lt $sevenDaysAgo) {
                            $staleProjectList[-1] = "$($staleProjectList[-1]) ⚠️ CRITICAL (>7 days)"
                        }
                    }
                }
            } catch {
                # Git command failed, skip staleness check for this project
                Write-Log "Warning: Could not check staleness for $projectName"
            }
        }
    }

    if ($project.unpushed_count -gt 0) {
        $unpushedProjects++
    }

    if ($project.status -eq "clean") {
        $cleanProjects++
    }
}

Write-Log "Statistics:"
Write-Log "  Total projects: $totalProjects"
Write-Log "  Clean projects: $cleanProjects"
Write-Log "  Uncommitted: $uncommittedProjects"
Write-Log "  Unpushed: $unpushedProjects"
Write-Log "  Stale (>3 days): $staleProjects"

# Log dirty projects for debugging
if ($dirtyProjectList.Count -gt 0) {
    Write-Log "Dirty projects: $($dirtyProjectList -join ', ')"
}

# Generate morning summary
$today = Get-Date -Format "yyyy-MM-dd"
$currentTime = Get-Date -Format "HH:mm"

$summary = @"
# Git Status Morning Summary: $today

## Overview
- Total projects scanned: $totalProjects
- Clean projects: $cleanProjects
- Projects with uncommitted changes: $uncommittedProjects
- Projects with unpushed commits: $unpushedProjects
- Stale projects (>3 days uncommitted): $staleProjects

## Projects Requiring Attention
"@

if ($dirtyProjectList.Count -eq 0) {
    $summary += "`nNo projects with uncommitted changes. All clean! ✅"
} else {
    $summary += "`nThe following projects have uncommitted changes:`n"
    foreach ($project in $dirtyProjectList) {
        $summary += "- $project`n"
    }
}

$summary += @"

## Stale Projects (>3 days uncommitted)
"@

if ($staleProjectList.Count -eq 0) {
    $summary += "`nNo stale projects. Great work staying current! ✅"
} else {
    $summary += "`nThe following projects have uncommitted changes for more than 3 days:`n"
    foreach ($project in $staleProjectList) {
        $summary += "- $project`n"
    }
}

$summary += @"

## Action Items for Claude
"@

$actionItems = @()

if ($uncommittedProjects -gt 0) {
    $actionItems += "- [ ] Review $($uncommittedProjects) project(s) with uncommitted changes (run git-status-all.py --dirty for details)"
}

if ($unpushedProjects -gt 0) {
    $actionItems += "- [ ] Review $($unpushedProjects) project(s) with unpushed commits"
}

if ($staleProjects -gt 0) {
    $actionItems += "- [ ] Commit stale projects if work is complete"
    if ($staleProjectList -match "CRITICAL") {
        $actionItems += "- [ ] **URGENT:** Investigate why project(s) have been dirty >7 days"
    }
}

if ($uncommittedProjects -gt 5) {
    $actionItems += "- [ ] **ANOMALY:** $($uncommittedProjects) dirty projects detected (normal range: 0-5)"
}

if ($actionItems.Count -eq 0) {
    $actionItems += "- [ ] No action items - all projects clean! ✅"
}

$summary += ($actionItems -join "`n")

# Add anomaly detection if needed
$summary += @"

---
*Generated at $currentTime by git_status_monitor.ps1*
*Last git status check: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
"@

# Write morning summary to file
$summary | Out-File -FilePath $MORNING_SUMMARY_FILE -Encoding UTF8 -Force
Write-Log "Morning summary written to $MORNING_SUMMARY_FILE"

# Check for anomalies and create alerts
if ($uncommittedProjects -gt 10) {
    Write-Log "WARNING: More than 10 dirty projects detected - potential systematic issue"
}

if ($staleProjects -gt 0) {
    Write-Log "ALERT: $staleProjects stale projects detected"
}

# Output summary to console
Write-Log "=== MORNING SUMMARY ==="
Write-Host $summary
Write-Log "=== END SUMMARY ==="

Write-Log "Git Status Monitor completed successfully"
exit 0
