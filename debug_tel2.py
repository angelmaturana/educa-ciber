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

ok = build.build(root, no_validate=True)
print('Build ok:', ok)

# Check ALL pages for tel:
pattern = r'tel:[^"\']*'
for p in (root / 'dist').rglob('*.html'):
    content = p.read_text(encoding='utf-8')
    if 'tel:' in content:
        print('FOUND tel: in', p.relative_to(root / 'dist'))
        matches = list(re.finditer(pattern, content))
        for m in matches[:3]:
            print('  Match at', m.start(), ':', m.group()[:100])