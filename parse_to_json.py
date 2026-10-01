import json
import re

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions_raw.js') as f:
    content = f.read()

# Remove 'const institutions = ' and ';\nconsole.log(JSON.stringify(institutions));\n'
prefix = 'const institutions = '
if content.startswith(prefix):
    content = content[len(prefix):]
suffix = ';\nconsole.log(JSON.stringify(institutions));\n'
if content.endswith(suffix):
    content = content[:-len(suffix)]

# We can parse the array of objects
# Format is [{n:`ARoS`,c:`Aarhus, Denmark`,t:`A`,s:`L`,f:`...`,w:`...`,u:[`...`],la:56.153,lo:10.199}, ...]
pattern = re.compile(r'\{n:`(?P<name>[^`]*)`,\s*c:`(?P<city>[^`]*)`,\s*t:`(?P<tier>[^`]*)`,\s*s:`(?P<size>[^`]*)`,\s*f:`(?P<funding>[^`]*)`,\s*w:`(?P<watch>[^`]*)`,\s*u:\[(?P<urls>[^\]]*)\],\s*la:(?P<lat>[-0-9.]+),\s*lo:(?P<lon>[-0-9.]+)\}')

items = []
for m in pattern.finditer(content):
    urls_raw = m.group('urls')
    urls = [u.strip('`').strip() for u in urls_raw.split(',') if u.strip('`').strip()]
    items.append({
        'name': m.group('name'),
        'location': m.group('city'),
        'tier': m.group('tier'),
        'size': m.group('size'),
        'funding': m.group('funding'),
        'watch': m.group('watch'),
        'sources': urls,
        'lat': float(m.group('lat')),
        'lon': float(m.group('lon')),
    })

print(f"Parsed {len(items)} institutions")
if items:
    print("First item:", json.dumps(items[0], indent=2))
    print("Last item:", json.dumps(items[-1], indent=2))

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json', 'w') as f:
    json.dump(items, f, indent=2)
