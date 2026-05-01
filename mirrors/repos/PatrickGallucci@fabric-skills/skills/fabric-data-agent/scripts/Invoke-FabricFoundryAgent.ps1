<#
.SYNOPSIS
    Invokes a Fabric Data Agent through Azure AI Foundry using the REST API.

.DESCRIPTION
    Creates an agent with the Fabric tool enabled, sends a user question,
    polls for completion, and returns the response. Uses identity passthrough
    so queries execute under the caller's Entra ID permissions.

.PARAMETER ProjectEndpoint
    Azure AI Foundry project endpoint URL.

.PARAMETER FabricConnectionId
    Full resource ID of the Microsoft Fabric connection in the Foundry project.

.PARAMETER ModelDeployment
    Name of the model deployment to use for agent orchestration.

.PARAMETER Question
    Natural language question to ask the Fabric Data Agent.

.PARAMETER AgentInstructions
    Optional instructions for the Foundry agent describing when to use the Fabric tool.

.PARAMETER TimeoutSeconds
    Maximum seconds to wait for the run to complete. Default: 120.

.EXAMPLE
    .\Invoke-FabricFoundryAgent.ps1 `
        -ProjectEndpoint "https://myproject.services.ai.azure.com/api" `
        -FabricConnectionId "/subscriptions/.../connections/fabric-conn" `
        -ModelDeployment "gpt-4o-mini" `
        -Question "What were our top 5 products by revenue last quarter?"

.NOTES
    Requires: PowerShell 7.4+, Az.Accounts module
    API Version: 2025-05-15-preview
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectEndpoint,

    [Parameter(Mandatory)]
    [string]$FabricConnectionId,

    [Parameter(Mandatory)]
    [string]$ModelDeployment,

    [Parameter(Mandatory)]
    [string]$Question,

    [Parameter()]
    [string]$AgentInstructions = 'You are a helpful data analyst. For data-related questions, use the Fabric tool to query enterprise data sources.',

    [Parameter()]
    [ValidateRange(30, 600)]
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$apiVersion = '2025-05-15-preview'

#region Authentication
Write-Host '[1/6] Authenticating...' -ForegroundColor Cyan
$tokenResponse = Get-AzAccessToken -ResourceUrl 'https://cognitiveservices.azure.com'
$token = $tokenResponse.Token
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}
Write-Host '      Authenticated.' -ForegroundColor Green
#endregion

#region Create Agent
Write-Host '[2/6] Creating Foundry agent with Fabric tool...' -ForegroundColor Cyan
$agentBody = @{
    model        = $ModelDeployment
    name         = 'Fabric-DataAgent-Session'
    instructions = $AgentInstructions
    tools        = @(
        @{
            type             = 'fabric_dataagent'
            fabric_dataagent = @{
                connection_id = $FabricConnectionId
            }
        }
    )
} | ConvertTo-Json -Depth 10

$agent = Invoke-RestMethod `
    -Uri "$ProjectEndpoint/assistants?api-version=$apiVersion" `
    -Method Post -Headers $headers -Body $agentBody

$assistantId = $agent.id
Write-Host "      Agent created: $assistantId" -ForegroundColor Green
#endregion

#region Create Thread
Write-Host '[3/6] Creating thread...' -ForegroundColor Cyan
$thread = Invoke-RestMethod `
    -Uri "$ProjectEndpoint/threads?api-version=$apiVersion" `
    -Method Post -Headers $headers -Body '{}'

$threadId = $thread.id
Write-Host "      Thread: $threadId" -ForegroundColor Green
#endregion

#region Add Message
Write-Host '[4/6] Sending question...' -ForegroundColor Cyan
$messageBody = @{
    role    = 'user'
    content = $Question
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "$ProjectEndpoint/threads/$threadId/messages?api-version=$apiVersion" `
    -Method Post -Headers $headers -Body $messageBody | Out-Null

Write-Host "      Question: $Question" -ForegroundColor Green
#endregion

#region Run Thread
Write-Host '[5/6] Running agent...' -ForegroundColor Cyan
$runBody = @{ assistant_id = $assistantId } | ConvertTo-Json

$run = Invoke-RestMethod `
    -Uri "$ProjectEndpoint/threads/$threadId/runs?api-version=$apiVersion" `
    -Method Post -Headers $headers -Body $runBody

$runId = $run.id
$startTime = Get-Date

do {
    Start-Sleep -Seconds 2
    $runStatus = Invoke-RestMethod `
        -Uri "$ProjectEndpoint/threads/$threadId/runs/$runId`?api-version=$apiVersion" `
        -Method Get -Headers $headers

    $elapsed = ((Get-Date) - $startTime).TotalSeconds
    Write-Host "      Status: $($runStatus.status) ($([math]::Round($elapsed))s)" -ForegroundColor Yellow

    if ($elapsed -gt $TimeoutSeconds) {
        Write-Error "Run timed out after $TimeoutSeconds seconds."
        exit 1
    }
} while ($runStatus.status -notin @('completed', 'failed', 'cancelled', 'expired'))

if ($runStatus.status -ne 'completed') {
    Write-Error "Run ended with status: $($runStatus.status)"
    exit 1
}
Write-Host '      Run completed.' -ForegroundColor Green
#endregion

#region Retrieve Response
Write-Host '[6/6] Retrieving response...' -ForegroundColor Cyan
$messages = Invoke-RestMethod `
    -Uri "$ProjectEndpoint/threads/$threadId/messages?api-version=$apiVersion" `
    -Method Get -Headers $headers

$assistantMessage = $messages.data |
    Where-Object { $_.role -eq 'assistant' } |
    Select-Object -First 1

$responseText = ($assistantMessage.content |
    Where-Object { $_.type -eq 'text' } |
    ForEach-Object { $_.text.value }) -join "`n"

Write-Host ''
Write-Host '=== Agent Response ===' -ForegroundColor Cyan
Write-Host $responseText
Write-Host '=====================' -ForegroundColor Cyan
#endregion

#region Output Object
[PSCustomObject]@{
    AssistantId = $assistantId
    ThreadId    = $threadId
    RunId       = $runId
    Question    = $Question
    Response    = $responseText
    Status      = $runStatus.status
    Duration    = [math]::Round($elapsed)
}
#endregion
