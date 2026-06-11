param(
  [string]$ProjectPath = ".",
  [ValidateSet("codex", "trae", "claude", "cursor", "all")]
  [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$KitRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ProjectFull = Resolve-Path $ProjectPath

Write-Host "Installing DemandSpec Kit"
Write-Host "KitRoot: $KitRoot"
Write-Host "Project: $ProjectFull"
Write-Host "Target: $Target"

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectFull ".demandspec") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectFull "demands") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectFull ".demandspec\templates") | Out-Null

Copy-Item (Join-Path $KitRoot "configs\config.yaml") (Join-Path $ProjectFull ".demandspec\config.yaml") -Force
Copy-Item (Join-Path $KitRoot "configs\glossary.md") (Join-Path $ProjectFull ".demandspec\glossary.md") -Force
Copy-Item (Join-Path $KitRoot "configs\stakeholders.md") (Join-Path $ProjectFull ".demandspec\stakeholders.md") -Force
Copy-Item (Join-Path $KitRoot "configs\standards.md") (Join-Path $ProjectFull ".demandspec\standards.md") -Force
Copy-Item (Join-Path $KitRoot "templates\*.md") (Join-Path $ProjectFull ".demandspec\templates") -Force

if ($Target -eq "codex" -or $Target -eq "all") {
  if ($env:CODEX_HOME) { $CodexHome = $env:CODEX_HOME } else { $CodexHome = Join-Path $HOME ".codex" }
  New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome "prompts") | Out-Null
  Copy-Item (Join-Path $KitRoot "commands\codex\*.md") (Join-Path $CodexHome "prompts") -Force
  Copy-Item (Join-Path $KitRoot "rules\AGENTS.md") (Join-Path $ProjectFull "AGENTS.md") -Force
  Write-Host "Installed Codex prompts to $CodexHome\prompts"
}

if ($Target -eq "trae" -or $Target -eq "all") {
  $TraeSkill = Join-Path $ProjectFull ".trae\skills\demandspec"
  $TraeRules = Join-Path $ProjectFull ".trae\rules"
  New-Item -ItemType Directory -Force -Path $TraeSkill | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $TraeSkill "templates") | Out-Null
  New-Item -ItemType Directory -Force -Path $TraeRules | Out-Null
  Copy-Item (Join-Path $KitRoot "skills\demandspec\SKILL.md") (Join-Path $TraeSkill "SKILL.md") -Force
  Copy-Item (Join-Path $KitRoot "templates\*.md") (Join-Path $TraeSkill "templates") -Force
  Copy-Item (Join-Path $KitRoot "rules\trae-demandspec-rules.md") (Join-Path $TraeRules "demandspec-rules.md") -Force
  Write-Host "Installed Trae skill to $TraeSkill"
}

if ($Target -eq "claude" -or $Target -eq "all") {
  $ClaudeCommands = Join-Path $ProjectFull ".claude\commands"
  New-Item -ItemType Directory -Force -Path $ClaudeCommands | Out-Null
  Copy-Item (Join-Path $KitRoot "commands\claude\*.md") $ClaudeCommands -Force
  Copy-Item (Join-Path $KitRoot "rules\AGENTS.md") (Join-Path $ProjectFull "AGENTS.md") -Force
  Write-Host "Installed Claude commands to $ClaudeCommands"
}

if ($Target -eq "cursor" -or $Target -eq "all") {
  $CursorRules = Join-Path $ProjectFull ".cursor\rules"
  New-Item -ItemType Directory -Force -Path $CursorRules | Out-Null
  Copy-Item (Join-Path $KitRoot "rules\cursor-demandspec.mdc") (Join-Path $CursorRules "demandspec.mdc") -Force
  Write-Host "Installed Cursor rules to $CursorRules"
}

Write-Host "DemandSpec installation complete."
