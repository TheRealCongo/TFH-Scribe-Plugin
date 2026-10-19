# Creates a release ZIP that includes the optional private dependency bundle.
Set-Location $PSScriptRoot

$stage = Join-Path $env:TEMP "TFH-Scribe-Plugin-release"
$output = Join-Path $PSScriptRoot "dist\TFH-Scribe-Plugin.zip"

if (Test-Path $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item -Path @(
    "plugin.py", "discord_service.py", "plugin.json", "README.md",
    "LOCAL_ENCRYPTED_TRANSCRIPTS.md", "requirements.txt",
    "install.py", "LICENSE"
) -Destination $stage -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath "lib") {
    Copy-Item -Path "lib" -Destination (Join-Path $stage "lib") -Recurse -Force
}
New-Item -ItemType Directory -Path (Split-Path $output) -Force | Out-Null
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $output -Force
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Host "Built: $output"
