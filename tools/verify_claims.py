#!/usr/bin/env python3
"""Check what each record says against the sources it cites. Run it where there is network access.

    python3 tools/verify_claims.py                  # every record
    python3 tools/verify_claims.py --tier A         # one tier
    python3 tools/verify_claims.py --limit 50       # the first 50
    python3 tools/verify_claims.py --id aros        # one record

Three checks, in order. A claim is `verified` only when one source that is not the museum's own site passes all three:
  1. reachable   the source answers with HTTP 200 and returns text
  2. about       the text names the institution (its name or an alias)
  3. supports    the text names the funders or sponsors the record cites (at least 2 of them, or all if fewer)

`partial` = some sources reach checks 1 and 2 but none supports the claim. `unverified` = nothing was reachable.
Writes data/verification.json. Nothing here edits institutions.json; run tools/apply_verification.py for that.
This checks that the sources say what the record says. It does not check that the sources are right.
"""
import argparse
import concurrent.futures as cf
import datetime
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from clean_data import host_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
UA = 'Mozilla/5.0 (compatible; CultureAtlasVerifier/1.0)'
STOP = {'The', 'A', 'An', 'And', 'Of', 'For', 'In', 'On', 'At', 'By', 'To', 'With', 'From', 'Its', 'Is', 'Was', 'Has',
        'Museum', 'Art', 'Gallery', 'Foundation', 'Fund', 'City', 'State', 'Public', 'National', 'Private', 'Board',
        'Admissions', 'Individual', 'Donors', 'Corporate', 'Government', 'Council', 'Trust'}


def fetch_text(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,text/plain'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None, resp.status
            raw = resp.read(2_000_000).decode(resp.headers.get_content_charset() or 'utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, 0
    raw = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', raw)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', raw))), 200


def named_things(text):
    """Capitalised names in a claim, minus filler: 'Salling and Ny Carlsberg foundations' -> Salling, Ny Carlsberg."""
    names = []
    for m in re.finditer(r"(?<![\w'])((?:[A-Z][\w&'.-]+)(?:\s+(?:[A-Z][\w&'.-]+|de|van|von|of|la|le|du)){0,3})", text or ''):
        words = [w for w in m.group(1).split() if w not in STOP]
        if words:
            names.append(' '.join(words))
    seen, out = set(), []
    for n in names:
        if n.lower() not in seen and len(n) > 2:
            seen.add(n.lower())
            out.append(n)
    return out


def check_record(rec, delay):
    own = host_of(rec.get('website'))
    claim = ' '.join(filter(None, [rec.get('funding'), rec.get('why_flagged')]))
    needles = [n for n in named_things(claim) if n.lower() != (rec.get('name') or '').lower()]
    ids = [rec['name']] + list(rec.get('aliases') or [])
    sources, best = [], 'unverified'
    for url in [u for u in rec.get('sources') or [] if re.match(r'https?://', u)][:6]:
        time.sleep(delay)
        text, status = fetch_text(url)
        item = {'url': url, 'independent': host_of(url) != own, 'reachable': text is not None, 'http': status}
        if text is not None:
            low = text.lower()
            item['about'] = any(i and i.lower() in low for i in ids)
            found = [n for n in needles if n.lower() in low]
            item['supports'] = bool(needles) and len(found) >= min(2, len(needles))
            item['found'] = found[:8]
        sources.append(item)
        if item['independent'] and item.get('about') and item.get('supports'):
            best = 'verified'
        elif item.get('about') and best != 'verified':
            best = 'partial'
    return {'status': best, 'claim_names': needles[:12], 'sources': sources,
            'checked_on': datetime.date.today().isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tier'); ap.add_argument('--limit', type=int); ap.add_argument('--id')
    ap.add_argument('--workers', type=int, default=6); ap.add_argument('--delay', type=float, default=0.5)
    ap.add_argument('--out', default=str(ROOT / 'data' / 'verification.json'))
    a = ap.parse_args()
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    if a.tier:
        records = [r for r in records if r['tier'] == a.tier]
    if a.id:
        records = [r for r in records if r['id'] == a.id]
    if a.limit:
        records = records[:a.limit]
    out_path = Path(a.out)
    results = json.load(open(out_path)) if out_path.exists() else {}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(check_record, r, a.delay): r for r in records}
        for n, f in enumerate(cf.as_completed(futs), 1):
            r = futs[f]
            results[r['id']] = f.result()
            if n % 20 == 0:
                print(f'{n}/{len(records)}', flush=True)
                json.dump(results, open(out_path, 'w'), indent=1)
    json.dump(results, open(out_path, 'w'), indent=1)
    c = {}
    for v in results.values():
        c[v['status']] = c.get(v['status'], 0) + 1
    print('done', c)


if __name__ == '__main__':
    main()
