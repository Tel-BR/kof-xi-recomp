@echo off
echo ===================================================
echo  KOF XI Native PC Port - Launch Reference Replay
echo ===================================================
cd /d "%~dp0"
python tools\runtime\run_native.py --replay private\tools\pcsx2\ticket19_trunc1000.p2m2
pause
