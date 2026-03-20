@echo off
REM Install MPV player and copy DLLs to binaries folder
REM Run this from: binaries\install-mpv.bat

echo === MPV DLL Installer ===
echo.

set "BIN_DIR=%~dp0"
set "MPV_TEMP=%TEMP%\mpv-installer"

echo Step 1: Installing MPV via winget...
winget install --id mpv.player -e --accept-source-agreements --accept-package-agreements

if errorlevel 1 (
    echo ERROR: winget install failed
    echo Please install manually from: https://mpv.io/installation/
    pause
    exit /b 1
)

echo.
echo Step 2: Finding MPV installation...
for /f "delims=" %%i in ('winget list mpv.player 2^>nul ^| findstr mpv.player') do set "MPV_LINE=%%i"

REM Try common installation paths
set "MPV_PATH="
if exist "C:\Program Files\mpv-x86_64\" set "MPV_PATH=C:\Program Files\mpv-x86_64"
if exist "C:\Program Files (x86)\mpv-x86_64\" set "MPV_PATH=C:\Program Files (x86)\mpv-x86_64"
if exist "%LOCALAPPDATA%\Programs\mpv-x86_64\" set "MPV_PATH=%LOCALAPPDATA%\Programs\mpv-x86_64"

if "%MPV_PATH%"=="" (
    echo ERROR: Cannot find MPV installation directory
    echo Please copy these files manually to: %BIN_DIR%
    echo   - mpv-2.dll
    echo   - avcodec-61.dll
    echo   - avformat-61.dll
    echo   - avutil-59.dll
    echo   - swresample-5.dll
    echo   - swscale-7.dll
    pause
    exit /b 1
)

echo Found MPV at: %MPV_PATH%
echo.
echo Step 3: Copying DLLs...

copy /Y "%MPV_PATH%\mpv-2.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X mpv-2.dll NOT FOUND) else (echo   OK mpv-2.dll)

copy /Y "%MPV_PATH%\avcodec-61.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X avcodec-61.dll NOT FOUND) else (echo   OK avcodec-61.dll)

copy /Y "%MPV_PATH%\avformat-61.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X avformat-61.dll NOT FOUND) else (echo   OK avformat-61.dll)

copy /Y "%MPV_PATH%\avutil-59.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X avutil-59.dll NOT FOUND) else (echo   OK avutil-59.dll)

copy /Y "%MPV_PATH%\swresample-5.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X swresample-5.dll NOT FOUND) else (echo   OK swresample-5.dll)

copy /Y "%MPV_PATH%\swscale-7.dll" "%BIN_DIR%" >nul
if errorlevel 1 (echo   X swscale-7.dll NOT FOUND) else (echo   OK swscale-7.dll)

echo.
echo === Done! ===
echo MPV DLLs are now in: %BIN_DIR%
echo You can now run the app.
pause
