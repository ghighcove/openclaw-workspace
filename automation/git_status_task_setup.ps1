# Git Status Monitor - Task Scheduler Setup Script
# Creates Windows Task Scheduler entry for daily 6 AM git status monitoring

$ErrorActionPreference = "Stop"

# Configuration
$TASK_NAME = "Billy-GitStatusMonitor"
$WORKSPACE = $PSScriptRoot | Split-Path -Parent
$MONITOR_SCRIPT = Join-Path $WORKSPACE "automation\git_status_monitor.ps1"
$LOG_FILE = Join-Path $WORKSPACE ".signals\task_scheduler_log.txt"
$USER_HOME = $env:USERPROFILE

# Function to write to log
function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Write-Host $logEntry
    $logEntry | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
}

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check if running as administrator
if (-not (Test-Admin)) {
    Write-Log "ERROR: This script must be run as Administrator"
    Write-Log "Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

Write-Log "=== Git Status Monitor Task Scheduler Setup ==="
Write-Log "Task Name: $TASK_NAME"
Write-Log "Monitor Script: $MONITOR_SCRIPT"
Write-Log "Schedule: Daily at 6:00 AM"
Write-Log ""

# Check if monitor script exists
if (-not (Test-Path $MONITOR_SCRIPT)) {
    Write-Log "ERROR: Monitor script not found at $MONITOR_SCRIPT"
    exit 1
}

# Create signal directory if it doesn't exist
$signalDir = "$WORKSPACE/.signals"
if (-not (Test-Path $signalDir)) {
    New-Item -ItemType Directory -Path $signalDir -Force | Out-Null
    Write-Log "Created signal directory: $signalDir"
}

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Log "Task '$TASK_NAME' already exists"
    Write-Log "Current state: $($existingTask.State)"
    Write-Log ""

    $response = Read-Host "Do you want to replace the existing task? (Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Log "Setup cancelled"
        exit 0
    }

    Write-Log "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Log "Existing task removed"
}

# Create PowerShell action
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$MONITOR_SCRIPT`"" `
    -WorkingDirectory "$WORKSPACE"

# Create trigger (daily at 6:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM

# Create principal (run as current user, highest privileges)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -WakeToRun `
    -Compatibility Win8 `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register the task
Write-Log "Creating scheduled task..."
try {
    Register-ScheduledTask `
        -TaskName $TASK_NAME `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "Billy's Git Status Monitor - Daily 6 AM check for uncommitted changes and stale projects" `
        -Force | Out-Null

    Write-Log "Task '$TASK_NAME' created successfully"
} catch {
    Write-Log "ERROR: Failed to create scheduled task: $_"
    exit 1
}

# Verify task was created
$task = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue
if ($task) {
    Write-Log ""
    Write-Log "=== Task Verification ==="
    Write-Log "Task Name: $($task.TaskName)"
    Write-Log "State: $($task.State)"
    Write-Log "Description: $($task.Description)"
    Write-Log ""

    # Show next run time
    $nextRun = $task.Triggers[0].StartBoundary
    Write-Log "Next scheduled run: $nextRun"
} else {
    Write-Log "ERROR: Task creation verification failed"
    exit 1
}

Write-Log ""
Write-Log "=== Setup Complete ==="
Write-Log ""
Write-Log "The task is now configured to run:"
Write-Log "  - Frequency: Daily"
Write-Log "  - Time: 6:00 AM"
Write-Log "  - Output: $WORKSPACE/.signals/morning_summary.md"
Write-Log "  - Log: $LOG_FILE"
Write-Log ""
Write-Log "To manually test the task now:"
Write-Log "  Start-ScheduledTask -TaskName `"$TASK_NAME`""
Write-Log ""
Write-Log "To view task history:"
Write-Log "  Get-ScheduledTaskInfo -TaskName `"$TASK_NAME`""
Write-Log ""
Write-Log "To uninstall:"
Write-Log "  Unregister-ScheduledTask -TaskName `"$TASK_NAME`" -Confirm:`$false"
Write-Log ""

# Ask if user wants to test now
$response = Read-Host "Do you want to test the task now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Log ""
    Write-Log "Starting task for testing..."
    Start-ScheduledTask -TaskName $TASK_NAME

    Write-Log "Task started. Waiting for completion..."
    Start-Sleep -Seconds 30

    # Check if morning summary was created
    $morningSummary = "$signalDir/morning_summary.md"
    if (Test-Path $morningSummary) {
        Write-Log "Test successful! Morning summary created at:"
        Write-Log "  $morningSummary"
        Write-Log ""
        Write-Log "=== TEST OUTPUT ==="
        Get-Content $morningSummary | Write-Host
        Write-Log "=== END TEST OUTPUT ==="
    } else {
        Write-Log "Warning: Morning summary not found at $morningSummary"
        Write-Log "Check Task Scheduler event logs for errors"
    }
}

Write-Log ""
Write-Log "Setup complete. Task will run automatically at 6:00 AM daily."
