$pkg = Get-AppxPackage -Name "DiscordVideoCompressor.ShellExtension" -ErrorAction SilentlyContinue
if ($pkg) {
    Remove-AppxPackage -Package $pkg.PackageFullName -ErrorAction SilentlyContinue
}
