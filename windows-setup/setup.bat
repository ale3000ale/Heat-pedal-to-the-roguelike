@echo off
REM setup.bat - lancia setup.ps1 bypassando la ExecutionPolicy di PowerShell,
REM senza bisogno di modificare impostazioni di sistema.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
pause
