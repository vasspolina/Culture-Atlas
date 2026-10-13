#!/usr/bin/env python3
"""Rewrite the institution data embedded in index.html from institutions.json (after tools/clean_data.py)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / 'index.html').read_text(encoding='utf-8')
data = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
new = 'const ALL_INSTITUTIONS = ' + json.dumps(data, ensure_ascii=True, separators=(',', ':')) + ';\n'
page, n = re.subn(r'const ALL_INSTITUTIONS = \[.*?\];\n', lambda m: new, page, count=1, flags=re.S)
assert n == 1, 'ALL_INSTITUTIONS not found'
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print('embedded', len(data), 'records')
