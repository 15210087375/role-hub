param(
  [Parameter(Mandatory = $true)]
  [string]$RepoRoot,
  [string]$TargetRoles = "$HOME/.config/opencode/roles",
  [string]$TargetSkills = "$HOME/.claude/skills"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (!(Test-Path $RepoRoot)) {
  throw "repo root not found: $RepoRoot"
}

git -C "$RepoRoot" pull
if ($LASTEXITCODE -ne 0) {
  throw "git pull failed: $RepoRoot"
}

$installScript = Join-Path $PSScriptRoot "install.ps1"
powershell -ExecutionPolicy Bypass -File "$installScript" -SourceRoot "$RepoRoot" -TargetRoles "$TargetRoles" -TargetSkills "$TargetSkills"
if ($LASTEXITCODE -ne 0) {
  throw "install step failed"
}

Write-Output "Update completed."
