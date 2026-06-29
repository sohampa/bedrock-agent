# Run Bandit against intentional SAST vulnerability samples.
# Usage: .\scripts\run-sast-samples.ps1

$ErrorActionPreference = "Stop"
$env:UV_LINK_MODE = "copy"

Push-Location "$PSScriptRoot\..\app\MyAgent"
try {
    uv sync --quiet
    uv pip install bandit --quiet
    Write-Host "`n=== Bandit: sast_samples/ (expect failures) ===`n" -ForegroundColor Cyan
    uv run bandit -r sast_samples/ -ll
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
