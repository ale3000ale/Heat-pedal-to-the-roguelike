@echo off
REM run_backend.bat - lancia run_backend.ps1 bypassando la ExecutionPolicy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_backend.ps1"
pause
