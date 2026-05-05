[Setup]
AppId={{E8B6B4E5-2A59-4A6E-9D37-0D2F1B5D9B9F}
AppName=Compress to ~9MB
AppVersion=1.0.0
AppPublisher=YourName
DefaultDirName={autopf}\Compress to 9MB
DefaultGroupName=Compress to 9MB
UninstallDisplayIcon={app}\app.exe
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
OutputBaseFilename=Setup_Compress9MB
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "app.exe";     DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "shell_extension\CompressVideoExtension.msix"; DestDir: "{app}\shell_extension"; Flags: ignoreversion; Tasks: modernmenu
Source: "shell_extension\DiscordVideoCompressor.cer"; DestDir: "{app}\shell_extension"; Flags: ignoreversion; Tasks: modernmenu
Source: "shell_extension\install_msix.ps1"; DestDir: "{app}\shell_extension"; Flags: ignoreversion; Tasks: modernmenu
Source: "shell_extension\uninstall_msix.ps1"; DestDir: "{app}\shell_extension"; Flags: ignoreversion; Tasks: modernmenu

[Icons]
; Start Menu (ใช้ชื่อเต็ม ~9MB)
Name: "{group}\Compress to ~9MB"; Filename: "{app}\app.exe"

; Desktop (ชื่อสั้น Compress to 9MB)
Name: "{autodesktop}\Compress to 9MB"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Tasks]
; ลบ Flags: unchecked → เป็นติ๊กค่าเริ่มต้น
Name: "desktopicon"; Description: "Create desktop icon"
Name: "modernmenu"; Description: "Add Windows 11 modern context menu (MSIX)"

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\shell_extension\install_msix.ps1"""; Flags: runhidden; Tasks: modernmenu
Filename: "{app}\app.exe"; Description: "Open program"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\shell_extension\uninstall_msix.ps1"""; Flags: runhidden
