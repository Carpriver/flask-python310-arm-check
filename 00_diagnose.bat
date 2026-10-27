@echo off
setlocal
if not exist "%~dp0logs" mkdir "%~dp0logs"
set "CLASS_DIAG=%~dp0logs\initial_diagnosis.txt"
>"%CLASS_DIAG%" echo Classroom preflight - no environment changes
>>"%CLASS_DIAG%" echo Date: %DATE% %TIME%
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "Get-CimInstance Win32_Processor | Select-Object Name,Architecture | Format-List; Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture | Format-List" >>"%CLASS_DIAG%" 2>&1
>>"%CLASS_DIAG%" echo CPU architecture: 12=ARM64, 9=x64
>>"%CLASS_DIAG%" echo Existing commands on PATH - paths only:
"%SystemRoot%\System32\where.exe" python >>"%CLASS_DIAG%" 2>&1
"%SystemRoot%\System32\where.exe" conda >>"%CLASS_DIAG%" 2>&1
call "%~dp0find_conda.bat" "%~1" >>"%CLASS_DIAG%" 2>&1
if defined CLASS_BASE >>"%CLASS_DIAG%" echo Miniconda: %CLASS_BASE%
if exist "C:\conda-envs\flask_python310" >>"%CLASS_DIAG%" echo Target flask_python310 already exists. Do not overwrite.
type "%CLASS_DIAG%"
echo Send logs\initial_diagnosis.txt to your teacher.
if not defined CLASS_CI pause
