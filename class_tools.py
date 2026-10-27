"""Create a separate classroom environment; never remove existing environments."""
import argparse
import datetime
import json
import os
import re
from pathlib import Path
import struct
import subprocess
import sys

HERE=Path(__file__).resolve().parent
LOG=None
def say(text):
    print(text,flush=True)
    if LOG:
        with LOG.open('a',encoding='utf-8') as f: f.write(str(text)+'\n')
def run(command,env=None):
    say('RUN: '+subprocess.list2cmdline([str(x) for x in command]))
    r=subprocess.run([str(x) for x in command],capture_output=True,text=True,errors='replace',env=env)
    say(r.stdout+r.stderr)
    if r.returncode: raise RuntimeError('Command failed, exit '+str(r.returncode))
    return r.stdout
def pe_arch(executable):
    with Path(executable).open('rb') as f:
        f.seek(0x3c); offset=struct.unpack('<I',f.read(4))[0]
        f.seek(offset)
        if f.read(4)!=b'PE\0\0': raise RuntimeError('Not a Windows PE executable')
        return struct.unpack('<H',f.read(2))[0]
def check(prefix):
    py=prefix/'python.exe'
    if pe_arch(py)!=0x8664: raise RuntimeError('Expected x64 Python. Native ARM64 is not this package target.')
    run([py,'-I','-B','-m','pip','check'])
    run([py,'-I','-B',HERE/'smoke_test.py'])
    run([py,'-I','-B','-m','flask','--version'])
def configure(project,prefix,base):
    settings=project/'.vscode/settings.json'
    if settings.exists():
        # JSONC or unexpected contents: stop without rewriting. README gives manual steps.
        try: data=json.loads(settings.read_text(encoding='utf-8-sig'))
        except ValueError: raise RuntimeError('settings.json uses JSONC or invalid JSON. Preserved. Follow manual VS Code steps in README.')
        if not isinstance(data,dict): raise RuntimeError('Unexpected settings structure; file preserved.')
    else: data={}
    profiles=data.get('terminal.integrated.profiles.windows',{})
    if not isinstance(profiles,dict): raise RuntimeError('Unexpected terminal profiles structure; file preserved.')
    profile='Flask Python 3.10'
    # The supported ASCII paths need no shell quoting inside the VS Code args array.
    if not all(re.fullmatch(r'[A-Za-z]:\\[A-Za-z0-9_.\\-]+',str(p)) for p in (base,prefix)):
        raise RuntimeError('Automatic terminal configuration requires ASCII paths without spaces or shell metacharacters. Use a school-approved ASCII Miniconda path; existing files preserved.')
    activation='call '+str(base/'condabin/conda.bat')+' activate '+str(prefix)
    profiles[profile]={'path':str(Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32/cmd.exe'),
                       'args':['/K',activation],'overrideName':True}
    data['terminal.integrated.profiles.windows']=profiles
    data['terminal.integrated.defaultProfile.windows']=profile
    data['python.defaultInterpreterPath']=str(prefix/'python.exe')
    data['python.terminal.activateEnvironment']=False
    data['python.useEnvironmentsExtension']=False
    data['terminal.integrated.cwd']=str(project)
    settings.parent.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    if settings.exists():
        backup=HERE/'logs'/('vscode_settings_before_'+stamp+'.json')
        backup.write_bytes(settings.read_bytes()); say('Settings backup: '+str(backup))
    settings.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    say('VS Code defaults saved. Select the exact interpreter once; see README. Existing terminals must be reopened.')
def main():
    global LOG
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['setup','check','vscode'])
    p.add_argument('--base',required=True)
    p.add_argument('--prefix',help='Read-only teacher verification override; check mode only')
    a=p.parse_args()
    (HERE/'logs').mkdir(exist_ok=True)
    LOG=HERE/'logs'/(a.mode+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.txt')
    cfg=json.loads((HERE/'student_config.json').read_text(encoding='utf-8-sig'))
    if a.prefix and a.mode!='check': raise RuntimeError('--prefix only allowed for read-only check')
    prefix=Path(a.prefix or cfg['env_prefix'])
    project=Path(cfg['project_dir']); base=Path(a.base)
    if a.mode!='check' and (str(prefix).lower()!=r'C:\conda-envs\flask_python310'.lower() or str(project).lower()!=r'C:\work_flask'.lower()):
        raise RuntimeError('Unexpected classroom paths; stop for teacher review.')
    if a.mode!='check' and not re.fullmatch(r'[A-Za-z]:\\[A-Za-z0-9_.\\-]+',str(base)):
        raise RuntimeError('Use an approved ASCII Miniconda path without spaces. Keep the existing installation; do not rename its folder.')
    if a.mode!='check' and (pe_arch(base/'python.exe')!=0x8664 or pe_arch(sys.executable)!=0x8664):
        raise RuntimeError('Use a separate school-approved Windows x64 Miniconda. Keep any existing ARM64 Python.')
    ps=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
    info=run([ps,'-NoProfile','-Command',
        '$ErrorActionPreference="Stop"; $cpu=Get-CimInstance Win32_Processor | Select-Object -First 1; '
        '$os=Get-CimInstance Win32_OperatingSystem; '
        '@{cpu=$cpu.Name; architecture=[int]$cpu.Architecture; os=$os.Caption; build=[int]$os.BuildNumber} | ConvertTo-Json -Compress'])
    cpu=json.loads(info)
    say('CPU 9=x64 (Intel or AMD etc.), 12=ARM64 (Snapdragon etc.).')
    if a.mode=='setup':
        if prefix.exists(): raise RuntimeError('Target already exists. No overwrite. Run 02_check.bat; ask teacher if incomplete.')
        if cpu['architecture'] not in (9,12) or cpu['build']<22000:
            raise RuntimeError('This package targets Windows 11 x64 or ARM64. Other platforms require teacher review.')
        if pe_arch(base/'python.exe')!=0x8664 or pe_arch(sys.executable)!=0x8664:
            raise RuntimeError('Selected Miniconda is not x64. Keep it, and use a separate school-approved Windows x64 Miniconda. Do not install native ARM packages into x64 Python.')
        if cpu['architecture']==12: say('ARM64 CPU: x64 emulation route. Not yet validated on the student device.')
        if not (base/'condabin/conda.bat').is_file(): raise RuntimeError('Incomplete Miniconda installation')
        env=os.environ.copy()
        env['CONDA_SUBDIR']='win-64'
        env['PYTHONNOUSERSITE']='1'
        env.pop('PYTHONPATH',None); env.pop('PYTHONHOME',None)
        project.mkdir(parents=True,exist_ok=True)
        prefix.parent.mkdir(parents=True,exist_ok=True)
        env['CONDA_PKGS_DIRS']=str(project/'.conda-pkgs-python310')
        say('Creating only '+str(prefix)+'. Existing 3.14 environments are retained.')
        run([base/'Scripts/conda.exe','create','--yes','--prefix',prefix,
             '--override-channels','--channel','defaults','python=3.10.20','pip=26.1.2'],env)
        run([prefix/'python.exe','-I','-B','-m','pip','install','--only-binary=:all:',
             '--requirement',HERE/'requirements.txt'],env)
    if a.mode=='check':
        run([ps,'-NoProfile','-Command',
          "try { Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-CodeIntegrity/Operational'; Id=3077; StartTime=(Get-Date).AddDays(-3)} -MaxEvents 8 -ErrorAction Stop | Select-Object TimeCreated,Id,Message | Format-List } catch { Write-Output ('Event log unavailable or no matching events: '+$_.Exception.Message) }"])
    check(prefix)
    if a.mode=='vscode': configure(project,prefix,base)
    say('PASS: '+str(prefix)+'; project='+str(project)+'; log='+str(LOG))
if __name__=='__main__':
    try: main()
    except (OSError,RuntimeError,ValueError,struct.error) as e:
        say('STOP: '+str(e))
        say('Access denied or Device Guard: ask school administrator. Do not disable policies or bypass a block.')
        say('No environment is deleted or overwritten. A failed new setup may leave a partial folder; ask teacher before retrying.')
        sys.exit(1)
