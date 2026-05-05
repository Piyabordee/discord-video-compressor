# Shell Extension — Windows 11 Modern Context Menu

Adds "Compress to ~9MB" to the Windows 11 top-level context menu (Modern Menu)
without needing "Show more options".

## How It Works

```
User right-clicks video file
        │
        ▼
Windows 11 Modern Menu displays "Compress to ~9MB"
        │
        ▼
MSIX package tells Windows about the menu item
(desktop4:FileExplorerContextMenus + com:ComServer)
        │
        ▼
Windows loads CompressVideoExtension.dll (native C++)
via COM Surrogate (dllhost.exe)
        │
        ▼
IExplorerCommand.Invoke() finds app.exe from registry
and launches: app.exe "C:\path\to\video.mp4"
```

## Architecture

| Component | Technology | Purpose |
|-----------|-----------|---------|
| `CompressVideoExtension.dll` | Native C++ (x64) | COM server implementing `IExplorerCommand` |
| `CompressVideoExtension.msix` | MSIX package | Registers COM server + context menu with Windows 11 |
| `DiscordVideoCompressor.pfx` | Self-signed cert | Signs the MSIX package |

## Key Technical Details

- **Interface**: `IExplorerCommand` (shobjidl.h) — the API Windows 11 uses for modern menu items
- **COM Registration**: `com:SurrogateServer` in MSIX manifest — DLL runs in dllhost.exe, not in Explorer
- **Context Menu Declaration**: `desktop4:FileExplorerContextMenus` with `desktop4:Verb Clsid="{GUID}"`
- **CLSID**: `{D4A8C520-E1C2-4F3E-9B7A-4A8D6C3E5F21}`
- **App Discovery**: DLL reads `InstallLocation` from Inno Setup registry key to find `app.exe`

## File Structure

```
shell_extension/
├── CompressVideoExtension.cpp    # Native C++ source (IExplorerCommand implementation)
├── CompressVideoExtension.dll    # Compiled DLL (native x64, ~111 KB)
├── CompressVideoExtension.msix   # MSIX package (signed, ~5 KB)
├── exports.def                   # DLL export definitions
├── build_cpp.bat                 # Build script (MSVC 2019)
├── build_msix.ps1                # MSIX build + install script
├── AppxManifest.xml              # MSIX manifest
├── DiscordVideoCompressor.pfx    # Signing certificate (private key)
├── DiscordVideoCompressor.cer    # Signing certificate (public key)
├── register.reg                  # Manual COM registration (legacy fallback)
├── unregister.reg                # Manual COM unregistration
└── staging/                      # MSIX build staging directory
    ├── app.exe                   # Dummy exe (required by MSIX schema)
    ├── CompressVideoExtension.dll
    ├── AppxManifest.xml
    └── Assets/
        ├── Square44x44Logo.png   # Placeholder icon
        └── Square150x150Logo.png # Placeholder icon
```

## Build Process

### 1. Build native C++ DLL

```powershell
cd shell_extension
.\build_cpp.bat
```

Requires: Visual Studio 2019+ Build Tools with MSVC (x64)

### 2. Build and install MSIX package

```powershell
# Build only
.\build_msix.ps1

# Build + install (requires Admin)
.\build_msix.ps1 -Install
```

Requires: Windows SDK 10.0.19041.0+ (MakeAppx.exe, SignTool.exe)

### Manual install (Admin PowerShell)

```powershell
cd shell_extension

# Trust the self-signed certificate
Import-Certificate -FilePath DiscordVideoCompressor.cer -CertStoreLocation Cert:\LocalMachine\Root

# Install MSIX package
Add-AppxPackage -Path CompressVideoExtension.msix

# Restart Explorer
Stop-Process -Name explorer -Force; Start-Process explorer
```

### Uninstall

```powershell
Get-AppxPackage | Where-Object { $_.Name -like '*DiscordVideo*' } | Remove-AppxPackage
```

## What We Learned

### What DOES NOT work for Windows 11 Modern Menu

| Approach | Result |
|----------|--------|
| `HKLM\Software\Classes\*\shell\...` registry only | Hidden in "Show more options" |
| `HKCU\Software\Classes\*\shell\...` registry only | Hidden in "Show more options" |
| `HKCR\SystemFileAssociations\video\shell\...` | Hidden in "Show more options" |
| `MUIVerb` + `Extended=0` registry hack | Hidden in "Show more options" |
| .NET Framework COM DLL + MSIX | DLL doesn't have native COM entry points |

### What DOES work

| Approach | Result |
|----------|--------|
| **Native C++ DLL** + MSIX with `com:SurrogateServer` + `desktop4:FileExplorerContextMenus` | Appears in Modern Menu |

The key insight: Windows 11 Modern Context Menu is a closed system.
Registry-only approaches do NOT work. You need:
1. A **native COM DLL** implementing `IExplorerCommand`
2. An **MSIX package** that declares the COM server and context menu
3. A **signing certificate** (self-signed is fine)
