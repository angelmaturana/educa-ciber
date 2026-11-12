import tempfile
import shutil
from pathlib import Path
import json
import sys
import re
sys.path.insert(0, 'legible')
import build

tmp = tempfile.TemporaryDirectory()
root = Path(tmp.name)
shutil.copytree('src', root / 'src')

# Modify site.json to have empty phone (like the test does)
path = root / 'src' / 'data' / 'site.json'
config = json.loads(path.read_text(encoding='utf-8'))
config['phone_e164'] = ''
path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

# Check what phone_value and phone_digits would be
phone_value = str(config.get('phone_e164') or '').strip()
print('phone_value:', repr(phone_value))
phone_digits = ''
if phone_value and not phone_value.startswith('https://'):
    phone_digits = re.sub(r'\D', '', phone_value)
print('phone_digits:', repr(phone_digits))

ok = build.build(root, no_validate=True)
print('Build ok:', ok)

# Check the specific page
teletrabajo_path = root / 'dist' / 'aprende' / 'ciberseguridad-en-el-trabajo' / 'teletrabajo' / 'index.html'
content = teletrabajo_path.read_text(encoding='utf-8')
print('Has tel: in teletrabajo:', 'tel:' in content)

# Search for tel: in the content
pattern = r'tel:[^"\']*'
matches = list(re.finditer(pattern, content))
for m in matches:
    print('Found tel: at', m.start(), ':', m.group())

# Check contact page
contact_path = root / 'dist' / 'contact' / 'index.html'
content = contact_path.read_text(encoding='utf-8')
print('Has tel: in contact:', 'tel:' in content)