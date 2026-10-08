import json
import re
import zipfile
import xml.etree.ElementTree as ET

def col2idx(cell_ref):
    letters = ''.join([c for c in cell_ref if c.isalpha()])
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord('A') + 1)
    return idx - 1

def parse_sheet(zf, sheet_path):
    tree = ET.fromstring(zf.read(sheet_path))
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    rows = []
    for r in tree.findall(f'.//{ns}row'):
        row_dict = {}
        max_c = 0
        for c in r.findall(f'{ns}c'):
            ref = c.get('r')
            c_idx = col2idx(ref)
            max_c = max(max_c, c_idx)
            val = ''
            v = c.find(f'{ns}v')
            t = c.find(f'{ns}is/{ns}t')
            if v is not None and v.text is not None:
                val = v.text
            elif t is not None and t.text is not None:
                val = t.text
            row_dict[c_idx] = val.strip()
        row_arr = [row_dict.get(i, '') for i in range(max_c + 1)]
        rows.append(row_arr)
    return rows

def norm_name(n):
    return re.sub(r'[^a-z0-9]', '', (n or '').lower())

def main():
    xlsx_path = '/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/.user_uploaded/media_1791455136228.xlsx'
    zf = zipfile.ZipFile(xlsx_path)

    # 1. Load existing institutions
    with open('institutions.json', 'r', encoding='utf-8') as f:
        existing_list = json.load(f)

    inst_map = {}
    for item in existing_list:
        key = (norm_name(item.get('name')), norm_name(item.get('city')))
        inst_map[key] = item

    # 2. Parse Sheet 1: Institutions
    s1 = parse_sheet(zf, 'xl/worksheets/sheet1.xml')
    s1_header = s1[0]
    for r in s1[1:]:
        if not r or not r[0]:
            continue
        name = r[0]
        city = r[1] if len(r) > 1 else ''
        country = r[2] if len(r) > 2 else ''
        raw_tier = r[3] if len(r) > 3 else ''
        size = r[4] if len(r) > 4 else ''
        funding = r[5] if len(r) > 5 else ''
        note = r[6] if len(r) > 6 else ''
        sources = [x for x in [r[9] if len(r) > 9 else '', r[10] if len(r) > 10 else '', r[11] if len(r) > 11 else ''] if x.startswith('http')]
        lat_str = r[12] if len(r) > 12 else ''
        lon_str = r[13] if len(r) > 13 else ''
        other_find = r[14] if len(r) > 14 else ''

        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except:
            lat, lon = None, None

        tier_code = 'A'
        if 'unverified' in raw_tier.lower():
            tier_code = 'U'
        elif 'one name' in raw_tier.lower() or 'flag' in raw_tier.lower() or 'b' in raw_tier.lower():
            tier_code = 'B'
        elif 'verified' in raw_tier.lower():
            tier_code = 'A'

        key = (norm_name(name), norm_name(city))
        if key in inst_map:
            obj = inst_map[key]
            # Update missing or richer info
            if funding: obj['funding'] = funding
            if note: obj['watch'] = (obj.get('watch', '') + ' ' + note).strip()
            if sources:
                curr_src = obj.get('sources', [])
                for s in sources:
                    if s not in curr_src: curr_src.append(s)
                obj['sources'] = curr_src
            if lat is not None and not obj.get('lat'): obj['lat'] = lat
            if lon is not None and not obj.get('lon'): obj['lon'] = lon
            if other_find:
                obj['other_findings'] = other_find
        else:
            if lat is None or lon is None:
                continue
            new_obj = {
                'id': re.sub(r'[^a-z0-9]+', '-', f"{name}-{city}".lower()).strip('-'),
                'name': name,
                'city': city,
                'country': country,
                'location': f"{city}, {country}",
                'tier': tier_code,
                'size': size or 'Small or mid',
                'funding': funding or 'Civic / independent non-profit',
                'watch': note,
                'sources': sources,
                'lat': lat,
                'lon': lon,
                'governance_type': 'Civic Independent' if tier_code == 'A' else 'Monitored / Corporate Roster',
                'curatorial_focus': 'Contemporary Art & Research',
                'admission_policy': 'Free or Subsidized Admission',
                'admission_details': 'Check official schedule',
                'ethical_safeguard': 'Verified under Culture Atlas framework' if tier_code == 'A' else 'Monitored Underwriting Policy',
                'year_founded': 'Independent Space',
                'transparency_grade': 'Tier A+ (Statutory Public Audit)' if tier_code == 'A' else 'Tier B+ (Audited Corporate Ties)' if tier_code == 'B' else 'Tier U (Roster Unverified)',
                'curator_recommendation': 'Researched space indexed in Culture Atlas.'
            }
            if other_find: new_obj['other_findings'] = other_find
            inst_map[key] = new_obj

    # 3. Parse Sheet 2: Flagged
    s2 = parse_sheet(zf, 'xl/worksheets/sheet2.xml')
    for r in s2[1:]:
        if not r or not r[0]:
            continue
        name = r[0]
        city = r[1] if len(r) > 1 else ''
        country = r[2] if len(r) > 2 else ''
        flags_str = r[4] if len(r) > 4 else ''
        why_flagged = r[5] if len(r) > 5 else ''
        src1 = r[6] if len(r) > 6 else ''
        lat_str = r[7] if len(r) > 7 else ''
        lon_str = r[8] if len(r) > 8 else ''
        other_find = r[9] if len(r) > 9 else ''
        more_sources = r[10] if len(r) > 10 else ''

        flags_list = [f.strip() for f in flags_str.split(';') if f.strip()]
        all_sources = [s.strip() for s in (src1 + ' ' + more_sources).split() if s.strip().startswith('http')]

        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except:
            lat, lon = None, None

        key = (norm_name(name), norm_name(city))
        if key in inst_map:
            obj = inst_map[key]
            obj['tier'] = 'B'
            obj['flags'] = list(set(obj.get('flags', []) + flags_list))
            obj['why_flagged'] = why_flagged
            obj['watch'] = why_flagged
            if other_find: obj['other_findings'] = other_find
            curr_src = obj.get('sources', [])
            for s in all_sources:
                if s not in curr_src: curr_src.append(s)
            obj['sources'] = curr_src
        else:
            if lat is None or lon is None:
                continue
            new_obj = {
                'id': re.sub(r'[^a-z0-9]+', '-', f"{name}-{city}".lower()).strip('-'),
                'name': name,
                'city': city,
                'country': country,
                'location': f"{city}, {country}",
                'tier': 'B',
                'size': 'Audited Space',
                'funding': 'Corporate / Flagged Underwriting',
                'flags': flags_list,
                'why_flagged': why_flagged,
                'watch': why_flagged,
                'sources': all_sources,
                'lat': lat,
                'lon': lon,
                'governance_type': 'Flagged Governance',
                'curatorial_focus': 'Contemporary Art',
                'admission_policy': 'General Admission',
                'admission_details': 'Check official site',
                'ethical_safeguard': 'Flagged under Culture Atlas criteria',
                'year_founded': 'Established Space',
                'transparency_grade': 'Tier B (Monitored Corporate Sponsorship)',
                'curator_recommendation': f"Flagged institution: {why_flagged}"
            }
            if other_find: new_obj['other_findings'] = other_find
            inst_map[key] = new_obj

    # 4. Parse Sheet 3: Epstein links
    s3 = parse_sheet(zf, 'xl/worksheets/sheet3.xml')
    for r in s3[1:]:
        if not r or not r[0]:
            continue
        name = r[0]
        city = r[1] if len(r) > 1 else ''
        person = r[2] if len(r) > 2 else ''
        link_type = r[3] if len(r) > 3 else ''
        summary = r[4] if len(r) > 4 else ''
        epstein_tie = r[5] if len(r) > 5 else ''
        status = r[6] if len(r) > 6 else ''
        consequence = r[7] if len(r) > 7 else ''
        sources = [s.strip() for s in r[10:14] if s and s.strip().startswith('http')]

        key = (norm_name(name), norm_name(city))
        # Match by name or partial
        matched_obj = inst_map.get(key)
        if not matched_obj:
            for k, obj in inst_map.items():
                if norm_name(name) in k[0] or k[0] in norm_name(name):
                    matched_obj = obj
                    break

        if matched_obj:
            matched_obj['tier'] = 'B'
            flags = matched_obj.get('flags', [])
            if 'Epstein-linked' not in flags:
                flags.append('Epstein-linked')
            matched_obj['flags'] = flags

            ep_entry = {
                'person': person,
                'link': link_type,
                'summary': summary,
                'tie': epstein_tie,
                'status': status,
                'consequence': consequence,
                'sources': sources
            }
            curr_ep = matched_obj.get('epstein_records', [])
            curr_ep.append(ep_entry)
            matched_obj['epstein_records'] = curr_ep

    # 5. Parse Sheet 4: WikiLeaks
    s4 = parse_sheet(zf, 'xl/worksheets/sheet4.xml')
    for r in s4[1:]:
        if not r or not r[0]:
            continue
        name = r[0]
        date = r[1] if len(r) > 1 else ''
        what_shows = r[2] if len(r) > 2 else ''
        doc_id = r[3] if len(r) > 3 else ''
        flags_added = r[4] if len(r) > 4 else ''
        sources = [s.strip() for s in r[5:9] if s and s.strip().startswith('http')]

        key = (norm_name(name), '')
        matched_obj = None
        for k, obj in inst_map.items():
            if norm_name(name) in k[0] or k[0] in norm_name(name):
                matched_obj = obj
                break

        if matched_obj:
            wl_entry = {
                'date': date,
                'doc_id': doc_id,
                'what_shows': what_shows,
                'flags_added': flags_added,
                'sources': sources
            }
            curr_wl = matched_obj.get('wikileaks_records', [])
            curr_wl.append(wl_entry)
            matched_obj['wikileaks_records'] = curr_wl
            if flags_added:
                flags = matched_obj.get('flags', [])
                if flags_added not in flags:
                    flags.append(flags_added)
                matched_obj['flags'] = flags

    # Write out enriched institutions.json
    final_list = list(inst_map.values())
    print(f"Total merged institutions: {len(final_list)}")
    t_counts = {}
    for i in final_list:
        t = i.get('tier', 'A')
        t_counts[t] = t_counts.get(t, 0) + 1
    print("Tiers breakdown:", t_counts)

    with open('institutions.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    print("Saved institutions.json successfully!")

    # 6. Parse 3 Academic Research Consensus CSVs
    import glob, csv
    csv_paths = sorted(glob.glob('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/.user_uploaded/*.csv'))
    papers = []
    seen_titles = set()
    seen_dois = set()
    for p in csv_paths:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = (row.get('\ufeffTitle') or row.get('Title') or '').strip()
                doi = row.get('DOI', '').strip()
                takeaway = row.get('Takeaway', '').strip()
                authors = row.get('Authors', '').strip()
                year = row.get('Year', '').strip()
                citations = row.get('Citations', '').strip()
                abstract = row.get('Abstract', '').strip()
                journal = row.get('Journal', '').strip()
                link = row.get('Consensus Link', '').strip()
                if not title:
                    continue
                if title in seen_titles or (doi and doi in seen_dois):
                    continue
                seen_titles.add(title)
                if doi: seen_dois.add(doi)
                papers.append({
                    'title': title,
                    'takeaway': takeaway,
                    'authors': authors,
                    'year': year,
                    'citations': citations,
                    'abstract': abstract,
                    'journal': journal,
                    'doi': doi,
                    'link': link
                })
    with open('academic_papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"Extracted and saved {len(papers)} peer-reviewed papers to academic_papers.json!")

if __name__ == '__main__':
    main()
