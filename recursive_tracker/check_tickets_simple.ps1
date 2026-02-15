# Check whiteboard todo tickets.

$whiteboardDir = "C:\ai\whiteboard\tickets"
$todoDir = Join-Path $whiteboardDir "todo"

Write-Output "Scanning for todo tickets..."

$tickets = Get-ChildItem -Path $todoDir -File

if ($tickets) {
    $count = $tickets.Count
    Write-Output "Found $count tickets in todo status"

    if ($count -gt 0) {
        foreach ($ticket in $tickets) {
            $id = $ticket.id
            $title = $ticket.title
            Write-Output "  - $id : $title"
        }
    } else {
        Write-Output "No tickets found in todo status"
    }
} else {
    Write-Output "No tickets directory found"
}
