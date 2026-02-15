
# Check whiteboard tickets for todo status.

$whiteboardDir = "C:\ai\whiteboard\tickets"
$todoDir = Join-Path $whiteboardDir "todo"

if (Test-Path $todoDir)) {
    Write-Output "No tickets in todo status"
} else {
    $tickets = Get-ChildItem $todoDir -File | Where-Object { $_.Name -like '*.json' }

    if ($tickets.Count -eq 0) {
        Write-Output "No tickets in todo status"
    exit 0
    }

    Write-Output "Todo tickets ($($tickets.Count) total):"
    foreach ($ticket in $tickets) {
        Write-Output "$($ticket.FullName): $($ticket.id)"
    }
}
