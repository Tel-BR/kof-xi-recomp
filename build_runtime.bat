@echo off
echo ===================================================
echo  KOF XI Native PC Port - Build, Install, Speed Check
echo ===================================================
cd /d "%~dp0"
set "TOOLCHAIN=C:\Users\Admin\.local\share\retcomm\toolchains\cmake-clang-v1\latest\bin"
set "PATH=%TOOLCHAIN%;%PATH%"
set "BUILD_DIR=private\tools\PS2Recomp\out\build"

echo.
echo [1/3] Building the runtime (the link step takes several minutes)...
ninja -C "%BUILD_DIR%" ps2EntryRunner
if errorlevel 1 (
    echo Build failed. private\kof_xi_native.exe was not changed.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing as private\kof_xi_native.exe (previous copy kept as .previous)...
if exist private\kof_xi_native.exe copy /y private\kof_xi_native.exe private\kof_xi_native.exe.previous >nul
copy /y "%BUILD_DIR%\ps2xRuntime\ps2EntryRunner.exe" private\kof_xi_native.exe >nul

echo.
echo [3/3] 30-second headless speed check (real speed is 60)...
python tools\runtime\run_native.py --headless --timeout 30 --stdout private\scratch\speed_out.txt --stderr private\scratch\speed_err.txt >nul
python tools\runtime\speed_report.py private\scratch\speed_out.txt private\scratch\speed_err.txt

echo.
echo Done. Use run_game.bat to play.
pause
