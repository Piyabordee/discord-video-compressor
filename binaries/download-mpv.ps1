#!/usr/bin/env pwsh
# Download MPV DLLs for video preview
# Run this script from PowerShell: .\binaries\download-mpv.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== MPV DLL Download Script ===" -ForegroundColor Cyan
Write-Host ""

$binDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$zipPath = Join-Path $binDir "mpv.7z"
$extractPath = Join-Path $binDir "mpv-temp"

# MPV download URL (Windows x64)
$mpvUrl = "https://github.com/mpv-player/mpv/releases/download/v0.39.0/mpv-x86_64-v3-0.39.0-win7.7z"
$mpvVersion = "0.39.0"

Write-Host "Target Directory: $binDir" -ForegroundColor Yellow
Write-Host "MPV Version: $mpvVersion" -ForegroundColor Yellow
Write-Host ""

# Check if 7z is available
$sevenZip = Get-Command "7z" -ErrorAction SilentlyContinue
if (-not $sevenZip) {
    Write-Host "ERROR: 7-Zip not found in PATH" -ForegroundColor Red
    Write-Host "Install from: https://www.7-zip.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Download manually from:" -ForegroundColor Yellow
    Write-Host "https://github.com/mpv-player/mpv/releases" -ForegroundColor Cyan
    Write-Host "And extract these DLLs to: $binDir" -ForegroundColor Cyan
    Write-Host "  - mpv-2.dll"
    Write-Host "  - avcodec-61.dll"
    Write-Host "  - avformat-61.dll"
    Write-Host "  - avutil-59.dll"
    Write-Host "  - swresample-5.dll"
    Write-Host "  - swscale-7.dll"
    exit 1
}

Write-Host "Step 1: Downloading MPV..." -ForegroundColor Green
Invoke-WebRequest -Uri $mpvUrl -OutFile $zipPath -UseBasicParsing

Write-Host "Step 2: Extracting..." -ForegroundColor Green
& 7z x $zipPath "-o$extractPath" -y | Out-Null

Write-Host "Step 3: Copying DLLs..." -ForegroundColor Green
$sourceDir = Join-Path $extractPath "mpv-*"
$dlls = @(
    "mpv-2.dll",
    "avcodec-61.dll",
    "avformat-61.dll",
    "avutil-59.dll",
    "swresample-5.dll",
    "swscale-7.dll"
)

foreach ($dll in $dlls) {
    $sourceFile = Get-ChildItem -Path $sourceDir -Filter $dll -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($sourceFile) {
        Copy-Item $sourceFile.FullName -Destination (Join-Path $binDir $dll) -Force
        Write-Host "  ✓ $dll" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dll NOT FOUND" -ForegroundColor Red
    }
}

Write-Host "Step 4: Cleaning up..." -ForegroundColor Green
Remove-Item $zipPath -Force
Remove-Item $extractPath -Recurse -Force

Write-Host ""
Write-Host "=== Done! MPV DLLs are ready ===" -ForegroundColor Cyan
Write-Host "You can now run the app with video preview support." -ForegroundColor Green
