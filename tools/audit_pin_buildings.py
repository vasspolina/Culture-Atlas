#!/usr/bin/env python3
"""Is there a building under each space's pin on the street map?

The street map draws OpenStreetMap's buildings (OpenFreeMap vector tiles, the same the page loads). This reads the zoom 14
tile each record's pin is in and says where the pin stands: in a building's footprint; on ground OpenStreetMap outlines
as the space's own (assets/sites.json); or on neither, with the distance to the nearest building edge. The last group
is the list to look at: a pin in a street or a yard, a building OpenStreetMap does not have, or a space with no building.
Nothing in institutions.json changes here.

Usage: python3 tools/audit_pin_buildings.py [--out data/web_research/pin_building_audit_2026-11-15.json]
"""
import gzip
import json
import math
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'pin-audit/1'
Z = 14
out = ROOT / 'data' / 'web_research' / 'pin_building_audit_2026-11-15.json'
if sys.argv[1:2] == ['--out']:
    out = Path(sys.argv[2])


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                b = r.read()
            return gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
        except Exception as e:
            if getattr(e, 'code', None) in (204, 404):
                return b''
            if attempt == 3:
                raise


def fields(buf):
    """A protobuf message as (field number, wire type, value) triples."""
    i, n = 0, len(buf)
    while i < n:
        key = shift = 0
        while True:
            c = buf[i]; i += 1
            key |= (c & 127) << shift; shift += 7
            if c < 128: break
        num, wt = key >> 3, key & 7
        if wt == 0:
            v = shift = 0
            while True:
                c = buf[i]; i += 1
                v |= (c & 127) << shift; shift += 7
                if c < 128: break
            yield num, wt, v
        elif wt == 2:
            ln = shift = 0
            while True:
                c = buf[i]; i += 1
                ln |= (c & 127) << shift; shift += 7
                if c < 128: break
            yield num, wt, buf[i:i + ln]; i += ln
        elif wt == 5:
            yield num, wt, buf[i:i + 4]; i += 4
        elif wt == 1:
            yield num, wt, buf[i:i + 8]; i += 8
        else:
            return


def _varints(buf):
    res, i, n = [], 0, len(buf)
    while i < n:
        v = shift = 0
        while True:
            c = buf[i]; i += 1
            v |= (c & 127) << shift; shift += 7
            if c < 128: break
        res.append(v)
    return res


def building_rings(tile):
    """Every building polygon in the tile, as a list of features, each a list of rings in tile units (0..extent)."""
    feats, extent = [], 4096
    for num, wt, layer in fields(tile):
        if num != 3 or wt != 2:
            continue
        name, raw = None, []
        for n2, w2, v in fields(layer):
            if n2 == 1: name = bytes(v).decode()
            elif n2 == 2: raw.append(v)
            elif n2 == 5: extent = v
        if name != 'building':
            continue
        for f in raw:
            gtype, geom = 0, b''
            for n3, w3, v in fields(f):
                if n3 == 3: gtype = v
                elif n3 == 4: geom = v
            if gtype != 3:
                continue
            cmds, rings, ring, x, y, i = _varints(geom), [], [], 0, 0, 0
            while i < len(cmds):
                cid, cnt = cmds[i] & 7, cmds[i] >> 3; i += 1
                if cid == 7:
                    if ring: rings.append(ring)
                    ring = []
                    continue
                for _ in range(cnt):
                    dx, dy = cmds[i], cmds[i + 1]; i += 2
                    x += (dx >> 1) ^ -(dx & 1); y += (dy >> 1) ^ -(dy & 1)
                    if cid == 1: ring = [(x, y)]
                    else: ring.append((x, y))
            if rings:
                feats.append(rings)
    return feats, extent


def inside(ring, px, py):
    hit = False
    for i in range(len(ring)):
        a, b = ring[i], ring[i - 1]
        if (a[1] > py) != (b[1] > py) and px < (b[0] - a[0]) * (py - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit


def edge_dist(ring, px, py):
    best = 1e18
    for i in range(len(ring)):
        (ax, ay), (bx, by) = ring[i], ring[i - 1]
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
        best = min(best, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
    return best


records = [r for r in json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
           if r.get('lat') not in (None, 0) and r.get('lon') not in (None, 0) and r.get('fixed_venue') is not False]
sites = json.load(open(ROOT / 'assets' / 'sites.json', encoding='utf-8')) if (ROOT / 'assets' / 'sites.json').exists() else {}
template = json.loads(get('https://tiles.openfreemap.org/planet'))['tiles'][0]


def tile_of(lat, lon):
    n = 2 ** Z
    fx = (lon + 180) / 360 * n
    s = math.sin(math.radians(lat))
    fy = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return int(fx), int(fy), fx - int(fx), fy - int(fy)


def check(r):
    try:
        tx, ty, u, v = tile_of(r['lat'], r['lon'])
        feats, extent = building_rings(get(template.format(z=Z, x=tx, y=ty)))
        px, py = u * extent, v * extent
        metres = 40075016.686 * math.cos(math.radians(r['lat'])) / 2 ** Z / extent  # one tile unit
        near, under = 1e18, False
        for rings in feats:
            if sum(inside(rg, px, py) for rg in rings) % 2:
                under = True
                break
            near = min(near, min(edge_dist(rg, px, py) for rg in rings))
        where = 'building' if under else 'own ground' if r['id'] in sites else 'neither'
        row = {'name': r['name'], 'city': r.get('city'), 'country': r.get('country'), 'where': where}
        if not under:
            row['nearest_building_m'] = None if near > 1e17 else round(near * metres, 1)
        return r['id'], row
    except Exception as e:
        return r['id'], {'name': r['name'], 'city': r.get('city'), 'where': 'error', 'error': str(e)[:120]}


with ThreadPoolExecutor(8) as pool:
    done = dict(pool.map(check, records))
json.dump(done, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
count = {}
for row in done.values():
    count[row['where']] = count.get(row['where'], 0) + 1
print(len(done), 'pins:', count)
