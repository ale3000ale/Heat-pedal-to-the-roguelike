@echo off
cd /d "%~dp0"
where py >nul 2>nul && (py -3 tools\heat.py setup %* & goto :end)
python tools\heat.py setup %*
:end
pause