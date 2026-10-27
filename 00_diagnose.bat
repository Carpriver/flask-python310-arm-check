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
if defined CLASS_BASE "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "$p=Join-Path $env:CLASS_BASE 'python.exe'; try { $f=[IO.File]::OpenRead($p); $r=New-Object IO.BinaryReader($f); $f.Position=60; $o=$r.ReadInt32(); $f.Position=$o+4; $m=$r.ReadUInt16(); $a=switch($m) { 34404 {'x64 (Intel/AMD build; also usable via emulation on ARM64)'} 43620 {'ARM64 native build'} 332 {'x86 32-bit build'} default {'Unknown PE machine '+$m} }; Write-Output ('Detected Miniconda Python executable: '+$p); Write-Output ('Miniconda architecture: '+$a) } catch { Write-Output ('Miniconda architecture could not be read: '+$_.Exception.Message) } finally { if($r) {$r.Dispose()} elseif($f) {$f.Dispose()} }" >>"%CLASS_DIAG%" 2>&1
if exist "C:\conda-envs\flask_python310" >>"%CLASS_DIAG%" echo Target flask_python310 already exists. Do not overwrite.
type "%CLASS_DIAG%"
echo Send logs\initial_diagnosis.txt to your teacher.
if not defined CLASS_CI pause
