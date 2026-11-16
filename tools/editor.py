#!/usr/bin/env python3
"""The data editor: a local page for reading and correcting the records in institutions.json one field at a time.

    python3 tools/editor.py            # then open http://127.0.0.1:8790/
    python3 tools/editor.py --port 9000

It serves editor/ and a small JSON API, on this machine only (127.0.0.1). Nothing here is deployed: the Pages workflow copies
named files and assets/, and editor/ is neither.

  GET  /api/records          every record, as stored
  GET  /api/problems         {record id: [{field, problem}]}, from tools/lint_text.py, for the whole file
  POST /api/lint             body: one record; returns its wording problems, so the page can mark a field as it is typed
  PUT  /api/records/<id>     body: {"record": {...}, "base": {...}}; writes that record back to institutions.json
  POST /api/rebuild          runs tools/clean_data.py then tools/embed_data.py, as after any edit to the records

A save is refused (409) when the record on disk is no longer the one the page loaded (`base`), so an import or a second
window is never overwritten unseen; the page then offers to reload. The file is written the way tools/clean_data.py writes it
(indent 2, ASCII escapes), through a temporary file, so a failed write never leaves half a file.

The rules a record must meet to be saved are deliberately few, the ones every other tool relies on: an object whose `id` is
the one in the address, a non-empty `name`, and numeric `lat` and `lon`. Wording is reported, never refused: the lint is advice.
"""
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
RECORDS = Path(os.environ.get('INSTITUTIONS_FILE') or ROOT / 'institutions.json')
PAGE = ROOT / 'editor'
STATIC = {'/fonts/': ROOT / 'fonts'}

sys.path.insert(0, str(ROOT / 'tools'))
import lint_text  # noqa: E402  (the same rules `python3 tools/lint_text.py` reports)

LOCK = threading.Lock()


def load():
    return json.loads(RECORDS.read_text(encoding='utf-8'))


def write(data):
    text = json.dumps(data, indent=2, ensure_ascii=True)
    fd, tmp = tempfile.mkstemp(dir=RECORDS.parent, prefix='.institutions-', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
        os.replace(tmp, RECORDS)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def problems(rec):
    return [{'field': f, 'problem': p} for f, p in lint_text.problems(rec)]


def keep_types(old, new):
    """A browser reads 12983000.0 as 12983000. Where a number is unchanged, write it back as it was stored, so a save changes
    only the lines that were edited."""
    if isinstance(old, float) and isinstance(new, int) and not isinstance(new, bool) and old == new:
        return old
    if isinstance(old, dict) and isinstance(new, dict):
        return {k: keep_types(old.get(k), v) if k in old else v for k, v in new.items()}
    if isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        return [keep_types(o, n) for o, n in zip(old, new)]
    return new


def invalid(rec, rid):
    if not isinstance(rec, dict):
        return 'The record must be an object.'
    if rec.get('id') != rid:
        return f'The record\'s id is {rec.get("id")!r}, not {rid!r}. An id is not changed here: other files point to it.'
    if not isinstance(rec.get('name'), str) or not rec['name'].strip():
        return 'The record needs a name.'
    for k in ('lat', 'lon'):
        if not isinstance(rec.get(k), (int, float)) or isinstance(rec.get(k), bool):
            return f'{k} must be a number.'
    if not -90 <= rec['lat'] <= 90 or not -180 <= rec['lon'] <= 180:
        return 'lat must be between -90 and 90, and lon between -180 and 180.'
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = 'AtlasEditor/1'

    def log_message(self, fmt, *args):  # one short line per request, no bodies
        sys.stderr.write('%s %s\n' % (self.command, self.path.split('?')[0]))

    def send(self, code, body, kind='application/json; charset=utf-8'):
        raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n).decode('utf-8')) if n else None

    def same_origin(self):
        # The API writes files, so a page on another site must not be able to call it from this machine's browser.
        origin = self.headers.get('Origin')
        return origin is None or urlparse(origin).netloc == self.headers.get('Host')

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/records':
            with LOCK:
                return self.send(200, RECORDS.read_bytes())
        if path == '/api/problems':
            with LOCK:
                data = load()
            found = {r["id"]: problems(r) for r in data}
            return self.send(200, {k: v for k, v in found.items() if v})
        if path == '/':
            path = '/index.html'
        for prefix, base in STATIC.items():
            if path.startswith(prefix):
                return self.file(base, path[len(prefix):])
        return self.file(PAGE, path.lstrip('/'))

    def file(self, base, rel):
        target = (base / unquote(rel)).resolve()
        if base.resolve() not in target.parents or not target.is_file():
            return self.send(404, {'error': 'Not found.'})
        kind = mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        if kind.startswith('text/') or kind.endswith('javascript'):
            kind += '; charset=utf-8'
        return self.send(200, target.read_bytes(), kind)

    def do_POST(self):
        if not self.same_origin():
            return self.send(403, {'error': 'Cross-site request refused.'})
        path = urlparse(self.path).path
        if path == '/api/lint':
            rec = self.body()
            return self.send(200, problems(rec) if isinstance(rec, dict) else [])
        if path == '/api/rebuild':
            out = []
            with LOCK:
                for tool in ('clean_data.py', 'embed_data.py'):
                    p = subprocess.run([sys.executable, str(ROOT / 'tools' / tool)], cwd=ROOT, capture_output=True, text=True)
                    out.append(f'$ python3 tools/{tool}\n' + (p.stdout[-4000:] + p.stderr[-4000:]).strip())
                    if p.returncode:
                        return self.send(500, {'error': f'tools/{tool} stopped.', 'log': '\n\n'.join(out)})
            return self.send(200, {'log': '\n\n'.join(out)})
        return self.send(404, {'error': 'Not found.'})

    def do_PUT(self):
        if not self.same_origin():
            return self.send(403, {'error': 'Cross-site request refused.'})
        path = urlparse(self.path).path
        if not path.startswith('/api/records/'):
            return self.send(404, {'error': 'Not found.'})
        rid = unquote(path[len('/api/records/'):])
        try:
            payload = self.body() or {}
        except ValueError:
            return self.send(400, {'error': 'The request is not JSON.'})
        rec = payload.get('record')
        why = invalid(rec, rid)
        if why:
            return self.send(400, {'error': why})
        with LOCK:
            data = load()
            at = next((i for i, r in enumerate(data) if r.get('id') == rid), None)
            if at is None:
                return self.send(404, {'error': f'No record has the id {rid!r}.'})
            if 'base' in payload and payload['base'] != data[at]:
                return self.send(409, {'error': 'This record changed on disk since the page loaded it.', 'current': data[at]})
            rec = keep_types(data[at], rec)
            data[at] = rec
            write(data)
        return self.send(200, {'record': rec, 'problems': problems(rec)})


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--port', type=int, default=8790)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Data editor on http://127.0.0.1:{args.port}/  ({RECORDS.relative_to(ROOT) if RECORDS.is_relative_to(ROOT) else RECORDS})')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
