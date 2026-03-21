#!/usr/bin/env pwsh
# Download MPV libmpv DLLs from GitHub (for python-mpv)

$ErrorActionPreference = "Stop"

$binDir = "c:\Users\snowb4ll\Documents\discord-video-compressor\binaries"
# Direct GitHub release download
$mpvUrl = "https://github.com/zhongyang219/MusicPlayer2/releases/download/v2.76/mpv-2.dll.zip"
$zipPath = "c:\Users\snowb4ll\Downloads\mpv-dll.zip"
$extractPath = "c:\Users\snowb4ll\Downloads\mpv-temp"

Write-Host "Downloading mpv-2.dll..." -ForegroundColor Cyan
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $mpvUrl -OutFile $zipPath -UseBasicParsing

Write-Host "Extracting..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "Copying DLLs..." -ForegroundColor Cyan
$dllFiles = Get-ChildItem $extractPath -Filter '*.dll' -Recurse

foreach ($dll in $dllFiles) {
    Copy-Item $dll.FullName -Destination $binDir\ -Force
    Write-Host "  Copied: $($dll.Name)" -ForegroundColor Green
}

Write-Host "Cleaning up..." -ForegroundColor Cyan
Remove-Item $zipPath -Force
Remove-Item $extractPath -Recurse -Force

Write-Host ""
Write-Host "Done! DLLs in binaries:" -ForegroundColor Green
Get-ChildItem $binDir\*.dll | Select-Object Name
