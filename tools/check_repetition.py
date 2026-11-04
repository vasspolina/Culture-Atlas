#!/usr/bin/env python3
"""No statement twice in one record: the repetition check for institutions.json.

A record is built from fields researched at different times (the funding line, the researched report, the Epstein records, the
press items, the reported findings), and the same sentence keeps landing in two of them. The page drops a repeat when it renders
(assets/repeats.js); this tool keeps the data itself clean, so the repeat is gone at the source and the chat model is never fed
the same fact twice.

The rules are the same as assets/repeats.js: sentences are compared once case, accents, quotes and punctuation are set aside; a
sentence held whole in an earlier one (8 words or more) or sharing nine in ten words with one (10 words or more) counts as a
repeat; strings under five words, or with fewer than three lower-case words (names, addresses, outlet labels), are never compared.

Fields are read in the order of FIELDS, the order a reader meets them; the first copy stays and later copies go. why_flagged is not
compared: it marks a record as flagged and the page already hides it when it says what funding or watch says. Citation fields
(titles, authors, publications, outlets, dates, urls) are names and are not compared either.

Usage: python3 tools/check_repetition.py [--fix] [--json report.json] [--max N] [path]
  --fix   take the later copies out (a string loses the sentence; a list item, quote or press item that is all repeat goes)
  --max N exit 1 when more than N repeats are found (deploy.yml runs it with --max 0, so a repeat never ships)
  path    another file of records, such as a research batch before it is merged (default institutions.json)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_WORDS, CONTAIN_WORDS, NEAR_WORDS, NEAR = 5, 8, 10, 0.9

# The order a reader meets a record's text in. A path is dotted; [] walks a list. Anything not named here is not compared.
FIELDS = [
    'highlight', 'watch', 'funding', 'note', 'grade_basis',   # note: the research batches' name for watch
    'tier_note', 'records_note', 'finances_note', 'affiliations_note', 'critique_note',
    'details.overview[]', 'details.funding_verdict', 'details.funding[]', 'details.red_flags[].points[]', 'details.wider_context[]',
    'details.not_related[]', 'details.press.overall', 'details.press.items[].points[]', 'details.bottom_line',
    'epstein_records[].summary', 'epstein_records[].tie', 'epstein_records[].consequence', 'wikileaks_records[].what_shows',
    'flag_details[].text', 'case_notes[].text', 'case_study.summary[]', 'case_study.bullets[]', 'case_study.timeline[].event',
    'propaganda[].summary', 'propaganda[].mechanism', 'other_findings',
    'gossip_data.real_cases[].facts[]', 'gossip_data.real_cases[].claims[]', 'gossip_data.real_cases[].response',
    'gossip_data.real_cases[].outcome', 'gossip_data.real_cases[].follow_up', 'gossip_data.real_cases[].limits[]',
    'gossip_data.gossip[].said', 'gossip_data.gossip[].response', 'gossip_data.gossip[].outcome',
    'visual_critiques[].summary', 'visual_critiques[].historical_impact', 'visual_critiques[].quotes[].text',
    'visual_critiques[].quotes[].context', 'study_notes[].text', 'bureaucracy.level_basis',
]
# Lists whose items are whole statements: an item that is all repeat is taken out of the list.
ITEM_LISTS = {'details.overview', 'details.funding', 'details.wider_context', 'details.not_related', 'details.press.items[].points',
              'details.red_flags[].points', 'case_study.summary', 'case_study.bullets', 'gossip_data.real_cases[].facts',
              'gossip_data.real_cases[].claims', 'gossip_data.real_cases[].limits'}

ABBR = re.compile(r"(?:^|[\s(])(?:[A-Z]|[A-Z]\.[A-Z]|[A-Z]\.[A-Z]\.[A-Z]|Mr|Mrs|Ms|Dr|Prof|St|Ste|Mt|Inc|Ltd|Co|Corp|Jr|Sr|No|Nos|Nr|"
                  r"vs|etc|e\.g|i\.e|approx|ca|cf|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|U\.S|U\.K)\.$")
TAIL_CITE = re.compile(r"\s*\((?:[^()]|\([^()]*\))*\)\s*[.!?]*[\"'’”\]]*\s*$")
PIECE = re.compile(r"[^.!?]*(?:[.!?]+[\"'’”)\]]*\s*|$)")


def norm(s):
    s = unicodedata.normalize('NFKD', str(s or '').lower())
    s = ''.join(c for c in s if not unicodedata.combining(c)).replace('’', "'").replace('‘', "'").replace('`', "'")
    s = re.sub(r"[^a-z0-9$€£%']+", ' ', s)
    s = re.sub(r"(^| )'+|'+( |$)", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def is_statement(raw):
    return len(norm(raw).split()) >= MIN_WORDS and len(re.findall(r"(?:^|[\s(,;:'\"“‘])[a-z][a-z'’-]+", str(raw))) >= 3


def sentences(text):
    out = []
    for p in PIECE.findall(str(text or '')):
        if not p:
            continue
        if out and (not re.search(r'\s$', out[-1]) or ABBR.search(out[-1].rstrip())):
            out[-1] += p
        else:
            out.append(p)
    return out


class Seen:
    def __init__(self):
        self.exact, self.long = set(), []
        self.first, self.cite = {}, []   # first: key -> (holder, key, sentence); cite: citations to move onto a first copy

    def has(self, k):
        """The earlier key k repeats (truthy), or None."""
        if k in self.exact:
            return k
        n = len(k.split())
        if n >= CONTAIN_WORDS:
            for o, _ in self.long:
                if len(o) > len(k) and f' {k} ' in f' {o} ':
                    return o
        if n >= NEAR_WORDS:
            mine = set(k.split())
            for o, words in self.long:
                if len(words) >= NEAR_WORDS and len(mine & words) / max(len(mine), len(words)) >= NEAR:
                    return o
        return None

    def add(self, k):
        if k not in self.exact:
            self.exact.add(k)
            if len(k.split()) >= CONTAIN_WORDS:
                self.long.append((k, set(k.split())))

    def check(self, s, where=None):
        """True when s was said already; otherwise s is remembered (with where, the (holder, key) it sits in)."""
        if not is_statement(s):
            return False
        k = norm(TAIL_CITE.sub('', str(s))) or norm(s)   # a closing "(English Wikipedia)." is the source, not the statement
        hit = self.has(k)
        if hit:
            first = self.first.get(hit)
            # The same sentence, cited here and uncited where it was first said: the source moves onto the first copy, so the one
            # copy kept is the cited one.
            if first and where and TAIL_CITE.search(str(s)) and not TAIL_CITE.search(first[2]):
                self.cite.append((first, first[2].rstrip().rstrip('.!?') + TAIL_CITE.search(str(s)).group(0).rstrip()))
            return True
        self.add(k)
        if where:
            self.first[k] = (where[0], where[1], str(s))
        return False


def slots(rec, path):
    """Every (container, key, label) the dotted path reaches, in order. key is an index for list items."""
    parts = path.split('.')
    out = []

    def go(obj, i, label):
        if i == len(parts):
            return
        part = parts[i]
        many = part.endswith('[]')
        name = part[:-2] if many else part
        if not isinstance(obj, dict) or name not in obj:
            return
        val = obj[name]
        last = i == len(parts) - 1
        if many:
            if not isinstance(val, list):
                return
            for j, item in enumerate(val):
                if last:
                    out.append((val, j, f'{label}{name}[{j}]'))
                else:
                    go(item, i + 1, f'{label}{name}[{j}].')
        elif last:
            out.append((obj, name, label + name))
        else:
            go(val, i + 1, label + name + '.')
    go(rec, 0, '')
    return out


LABEL = re.compile(r"^([^.:|]{1,80}:\s+)")              # "Epstein link · Leon Black: " heads an item
CITE = re.compile(r"(\s*\((?:[^()]|\([^()]*\))*\))\s*$")   # "(Cablegate 10RIYADH31; Saudi Cables)" closes one


def clean_text(text, seen, found, label, where=None):
    """text with its repeats taken out. A field of items joined by ' | ' (other_findings) is read item by item: an item whose
    statements were all said before goes whole, with its label and its citation, so no stub such as "(Cablegate 09CANBERRA221)" is
    left behind."""
    items = text.split(' | ')
    out = []
    for item in items:
        head = LABEL.match(item)
        head = head.group(1) if head else ''
        body = item[len(head):]
        tail = CITE.search(body)
        tail = tail.group(1) if tail else ''
        body = body[:len(body) - len(tail)] if tail else body
        parts = sentences(body)
        said = [seen.check(x, where) for x in parts]
        statements = [x for x in parts if is_statement(x)]
        for x, rep in zip(parts, said):
            if rep:
                found.append((label, x.strip()))
        kept = [x for x, rep in zip(parts, said) if not rep]
        if any(said) and not any(is_statement(x) for x in kept) and statements:
            continue                                         # nothing new left in the item: it goes whole
        out.append(head + ''.join(kept).strip() + tail if any(said) else item)
    return ' | '.join(out).strip()


def check_record(rec, fix=False):
    """The repeats in one record, as (field, sentence) pairs; with fix, they are taken out of rec."""
    seen, found, drop_items = Seen(), [], []
    for path in FIELDS:
        for holder, key, label in slots(rec, path):
            text = holder[key]
            if not isinstance(text, str) or not text.strip():
                continue
            before = len(found)
            new = clean_text(text, seen, found, label, (holder, key))
            if fix and len(found) != before:
                if new:
                    holder[key] = new
                elif holder is rec and key not in ('funding', 'watch'):
                    del rec[key]                             # a top-level field with nothing new in it is not kept empty
                elif not isinstance(holder, list):
                    holder[key] = new
                else:
                    drop_items.append((holder, key))
    if fix:
        for (holder, key, first), cited in seen.cite:
            text = holder[key] if isinstance(holder, (dict, list)) and (isinstance(holder, list) or key in holder) else None
            body = first.strip()
            if isinstance(text, str) and text.count(body) == 1:
                holder[key] = text.replace(body, cited)
        # Items emptied by the pass go, last index first so the others keep their place.
        for holder, key in sorted(drop_items, key=lambda x: (id(x[0]), -x[1])):
            del holder[key]
        for q in [v for v in (rec.get('visual_critiques') or []) if isinstance(v, dict)]:
            if isinstance(q.get('quotes'), list):
                q['quotes'] = [x for x in q['quotes'] if not isinstance(x, dict) or (x.get('text') or '').strip() or x.get('parts')]
    return found


def main():
    args = sys.argv[1:]
    fix = '--fix' in args
    limit = int(args[args.index('--max') + 1]) if '--max' in args else None
    report = args[args.index('--json') + 1] if '--json' in args else None
    skip = {i + 1 for i, a in enumerate(args) if a in ('--max', '--json')}
    rest = [a for i, a in enumerate(args) if not a.startswith('--') and i not in skip]
    path = Path(rest[0]) if rest else ROOT / 'institutions.json'
    raw = json.loads(path.read_text(encoding='utf-8'))
    data = raw if isinstance(raw, list) else raw.get('institutions') or next(iter(raw.values()))
    per, total = {}, 0
    for rec in data:
        if not isinstance(rec, dict):
            continue
        found = check_record(rec, fix)
        if found:
            per[rec.get('id') or rec.get('name')] = [{'field': f, 'sentence': s} for f, s in found]
            total += len(found)
    print(f'{len(data)} records, {len(per)} with a repeated statement, {total} repeats')
    for rid, items in list(per.items())[:25]:
        for it in items[:2]:
            print(f"  {rid[:40]:40} {it['field'][:34]:34} {it['sentence'][:90]}")
    if report:
        Path(report).write_text(json.dumps(per, ensure_ascii=False, indent=1), encoding='utf-8')
    if fix and total:
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=True), encoding='utf-8')   # the file's own shape (clean_data.py)
        print(f'took out {total} repeats')
    if limit is not None and not fix and total > limit:
        print(f'FAIL: {total} repeats, more than {limit}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
