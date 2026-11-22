#!/usr/bin/env python3
"""No label that its own line says again: the label check for the text of institutions.json.

The researched lines often open on a label, "Building: since 2011 it occupies a 4,000 m2 building designed by Shigeru Ban", and
the sentence then says the label's words itself, so the reader meets them twice in six words (user, 21 Nov 2026: "Fix the labels
in the record text too"). The page drops a label it draws itself when the line opens on it (leadUnsaid in index.html); this tool
does the same for labels written into the text, at the source, so the chat model is not fed them either.

A label goes only when nothing is lost with it:
  - every word of the label that carries meaning, figures included, is said again in the first sentence after it, outside
    brackets (a source named in brackets, "(Warhol Foundation grants archive)", does not count); or
  - the line is a point of a flagged section and every word of the label is in that section's heading ("Plea:" under
    "TD Bank's 2024 money-laundering plea"), the label holding no figure.
A line that leans on its label stays as it is: one that opens on "it", "its", "they", "this", and one whose words after the label
are a list or an amount, not a sentence. The words after the label then open with a capital.

Usage: python3 tools/unlabel_repeats.py [--fix] [--json report.json] [--max N] [path]
  --fix   take the labels out
  --max N exit 1 when more than N are found (deploy.yml and test.yml run it with --max 0)
After --fix: python3 tools/embed_data.py
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_repetition import sentences, slots  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# Fields whose lines can open on a label. Points of a flagged section are read with their heading.
FIELDS = ['details.overview[]', 'details.funding[]', 'details.wider_context[]', 'details.not_related[]', 'flag_details[].text',
          'case_notes[].text', 'finances_note', 'affiliations_note', 'critique_note', 'watch', 'highlight']
LABEL = re.compile(r'^([A-Z0-9][^:.!?|]{1,60}):\s+(\S.*)$', re.S)
STOP = set('the a an and of in to by is it its for on at as from with that this was are be or not has have had what how who '
           'their his her after over under per via'.split())
LEANS = re.compile(r"^(it|its|it's|they|their|this|these|those|he|she|his|her|which|who|whose|also)\b", re.I)
PAREN = re.compile(r'\((?:[^()]|\([^()]*\))*\)')


def stems(text):
    s = unicodedata.normalize('NFKD', str(text or '').lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    out = []
    for w in re.findall(r"[a-z0-9$€£%]+", s):
        if w in STOP or (len(w) < 3 and not w.isdigit()):
            continue
        if not w.isdigit():
            w = re.sub(r'(ing|ed|es|s|y|e)$', '', w) if len(w) > 4 else w
        out.append(w)
    return out


def said(word, have):
    """A label word is said again when a word after it is the same, or one opens on the other (plea, pleaded)."""
    if word.isdigit():
        return word in have
    return any(h == word or (min(len(h), len(word)) >= 4 and abs(len(h) - len(word)) <= 2 and (h.startswith(word) or word.startswith(h)))
               for h in have)   # two letters apart at most: "Operator" is not said by "Opera"


VERBS = set('''is are was were has have had does did would could says said holds runs owns gives pays sits mentions describes
includes provides sells occupies operates receives keeps publishes cites won gave took made bought sold began became
built held paid ran rose fell came went wrote told sent led grew got lost withdrew drew remains writes'''.split())
NOT_BEFORE_VERB = set('a an the its their his her and or of to by for with newly so-called then-'.split())


def is_verb(words, k):
    """A finite verb, read plainly: one of VERBS (none that is as often a noun: calls, lists, shows, may), or a word in -ed that does not follow an article ("a listed building")."""
    w = words[k].strip('.,;:"“”\'’').lower()
    if w in VERBS:
        return True
    prev = words[k - 1].strip('.,;:"“”\'’').lower() if k else ''
    return len(w) > 4 and w.endswith('ed') and w not in ('listed', 'based') and prev not in NOT_BEFORE_VERB and not prev.endswith('ly')


def unlabel(text, heading=None):
    """The text without its label, or None when the label stays."""
    m = LABEL.match(str(text or ''))
    if not m:
        return None
    label, rest = m.group(1), m.group(2)
    lw = stems(label)
    if not lw or LEANS.match(rest) or rest[0] in '"“‘\'' or re.match(r'^https?:|^\d{1,2}$', label):   # a quotation keeps its label
        return None
    first = (sentences(rest) or [rest])[0]
    have = stems(PAREN.sub(' ', first))
    in_line = all(said(w, have) for w in lw)
    in_head = bool(heading) and not re.search(r'\d', label) and all(said(w, stems(heading)) for w in lw)
    if not (in_line or in_head):
        return None
    # The label may be who "he" or "her statement" is: it stays when such a word comes before the line names the label itself
    # ("Mikhelson finances GES-2: Forbes says he spent more than $470 million"), or when only the heading names it.
    toks = re.findall(r"[^\s]+", PAREN.sub(' ', first))
    who = next((k for k, t in enumerate(toks) if re.fullmatch(r"(he|she|his|her|hers|him|they|their|them)", t.strip('.,;:"“”\'’').lower())), None)
    named = next((k for k, t in enumerate(toks) if any(said(w, stems(t)) for w in lw)), None)
    if who is not None and (not in_line or named is None or who < named):
        return None
    # What is left must be a sentence of its own, with its own subject and verb, not a list, an amount or a clause that leaned
    # on the label ("Director: Washida Meruro since 1 April 2025", "Hyundai Motor: sponsored the series"): five words, and a
    # verb before the first comma, semicolon or bracket that is not the first word.
    # A relative clause is not the sentence's verb ("a programme since 2008 that has taken in 70 artists"), and words that open
    # on "a" or "an" are nearly always a description of the label ("a Grade II listed building by G. A. Humphreys").
    head = re.split(r'[,;(]|\b(?:that|which|who|whose|where)\b', first, maxsplit=1)[0].split()
    if len(first.split()) < 5 or not head or head[0].lower() in ('a', 'an') or is_verb(head, 0) or not any(is_verb(head, k) for k in range(1, len(head))):
        return None
    # A capital opens it, unless the first word is a name written its own way (e-flux, iPhone, de Appel).
    w = rest.split()[0]
    if re.match(r'^[a-z]+$', w.strip('.,;:')) or re.match(r"^[a-z]+['’]s$", w):
        rest = rest[0].upper() + rest[1:]
    return rest


def check_record(rec, fix=False):
    found = []

    def see(box, key, where, heading=None):
        text = box[key]
        if not isinstance(text, str):
            return
        new = unlabel(text, heading)
        if new is None:
            return
        found.append((where, text, new))
        if fix:
            box[key] = new

    for path in FIELDS:
        for box, key, where in slots(rec, path):
            see(box, key, where)
    for i, flag in enumerate(((rec.get('details') or {}).get('red_flags')) or []):
        if not isinstance(flag, dict) or not isinstance(flag.get('points'), list):
            continue
        for j in range(len(flag['points'])):
            see(flag['points'], j, f'details.red_flags[{i}].points[{j}]', flag.get('heading'))
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
            per[rec.get('id') or rec.get('name')] = [{'field': f, 'before': b, 'after': a} for f, b, a in found]
            total += len(found)
    print(f'{len(data)} records, {len(per)} with a label its line says again, {total} labels')
    for rid, items in list(per.items())[:25]:
        for it in items[:2]:
            print(f"  {str(rid)[:36]:36} {it['field'][:30]:30} {it['before'][:90]}")
    if report:
        Path(report).write_text(json.dumps(per, ensure_ascii=False, indent=1), encoding='utf-8')
    if fix and total:
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=True), encoding='utf-8')   # the file's own shape (clean_data.py)
        print(f'took out {total} labels')
    if limit is not None and not fix and total > limit:
        print(f'FAIL: {total} labels, more than {limit}. Fix with python3 tools/unlabel_repeats.py --fix, then tools/embed_data.py', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
