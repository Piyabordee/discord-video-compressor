$ErrorActionPreference = "Stop"

$msix = Join-Path $PSScriptRoot "CompressVideoExtension.msix"
$cert = Join-Path $PSScriptRoot "DiscordVideoCompressor.cer"

$pkg = Get-AppxPackage -Name "DiscordVideoCompressor.ShellExtension" -ErrorAction SilentlyContinue
if ($pkg) {
    Remove-AppxPackage -Package $pkg.PackageFullName -ErrorAction SilentlyContinue
}

Import-Certificate -FilePath $cert -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
Add-AppxPackage -Path $msix -ErrorAction Stop
