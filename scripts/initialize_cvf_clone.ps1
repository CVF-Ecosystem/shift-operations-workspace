param(
    [string]$ProjectPath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-FromProject([string]$Root, [string]$RelativePath) {
    return [System.IO.Path]::GetFullPath((Join-Path $Root $RelativePath))
}

if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
    $ProjectPath = Split-Path -Parent $PSScriptRoot
}
$projectResolved = [System.IO.Path]::GetFullPath($ProjectPath)
$manifestPath = Join-Path $projectResolved ".cvf\manifest.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Portable CVF manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$required = @("cvfCoreRepository", "cvfCoreCommit", "cvfCoreRelativePath", "workspaceRulesRelativePath")
$missing = @($required | Where-Object { -not ($manifest.PSObject.Properties.Name -contains $_) })
if ($missing.Count -gt 0) {
    throw "Manifest is not portable schema v2; missing: $($missing -join ', ')"
}
if ([string]$manifest.cvfCoreRepository -ne "https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git") {
    throw "Fresh-clone initializer requires the approved public CVF Core repository"
}
if ([string]$manifest.cvfCoreCommit -cnotmatch '^[0-9a-f]{40}$') {
    throw "Fresh-clone initializer requires an exact 40-character public Core pin"
}

$corePath = Resolve-FromProject $projectResolved $manifest.cvfCoreRelativePath
$workspaceRulesPath = Resolve-FromProject $projectResolved $manifest.workspaceRulesRelativePath
$workspaceRoot = Split-Path -Parent $workspaceRulesPath

$freshClone = -not (Test-Path -LiteralPath $corePath -PathType Container)
if ($freshClone) {
    New-Item -ItemType Directory -Path $workspaceRoot -Force | Out-Null
    git -c core.longpaths=true clone $manifest.cvfCoreRepository $corePath
    if ($LASTEXITCODE -ne 0) { throw "CVF core clone failed" }
}

$origin = (git -C $corePath remote get-url origin | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -ne [string]$manifest.cvfCoreRepository) {
    throw "Installed CVF Core origin differs from approved public repository"
}
if ($freshClone) {
    git -C $corePath config core.longpaths true
    if ($LASTEXITCODE -ne 0) { throw "Unable to enable long-path support in the new CVF core clone" }
}

$pending = (git -C $corePath status --porcelain | Out-String).Trim()
if (-not [string]::IsNullOrWhiteSpace($pending)) {
    throw "Hidden CVF core is dirty; reconcile it before initialization: $corePath"
}

$pin = [string]$manifest.cvfCoreCommit
git -C $corePath cat-file -e "$pin`^{commit}" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Pinned CVF commit is not available in installed public Core: $pin"
}

$head = (git -C $corePath rev-parse HEAD | Out-String).Trim()
if (-not $head.Equals($pin, [System.StringComparison]::OrdinalIgnoreCase)) {
    if (-not $freshClone) {
        throw "Installed shared CVF Core HEAD differs from project pin; request separately reviewed adoption. Local=$head Pin=$pin"
    }
    git -C $corePath checkout --detach $pin --quiet
    if ($LASTEXITCODE -ne 0) { throw "Hidden core checkout of declared pin failed" }
}

$binding = [ordered]@{
    schemaVersion = "1.0"
    workspaceRoot = $workspaceRoot
    workspaceRulesPath = $workspaceRulesPath
    cvfCorePath = $corePath
    projectPath = $projectResolved
    resolvedCoreCommit = (git -C $corePath rev-parse HEAD | Out-String).Trim()
}
$bindingPath = Join-Path $projectResolved ".cvf\local-binding.json"
$binding | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $bindingPath -Encoding utf8

if (-not (Test-Path -LiteralPath $workspaceRulesPath -PathType Leaf)) {
    $sourceRules = Join-Path $corePath "docs\reference\CVF_WORKSPACE_RULES.md"
    Copy-Item -LiteralPath $sourceRules -Destination $workspaceRulesPath
}

$adapter = Join-Path $projectResolved "scripts\check_cvf_core_machine_inheritance.py"
& python $adapter --enforce
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "FRESH_CLONE_CONTINUITY_PASS" -ForegroundColor Green
Write-Host "Project: $projectResolved"
Write-Host "Core:    $corePath @ $pin"
Write-Host "Read AGENTS.md, then resolve the canonical session state and active handoff."
