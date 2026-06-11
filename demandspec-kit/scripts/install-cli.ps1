$ErrorActionPreference = "Stop"
$KitRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
python -m pip install -e $KitRoot
Write-Host "DemandSpec CLI installed. Run: demandspec --version"
