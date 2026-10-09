import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("assets/visual_critique", exist_ok=True)

# Try to find system fonts on macOS
font_paths = [
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Geneva.ttf"
]
base_font_path = None
for p in font_paths:
    if os.path.exists(p):
        base_font_path = p
        break

def get_font(size):
    if base_font_path:
        try:
            return ImageFont.truetype(base_font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

critiques = [
    {
        "filename": "haacke_shapolsky_guggenheim_thumb.jpg",
        "artist": "Hans Haacke",
        "artwork": "Shapolsky et al. Manhattan Real Estate",
        "year": "1971",
        "target": "Solomon R. Guggenheim Museum",
        "strategy": "Sponsor Network Exposure",
        "medium": "Photographs, Deeds, Real Estate Charts",
        "border_color": (245, 158, 11),
        "bg_color": (15, 13, 19),
        "tag": "CENSORED BY GUGGENHEIM TRUSTEES"
    },
    {
        "filename": "forensic_architecture_triple_chaser_thumb.jpg",
        "artist": "Forensic Architecture & Laura Poitras",
        "artwork": "Triple-Chaser (Safariland Investigation)",
        "year": "2019",
        "target": "Whitney Museum of American Art",
        "strategy": "Algorithmic Forensic Investigation",
        "medium": "Computer Vision & Acoustic Ballistics",
        "border_color": (239, 68, 68),
        "bg_color": (18, 10, 10),
        "tag": "LED TO VICE CHAIR RESIGNATION"
    },
    {
        "filename": "nan_goldin_pain_sackler_met_thumb.jpg",
        "artist": "Nan Goldin & P.A.I.N. Collective",
        "artwork": "Sackler Die-In at Temple of Dendur",
        "year": "2018–2021",
        "target": "The Metropolitan Museum of Art",
        "strategy": "Pharma Philanthropy De-Naming",
        "medium": "Prescription Bottles, Banners, Die-In",
        "border_color": (168, 85, 247),
        "bg_color": (16, 11, 24),
        "tag": "SACKLER NAME STRIPPED WORLDWIDE"
    },
    {
        "filename": "guerrilla_girls_met_thumb.jpg",
        "artist": "Guerrilla Girls",
        "artwork": "Do women have to be naked to get into the Met?",
        "year": "1989–2025",
        "target": "Metropolitan Museum & Whitney",
        "strategy": "Feminist Statistical Counter-Surveys",
        "medium": "Agitprop Posters, Yellow Bus Ads",
        "border_color": (234, 179, 8),
        "bg_color": (22, 20, 10),
        "tag": "<5% ARTISTS WOMEN vs 85% NUDES"
    },
    {
        "filename": "fred_wilson_mining_museum_thumb.jpg",
        "artist": "Fred Wilson",
        "artwork": "Mining the Museum (Metalwork & Slave Shackles)",
        "year": "1992–1993",
        "target": "Maryland Historical Society / Baltimore",
        "strategy": "Curatorial Subversion & Archive Juxtaposition",
        "medium": "Repoussé Silver & Iron Slave Shackles",
        "border_color": (217, 119, 6),
        "bg_color": (20, 14, 10),
        "tag": "CURATORIAL SUBVERSION LANDMARK"
    },
    {
        "filename": "andrea_fraser_museum_highlights_thumb.jpg",
        "artist": "Andrea Fraser",
        "artwork": "Museum Highlights: A Gallery Talk",
        "year": "1989",
        "target": "Philadelphia Museum of Art & Whitney",
        "strategy": "Performative Institutional Tour",
        "medium": "Scripted Docent Performance & Video",
        "border_color": (14, 165, 233),
        "bg_color": (10, 16, 24),
        "tag": "CLASS & PATRONAGE INTERROGATION"
    },
    {
        "filename": "decolonize_this_place_whitney_thumb.jpg",
        "artist": "Decolonize This Place",
        "artwork": "Nine Weeks of Art & Agitation: Taking the Museum",
        "year": "2019",
        "target": "Whitney Museum & Brooklyn Museum",
        "strategy": "Grassroots Agitation & Board Boycotts",
        "medium": "Town Halls, Zines, Direct Action",
        "border_color": (249, 115, 22),
        "bg_color": (24, 12, 8),
        "tag": "8 BIENNIAL ARTISTS WITHDREW"
    },
    {
        "filename": "cildo_meireles_coca_cola_thumb.jpg",
        "artist": "Cildo Meireles",
        "artwork": "Insertions into Ideological Circuits",
        "year": "1970",
        "target": "Tate Modern & MACBA Barcelona",
        "strategy": "Ideological & Currency Circulation",
        "medium": "Coca-Cola Bottles & Screenprinted Banknotes",
        "border_color": (16, 185, 129),
        "bg_color": (8, 20, 14),
        "tag": "SUBVERTING CAPITALIST CIRCUITS"
    },
    {
        "filename": "mel_chin_gala_committee_thumb.jpg",
        "artist": "Mel Chin & GALA Committee",
        "artwork": "Total Proof: Prime-Time Prop Infiltration",
        "year": "1995–1997",
        "target": "MOCA Los Angeles & MCA Chicago",
        "strategy": "Subversive Mass Media Infiltration",
        "medium": "Viral Art Props on Melrose Place TV Show",
        "border_color": (59, 130, 246),
        "bg_color": (10, 14, 26),
        "tag": "PRIME-TIME TELEVISION HIJACK"
    },
    {
        "filename": "occupy_museums_debtfair_thumb.jpg",
        "artist": "Occupy Museums",
        "artwork": "Debtfair at the Whitney Biennial",
        "year": "2017",
        "target": "Whitney Museum of American Art",
        "strategy": "Artist Debt & Predatory Finance Ledger",
        "medium": "Architectural Debt Wall & Financial Index",
        "border_color": (236, 72, 153),
        "bg_color": (24, 8, 16),
        "tag": "EXPOSING PREDATORY BOARD DEBT"
    },
    {
        "filename": "bp_or_not_bp_british_museum_thumb.jpg",
        "artist": "BP or not BP? (Culture Unstained)",
        "artwork": "The Trojan Horse & Stolen Goods Actions",
        "year": "2012–2024",
        "target": "British Museum",
        "strategy": "Fossil Fuel Sponsorship Disruption",
        "medium": "13-ft Trojan Horse, Flash Mobs, Oil Spills",
        "border_color": (234, 88, 12),
        "bg_color": (20, 10, 6),
        "tag": "ENDED 27-YEAR BP SPONSORSHIP"
    },
    {
        "filename": "michael_asher_art_institute_thumb.jpg",
        "artist": "Michael Asher",
        "artwork": "Institutional Deconstruction / Washington Relocation",
        "year": "1979",
        "target": "Art Institute of Chicago",
        "strategy": "Curatorial & Spatial Displacement",
        "medium": "Bronze Statue Relocation to 18th-C Gallery",
        "border_color": (148, 163, 184),
        "bg_color": (15, 17, 21),
        "tag": "DECONSTRUCTING CIVIC MYTHOLOGY"
    },
    {
        "filename": "coco_fusco_couple_cage_thumb.jpg",
        "artist": "Coco Fusco & Guillermo Gómez-Peña",
        "artwork": "Two Undiscovered Amerindians (The Couple in Cage)",
        "year": "1992–1993",
        "target": "Walker Art Center & Natural History Museums",
        "strategy": "Ethnographic Gaze Satire & Parodic Cage",
        "medium": "Golden Cage, Performers, Museum Docents",
        "border_color": (202, 138, 4),
        "bg_color": (22, 18, 6),
        "tag": "EXPOSING ETHNOGRAPHIC GAZE"
    },
    {
        "filename": "adrian_piper_cornered_thumb.jpg",
        "artist": "Adrian Piper",
        "artwork": "Cornered: Race & Institutional Complicity",
        "year": "1988–2018",
        "target": "MoMA & MoMA PS1",
        "strategy": "Performative Video & White Cube Confrontation",
        "medium": "Overturned Table, Birth Certificates, Video",
        "border_color": (129, 140, 248),
        "bg_color": (12, 14, 24),
        "tag": "DIRECT INSTITUTIONAL CONFRONTATION"
    }
]

for c in critiques:
    w, h = 640, 420
    img = Image.new("RGB", (w, h), color=c["bg_color"])
    draw = ImageDraw.Draw(img)

    # Frame
    b_col = c["border_color"]
    draw.rectangle([(8, 8), (w - 9, h - 9)], outline=b_col, width=3)
    draw.rectangle([(16, 16), (w - 17, h - 17)], outline=(b_col[0]//3, b_col[1]//3, b_col[2]//3), width=1)

    # Header bar
    draw.rectangle([(18, 18), (w - 18, 68)], fill=(28, 25, 23))
    draw.text((32, 28), "🎨 ARTIST & DESIGNER VISUAL CRITIQUE", fill=b_col, font=get_font(14))
    draw.text((32, 48), f"CRITIQUE DOSSIER · {c['year']}", fill=(160, 160, 160), font=get_font(12))

    # Tag badge
    draw.rectangle([(w - 280, 26), (w - 28, 56)], fill=(40, 20, 20), outline=b_col, width=1)
    draw.text((w - 272, 34), c["tag"], fill=b_col, font=get_font(11))

    # Artist name
    draw.text((32, 85), "ARTIST / DESIGNER CREDITS:", fill=(168, 162, 158), font=get_font(12))
    draw.text((32, 105), c["artist"], fill=(255, 255, 255), font=get_font(26))

    # Artwork title
    draw.text((32, 148), "WORK / INTERVENTION:", fill=(168, 162, 158), font=get_font(12))
    draw.text((32, 168), f"\"{c['artwork']}\"", fill=b_col, font=get_font(20))

    # Institutional Target
    draw.rectangle([(32, 210), (w - 32, 260)], fill=(20, 20, 25), outline=(60, 60, 70), width=1)
    draw.text((44, 218), "INSTITUTIONAL TARGET:", fill=(200, 200, 200), font=get_font(11))
    draw.text((44, 236), c["target"], fill=(255, 255, 255), font=get_font(15))

    # Strategy and medium
    draw.text((32, 280), f"STRATEGY: {c['strategy']}", fill=(220, 220, 220), font=get_font(13))
    draw.text((32, 305), f"MEDIUM:   {c['medium']}", fill=(180, 180, 180), font=get_font(12))

    # Bottom bar: Academic citation & verified badge
    draw.rectangle([(18, h - 68), (w - 18, h - 18)], fill=(12, 10, 15))
    draw.line([(18, h - 68), (w - 18, h - 68)], fill=(60, 60, 60), width=1)
    draw.text((32, h - 56), "CONSENSUS EMPIRICAL RESEARCH ARCHIVE", fill=b_col, font=get_font(11))
    draw.text((32, h - 38), "Curatorial Studies & Institutional Critique Dataset · Verified Credits", fill=(140, 140, 140), font=get_font(10))

    dest = os.path.join("assets/visual_critique", c["filename"])
    img.save(dest, quality=92)
    print(f"Generated {dest}")

print("All visual critique assets created successfully!")
