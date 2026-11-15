#!/usr/bin/env python3
"""Add newly researched reports to the atlas in one step, for the daily update (notes/daily-reports.md).

Takes a JSON file holding a list of items written as notes/gossip-criteria.md §4 says, and:
  1. checks each one beyond what tools/attach_gossip.py checks: `when` is a full date no later than today,
     `retrieved_on` is today or yesterday (every address was opened for this run, §4), and the item's first address is not
     already the address of an item on the same space (the same story twice);
  2. numbers them (`id` may be left out or set to "NEW") and appends them to data/gossip_items.json;
  3. runs the records pipeline: attach_gossip, clean_data, embed_data, check_repetition, build_live_feed;
  4. moves the release on by one (CACHE_NAME in sw.js, ATLAS_RELEASE and the sw.js registration in index.html, and the
     `?v=` on assets/institutions.js), so open pages and the service worker take the new records;
  5. adds a line to the log at the foot of notes/daily-reports.md.

Nothing is written unless every item passes: a refused item stops the run and data/gossip_items.json is left as it was.
The tool writes no report itself and opens no address: the words, the dates and the reading of the sources are the
researcher's, under the rules.

Usage: python3 tools/add_reports.py new_items.json [--left-out "what was searched and left out, and why"]
       python3 tools/add_reports.py --none --left-out "..."     (a day with nothing to add: only the log line)
"""
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / 'data' / 'gossip_items.json'
LOG = ROOT / 'notes' / 'daily-reports.md'
DAY = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def run(*cmd):
    p = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
    tail = '\n'.join((p.stdout + p.stderr).strip().splitlines()[-12:])
    return p.returncode, tail


def norm_url(u):
    return re.sub(r'[/#?]+$', '', re.sub(r'^https?://(www\.)?', '', str(u).strip().lower()))


def log_line(text):
    body = LOG.read_text(encoding='utf-8') if LOG.exists() else ''
    LOG.write_text(body.rstrip('\n') + '\n' + text + '\n', encoding='utf-8')


def bump_release():
    sw = (ROOT / 'sw.js').read_text(encoding='utf-8')
    m = re.search(r"CACHE_NAME\s*=\s*'culture-atlas-v(\d+)'", sw)
    if not m:
        sys.exit('sw.js: CACHE_NAME not found; release not moved')
    old, new = m.group(1), str(int(m.group(1)) + 1)
    (ROOT / 'sw.js').write_text(sw.replace("culture-atlas-v%s'" % old, "culture-atlas-v%s'" % new, 1), encoding='utf-8')
    page = (ROOT / 'index.html').read_text(encoding='utf-8')
    swaps = [("const ATLAS_RELEASE = 'culture-atlas-v%s'" % old, "const ATLAS_RELEASE = 'culture-atlas-v%s'" % new),
             ("register('sw.js?v=%s')" % old, "register('sw.js?v=%s')" % new)]
    for a, b in swaps:
        if page.count(a) != 1:
            sys.exit('index.html: expected one %r, found %d; release not moved' % (a, page.count(a)))
        page = page.replace(a, b)
    page, n = re.subn(r'(assets/institutions\.js\?v=)\d+', r'\g<1>' + new, page)
    if n != 1:
        sys.exit('index.html: expected one assets/institutions.js tag, found %d' % n)
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    return new


def main(argv):
    left_out = ''
    if '--left-out' in argv:
        i = argv.index('--left-out')
        left_out = argv[i + 1].strip().replace('\n', ' ').replace('|', '/')
        del argv[i:i + 2]
    today = dt.date.today()
    if '--none' in argv:
        log_line('| %s | none | Nothing added. %s |' % (today.isoformat(), left_out))
        print('logged a day with nothing added')
        return 0
    if len(argv) != 1:
        sys.exit(__doc__)
    new = json.load(open(argv[0], encoding='utf-8'))
    if not isinstance(new, list) or not new:
        sys.exit('the file must hold a list with at least one item; use --none for a day with nothing')
    before = ITEMS.read_text(encoding='utf-8')
    items = json.loads(before)
    seen = {}
    for it in items:
        for u in it.get('urls') or []:
            seen.setdefault(norm_url(u), []).append(it)
    next_id = max(int(it['id'][1:]) for it in items) + 1
    errors = []
    for n, it in enumerate(new, 1):
        tag = 'item %d (%s)' % (n, str(it.get('headline', ''))[:50])
        when, got = str(it.get('when', '')), str(it.get('retrieved_on', ''))
        if not DAY.match(when) or when > today.isoformat():
            errors.append('%s: when must be a full date, YYYY-MM-DD, not after today' % tag)
        if not DAY.match(got) or not (today - dt.timedelta(days=1)).isoformat() <= got <= today.isoformat():
            errors.append('%s: retrieved_on must be today or yesterday: every address is opened for this run' % tag)
        if '—' in str(it.get('headline', '')) + str(it.get('said', '')):
            errors.append('%s: an em dash in the text; the records do not use one' % tag)
        urls = it.get('urls') or []
        if urls:
            for old in seen.get(norm_url(urls[0]), []):
                if old.get('institution') == it.get('institution'):
                    errors.append('%s: its first address is already the source of %s on the same space' % (tag, old['id']))
        it['id'] = 'G%d' % next_id
        next_id += 1
    if errors:
        for e in errors:
            print('ERROR', e)
        sys.exit('%d error(s); nothing written.' % len(errors))
    ITEMS.write_text(json.dumps(items + new, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    code, out = run('tools/attach_gossip.py')
    if code:
        ITEMS.write_text(before, encoding='utf-8')
        print(out)
        sys.exit('tools/attach_gossip.py refused the items; data/gossip_items.json is as it was.')
    print(out)
    for step in (['tools/clean_data.py'], ['tools/embed_data.py'], ['tools/check_repetition.py', '--max', '0'],
                 ['tools/build_live_feed.py']):
        code, out = run(*step)
        print('%s: %s' % (step[0], out.splitlines()[-1] if out else 'done') if step[0] != 'tools/build_live_feed.py' else out)
        if code:
            print(out)
            sys.exit('%s failed. The records are half rebuilt: fix the cause and run the step again, or '
                     '`git checkout .` to start over.' % step[0])
    release = bump_release()
    ids = ', '.join(it['id'] for it in new)
    spaces = sorted({it['institution'] for it in new})
    log_line('| %s | %s | %d item%s on %s (release %s). %s |' % (
        today.isoformat(), ids, len(new), '' if len(new) == 1 else 's', '; '.join(spaces), release, left_out))
    print('added %s; release %s. Next: npm test, then commit.' % (ids, release))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
