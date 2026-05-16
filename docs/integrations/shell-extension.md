# Windows Shell Extension

> Native C++ COM DLL for Windows 11 modern context menu integration.

---

## Overview

The shell extension adds "Compress to ~9MB" to the Windows Explorer right-click context menu. It uses the `IExplorerCommand` COM interface to integrate with the Windows 11 modern context menu (the one with icons and sections). The extension is built as a C++ DLL and packaged as an MSIX app.

## Context Snapshot

- Only applies to Windows 11 (modern context menu)
- Built with Visual Studio 2019 BuildTools
- Uses COM `IExplorerCommand` interface (not the legacy registry-based context menu)
- MSIX packaging requires self-signed certificate
- Legacy context menu still available via Inno Setup registry keys (see [[docs/build/build-and-release]])

## When to Read This

### Trigger

- Modifying the context menu text, icon, or behavior
- Debugging context menu registration issues
- Building or packaging the shell extension
- Adding support for additional file types

### Read With

- `docs/build/build-and-release.md` [[docs/build/build-and-release]] — full build chain including MSIX
- `docs/features/entry-modes.md` [[docs/features/entry-modes]] — how the context menu invokes the app

## Setup

### Build Prerequisites

| Tool | Purpose |
|------|---------|
| Visual Studio 2019 BuildTools | C++ compiler for COM DLL |
| MakeAppx.exe | MSIX package creation |
| SignTool.exe | MSIX signing |

### Build Steps

```bash
# 1. Build the C++ DLL
cd shell_extension
build_cpp.bat

# 2. Package as MSIX (includes certificate generation)
powershell -ExecutionPolicy Bypass -File build_msix.ps1

# 3. Install (requires admin)
powershell -ExecutionPolicy Bypass -File install_msix.ps1
```

## Architecture

### COM Server (CompressVideoExtension.cpp)

- Implements `IExplorerCommand` interface
- CLSID: `{D4A8C520-E1C2-4F3E-9B7A-4A8D6C3E5F21}`
- Menu text: "Compress to ~9MB"
- On click: launches `app.exe` from the installed path with the selected file as argument

### App Discovery

The DLL finds `app.exe` by:
1. Reading the install path from registry (set by Inno Setup installer)
2. Falling back to hardcoded path: `C:\Program Files\Compress to 9MB\app.exe`

### Packaging (MSIX)

- `AppxManifest.xml` defines the package identity and COM registration
- `mapping.txt` maps files for MakeAppx
- `build_msix.ps1` creates a self-signed certificate, signs the package
- Assets: minimal placeholder icons (`Square150x150Logo.png`, `Square44x44Logo.png`)

## Key Files

| File | Purpose |
|------|---------|
| `CompressVideoExtension.cpp` | COM server implementation |
| `exports.def` | DLL export definitions |
| `AppxManifest.xml` | MSIX package manifest |
| `build_cpp.bat` | Compile DLL with MSVC |
| `build_msix.ps1` | Package DLL into MSIX |
| `install_msix.ps1` | Install MSIX (import cert + add package) |
| `uninstall_msix.ps1` | Remove MSIX package |
| `register.reg` | Legacy COM registration (non-MSIX) |
| `unregister.reg` | Remove legacy COM registration |
| `mapping.txt` | File mapping for MakeAppx |

## Gotchas

- **MSIX requires self-signed certificate** — `build_msix.ps1` generates one automatically, but it must be imported to Trusted Root on each machine
- **Explorer restart needed** — after installing, restart Explorer: `taskkill /f /im explorer.exe && start explorer.exe`
- **Admin required** — MSIX install and certificate import need elevated privileges
- **Both mechanisms coexist** — Inno Setup writes legacy registry keys; MSIX adds the modern context menu. They don't conflict.

## Troubleshooting

### Context menu not appearing after install

1. Verify MSIX is installed: `Get-AppxPackage *Compress*`
2. Check certificate is in Trusted Root: `certmgr.msc` → Trusted Root Certification Authorities
3. Restart Explorer: `taskkill /f /im explorer.exe && start explorer.exe`
4. Try legacy registration instead: merge `register.reg`

### DLL not loading

1. Check the DLL is signed correctly: `signtool verify /pa CompressVideoExtension.dll`
2. Verify CLSID in registry matches `AppxManifest.xml`
3. Check MSIX package status is "OK": `Get-AppxPackage *Compress* | fl`

---

Related: [[docs/features/entry-modes]] | [[docs/build/build-and-release]] | [[docs/integrations/ffmpeg]]
