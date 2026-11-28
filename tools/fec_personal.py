"""Personal political giving of the people behind family and individual funders, from the FEC's individual
contributions bulk file for a two-year cycle (indivNN.zip, itcont.txt, about 58 million rows for 2023 to 2024).

    python3 -I tools/fec_personal.py /path/to/indiv24.zip matches.json

A row counts only when the contributor's name matches one of PEOPLE and the employer or occupation they reported matches
that person's pattern, so namesakes are left out. Refunds (20Y, 22Y) are taken off, memo lines (MEMO_CD X) left out,
as in the first pass (data/influence_senders.json, `_about`). The script writes every matched row with its employer to
the output file, for the editor to read before any figure is used; it changes no data file.
"""
import io, json, re, sys, zipfile, collections

# funder key -> [(display name, NAME pattern over "LAST, FIRST ...", employer-or-occupation pattern)]
PEOPLE = {
    'leonblack': [('Leon Black', r'^BLACK, LEON\b', r'APOLLO|ELYSIUM|BLACK FAMILY')],
    'right:cohen': [('Steven Cohen', r'^COHEN, STEVEN? ?A?\b', r'POINT ?72|NEW YORK METS|S\.?A\.?C\.? CAPITAL')],
    'schwarzman': [('Stephen Schwarzman', r'^SCHWARZMAN, STEPHEN\b', r'BLACKSTONE')],
    'paulsonfamily': [('John Paulson', r'^PAULSON, JOHN\b', r'PAULSON')],
    'glenndubin': [('Glenn Dubin', r'^DUBIN, GLENN\b', r'DUBIN|HIGHBRIDGE|ENGINEERS GATE')],
    'kanderses': [('Warren Kanders', r'^KANDERS, WARREN\b', r'KANDERS|CADRE|SAFARILAND|CLARUS')],
    'kkr': [('Henry Kravis', r'^KRAVIS, HENRY\b', r'KKR|KOHLBERG')],
    'opensociety': [('George Soros', r'^SOROS, GEORGE\b', r'SOROS|OPEN SOCIETY'),
                    ('Alexander Soros', r'^SOROS, ALEX(ANDER)?\b', r'SOROS|OPEN SOCIETY')],
    'wexner': [('Les Wexner', r'^WEXNER, LES(LIE)?\b', r'WEXNER|L BRANDS|LIMITED BRANDS|BATH & BODY')],
    'adelson': [('Miriam Adelson', r'^ADELSON, MIRIAM\b', r'SANDS|ADELSON')],
    'murdoch': [('Rupert Murdoch', r'^MURDOCH, (K\.? ?)?RUPERT\b', r'NEWS CORP|FOX|TWENTY-FIRST|21ST CENTURY')],
    'waltonfamily': [('Alice Walton', r'^WALTON, ALICE\b', r'WAL-?MART|WALTON|ARVEST|CRYSTAL BRIDGES'),
                     ('Jim Walton', r'^WALTON, JIM\b', r'WAL-?MART|WALTON|ARVEST'),
                     ('Rob Walton', r'^WALTON, (S\.? ?)?ROB(SON)?\b', r'WAL-?MART|WALTON|ARVEST|BRONCOS')],
    'tisch': [('James Tisch', r'^TISCH, JAMES\b', r'LOEWS|TISCH'), ('Jonathan Tisch', r'^TISCH, JONATHAN\b', r'LOEWS|TISCH'),
              ('Andrew Tisch', r'^TISCH, ANDREW\b', r'LOEWS|TISCH'), ('Steve Tisch', r'^TISCH, STEVEN?\b', r'LOEWS|TISCH|GIANTS|ESCAPE ARTISTS')],
    'pritzkerfamily': [('Penny Pritzker', r'^PRITZKER, PENNY\b', r'PSP|PRITZKER'), ('Thomas Pritzker', r'^PRITZKER, THOMAS\b', r'HYATT|PRITZKER')],
    'dell': [('Michael Dell', r'^DELL, MICHAEL\b', r'DELL|MSD')],
    'ericschmidt': [('Eric Schmidt', r'^SCHMIDT, ERIC\b', r'SCHMIDT FUTURES|GOOGLE|ALPHABET|HILLSPIRE|RELATIVITY SPACE|SCHMIDT FAMILY'),
                    ('Wendy Schmidt', r'^SCHMIDT, WENDY\b', r'SCHMIDT')],
    'lucas': [('George Lucas', r'^LUCAS, GEORGE\b', r'LUCASFILM|SKYWALKER|LUCAS MUSEUM'),
              ('Mellody Hobson', r'^HOBSON, MELLODY\b', r'ARIEL')],
    'bezos': [('Jeff Bezos', r'^BEZOS, JEFF(REY)?\b', r'AMAZON|BLUE ORIGIN|BEZOS')],
    'gates': [('Bill Gates', r'^GATES, (BILL|WILLIAM)\b', r'GATES FOUNDATION|GATES VENTURES|BREAKTHROUGH ENERGY|BILL & MELINDA|CASCADE')],
    'geffen': [('David Geffen', r'^GEFFEN, DAVID\b', r'GEFFEN|DREAMWORKS')],
    'perelman': [('Ronald Perelman', r'^PERELMAN, RON(ALD)?\b', r'MACANDREWS|PERELMAN|REVLON')],
    'crownfamily': [('Lester Crown', r'^CROWN, LESTER\b', r'HENRY CROWN|CROWN'), ('James Crown', r'^CROWN, JAMES\b', r'HENRY CROWN')],
    'arisonarts': [('Micky Arison', r'^ARISON, MICKY\b', r'CARNIVAL|MIAMI HEAT|HEAT GROUP')],
    'agnesgund': [('Agnes Gund', r'^GUND, AGNES\b', r'.*')],
    'annenberg': [('Wallis Annenberg', r'^ANNENBERG, WALLIS\b', r'ANNENBERG')],
    'heinz': [('Teresa Heinz', r'^HEINZ(?: KERRY)?, TERESA\b', r'HEINZ')],
    'getty': [('Gordon Getty', r'^GETTY, GORDON\b', r'.*')],
    'broad': [('Edythe Broad', r'^BROAD, EDYTHE\b', r'.*')],
    'fidelity': [('Abigail Johnson', r'^JOHNSON, ABIGAIL\b', r'FIDELITY|FMR')],
    'wynn': [('Steve Wynn', r'^WYNN, (STEPHEN|STEVE)\b', r'.*')],
}


def main(zpath, out):
    pats = [(k, n, re.compile(a), re.compile(b)) for k, ps in PEOPLE.items() for n, a, b in ps]
    surnames = {a.pattern[1:].split(',')[0].split('(')[0] for _, _, a, _ in pats}
    pre = re.compile(r'\|(?:' + '|'.join(sorted(re.escape(s) for s in surnames)) + r')[ ,(]')
    z = zipfile.ZipFile(zpath)
    name = next(n for n in z.namelist() if n.endswith('itcont.txt') and '/' not in n) if any(n == 'itcont.txt' for n in z.namelist()) else z.namelist()[0]
    rows, seen, n = [], collections.Counter(), 0
    for line in io.TextIOWrapper(z.open(name), encoding='latin-1'):
        n += 1
        if not pre.search(line):
            continue
        c = line.rstrip('\n').split('|')
        if len(c) < 21:
            continue
        nm, emp, occ = c[7].upper(), c[11].upper(), c[12].upper()
        for k, disp, a, b in pats:
            if a.search(nm):
                ok = bool(b.search(emp) or b.search(occ))
                seen[(disp, emp, occ, ok)] += 1
                if ok and c[19] != 'X':
                    rows.append({'funder': k, 'person': disp, 'name': c[7], 'employer': c[11], 'occupation': c[12], 'city': c[8], 'state': c[9],
                                 'type': c[5], 'date': c[13], 'usd': float(c[14] or 0), 'cmte': c[0], 'memo': c[19]})
    json.dump({'rows_read': n, 'rows': rows,
               'employers': [{'person': p, 'employer': e, 'occupation': o, 'counted': ok, 'rows': v} for (p, e, o, ok), v in sorted(seen.items(), key=lambda x: (x[0][0], -x[1]))]},
              open(out, 'w'), indent=1)
    print(n, 'rows read;', len(rows), 'kept')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
