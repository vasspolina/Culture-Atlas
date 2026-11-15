#!/usr/bin/env python3
"""The outline of each space's own ground, from OpenStreetMap, for the street map.

A pin stands on one point. Where the space is one building, the building is under it. Where it is a compound (Nafasi Art
Space is a yard of studios, not a building) the pin stands in the middle of open ground and no building reads as the
space's. tools/geocode_pins.py already found the OpenStreetMap object each record was matched to by name; this asks
Nominatim for the outline of those that are areas and keeps the ones the record's pin is inside. The page fills that
ground and edges it when the space is open (index.html, "THE SPACE'S OWN GROUND").

Kept: an area in one of the classes below, found by the record's name, under half a square kilometre, with the pin in it.
Left out: roads, places and land use (a match on a street or a district is not the space), and campuses and parks.

Usage: python3 tools/site_outlines.py [--geocode data/web_research/geocode_2026-11-03.json]
Writes assets/sites.json: { record id: [ring, ...] }, each ring a list of [lon, lat] to six decimals, outer rings only.
Fifty objects a request, one request a second, as Nominatim asks.
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'site-outlines/1'
CLASSES = {'amenity', 'tourism', 'building', 'leisure', 'historic', 'office', 'craft', 'shop', 'man_made'}
MAX_M2 = 500_000
args = sys.argv[1:]
geocode = ROOT / 'data' / 'web_research' / 'geocode_2026-11-03.json'
if args[:1] == ['--geocode']:
    geocode = Path(args[1])

found = json.load(open(geocode, encoding='utf-8'))
records = {r['id']: r for r in json.load(open(ROOT / 'institutions.json', encoding='utf-8'))}

want = {}  # 'W123' -> [record ids]
for rid, g in found.items():
    osm = str(g.get('osm') or '')
    if rid not in records or not str(g.get('how') or '').startswith('name') or '/' not in osm:
        continue
    kind, num = osm.split('/', 1)
    if kind in ('way', 'relation'):
        want.setdefault(kind[0].upper() + num, []).append(rid)


def inside(ring, lon, lat):
    hit = False
    for i in range(len(ring)):
        a, b = ring[i], ring[i - 1]
        if (a[1] > lat) != (b[1] > lat) and lon < (b[0] - a[0]) * (lat - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit


def area_m2(ring):
    k = math.cos(math.radians(ring[0][1])) * 111320
    s = sum(ring[i - 1][0] * k * ring[i][1] * 111320 - ring[i][0] * k * ring[i - 1][1] * 111320 for i in range(len(ring)))
    return abs(s) / 2


def simplify(ring, tol_m=0.4):
    """Douglas-Peucker in metres: a vertex nearer than tol_m to the line between its neighbours is dropped."""
    k = math.cos(math.radians(ring[0][1])) * 111320
    pts = [(p[0] * k, p[1] * 111320) for p in ring]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    far = max(range(len(pts)), key=lambda i: math.dist(pts[i], pts[0]))
    keep[far] = True
    stack = [(0, far), (far, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        (ax, ay), (bx, by) = pts[i], pts[j]
        ln = math.hypot(bx - ax, by - ay)
        best, bd = -1, tol_m
        for m in range(i + 1, j):
            d = abs((by - ay) * (pts[m][0] - ax) - (bx - ax) * (pts[m][1] - ay)) / ln if ln > 1e-9 else math.dist(pts[m], pts[i])
            if d > bd:
                best, bd = m, d
        if best >= 0:
            keep[best] = True
            stack += [(i, best), (best, j)]
    return [ring[i] for i in range(len(ring)) if keep[i]]


out, ids = {}, sorted(want)
for at in range(0, len(ids), 50):
    q = urllib.parse.urlencode({'osm_ids': ','.join(ids[at:at + 50]), 'format': 'jsonv2', 'polygon_geojson': 1})
    req = urllib.request.Request('https://nominatim.openstreetmap.org/lookup?' + q, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            hits = json.load(r)
    except Exception as e:
        print('  error', e, file=sys.stderr)
        hits = []
    time.sleep(1.1)
    for h in hits:
        geo = h.get('geojson') or {}
        polys = [geo['coordinates']] if geo.get('type') == 'Polygon' else geo.get('coordinates') if geo.get('type') == 'MultiPolygon' else []
        if not polys or h.get('category') not in CLASSES:
            continue
        rings = [p[0] for p in polys if p and len(p[0]) >= 4]
        if not rings or sum(area_m2(r) for r in rings) > MAX_M2:
            continue
        for rid in want.get(h['osm_type'][0].upper() + str(h['osm_id']), []):
            rec = records[rid]
            lat, lon = rec.get('lat'), rec.get('lon')
            if lat is None or lon is None or not any(inside(r, lon, lat) for r in rings):
                continue
            out[rid] = [[[round(p[0], 6), round(p[1], 6)] for p in simplify(r)] for r in rings]
    print(f'{min(at + 50, len(ids))}/{len(ids)} asked, {len(out)} kept', file=sys.stderr)

dest = ROOT / 'assets' / 'sites.json'
json.dump(dict(sorted(out.items())), open(dest, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'{len(out)} outlines written to {dest.relative_to(ROOT)}')
