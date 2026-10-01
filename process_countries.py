import json
from collections import Counter

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/world-topo.json') as f:
    topo = json.load(f)

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

scale = topo['transform']['scale']
translate = topo['transform']['translate']

# Decode all arcs
decoded_arcs = []
for arc in topo['arcs']:
    curr_x, curr_y = 0, 0
    points = []
    for dx, dy in arc:
        curr_x += dx
        curr_y += dy
        lon = round(curr_x * scale[0] + translate[0], 2)
        lat = round(curr_y * scale[1] + translate[1], 2)
        points.append([lon, lat])
    decoded_arcs.append(points)

# Count institutions per country
inst_countries = {}
for inst in institutions:
    parts = [p.strip() for p in inst['location'].split(',')]
    c_name = parts[-1] if len(parts) > 1 else parts[0]
    # normalize aliases
    if c_name in ['USA', 'United States']:
        c_name = 'United States'
    elif c_name in ['UK', 'United Kingdom', 'England', 'Scotland', 'Wales']:
        c_name = 'United Kingdom'
    inst['country'] = c_name
    inst_countries[c_name] = inst_countries.get(c_name, 0) + 1

# Get country centroids from geometries
country_list = []
for geom in topo['objects']['world']['geometries']:
    name = geom.get('properties', {}).get('name', '')
    if not name:
        continue
    # find all points for this country
    all_lons, all_lats = [], []
    arcs_ref = geom['arcs']
    if geom['type'] == 'Polygon':
        for ring in arcs_ref:
            for a_idx in ring:
                arc = decoded_arcs[a_idx] if a_idx >= 0 else decoded_arcs[~a_idx]
                for p in arc:
                    all_lons.append(p[0])
                    all_lats.append(p[1])
    elif geom['type'] == 'MultiPolygon':
        for poly in arcs_ref:
            for ring in poly:
                for a_idx in ring:
                    arc = decoded_arcs[a_idx] if a_idx >= 0 else decoded_arcs[~a_idx]
                    for p in arc:
                        all_lons.append(p[0])
                        all_lats.append(p[1])
    if all_lons and all_lats:
        avg_lon = round(sum(all_lons) / len(all_lons), 2)
        avg_lat = round(sum(all_lats) / len(all_lats), 2)
        inst_cnt = inst_countries.get(name, 0)
        # Check alias
        if inst_cnt == 0:
            if name == 'United States of America' and 'United States' in inst_countries:
                inst_cnt = inst_countries['United States']
            elif name == 'United Kingdom' and 'United Kingdom' in inst_countries:
                inst_cnt = inst_countries['United Kingdom']
        country_list.append({
            'name': name,
            'lon': avg_lon,
            'lat': avg_lat,
            'count': inst_cnt
        })

country_list.sort(key=lambda x: (x['count'] == 0, -x['count'], x['name']))

print(f"Computed centroids for {len(country_list)} countries")
print("Top countries by institutions count:")
for c in country_list[:15]:
    print(f"  {c['name']}: {c['count']} institutions at ({c['lon']}, {c['lat']})")
