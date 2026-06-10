# Deploy MyAgent to dev (us-east-1).
# Windows: UV_LINK_MODE=copy is REQUIRED — uv hardlinks fail across drives during CDK synth.
# First time in account/region: run cdk bootstrap (see docs/AWS_CICD.md).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

# Always use copy mode on Windows (uv hardlink fails across D: cache vs C: user profile).
$env:UV_LINK_MODE = "copy"

$envFile = Join-Path (Get-Location) "agentcore\.env.deploy"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
        }
    }
}

Write-Host "UV_LINK_MODE=$env:UV_LINK_MODE | Region: us-east-1 | Target: dev"
agentcore deploy --target dev
