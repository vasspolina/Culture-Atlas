#!/usr/bin/env python3
"""
enrich_gossip_and_shows.py
Enriches all institutions with:
1. temporary_shows with opening_night trackers (vernissages, opening hours, RSVP status).
2. gossip_data for Yellow Gossip Mode (Reddit threads, Twitter/X curatorial discourse, chat whispers, controversy scores).
"""

import json
import os
import random

def build_gossip_and_shows():
    with open('institutions.json', 'r', encoding='utf-8') as f:
        insts = json.load(f)

    # Deterministic seed for consistency
    random.seed(42)

    gossip_themes = [
        {
            "category": "board_donor",
            "tag": "#BoardDrama",
            "headline": "Trustee friction over private equity underwriting and donor transparency charter",
            "reddit": "r/contemporaryart: Anyone else hearing about the quiet board shakeup and sponsor pushback?",
            "twitter": "Major friction behind closed doors as curatorial staff push for ethical donor audits. Letter leaked.",
            "chat": "Signal leak: 3 guest curators threatened withdrawal over hedge fund endowment seat."
        },
        {
            "category": "artist_fees",
            "tag": "#WAGEWatch",
            "headline": "Union organizing and artist fee disputes surface during biennial planning",
            "reddit": "r/museums: Staff organizing update: negotiations stall over independent curator compensation.",
            "twitter": "Open letter signed by 45 exhibiting artists demanding W.A.G.E. certified honorariums.",
            "chat": "Telegram backchannel: solidarity strike vote scheduled ahead of opening vernissage."
        },
        {
            "category": "curatorial_discourse",
            "tag": "#TwitterDiscourse",
            "headline": "Heated debate over controversial acquisition of unvetted collection provenance",
            "reddit": "r/art: Deep dive into the contested acquisition records and institutional silence.",
            "twitter": "Art historians pointing out serious provenance gaps in the new permanent wing catalogue. Thread 🧵",
            "chat": "Curator WhatsApp group: provenance researchers flagged undocumented colonial-era paperwork."
        },
        {
            "category": "secret_gifts",
            "tag": "#GossipWhisper",
            "headline": "Rumors of anonymous crypto-philanthropist offering multi-million dollar unrestricted endowment",
            "reddit": "r/contemporaryart: Rumor mill: anonymous donor attempting to rewrite acquisition committee rules.",
            "twitter": "Insiders whispering about massive endowment pledge tied to unannounced digital media pavilion.",
            "chat": "Art Basel VIP lounge murmur: director privately turned down strings-attached private gift."
        },
        {
            "category": "director_scandal",
            "tag": "#DirectorIntrigue",
            "headline": "Disagreements between artistic director and trustees over politically charged autumn commission",
            "reddit": "r/museums: Why are so many European and US museum directors resigning this season?",
            "twitter": "Director reportedly refused trustee board edits on upcoming retrospective catalog essay.",
            "chat": "Curator Signal channel: emergency all-hands meeting called Friday afternoon."
        }
    ]

    for idx, inst in enumerate(insts):
        name = inst.get('name', 'Cultural Space')
        city = inst.get('city', 'Metropolis')
        tier = inst.get('tier', 'A')

        # 1. TEMPORARY SHOWS & OPENING NIGHT TRACKER
        floors = inst.get('floor_plans', [])
        primary_floor = floors[0] if floors else {}
        first_show = (primary_floor.get('current_shows') or [{}])[0]
        show_title = first_show.get('title') or inst.get('highlight') or f"{name} Autumn Curatorial Exhibition"

        opening_days = ["Thu, Oct 15", "Fri, Oct 16", "Sat, Oct 17", "Thu, Oct 22", "Fri, Oct 23", "Thu, Nov 05"]
        opening_day = opening_days[(idx * 7) % len(opening_days)]
        opening_hours = "18:00–21:30"
        
        status_opts = ["Now On View", "Opening Soon", "Opening Night This Week", "Closing Soon"]
        show_status = status_opts[(idx * 3) % len(status_opts)]
        
        opening_night = {
            "date": opening_day + ", 2026",
            "hours": opening_hours,
            "reception_type": "Public Vernissage, Artist Q&A & Curatorial Reception",
            "admission": "Free Public Admission · RSVP Open",
            "is_upcoming": ("Opening" in show_status)
        }

        temporary_shows = [
            {
                "title": show_title,
                "curator_artists": first_show.get('curator_artists') or "Resident International Fellows",
                "dates": first_show.get('dates') or "Autumn 2026",
                "synopsis": first_show.get('synopsis') or inst.get('curatorial_focus') or "Contemporary critical exhibition.",
                "floor_level": primary_floor.get('level_code') or "L1",
                "status": show_status,
                "opening_night": opening_night
            }
        ]

        # Add second temporary show if building has multiple floors
        if len(floors) > 1:
            second_floor = floors[1]
            second_show = (second_floor.get('current_shows') or [{}])[0]
            temporary_shows.append({
                "title": second_show.get('title') or f"Project Room: New Commissions at {name}",
                "curator_artists": second_show.get('curator_artists') or "Emerging Practitioners Collective",
                "dates": "On View through Dec 2026",
                "synopsis": second_show.get('synopsis') or "Site-specific temporal installation and artist research.",
                "floor_level": second_floor.get('level_code') or "L2",
                "status": "Now On View",
                "opening_night": {
                    "date": "Fri, Nov 13, 2026",
                    "hours": "19:00–22:00",
                    "reception_type": "Artist Performance & Gallery Night",
                    "admission": "Free Entry",
                    "is_upcoming": True
                }
            })

        inst['temporary_shows'] = temporary_shows

        # 2. YELLOW GOSSIP MODE DOSSIER
        theme = gossip_themes[(idx * 13) % len(gossip_themes)]
        intensity_levels = ["HOT 🔥", "VIRAL ⚡", "SPICY 🌶️", "WHISPER 💬", "DISCOURSE 🗣️"]
        intensity = intensity_levels[(idx * 5) % len(intensity_levels)]
        rumor_score = 65 + ((idx * 17) % 34)

        upvotes = 120 + ((idx * 83) % 850)
        comments = 32 + ((idx * 29) % 190)
        retweets = 240 + ((idx * 137) % 2100)

        # Bespoke adjustments for landmarks
        if "Slought" in name:
            headline = "Whispers over radical university spatial independence and endowment firewall negotiations"
            reddit_snippet = f"r/contemporaryart: Slought's non-traditional governance model discussed as antidote to trustee capture in Philadelphia."
            twitter_snippet = f"Curators applauding @Slought's refusal of corporate branding. How non-profits can hold the line. 🧵"
            chat_snippet = f"Penn humanities signal group: discussion on long-term deed protections for the 4015 Walnut space."
            intensity = "SPICY 🌶️"
            rumor_score = 92
        elif "Chisenhale" in name:
            headline = "Debate over London East-end grassroots funding vs public subsidy cuts across Tower Hamlets"
            reddit_snippet = f"r/contemporaryart: Chisenhale's artist commission model: how they navigate Arts Council UK tightrope."
            twitter_snippet = f"Overheard at opening: London independent spaces discussing shared defense against property redevelopment. #Chisenhale"
            chat_snippet = f"East London curator chat: artists praising commission fees while discussing rising studio overhead."
            intensity = "VIRAL ⚡"
            rumor_score = 94
        elif "FESPACO" in name:
            headline = "Discourse regarding archive digitization sovereignty and repatriation of master 35mm prints"
            reddit_snippet = f"r/filmmakers: FESPACO's pan-African film preservation protocols compared to European archives."
            twitter_snippet = f"Cinema scholars celebrating FESPACO holding African celluloid heritage in Ouagadougou against foreign repository bids."
            chat_snippet = f"African Film Festival Signal thread: preparations underway for 2027 edition and director summit."
            intensity = "HOT 🔥"
            rumor_score = 96
        elif "Kitchen" in name:
            headline = "Discussions surrounding multi-million historic loft renovation and video archive preservation"
            reddit_snippet = f"r/contemporaryart: The Kitchen's Chelsea legacy: discussions on experimental media archives."
            twitter_snippet = f"Remembering Steina & Woody Vasulka's video lab at The Kitchen. Incredible archival integrity."
            chat_snippet = f"NYC downtown arts channel: rumors on upcoming avant-garde season preview."
            intensity = "SPICY 🌶️"
            rumor_score = 90
        else:
            headline = f"{name}: {theme['headline']} ({city})"
            reddit_snippet = f"{theme['reddit']} Discussing {name} in {city}."
            twitter_snippet = f"{theme['twitter']} ({name}, {city})"
            chat_snippet = f"{theme['chat']} Regarding {name}."

        inst['gossip_data'] = {
            "has_gossip": True,
            "intensity": intensity,
            "rumor_score": rumor_score,
            "headline": headline,
            "tag": theme["tag"],
            "reddit": {
                "subreddit": "r/contemporaryart" if idx % 2 == 0 else "r/museums",
                "upvotes": upvotes,
                "comments": comments,
                "snippet": reddit_snippet
            },
            "twitter_x": {
                "handle": "@art_curator_watch" if idx % 2 == 0 else "@culture_insider",
                "retweets": retweets,
                "snippet": twitter_snippet
            },
            "chat_backchannels": {
                "channel": "Curator Signal Group" if idx % 2 == 0 else "Vernissage Telegram",
                "whisper": chat_snippet
            }
        }

    # Save to all 3 paths
    paths = ['institutions.json', 'app/institutions.json', 'src/data/institutions.json']
    for p in paths:
        if os.path.exists(os.path.dirname(p)) or not os.path.dirname(p):
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(insts, f, indent=2, ensure_ascii=False)
            print(f"Updated {p} with temporary shows, opening nights, and Yellow Gossip dossiers!")

if __name__ == '__main__':
    build_gossip_and_shows()
