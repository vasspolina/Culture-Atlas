#!/usr/bin/env python3
"""Which link hosts refuse to be shown inside another page, for the link pane (assets/link-pane.js).

The atlas opens outside links in a pane with a frame. A page in a frame cannot tell whether the site it frames refused
(X-Frame-Options or CSP frame-ancestors), so the hosts are checked here, ahead of time, from the headers each one sends.

  python3 tools/frame_refusers.py hosts  > hosts.tsv     # one host and one real link per host, from the page and the data
  tools/check_frames.sh hosts.tsv headers.tsv             # fetch each link's headers (needs the network; ~15 min)
  python3 tools/frame_refusers.py build headers.tsv       # write assets/frame-refusers.js

The built file maps each host that answered to 1 (refuses) or 0 (allows). Hosts that did not answer, or answered with an
error status (a bot wall often sends headers the real page does not), are left out: the pane then tries the frame, and
falls back to a note with the link if nothing draws.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'frame-refusers.js'
OUR_HOSTS = {'vasspolina.github.io'}
SOURCES = ['index.html', 'institutions.json', 'assets/*.js', 'assets/*.json', 'data/*.json']
URL = re.compile(r'https?://[A-Za-z0-9.-]+(?:/[^"\'<>\\)\s]*)?')


def norm(host):
    host = host.lower().rstrip('.')
    return host[4:] if host.startswith('www.') else host


def hosts():
    seen = {}
    for pattern in SOURCES:
        for path in sorted(ROOT.glob(pattern)):
            if path.name == OUT.name:
                continue
            for url in URL.findall(path.read_text(errors='ignore')):
                h = norm(url.split('/')[2])
                if '.' not in h or h.startswith(('localhost', '127.')) or h in seen:
                    continue
                seen[h] = url
    for h, url in seen.items():
        print(f'{h}\t{url}')


def refuses(xfo, ancestors):
    """CSP frame-ancestors, where sent, decides (browsers then ignore X-Frame-Options); else X-Frame-Options."""
    if ancestors:
        sources = ancestors.split()[1:]
        if '*' in sources or 'https:' in sources:
            return False
        return not any(s.replace('https://', '').rstrip('/') in OUR_HOSTS for s in sources)
    x = xfo.strip().lower()
    return bool(x) and (x.startswith('deny') or x.startswith('sameorigin') or x.startswith('allow-from'))


def build(path):
    table = {}
    for line in Path(path).read_text(errors='ignore').splitlines():
        parts = (line.split('\t') + ['', '', '', ''])[:4]
        host, status, xfo, ancestors = parts
        if not host or not status.isdigit() or not (200 <= int(status) < 400):
            continue
        table[host] = 1 if refuses(xfo, ancestors) else 0
    table = dict(sorted(table.items()))
    body = json.dumps(table, separators=(',', ':'))
    OUT.write_text(
        '/* Built by tools/frame_refusers.py: each link host that answered, 1 if it refuses to be shown inside another page\n'
        '   (X-Frame-Options, CSP frame-ancestors), 0 if it allows it. Read by assets/link-pane.js. Do not edit by hand. */\n'
        f'window.ATLAS_FRAME_REFUSERS = {body};\n')
    n = sum(table.values())
    print(f'{len(table)} hosts, {n} refuse, {len(table) - n} allow -> {OUT.relative_to(ROOT)}', file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'hosts':
        hosts()
    elif len(sys.argv) >= 3 and sys.argv[1] == 'build':
        build(sys.argv[2])
    else:
        sys.exit(__doc__)
