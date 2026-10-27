@echo off
set "CLASS_BASE="
if not "%~1"=="" set "CLASS_BASE=%~1"
if defined CLASS_BASE goto validate
if exist "C:\Miniconda3\python.exe" set "CLASS_BASE=C:\Miniconda3"
if defined CLASS_BASE goto validate
if exist "C:\ProgramData\miniconda3\python.exe" set "CLASS_BASE=C:\ProgramData\miniconda3"
if defined CLASS_BASE goto validate
if exist "%USERPROFILE%\miniconda3\python.exe" set "CLASS_BASE=%USERPROFILE%\miniconda3"
if defined CLASS_BASE goto validate
if exist "%LOCALAPPDATA%\miniconda3\python.exe" set "CLASS_BASE=%LOCALAPPDATA%\miniconda3"
:validate
if not defined CLASS_BASE goto missing
if not exist "%CLASS_BASE%\python.exe" goto missing
if not exist "%CLASS_BASE%\Scripts\conda.exe" goto missing
exit /b 0
:missing
echo STOP: Miniconda not found. Run 00_diagnose.bat and read README.md.
echo Existing standalone Python 3.14 can remain installed.
echo You may pass the approved x64 Miniconda folder as the first argument.
exit /b 2
