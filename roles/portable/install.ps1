param(
  [Parameter(Mandatory = $true)]
  [string]$SourceRoot,
  [string]$TargetRoles = "$HOME/.config/opencode/roles",
  [string]$TargetSkills = "$HOME/.claude/skills"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Copy-RoleFiles {
  param([string]$FromRoles, [string]$ToRoles)

  if (!(Test-Path $FromRoles)) {
    throw "roles directory not found: $FromRoles"
  }

  New-Item -ItemType Directory -Force -Path $ToRoles | Out-Null

  $includeFiles = @("index.json", "role-*.md", "role_manager.py", "role_sync.py", "role_agents_sync.py", "README.md", "role-template.md")
  foreach ($pattern in $includeFiles) {
    Get-ChildItem -Path $FromRoles -Filter $pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
      Copy-Item -Force $_.FullName (Join-Path $ToRoles $_.Name)
    }
  }

  $agentsDir = Join-Path $FromRoles "agents"
  if (Test-Path $agentsDir) {
    Copy-Item -Path $agentsDir -Destination (Join-Path $ToRoles "agents") -Recurse -Force
  }
}

function Copy-RoleSkills {
  param([string]$FromSkills, [string]$ToSkills)

  if (!(Test-Path $FromSkills)) {
    throw "skills directory not found: $FromSkills"
  }

  New-Item -ItemType Directory -Force -Path $ToSkills | Out-Null

  Get-ChildItem -Path $FromSkills -Directory -Filter "role-*" | ForEach-Object {
    $src = $_.FullName
    $dst = Join-Path $ToSkills $_.Name
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
  }
}

$fromRoles = Join-Path $SourceRoot "roles"
$fromSkills = Join-Path $SourceRoot "skills"

Copy-RoleFiles -FromRoles $fromRoles -ToRoles $TargetRoles
Copy-RoleSkills -FromSkills $fromSkills -ToSkills $TargetSkills

$syncScript = Join-Path $TargetRoles "role_sync.py"
if (!(Test-Path $syncScript)) {
  throw "role_sync.py not found after copy: $syncScript"
}

python "$syncScript" sync
if ($LASTEXITCODE -ne 0) {
  throw "role_sync.py sync failed"
}

python "$syncScript" validate
if ($LASTEXITCODE -ne 0) {
  throw "role_sync.py validate failed"
}

$agentsSyncScript = Join-Path $TargetRoles "role_agents_sync.py"
if (Test-Path $agentsSyncScript) {
  python "$agentsSyncScript"
  if ($LASTEXITCODE -ne 0) {
    throw "role_agents_sync.py failed"
  }
}

Write-Output "Install completed. Roles and skills are synchronized."
