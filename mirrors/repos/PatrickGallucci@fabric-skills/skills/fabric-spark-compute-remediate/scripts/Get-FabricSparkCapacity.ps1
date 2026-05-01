<#
.SYNOPSIS
    Calculates Microsoft Fabric Spark compute capacity limits for a given SKU size.

.DESCRIPTION
    Determines VCore allocation, burst capacity, max nodes per node size, and queue
    limits for Microsoft Fabric capacity SKUs. Useful for remediate HTTP 430
    throttling errors and planning capacity for Spark workloads.

.PARAMETER SkuSize
    The Fabric capacity SKU size number (e.g., 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048).

.PARAMETER CompareWith
    Optional array of additional SKU sizes to compare side-by-side.

.PARAMETER NodeSize
    Optional node size filter. Valid values: Small, Medium, Large, XLarge, XXLarge.
    When specified, only shows max node calculation for that size.

.EXAMPLE
    .\Get-FabricSparkCapacity.ps1 -SkuSize 64

.EXAMPLE
    .\Get-FabricSparkCapacity.ps1 -SkuSize 64 -CompareWith 128,256

.EXAMPLE
    .\Get-FabricSparkCapacity.ps1 -SkuSize 64 -NodeSize Medium

.NOTES
    Based on Microsoft Fabric documentation as of July 2025.
    1 Capacity Unit = 2 Spark VCores. Burst factor = 3x.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = 'Fabric capacity SKU size (e.g., 64 for F64)')]
    [ValidateSet(2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048)]
    [int]$SkuSize,

    [Parameter(Mandatory = $false, HelpMessage = 'Additional SKU sizes to compare')]
    [int[]]$CompareWith,

    [Parameter(Mandatory = $false, HelpMessage = 'Filter to a specific node size')]
    [ValidateSet('Small', 'Medium', 'Large', 'XLarge', 'XXLarge')]
    [string]$NodeSize
)

#region Configuration Data

$BurstFactor = 3

$NodeSizes = @(
    [PSCustomObject]@{ Name = 'Small';   VCores = 4;  MemoryGB = 32  }
    [PSCustomObject]@{ Name = 'Medium';  VCores = 8;  MemoryGB = 64  }
    [PSCustomObject]@{ Name = 'Large';   VCores = 16; MemoryGB = 128 }
    [PSCustomObject]@{ Name = 'XLarge';  VCores = 32; MemoryGB = 256 }
    [PSCustomObject]@{ Name = 'XXLarge'; VCores = 64; MemoryGB = 512 }
)

$QueueLimits = @{
    2    = 4
    4    = 4
    8    = 8
    16   = 16
    32   = 32
    64   = 64
    128  = 128
    256  = 256
    512  = 512
    1024 = 1024
    2048 = 2048
}

$PowerBIEquiv = @{
    64  = 'P1'
    128 = 'P2'
    256 = 'P3'
    512 = 'P4'
}

#endregion

#region Functions

function Get-SkuCapacity {
    [CmdletBinding()]
    param([int]$Sku)

    $baseVCores   = $Sku * 2
    $maxVCores    = $baseVCores * $BurstFactor
    $queueLimit   = $QueueLimits[$Sku]
    $pbiEquiv     = if ($PowerBIEquiv.ContainsKey($Sku)) { $PowerBIEquiv[$Sku] } else { '-' }

    $nodeCalcs = foreach ($node in $NodeSizes) {
        [PSCustomObject]@{
            NodeSize  = $node.Name
            VCores    = $node.VCores
            MemoryGB  = $node.MemoryGB
            MaxNodes  = [math]::Floor($maxVCores / $node.VCores)
        }
    }

    if ($NodeSize) {
        $nodeCalcs = $nodeCalcs | Where-Object NodeSize -eq $NodeSize
    }

    [PSCustomObject]@{
        SkuName       = "F$Sku"
        CapacityUnits = $Sku
        PowerBIEquiv  = $pbiEquiv
        BaseVCores    = $baseVCores
        BurstFactor   = "${BurstFactor}x"
        MaxVCores     = $maxVCores
        QueueLimit    = $queueLimit
        NodeOptions   = $nodeCalcs
    }
}

function Write-SkuSummary {
    [CmdletBinding()]
    param([PSCustomObject]$Capacity)

    Write-Host ''
    Write-Host "=== $($Capacity.SkuName) Capacity Summary ===" -ForegroundColor Cyan
    Write-Host "  Capacity Units:     $($Capacity.CapacityUnits)"
    Write-Host "  Power BI Equiv:     $($Capacity.PowerBIEquiv)"
    Write-Host "  Base Spark VCores:  $($Capacity.BaseVCores)"
    Write-Host "  Burst Factor:       $($Capacity.BurstFactor)"
    Write-Host "  Max Spark VCores:   $($Capacity.MaxVCores)" -ForegroundColor Green
    Write-Host "  Queue Limit:        $($Capacity.QueueLimit)"
    Write-Host ''
    Write-Host '  Node Size Options:' -ForegroundColor Yellow

    $Capacity.NodeOptions | ForEach-Object {
        $line = "    {0,-10} {1,3} VCores | {2,4} GB RAM | Max {3,4} nodes" -f `
            $_.NodeSize, $_.VCores, $_.MemoryGB, $_.MaxNodes
        Write-Host $line
    }
    Write-Host ''
}

#endregion

#region Main Execution

$primaryCapacity = Get-SkuCapacity -Sku $SkuSize
Write-SkuSummary -Capacity $primaryCapacity

if ($CompareWith) {
    Write-Host '--- Comparison ---' -ForegroundColor Magenta

    $allSkus = @($SkuSize) + $CompareWith | Sort-Object
    $comparisonData = foreach ($sku in $allSkus) {
        $cap = Get-SkuCapacity -Sku $sku
        [PSCustomObject]@{
            SKU         = $cap.SkuName
            'Base VCores' = $cap.BaseVCores
            'Max VCores'  = $cap.MaxVCores
            'Queue Limit' = $cap.QueueLimit
        }
    }
    $comparisonData | Format-Table -AutoSize
}

# Output the primary capacity object for pipeline use
$primaryCapacity

#endregion
