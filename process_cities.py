import json
from collections import Counter

# Load TopoJSON
with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/world-topo.json') as f:
    topo = json.load(f)

# Load institutions
with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

scale = topo['transform']['scale']
translate = topo['transform']['translate']

# Decode and downsample arcs
arcs_downsampled = []
for arc in topo['arcs']:
    curr_x, curr_y = 0, 0
    pts = []
    last_pt = None
    for dx, dy in arc:
        curr_x += dx
        curr_y += dy
        p = [round(curr_x * scale[0] + translate[0], 1), round(curr_y * scale[1] + translate[1], 1)]
        if last_pt is None or (abs(p[0] - last_pt[0]) >= 0.4 or abs(p[1] - last_pt[1]) >= 0.4):
            pts.append(p)
            last_pt = p
    if len(pts) > 1:
        arcs_downsampled.append(pts)

# Extract cities and normalize countries
city_data = {}
inst_countries = {}

for inst in institutions:
    parts = [p.strip() for p in inst['location'].split(',')]
    city = parts[0]
    c_name = parts[-1] if len(parts) > 1 else parts[0]
    if c_name in ['USA', 'United States']:
        c_name = 'USA'
    elif c_name in ['UK', 'United Kingdom', 'England', 'Scotland', 'Wales']:
        c_name = 'UK'
    inst['country'] = c_name
    inst['city'] = city
    inst_countries[c_name] = inst_countries.get(c_name, 0) + 1

    if city not in city_data:
        city_data[city] = {
            'name': city,
            'country': c_name,
            'lat': inst['lat'],
            'lon': inst['lon'],
            'count': 0
        }
    city_data[city]['count'] += 1

sorted_cities = sorted(city_data.values(), key=lambda x: (-x['count'], x['name']))

# Extract country centroids
country_list = []
for geom in topo['objects']['world']['geometries']:
    name = geom.get('properties', {}).get('name', '')
    if not name:
        continue
    all_lons, all_lats = [], []
    arcs_ref = geom['arcs']
    if geom['type'] == 'Polygon':
        for ring in arcs_ref:
            for a_idx in ring:
                arc = arcs_downsampled[a_idx % len(arcs_downsampled)]
                for p in arc:
                    all_lons.append(p[0])
                    all_lats.append(p[1])
    elif geom['type'] == 'MultiPolygon':
        for poly in arcs_ref:
            for ring in poly:
                for a_idx in ring:
                    arc = arcs_downsampled[a_idx % len(arcs_downsampled)]
                    for p in arc:
                        all_lons.append(p[0])
                        all_lats.append(p[1])
    if all_lons and all_lats:
        avg_lon = round(sum(all_lons) / len(all_lons), 1)
        avg_lat = round(sum(all_lats) / len(all_lats), 1)
        matched_c = None
        for c in inst_countries:
            if c.lower() in name.lower() or name.lower() in c.lower():
                matched_c = c
                break
        cnt = inst_countries.get(matched_c, 0) if matched_c else 0
        country_list.append({
            'name': matched_c or name,
            'lon': avg_lon,
            'lat': avg_lat,
            'count': cnt
        })

unique_countries = {}
for c in country_list:
    n = c['name']
    if n not in unique_countries or c['count'] > unique_countries[n]['count']:
        unique_countries[n] = c

sorted_countries = sorted(unique_countries.values(), key=lambda x: (-x['count'], x['name']))

arcs_json = json.dumps(arcs_downsampled)
insts_json = json.dumps(institutions)
countries_json = json.dumps(sorted_countries)
cities_json = json.dumps(sorted_cities)

print(f"Processed {len(sorted_cities)} cities across {len(sorted_countries)} countries")
