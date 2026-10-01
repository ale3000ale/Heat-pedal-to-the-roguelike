@echo off
cd /d "%~dp0"
where py >nul 2>nul && (py -3 tools\heat.py start %* & goto :end)
python tools\heat.py start %*
:end