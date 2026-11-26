@echo off
setlocal
cd /d "%~dp0"
set "DOD_MUTE="
echo KOF XI - Jogo interativo ^(GPU^)
echo Logs em private\fixer-port\play_out.txt e play_err.txt
python tools\runtime\run_native.py --stdout private\fixer-port\play_out.txt --stderr private\fixer-port\play_err.txt %*
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo O jogo encerrou com codigo %RESULT%.
    pause
)
exit /b %RESULT%
