"""Write assets/live.json, the latest reports on the spaces, from institutions.json.

The phone page (assets/phone-maps.js) reads this file when it opens and again every minute, so a report the editor adds
reaches an open page without a reload once the site is deployed. Nothing here is written by this script: every item is a
record's own dated gossip item (gossip_data.gossip, written by tools/attach_gossip.py under notes/gossip-criteria.md) or
dated case note, copied field for field.

An item is left out unless it can be traced:
  - a gossip item needs a headline, a date (YYYY-MM-DD or YYYY-MM), at least one http(s) address, who says it, where,
    and the day the editor last opened its addresses (retrieved_on);
  - a case note needs a title, a YYYY-MM-DD date and at least one http(s) address.
The count of items left out, and why, is printed, so a gap shows up in the deploy log instead of on the page.

Run from the repository root: python3 tools/build_live_feed.py
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = re.compile(r'^\d{4}-\d{2}(-\d{2})?$')
DAY = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def urls_of(values):
    out = []
    for v in values or []:
        u = v if isinstance(v, str) else (v or {}).get('url') if isinstance(v, dict) else None
        if isinstance(u, str) and re.match(r'^https?://', u.strip()) and u.strip() not in out:
            out.append(u.strip())
    return out


def main():
    data = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    items, skipped = [], {}

    def skip(why):
        skipped[why] = skipped.get(why, 0) + 1

    for inst in data:
        base = {
            'inst': inst.get('id') or inst.get('name'),
            'name': inst.get('name'),
            'city': inst.get('city') or '',
            'country': inst.get('country') or '',
            'lat': inst.get('lat'),
            'lon': inst.get('lon'),
        }
        for g in ((inst.get('gossip_data') or {}).get('gossip') or []):
            if not isinstance(g, dict) or not g.get('headline'):
                skip('gossip: no headline'); continue
            if not DATE.match(str(g.get('when') or '')):
                skip('gossip: no date'); continue
            urls = urls_of(g.get('urls'))
            if not urls:
                skip('gossip: no source address'); continue
            if not g.get('who_says') or not g.get('where'):
                skip('gossip: no named source'); continue
            if not DAY.match(str(g.get('retrieved_on') or '')):
                skip('gossip: never checked (no retrieved_on)'); continue
            items.append(dict(base, type='gossip', id=g.get('id') or '', when=g['when'], headline=g['headline'],
                              said=g.get('said') or '', who_says=g['who_says'], where=g['where'], urls=urls,
                              kind=g.get('kind') or 'report', status=g.get('status') or 'talk',
                              response=g.get('response') or '', outcome=g.get('outcome') or '',
                              checked=g['retrieved_on']))
        for i, c in enumerate(inst.get('case_notes') or []):
            if not isinstance(c, dict) or not c.get('title'):
                skip('case: no title'); continue
            if not DAY.match(str(c.get('meta') or '')):
                skip('case: no date'); continue
            urls = urls_of(c.get('sources'))
            if not urls:
                skip('case: no source address'); continue
            items.append(dict(base, type='case', id='C-%s-%d' % (base['inst'], i), when=c['meta'], headline=c['title'],
                              said=c.get('text') or '', who_says='', where='', urls=urls, kind='case',
                              status='documented', response='', outcome='', checked=''))

    items.sort(key=lambda x: x['when'], reverse=True)
    out = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'newest': items[0]['when'] if items else None,
        'count': len(items),
        'items': items,
    }
    body = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    (ROOT / 'assets' / 'live.json').write_text(body, encoding='utf-8')
    # The page checks this small stamp every minute and fetches live.json only when the stamp changes. The digest is of the
    # items alone, so a rebuild that changes nothing does not make every open page fetch the whole file again.
    digest = hashlib.sha256(json.dumps(items, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
    stamp = {'generated': out['generated'], 'newest': out['newest'], 'count': out['count'], 'digest': digest}
    (ROOT / 'assets' / 'live-stamp.json').write_text(json.dumps(stamp, separators=(',', ':')), encoding='utf-8')
    print('assets/live.json: %d items, newest %s, digest %s' % (len(items), out['newest'], digest))
    for why, n in sorted(skipped.items()):
        print('  left out, %s: %d' % (why, n))
    return 0


if __name__ == '__main__':
    sys.exit(main())
