@echo off
REM run_frontend.bat - lancia run_frontend.ps1 bypassando la ExecutionPolicy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_frontend.ps1"
pause
