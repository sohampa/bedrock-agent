# Recover dev stack when Bedrock runtime was deleted but CloudFormation still references it.
# Symptom: Runtime 'MyAgent_MyAgent-...' was not found / UPDATE_ROLLBACK_FAILED

$ErrorActionPreference = "Stop"
$Stack = "AgentCore-MyAgent-dev"
$Region = "us-east-1"
$RuntimeLogicalId = "ApplicationAgentMyAgentRuntimeC813BE7A"

Set-Location $PSScriptRoot\..

$status = aws cloudformation describe-stacks --stack-name $Stack --region $Region `
    --query "Stacks[0].StackStatus" --output text 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Stack $Stack not found — ready for fresh deploy."
} else {
    Write-Host "Stack status: $status"
    if ($status -eq "UPDATE_ROLLBACK_FAILED") {
        Write-Host "Continuing rollback (skip missing runtime)..."
        aws cloudformation continue-update-rollback --stack-name $Stack --region $Region `
            --resources-to-skip $RuntimeLogicalId
        aws cloudformation wait stack-rollback-complete --stack-name $Stack --region $Region
    }
    Write-Host "Deleting stack $Stack..."
    aws cloudformation delete-stack --stack-name $Stack --region $Region
    aws cloudformation wait stack-delete-complete --stack-name $Stack --region $Region
    Write-Host "Stack deleted."
}

$stateFile = Join-Path (Get-Location) "agentcore\.cli\deployed-state.json"
Set-Content -Path $stateFile -Value '{"targets":{}}' -Encoding utf8
Write-Host "Reset $stateFile"

Write-Host "`nRedeploy with:"
Write-Host '  $env:UV_LINK_MODE = "copy"'
Write-Host "  agentcore deploy --target dev"
