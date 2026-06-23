param(
    [string]$OutputDir = (Join-Path (Split-Path -Parent (Split-Path -Parent $PSCommandPath)) "dist"),
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$skillDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$releaseDir = Join-Path $OutputDir "iflyrec-meeting-sync"
$zipPath = Join-Path $OutputDir "iflyrec-meeting-sync.zip"

if ($Help) {
    Write-Output "Usage: powershell -File build_skillhub_package.ps1 [-OutputDir <folder>]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}

if (Test-Path -LiteralPath $releaseDir) {
    throw "Release dir already exists: $releaseDir. Choose a clean OutputDir."
}
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

Copy-Item -LiteralPath (Join-Path $skillDir "SKILL.md") -Destination $releaseDir -Force

$allowedExtensions = @{
    agents = @(".yaml", ".yml", ".json")
    references = @(".md", ".txt")
    assets = @(".json", ".md", ".txt", ".png", ".jpg", ".jpeg", ".webp")
    scripts = @(".py", ".ps1")
}

foreach ($dirName in @("agents", "references", "assets", "scripts")) {
    $srcDir = Join-Path $skillDir $dirName
    $dstDir = Join-Path $releaseDir $dirName
    if (Test-Path -LiteralPath $srcDir) {
        New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
        Get-ChildItem -LiteralPath $srcDir -File | ForEach-Object {
            if ($_.Extension.ToLowerInvariant() -notin $allowedExtensions[$dirName]) {
                throw "Unsupported file type for SkillHub package: $dirName/$($_.Name)"
            }
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDir $_.Name) -Force
        }
    }
}

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -Path (Join-Path $releaseDir "*") -DestinationPath $zipPath -Force
Write-Output "Release dir: $releaseDir"
Write-Output "Zip: $zipPath"
