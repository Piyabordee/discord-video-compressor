# Build and register MSIX sparse package for Windows 11 Modern Context Menu
# Run as Administrator

param(
    [switch]$Install = $false
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$sdkBin = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64"

# --- Configuration ---
$packageName = "CompressVideoExtension"
$msixFile = Join-Path $scriptDir "$packageName.msix"
$certName = "DiscordVideoCompressor"
$pfxFile = Join-Path $scriptDir "$certName.pfx"
$cerFile = Join-Path $scriptDir "$certName.cer"
$installDir = "C:\Program Files\Compress to 9MB"
$dllSource = Join-Path $scriptDir "CompressVideoExtension.dll"

Write-Host "=== CompressVideo MSIX Sparse Package Builder ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build DLL
Write-Host "[1/6] Building DLL..." -ForegroundColor Yellow
& (Join-Path $scriptDir "build.ps1") -OutputDir $scriptDir
if ($LASTEXITCODE -ne 0) { Write-Host "Build failed"; exit 1 }

# Step 2: Create placeholder assets (required by MSIX)
Write-Host "[2/6] Creating placeholder assets..." -ForegroundColor Yellow
$assetsDir = Join-Path $scriptDir "Assets"
New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null

# Create minimal 1x1 PNG files for required icons
$minimalPng = [byte[]]@(0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,0x54,0x08,0xD7,0x63,0xF8,0xCF,0xC0,0x00,0x00,0x00,0x02,0x00,0x01,0xE2,0x21,0xBC,0x33,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82)
[IO.File]::WriteAllBytes((Join-Path $assetsDir "Square44x44Logo.png"), $minimalPng)
[IO.File]::WriteAllBytes((Join-Path $assetsDir "Square150x150Logo.png"), $minimalPng)

# DLL is already built in script directory, no copy needed

# Step 3: Create mapping file and MSIX package
Write-Host "[3/6] Creating MSIX package..." -ForegroundColor Yellow

$mappingFile = Join-Path $scriptDir "mapping.txt"
$manifestPath = Join-Path $scriptDir "AppxManifest.xml"
$logo44 = Join-Path $assetsDir "Square44x44Logo.png"
$logo150 = Join-Path $assetsDir "Square150x150Logo.png"

$mappingContent = @"
[Files]
"AppxManifest.xml" "$manifestPath"
"CompressVideoExtension.dll" "$dllSource"
"Assets\Square44x44Logo.png" "$logo44"
"Assets\Square150x150Logo.png" "$logo150"
"@
$mappingContent | Set-Content -Path $mappingFile -Encoding UTF8

Write-Host "  Mapping file:" -ForegroundColor Gray
Get-Content $mappingFile | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }

$makeAppx = Join-Path $sdkBin "MakeAppx.exe"
if (Test-Path $msixFile) { Remove-Item $msixFile -Force }
& $makeAppx pack /o /h SHA256 /f $mappingFile /p $msixFile
if ($LASTEXITCODE -ne 0) { Write-Host "MakeAppx failed"; exit 1 }
Write-Host "  Package: $msixFile ($((Get-Item $msixFile).Length) bytes)" -ForegroundColor Green

# Step 4: Create self-signed certificate
Write-Host "[4/6] Creating signing certificate..." -ForegroundColor Yellow
$signTool = Join-Path $sdkBin "SignTool.exe"

if (-not (Test-Path $pfxFile)) {
    $cert = New-SelfSignedCertificate `
        -Type Custom `
        -Subject "CN=$certName" `
        -KeyUsage DigitalSignature `
        -FriendlyName "$certName MSIX Signing" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

    # Export certificate
    $pwd = ConvertTo-SecureString -String "temp" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $pfxFile -Password $pwd | Out-Null
    Export-Certificate -Cert $cert -FilePath $cerFile | Out-Null

    Write-Host "  Certificate created: $($cert.Thumbprint)" -ForegroundColor Green
    Write-Host "  PFX: $pfxFile" -ForegroundColor Green
    Write-Host "  CER: $cerFile" -ForegroundColor Green
} else {
    Write-Host "  Using existing certificate" -ForegroundColor Green
}

# Step 5: Sign the package
Write-Host "[5/6] Signing MSIX package..." -ForegroundColor Yellow
$pwd = ConvertTo-SecureString -String "temp" -Force -AsPlainText
& $signTool sign /fd SHA256 /a /f $pfxFile /p temp $msixFile
if ($LASTEXITCODE -ne 0) { Write-Host "Signing failed"; exit 1 }
Write-Host "  Package signed successfully" -ForegroundColor Green

# Step 6: Install
if ($Install) {
    Write-Host "[6/6] Installing MSIX package..." -ForegroundColor Yellow

    # Trust the certificate (requires admin)
    if (Test-Path $cerFile) {
        Import-Certificate -FilePath $cerFile -CertStoreLocation "Cert:\LocalMachine\Root" | Out-Null
        Write-Host "  Certificate trusted" -ForegroundColor Green
    }

    # Copy DLL to install location
    $shellDir = Join-Path $installDir "shell"
    New-Item -ItemType Directory -Path $shellDir -Force | Out-Null
    Copy-Item $dllSource (Join-Path $shellDir "CompressVideoExtension.dll") -Force
    Write-Host "  DLL copied to: $shellDir" -ForegroundColor Green

    # Install the sparse package
    Add-AppxPackage -Path $msixFile -ExternalLocation $shellDir
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=== INSTALLED SUCCESSFULLY ===" -ForegroundColor Green
        Write-Host "Right-click a video file to see 'Compress to ~9MB' in the Modern Menu" -ForegroundColor Green

        # Restart Explorer
        Write-Host ""
        Write-Host "Restarting Explorer..." -ForegroundColor Yellow
        Stop-Process -Name explorer -Force
        Start-Process explorer
    } else {
        Write-Host "Installation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Package ready: $msixFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "To install, run:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File build_msix.ps1 -Install" -ForegroundColor White
}
