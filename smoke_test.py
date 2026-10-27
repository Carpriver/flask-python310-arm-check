import sys, platform, sqlite3, importlib, importlib.metadata as md
from pathlib import Path
print('Executable:', sys.executable)
print('Version:', sys.version)
print('platform.machine:', platform.machine())
assert sys.version_info[:2] == (3, 10), 'Expected Python 3.10'
import struct
with open(sys.executable, 'rb') as executable:
    executable.seek(0x3c)
    pe_offset = struct.unpack('<I', executable.read(4))[0]
    executable.seek(pe_offset)
    assert executable.read(4) == b'PE\x00\x00'
    machine = struct.unpack('<H', executable.read(2))[0]
print('Python executable PE machine:', hex(machine), '(0x8664=x64, 0xaa64=ARM64)')
assert machine == 0x8664, 'Expected x64 Python executable'
for line in Path(__file__).with_name('requirements.txt').read_text().splitlines():
    if not line or line.startswith('#'): continue
    name, expected = line.split('==')
    actual = md.version(name)
    assert actual == expected, (name, expected, actual)
for module in ['flask', 'flask_wtf', 'flask_sqlalchemy', 'flask_migrate', 'email_validator', 'greenlet']:
    importlib.import_module(module)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config.update(SECRET_KEY='local-smoke-only', WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
db = SQLAlchemy(app)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
class TestForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
@app.route('/')
def index(): return 'ok'
with app.app_context():
    db.create_all()
    db.session.add(Item(name='test'))
    db.session.commit()
    assert db.session.execute(db.select(Item)).scalar_one().name == 'test'
with app.test_request_context('/', method='POST', data={'name':'test'}):
    assert TestForm().validate()
assert app.test_client().get('/').data == b'ok'
print('PASS: versions, imports, Flask HTTP, SQLite/SQLAlchemy, WTForms')
