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

[Icons]
; Start Menu (ใช้ชื่อเต็ม ~9MB)
Name: "{group}\Compress to ~9MB"; Filename: "{app}\app.exe"

; Desktop (ชื่อสั้น Compress to 9MB)
Name: "{autodesktop}\Compress to 9MB"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Tasks]
; ลบ Flags: unchecked → เป็นติ๊กค่าเริ่มต้น
Name: "desktopicon"; Description: "Create desktop icon"
Name: "onlyvideo";  Description: "Add context menu only for video files (.mp4/.mkv/.avi/.mov/.webm)"

[Registry]
; All files
Root: HKLM; Subkey: "Software\Classes\*\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\*\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""
Root: HKLM; Subkey: "Software\Classes\*\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""

; Only when task selected
; MP4
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mp4\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""; Tasks: onlyvideo

; MKV
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mkv\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""; Tasks: onlyvideo

; AVI
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.avi\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""; Tasks: onlyvideo

; MOV
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.mov\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""; Tasks: onlyvideo

; WEBM
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\CompressTo9MB"; \
  ValueType: string; ValueName: ""; ValueData: "Compress to ~9MB"; Flags: uninsdeletekey; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\CompressTo9MB"; \
  ValueType: string; ValueName: "Icon"; ValueData: """{app}\app.exe"""; Tasks: onlyvideo
Root: HKLM; Subkey: "Software\Classes\SystemFileAssociations\.webm\shell\CompressTo9MB\command"; \
  ValueType: string; ValueName: ""; ValueData: """{app}\app.exe"" ""%1"""; Tasks: onlyvideo

[Run]
Filename: "{app}\app.exe"; Description: "Open program"; Flags: nowait postinstall skipifsilent
