@echo off
setlocal
call "%~dp0find_conda.bat" "%~1"
if errorlevel 1 goto stop
"%CLASS_BASE%\python.exe" -I -B "%~dp0class_tools.py" check --base "%CLASS_BASE%"
set "CLASS_RC=%ERRORLEVEL%"
echo Exit code: %CLASS_RC%
if not defined CLASS_CI pause
exit /b %CLASS_RC%
:stop
if not defined CLASS_CI pause
exit /b 2
