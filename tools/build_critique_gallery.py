#!/usr/bin/env python3
"""Build the artists' image gallery layer from the cultural space critique collection (references 1801-2000).

The collection (gallery.html, collection_index.json, images/) was assembled outside the atlas. Only the references whose
own metadata names a cultural space the atlas already has a record for are kept: the space is named in the image credit,
the connection note, or is the institution whose page the image comes from. A reference that names only a commercial
gallery, a publisher or a space the atlas has no record of is left out. The list is SPACES below, by atlas record id.

    python3 -I tools/build_critique_gallery.py <gallery.html> <dir of downloaded images named <number>.<ext>>

Writes assets/critique_gallery/<number>.jpg (at most 1600px on the long side, never enlarged), <number>_t.jpg (480px)
and assets/critique-gallery-data.js. Re-running replaces them.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'critique_gallery'
FULL, THUMB = 1600, 480

# Atlas record id -> what ties the reference to the space (from the reference's own credit, note or source page), and which
# references belong there. A reference can sit on more than one space.
SPACES = {
    'w139-amsterdam': ('People’s Forum, an exhibition at W139', lambda r: r['project'] == 'People’s Forum'),
    'raven-row-london': ('The Individual and the Organisation, an exhibition at Raven Row (2012)',
                         lambda r: r['project'] == 'The Individual and the Organisation'),
    'salt-galata-istanbul': ('The Piracy Project, shown by SALT', lambda r: r['project'] == 'The Piracy Project'),
    'moma-the-museum-of-modern-art': ('Disgorgement, in the collection of MoMA', lambda r: r['project'] == 'Disgorgement'),
    'taipei-fine-arts-museum-taipei': ('Trickle Down, in the 2012 Taipei Biennial at the Taipei Fine Arts Museum',
                                       lambda r: r['project'].startswith('Trickle Down')),
    'tate-modern': ('Museum of Contemporary African Art, shown at Tate Modern',
                    lambda r: r['project'] == 'Museum of Contemporary African Art'),
    'rijksakademie-amsterdam': ('Museum of Contemporary African Art, begun after the artist studied at the Rijksakademie',
                                lambda r: r['project'] == 'Museum of Contemporary African Art'),
    'walker-art-center': ('MsHeresies, published in the Walker Reader',
                          lambda r: r['source_page'].startswith('https://www.walkerart.org/')),
    'museum-folkwang-essen': ('Banners for Heresies, in Rietlanden Women’s Office’s exhibition at Museum Folkwang',
                              lambda r: r['source_page'].startswith('https://www.museum-folkwang.de/')),
}


def save(im, size, path):
    im = im.copy()
    if max(im.size) > size:
        im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, 'JPEG', quality=82, optimize=True, progressive=True)
    return im.size


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
                src = next(Path(img_dir).glob(f'{n}.*'))
                im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
                w, h = save(im, FULL, OUT / f'{n}.jpg')
                save(im, THUMB, OUT / f'{n}_t.jpg')
                done[n] = {
                    'n': n,
                    'src': f'assets/critique_gallery/{n}.jpg',
                    'thumb': f'assets/critique_gallery/{n}_t.jpg',
                    'w': w, 'h': h,
                    'artist': r['artist_or_project'],
                    'project': r['project'],
                    'type': r['type'],
                    'credit': r['image_credit'],
                    'source': r['source_page'],
                }
            items.append(done[n])
        spaces[sid] = {'name': names[sid], 'tie': tie, 'images': items}
        print(f'{sid}: {len(items)}')
    data = {'collection': 'Cultural space critique, references 1801–2000', 'retrieved': '2026-10-19', 'spaces': spaces}
    (ROOT / 'assets' / 'critique-gallery-data.js').write_text(
        '// Written by tools/build_critique_gallery.py; do not edit by hand.\n'
        'window.CRITIQUE_GALLERY = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print(f'{len(done)} images on {len(spaces)} spaces')


if __name__ == '__main__':
    main(*sys.argv[1:3])
