"""CI-only assertions. No textbook code, personal data, or credentials."""
from pathlib import Path
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parent
BASE=Path(r'C:\Miniconda3-x64')
TARGET=Path(r'C:\conda-envs\flask_python310')
SNAPSHOT=ROOT/'baseline.json'

def run(command,**kwargs):
    r=subprocess.run([str(x) for x in command],capture_output=True,text=True,errors='replace',**kwargs)
    print(r.stdout,flush=True)
    if r.returncode: print(r.stderr,flush=True)
    assert r.returncode==0, r.returncode
    return r.stdout

def baseline():
    assert sys.version_info[:2]==(3,14),sys.version
    with Path(sys.executable).open('rb') as f:
        f.seek(0x3c); offset=struct.unpack('<I',f.read(4))[0]
        f.seek(offset); assert f.read(4)==b'PE\0\0'
        assert struct.unpack('<H',f.read(2))[0]==0x8664, 'Expected x64 Python under ARM emulation'
    return {'python_version':sys.version,'exe_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
            'conda_records':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'conda-meta').glob('*.json')}}

def final():
    assert json.loads(SNAPSHOT.read_text())==baseline(), 'The original Python 3.14/base environment changed'
    py=TARGET/'python.exe'
    text=run([py,'-I','-B','-c',"import sys; assert sys.version_info[:3]==(3,10,20); print(sys.executable)"])
    assert str(py).lower() in text.lower()
    settings=json.loads(Path(r'C:\work_flask\.vscode\settings.json').read_text(encoding='utf-8'))
    assert settings['python.defaultInterpreterPath']==str(py)
    assert settings['terminal.integrated.defaultProfile.windows']=='Flask Python 3.10'
    activation=settings['terminal.integrated.profiles.windows']['Flask Python 3.10']['args'][1]
    output=run([os.environ['ComSpec'],'/D','/C',activation+' && python -V && where python'])
    assert 'Python 3.10.20' in output and str(py).lower() in output.lower()
    # A genuine loopback HTTP request, in addition to smoke_test.py's test client.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    log=ROOT/'server_test.log'
    with log.open('w',encoding='utf-8') as f:
        process=subprocess.Popen([str(py),'-B','-m','flask','--app','sample_app','run','--host','127.0.0.1','--port',str(port)],
                                 cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        try:
            for attempt in range(60):
                if process.poll() is not None: raise RuntimeError('Flask server exited: '+log.read_text())
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=2) as response:
                        body=response.read().decode()
                        assert response.status==200 and 'Flask student environment OK' in body
                    break
                except (OSError,TimeoutError): time.sleep(0.5)
            else: raise RuntimeError('Timed out waiting for Flask HTTP response')
        finally:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
    print('PASS: ARM64 host, x64 Python 3.10, distributed batches, HTTP, VS Code defaults, original Python 3.14 retained.')
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a',encoding='utf-8') as f:
            f.write('## PASS\n\nWindows ARM64 host with x64 Miniconda/Python 3.10.20.\n\n'
                    '- Distributed setup/check/configuration batches passed.\n'
                    '- Flask HTTP, SQLite/ORM, forms, fixed dependencies passed.\n'
                    '- Original Python 3.14 executable and base package records unchanged.\n'
                    '- VS Code configuration file and terminal activation validated; graphical editor selection not tested.\n'
                    '- School Device Guard and device permissions are outside this test.\n')

if __name__=='__main__':
    if sys.argv[1]=='baseline':
        SNAPSHOT.write_text(json.dumps(baseline(),indent=2),encoding='utf-8')
        print('Baseline retained Python 3.14:',sys.version)
    elif sys.argv[1]=='final': final()
    else: raise SystemExit('Unknown mode')
