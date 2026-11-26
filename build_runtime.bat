@echo off
setlocal
cd /d "%~dp0"
set "BUILD_DIR=private\tools\PS2Recomp-Fixer\build\ps2recomp"
if not exist "%BUILD_DIR%\CMakeCache.txt" (
    echo Configure o build GPU do PS2Recomp-Fixer em %BUILD_DIR%.
    pause
    exit /b 1
)
cmake --build "%BUILD_DIR%" --config Release --target ps2EntryRunner
set "RESULT=%ERRORLEVEL%"
if "%RESULT%"=="0" (
    echo Use run_game.bat para jogar ou run_replay.bat para reproduzir um replay .p2m2.
) else (
    echo Falha ao compilar o runtime GPU.
    pause
)
exit /b %RESULT%
