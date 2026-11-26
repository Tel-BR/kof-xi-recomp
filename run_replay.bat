@echo off
setlocal
cd /d "%~dp0"
set "DOD_MUTE="
set "REPLAY=private\tools\pcsx2\ticket19.p2m2"
if not exist "%REPLAY%" set "REPLAY=private\tools\pcsx2\ticket19_trunc1000.p2m2"
if not "%~1"=="" (
    set "REPLAY=%~1"
) else if not exist "%REPLAY%" (
    echo Arraste um replay .p2m2 para este arquivo ou passe o caminho como argumento.
    pause
    exit /b 1
)
echo KOF XI - Replay de referencia ^(GPU^)
echo Logs em private\fixer-port\replay_out.txt e replay_err.txt
python tools\runtime\run_native.py --replay "%REPLAY%" --stdout private\fixer-port\replay_out.txt --stderr private\fixer-port\replay_err.txt
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo O replay encerrou com codigo %RESULT%.
    pause
)
exit /b %RESULT%
