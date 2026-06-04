# Deploy MyAgent to dev (us-east-1).
# Windows: UV_LINK_MODE=copy fixes uv hardlink errors during CDK synth.
# First time in account/region: run cdk bootstrap (see docs/AWS_CICD.md).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

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
