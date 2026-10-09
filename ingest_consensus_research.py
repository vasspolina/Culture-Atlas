import json, csv, os

def load_academic():
    if os.path.exists("academic_papers.json"):
        with open("academic_papers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_academic(papers):
    with open("academic_papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved {len(papers)} academic papers to academic_papers.json")

def clean_str(val):
    if not val:
        return ""
    return str(val).strip()

def ingest():
    papers = load_academic()
    existing_titles = {clean_str(p.get("title")).lower() for p in papers if p.get("title")}
    existing_dois = {clean_str(p.get("doi")).lower() for p in papers if p.get("doi")}

    # CSV 1: Connections among cultural sponsors
    csv1 = "/Users/polinavasilyeva/Downloads/https__consensus.app_search_connections-among-cultural-sponsors_XLE_eoqtQDuDSIOdzcIn_w_utm_source=share&utm_medium=clipboard.  continue this research - Oct 09, 2026.csv"
    added_csv1 = 0
    if os.path.exists(csv1):
        with open(csv1, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                title = clean_str(r.get("Title"))
                doi = clean_str(r.get("DOI"))
                if not title:
                    continue
                if title.lower() in existing_titles or (doi and doi.lower() in existing_dois):
                    continue
                
                paper_obj = {
                    "title": title,
                    "takeaway": clean_str(r.get("Takeaway")),
                    "authors": clean_str(r.get("Authors")),
                    "year": clean_str(r.get("Year")),
                    "citations": clean_str(r.get("Citations") or "0"),
                    "abstract": clean_str(r.get("Abstract")),
                    "journal": clean_str(r.get("Journal") or "Consensus Research Synthesis"),
                    "doi": doi,
                    "link": clean_str(r.get("Consensus Link")),
                    "consensus_link": clean_str(r.get("Consensus Link")),
                    "study_type": clean_str(r.get("Study Type")),
                    "topic": "sponsor_connections"
                }
                papers.append(paper_obj)
                existing_titles.add(title.lower())
                if doi:
                    existing_dois.add(doi.lower())
                added_csv1 += 1
        print(f"Added {added_csv1} papers from Consensus Sponsor Connections CSV")

    # CSV 2: Museum participatory governance
    csv2 = "/Users/polinavasilyeva/Downloads/Museum participatory governance and community ownership - Oct 09, 2026.csv"
    added_csv2 = 0
    if os.path.exists(csv2):
        with open(csv2, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                title = clean_str(r.get("Title"))
                doi = clean_str(r.get("DOI"))
                if not title:
                    continue
                if title.lower() in existing_titles or (doi and doi.lower() in existing_dois):
                    continue
                
                paper_obj = {
                    "title": title,
                    "takeaway": clean_str(r.get("Takeaway")),
                    "authors": clean_str(r.get("Authors")),
                    "year": clean_str(r.get("Year")),
                    "citations": clean_str(r.get("Citations") or "0"),
                    "abstract": clean_str(r.get("Abstract")),
                    "journal": clean_str(r.get("Journal") or "Museum Governance & Social Practice"),
                    "doi": doi,
                    "link": clean_str(r.get("Consensus Link")),
                    "consensus_link": clean_str(r.get("Consensus Link")),
                    "study_type": clean_str(r.get("Study Type")),
                    "topic": "participatory_governance"
                }
                papers.append(paper_obj)
                existing_titles.add(title.lower())
                if doi:
                    existing_dois.add(doi.lower())
                added_csv2 += 1
        print(f"Added {added_csv2} papers from Museum Participatory Governance CSV")

    save_academic(papers)

if __name__ == "__main__":
    ingest()
