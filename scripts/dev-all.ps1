$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

# Free backend port if already occupied.
$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($connections) {
  $owningPids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $owningPids) {
    try {
      Stop-Process -Id $procId -Force -ErrorAction Stop
    }
    catch {
      # Ignore stale process IDs that may disappear between lookup and stop.
    }
  }
}

$backendCommand = "Set-Location '$repoRoot'; `$env:PYTHONPATH='backend'; `$env:SOCIETY_TICK_ACTIVE='5'; `$env:SOCIETY_TICK_IDLE='30'; c:/python314/python.exe -m uvicorn backend.main:app --port 8000"
$frontendCommand = "Set-Location '$repoRoot'; npm --prefix frontend run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Sleep -Seconds 1
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Started backend and frontend in separate terminals."
