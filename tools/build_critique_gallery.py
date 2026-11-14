#!/usr/bin/env python3
"""Build the artists' image gallery layer from the cultural space critique collection (references 1801-2000).

The collection (gallery.html, collection_index.json, images/) was assembled outside the atlas. Only the references whose
own metadata names a cultural space the atlas already has a record for are kept: the space is named in the image credit,
the connection note, or is the institution whose page the image comes from. A reference that names only a commercial
gallery, a publisher or a space the atlas has no record of is left out of the map layer. The list is SPACES below, by atlas
record id. artists-images.html shows every image of the collection that could be fetched, grouped by work, with the map
layer's spaces as a second view; assets/critique-collection-data.js holds that.

    python3 -I tools/build_critique_gallery.py <gallery.html> <dir of downloaded images named <number>.<ext>>

Writes assets/critique_gallery/<number>.jpg (at most 2400px on the long side, so artists-images.html can zoom, never enlarged), <number>_t.jpg (480px)
and assets/critique-gallery-data.js (the map layer) and assets/critique-collection-data.js (the images page). Re-running
replaces them. A reference whose image is not in the directory is listed in the collection data as missing, with its source.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'critique_gallery'
FULL, THUMB = 2400, 480
# The images the atlas shows while it loads (assets/load-image.js picks one at random): strong, legible pieces at 1000px or
# more, saved again at 1400px so the picture at 40% of a desktop screen stays sharp without the weight of the full file.
SPLASH = [1810, 1811, 1815, 1818, 1822, 1838, 1874, 1906, 1989]
SPLASH_SIZE = 1400

# Atlas record id -> what ties the reference to the space (from the reference's own credit, note or source page), and which
# references belong there. A reference can sit on more than one space.
SPACES = {
    'w139-amsterdam': ('Farida Sedoc, People’s Forum, an exhibition with Platform BK in residence', lambda r: r['project'] == 'People’s Forum'),
    'raven-row-london': ('Artist Placement Group, The Individual and the Organisation, exhibition, 2012',
                         lambda r: r['project'] == 'The Individual and the Organisation'),
    'salt-galata-istanbul': ('Andrea Francke and Eva Weinmayr, The Piracy Project', lambda r: r['project'] == 'The Piracy Project'),
    'moma-the-museum-of-modern-art': ('Cameron Rowland, Disgorgement, 2016, in the collection', lambda r: r['project'] == 'Disgorgement'),
    'taipei-fine-arts-museum-taipei': ('Andreas Siekmann, Trickle Down, Taipei Biennial 2012',
                                       lambda r: r['project'].startswith('Trickle Down')),
    'tate-modern': ('Meschac Gaba, Museum of Contemporary African Art',
                    lambda r: r['project'] == 'Museum of Contemporary African Art'),
    'rijksakademie-amsterdam': ('Meschac Gaba, Museum of Contemporary African Art, begun after his residency',
                                lambda r: r['project'] == 'Museum of Contemporary African Art'),
    'walker-art-center': ('Rietlanden Women’s Office, MsHeresies, in the Walker Reader',
                          lambda r: r['source_page'].startswith('https://www.walkerart.org/')),
    'museum-folkwang-essen': ('Rietlanden Women’s Office, Banners for Heresies, from their exhibition here',
                              lambda r: r['source_page'].startswith('https://www.museum-folkwang.de/')),
}


def build(r, img_dir):
    n = r['number']
    src = next(Path(img_dir).glob(f'{n}.*'))
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    w, h = save(im, FULL, OUT / f'{n}.jpg')
    save(im, THUMB, OUT / f'{n}_t.jpg')
    return item(r, w, h)


def save(im, size, path):
    im = im.copy()
    if max(im.size) > size:
        im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, 'JPEG', quality=82, optimize=True, progressive=True)
    return im.size


def item(r, w, h):
    n = r['number']
    return {'n': n, 'src': f'assets/critique_gallery/{n}.jpg', 'thumb': f'assets/critique_gallery/{n}_t.jpg', 'w': w, 'h': h,
            'artist': r['artist_or_project'], 'project': r['project'], 'type': r['type'],
            'credit': r['image_credit'], 'source': r['source_page']}


def main(gallery_html, img_dir):
    html = Path(gallery_html).read_text()
    recs = json.loads(re.search(r'<script type="application/json" id="records">(.*?)</script>', html, re.S).group(1))
    names = {r['id']: r['name'] for r in json.loads((ROOT / 'institutions.json').read_text())}
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob('*.jpg'):
        f.unlink()
    done, spaces = {}, {}
    for sid, (tie, test) in SPACES.items():
        if sid not in names:
            sys.exit(f'no atlas record {sid}')
        refs = sorted((r for r in recs if test(r)), key=lambda r: r['number'])
        items = []
        for r in refs:
            n = r['number']
            if n not in done:
                done[n] = build(r, img_dir)
            items.append(done[n])
        spaces[sid] = {'name': names[sid], 'tie': tie, 'images': items}
        print(f'{sid}: {len(items)}')
    # Every other reference, for the images page.
    missing = []
    for r in recs:
        if r['number'] in done:
            continue
        try:
            done[r['number']] = build(r, img_dir)
        except StopIteration:
            missing.append({'n': r['number'], 'artist': r['artist_or_project'], 'project': r['project'], 'source': r['source_page']})
    works = {}
    for r in sorted(recs, key=lambda r: r['number']):
        if r['number'] not in done:
            continue
        key = (r['artist_or_project'], r['project'])
        works.setdefault(key, {'artist': key[0], 'project': key[1], 'note': r.get('connection_note', ''), 'images': []})['images'].append(done[r['number']])
    on = {}
    for sid, sp in spaces.items():
        for im in sp['images']:
            on.setdefault(im['n'], []).append(sid)
    coll = {'collection': 'Cultural space critique, references 1801–2000', 'retrieved': '2026-10-19',
            'works': list(works.values()), 'on_spaces': on, 'missing': missing}
    (ROOT / 'assets' / 'critique-collection-data.js').write_text(
        '// Written by tools/build_critique_gallery.py; do not edit by hand.\n'
        'window.CRITIQUE_COLLECTION = ' + json.dumps(coll, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'collection: {len(done)} images in {len(works)} works, {len(missing)} missing')
    splash = []
    for n in SPLASH:
        if n not in done:
            continue
        im = Image.open(OUT / f'{n}.jpg')
        w, h = save(im, SPLASH_SIZE, OUT / f'splash_{n}.jpg')
        d = done[n]
        splash.append({'src': f'assets/critique_gallery/splash_{n}.jpg', 'w': w, 'h': h, 'project': d['project'], 'artist': d['artist']})
    (ROOT / 'assets' / 'load-image-data.js').write_text(
        '// Written by tools/build_critique_gallery.py; do not edit by hand.\n'
        'window.LOAD_IMAGES = ' + json.dumps(splash, ensure_ascii=False) + ';\n')
    data = {'collection': 'Cultural space critique, references 1801–2000', 'retrieved': '2026-10-19', 'spaces': spaces}
    (ROOT / 'assets' / 'critique-gallery-data.js').write_text(
        '// Written by tools/build_critique_gallery.py; do not edit by hand.\n'
        'window.CRITIQUE_GALLERY = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print(f'{sum(len(sp["images"]) for sp in spaces.values())} placements on {len(spaces)} spaces')


if __name__ == '__main__':
    main(*sys.argv[1:3])
