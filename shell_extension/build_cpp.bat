@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64 >nul 2>&1

echo Building CompressVideoExtension.dll (native C++)...
cl.exe /nologo /LD /EHsc /O2 /W3 /D "NDEBUG" /D "UNICODE" /D "_UNICODE" CompressVideoExtension.cpp /link /DEF:exports.def /OUT:CompressVideoExtension.dll

if exist CompressVideoExtension.dll (
    echo.
    echo Build successful!
    for %%f in (CompressVideoExtension.dll) do echo Size: %%~zf bytes
) else (
    echo Build FAILED
)

REM Clean up
if exist CompressVideoExtension.obj del CompressVideoExtension.obj
if exist CompressVideoExtension.exp del CompressVideoExtension.exp
if exist CompressVideoExtension.lib del CompressVideoExtension.lib
