#!/usr/bin/env python3
"""Add artists' critiques of art spaces to the images page, beside the cultural space critique collection.

The collection (references 1801-2000) is built by tools/build_critique_gallery.py from its own gallery.html. Works found
later (user, 15 Nov 2026: "find more images of critisizm of art spaces by artists and add to the archive, like andrea
frzer, hito sterl etc") are kept in data/critique_additions.json, one entry per image, each with the page it was taken
from, the credit that page gives and the date of the work, and this writes them out the same way:

    python3 -I tools/add_critique_images.py <dir of the downloaded files named as in the manifest>

Writes assets/critique_additions/<id>.jpg (at most 2400px on the long side, never enlarged), <id>_t.jpg (480px),
<id>_m.jpg (1200px) and assets/critique-additions-data.js, which artists-images.html sorts in with the collection by
date. Re-running replaces every picture whose downloaded file is in the folder given; a picture already written, whose
download is no longer at hand, is kept as it is, and one the manifest no longer names is removed. A file under MIN_LONG
pixels on its long side stops the run: nothing low-resolution goes in (user, 15 Nov 2026: "do not add low res or blurry
images"); sharpness and cropping were checked by eye, file by file.

A work that names spaces on the atlas lists them under `spaces` on its first entry, each with the record id and the
tie in words ("Hans Haacke, MoMA Poll, in the exhibition Information, 1970"). They are written out as `spaces` (one
group per space for the page's By space view) and `on_spaces` (the spaces each picture is about); a space id that
institutions.json does not hold stops the run.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'critique_additions'
MIN_LONG = 1200
FULL, MID, THUMB = 2400, 1200, 480


def save(im, size, path):
    im = im.copy()
    if max(im.size) > size:
        im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, 'JPEG', quality=82, optimize=True, progressive=True)
    return im.size


def main(img_dir):
    recs = json.loads((ROOT / 'data' / 'critique_additions.json').read_text())
    names = {x['id']: x['name'] for x in json.loads((ROOT / 'institutions.json').read_text())}
    OUT.mkdir(parents=True, exist_ok=True)
    stems = {Path(r['file']).stem for r in recs}
    for f in OUT.glob('*.jpg'):
        if re.sub(r'_[tm]$', '', f.stem) not in stems:
            f.unlink()
    works, spaces, on_spaces, work_spaces = {}, {}, {}, {}
    for r in recs:
        src = Path(img_dir) / r['file']
        n = Path(r['file']).stem
        if src.exists():
            im = ImageOps.exif_transpose(Image.open(src))
            if im.mode in ('RGBA', 'LA', 'P'):          # a transparent ground prints white, not black
                im = im.convert('RGBA')
                bg = Image.new('RGB', im.size, 'white')
                bg.paste(im, mask=im.split()[-1])
                im = bg
            im = im.convert('RGB')
            if max(im.size) < MIN_LONG:
                sys.exit(f'{r["file"]}: {im.size[0]}x{im.size[1]} is under {MIN_LONG}px')
            w, h = save(im, FULL, OUT / f'{n}.jpg')
            save(im, MID, OUT / f'{n}_m.jpg')
            save(im, THUMB, OUT / f'{n}_t.jpg')
        elif all((OUT / f'{n}{x}.jpg').exists() for x in ('', '_m', '_t')):
            w, h = Image.open(OUT / f'{n}.jpg').size   # written by an earlier run; the download is no longer at hand
        else:
            sys.exit(f'{r["file"]}: not in {img_dir} and not written before')
        credit = r['credit'].rstrip('.')
        if r.get('photographer') and 'Photo' not in credit:
            credit = f'{credit}. Photograph: {r["photographer"]}' if credit else f'Photograph: {r["photographer"]}'
        key = (r['artist'], r['title'])
        work = works.setdefault(key, {'artist': r['artist'], 'project': r['title'], 'year': r['year'], 'from': r['sort_year'],
                                      'note': r.get('note', ''), 'story': '', 'images': []})
        if r.get('story'):                          # the background story under Learn more, written once per work
            work['story'] = r['story']
        work['images'].append({'n': n, 'src': f'assets/critique_additions/{n}.jpg', 'thumb': f'assets/critique_additions/{n}_t.jpg',
                               'mid': f'assets/critique_additions/{n}_m.jpg', 'w': w, 'h': h, 'artist': r['artist'], 'project': r['title'],
                               'year': r['year'], 'kind': r['kind'], 'credit': credit + '.' if credit else '', 'licence': r.get('licence', ''),
                               'source': r['source_page']})
        for sp in r.get('spaces') or []:
            if sp['id'] not in names:
                sys.exit(f'{r["file"]}: no record {sp["id"]} in institutions.json')
            work_spaces.setdefault(key, []).append(sp)
    for key, work in works.items():
        for sp in work_spaces.get(key, []):
            g = spaces.setdefault(sp['id'], {'name': names[sp['id']], 'ties': [], 'images': []})
            if sp['tie'] not in g['ties']:
                g['ties'].append(sp['tie'])
            g['images'] += [im for im in work['images'] if im not in g['images']]
            for im in work['images']:
                if sp['id'] not in on_spaces.setdefault(im['n'], []):
                    on_spaces[im['n']].append(sp['id'])
    data = {'retrieved': max(r.get('retrieved', '2026-11-15') for r in recs), 'works': list(works.values()),
            'spaces': spaces, 'on_spaces': on_spaces}
    (ROOT / 'assets' / 'critique-additions-data.js').write_text(
        '// Written by tools/add_critique_images.py from data/critique_additions.json; do not edit by hand.\n'
        'window.CRITIQUE_ADDITIONS = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'{sum(len(w["images"]) for w in works.values())} images in {len(works)} works')


if __name__ == '__main__':
    main(sys.argv[1])
