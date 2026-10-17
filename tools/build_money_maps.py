"""Build assets/money-maps.json, the data behind money-maps.html.

For each record in institutions.json this reads who funds it (the funding text, funder_links,
flags, Epstein and WikiLeaks records) into a short list of nodes and edges, and links records that
name the same funder. Funders are read out of free text, so a name can be split or grouped wrongly;
the record itself stays the authority. Nothing is fetched and nothing is added to the records.

Run from anywhere:  python3 tools/build_money_maps.py
"""
import json,re,collections,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,'institutions.json')
OUT=os.path.join(ROOT,'assets','money-maps.json')
d=json.load(open(SRC,encoding='utf-8'))
GOV=re.compile(r"\b(dcms|statutory|grant-in-aid|ministry|ministerio|ministère|government|govt|council|state|city|municipal|municipality|federal|national endowment|lottery|lotto|culture fund|cultural affairs|department|commission|agency|region|regional|province|provincial|county|kommune|länder|land |bund|crown|canton|cantonal|kanton|generalitat|junta|comune|commune|gemeente|ayuntamiento|municipio|prefecture|diputaci[oó]n|treasury|european union|\bEU\b|creative europe|arts council|heritage fund|canada council|ville de|stadt|gemeente|prefecture|republic|embassy|consulate|parliament|senate|congress)\b",re.I)
FOUND=re.compile(r"\b(foundations?|funds?|fonds|fondation|fondazione|stiftung|fundación|trusts?|family|philanthrop\w*|endowments?|society|friends|patrons?|board|trustees?|donors?|bequest|legacy|charit\w*|institute|association)\b",re.I)
GENERIC=set(x.lower() for x in """Admissions Admission Tickets Ticket Donations Donation Memberships Membership Sponsorship Sponsors Sponsor Visitors Earned income Individual donors Grants Grant Revenue Public funding Private donors Private funding Corporate sponsors Retail Shop Events Rentals Fundraising Income Budget Operating budget Endowment Mostly Mainly Plus Also Other Others Various Several Some Many Free Funding Support Supported Founded""".split('\n')[0].split())
GENERIC|={'admissions','tickets','donations','memberships','sponsors','visitors','earned income','individual donors','private donors','public funding','ticket sales','retail','shop','events','income','budget','endowment','revenue','grants'}
PREFIX=re.compile(r"^(?:paid for by|paid by|funded (?:mainly |mostly |largely |directly |primarily |partly |chiefly |principally |wholly |entirely |jointly |largely |in part )?by|financed (?:mainly |mostly |largely |directly |primarily |partly )?by|supported (?:mainly |mostly |largely |directly |primarily |partly |principally )?by|funding (?:comes )?from|mainly|mostly|largely|plus|also|and|with|including|sponsors include|sponsors:|sponsored by|backed by|run by|owned by|operated by|founder|donors? include)\s+",re.I)
MONEY=re.compile(r"(?:US\$|[$£€¥]|CHF|JPY|RON|DKK|SEK|NOK|AUD|CAD|NZD|BRL|MXN|INR|CNY|RMB|KRW|PLN|CZK|HUF|ZAR|TRY|RUB)\s?\d[\d.,]*\s?(?:[MmBbKk]\b|million|billion|bn|m\b)?",re.I)
SPLIT=re.compile(r",|;|\band\b|\bplus\b|\bwith\b|\bvia\b|\bthrough\b|\bfrom\b| & |\bplus\b|:")
def norm(s):
    s=s.lower(); s=re.sub(r"\b(the|foundations?|funds?|fonds|stiftung|fondation|inc|ltd|llc|plc|co|corp|corporation|group|philanthropies)\b"," ",s); return re.sub(r"[^a-z0-9]","",s)
# Names that are not funders (the free text yields a few), and names that mean the same funder.
JUNK={'created','frank','german','spanish','projectsponsors','friendsassociation','eur','usd','gbp','municipal','triennial','artistrun','foundationcontributing','corporate','founding','privatephilanthropic','publicculturalbody','botdeal','francophonie','cabinet','senate','family','france','poland','namibianlaw','partnerscommittee','departement','christie','sotheby','expenses','culture','members','arts','tourism','501nonprofit','nonprofit','nonprofitassociation','related','founderfunded','selffunded','other','others','public','private','local','national','regional'}
# Fiscal years, percentages, counts and amounts are figures from the funding text, not funders.
JUNK_RE=re.compile(r"(registered charity|subsidiary of|part of |sat on |shows credit|residenc|\bno\. ?\d|\b(19|20)\d\d\b"
                   r"|\bFY\s?\d|\d\s?%|^\d[\d.,]*\+?\s+(?:works|members|individuals|families|for|non-?profit|edition|report|artists|donors|people|employees)\b"
                   r"|^\d|^(?:a|per)\s+year$|\b(?:report|expenses)$|^about\s+\d|\bof it\b|\b(?:EUR|USD|GBP|CHF|NIS|FCFA|JPY|DKK|SEK|NOK|EU)\s?\d"
                   r"|\bcost about$|^the \d+(?:st|nd|rd|th) edition|\b(?:donated|gave|funded its|co-funded|was)\b|^holds\b|\bis an?$|\b[A-Z]\.[A-Z]$|^main partner\b)",re.I)
SUFFIX_RE=re.compile(r"\s+(funds it|support|lead|founding gift|sat on its board|for the prize|as maintainer|media partner|collection|endowment|project grants|grants|bequest|gift|donation|contract|returns|civic environmental agreements|partners?|programme|program|partnership|preservation|civic|own|fortune|also)$",re.I)
LEAD_RE=re.compile(r"^under the (?:non-profit )?",re.I)
ROLE_RE=re.compile(r"\s+as\s+(?:the\s+|an?\s+|its\s+)?[a-z].*$")
# A sum glued to a name ('Intesa Sanpaolo 464k', 'Ministry of Culture 2.9M', 'Enel 600k as a promoter member') is cut off
# at the sum; a number without a unit ('Fonds 21', 'Tequila 1800', 'WDR 3') is part of the name and stays.
TRAIL_SUM_RE=re.compile(r"\s+\d[\d.,]*\s?(?:[kKmMbB]|million|billion|thousand|mn|bn)\b.*$")
ALIAS={'warhol':'andywarhol','nea':'nationalendowmentforarts','canadacouncil':'canadacouncilforarts','nycdcla':'nycdepartmentofculturalaffairs','artscouncilenglandnationalportfolio':'artscouncilengland'}  # values are norm() forms
GENERIC_GOV={'city government','state government','regional government','government','ministry of culture','county government','local authority','federal government','regional state'}
def clean_label(nm):
    nm=TRAIL_SUM_RE.sub('',LEAD_RE.sub('',ROLE_RE.sub('',SUFFIX_RE.sub('',nm)))).strip(' .,;-')
    if len(nm)<3 or len(nm)>60 or JUNK_RE.search(nm) or norm(nm) in JUNK: return None
    return nm
def merge_key(label,cat,country,rid):
    """One key per funder across the whole atlas. Public bodies are told apart by country, and generic
    ones ('City government') stay with their own record, so they never merge into one false hub."""
    k=norm(label)
    if not k: return ''
    k=ALIAS.get(k,k)
    if label.lower() in GENERIC_GOV: return k+'|'+rid
    if cat=='gov': return k+'|'+country
    return k
# Funders the page can highlight as right-wing sponsors. The atlas records carry no political field, so this is a short
# curated list: only funders that appear in the records AND have a published source for their partisan giving.
RIGHT=[  # (id, label, regex on a sponsor name, regex on record text, basis, sources)
 ('koch','Koch',re.compile(r"\bkoch\b",re.I),re.compile(r"(?<!Robert )(?<!Robert-)\b(David |Charles )?Koch\b(?! Institut)"),
  "The Koch family funds a conservative and libertarian political network, including Americans for Prosperity.",
  ["https://www.cnbc.com/2018/05/23/koch-network-targets-republicans-democrats-for-spending-bill-support.html","https://www.factcheck.org/2018/10/americans-for-prosperity-4"]),
 ('griffin','Ken Griffin / Citadel',re.compile(r"\b(ken griffin|citadel)\b",re.I),re.compile(r"\bKen Griffin\b"),
  "Ken Griffin gave $75M to $100M+ to Republican groups in the 2022 cycle, according to InfluenceWatch.",
  ["https://www.influencewatch.org/person/ken-griffin/"]),
 ('lauder','Ronald Lauder',re.compile(r"^ronald (s\. )?lauder$",re.I),re.compile(r"\bRonald (S\. )?Lauder\b"),
  "Ronald Lauder was Reagan's ambassador to Austria and gave $1M to the Republican State Leadership Committee in 2022.",
  ["https://www.cnbc.com/2022/10/20/midterms-news-ronald-lauder-gives-1-million-to-republican-state-leadership-committee.html"]),
 ('cohen','Steven Cohen',re.compile(r"\bsteven (a\. )?cohen\b|\bsteven & alexandra cohen\b",re.I),re.compile(r"\bSteven (A\. )?Cohen\b|\bSteven & Alexandra Cohen\b"),
  "Steven Cohen was the top individual donor to the Senate Leadership Fund and the Congressional Leadership Fund in 2017, per Artnet; Fox Business reported he later cut back.",
  ["https://news.artnet.com/art-world/steve-cohen-republican-donor-1207619","https://foxbusiness.com/politics/steve-cohen-joins-other-billionaires-in-curbing-gop-donations"]),
 ('mercer','Rebekah Mercer',re.compile(r"\brebekah mercer\b",re.I),re.compile(r"\bMercer removed\b|\bRebekah Mercer\b"),
  "Rebekah Mercer leads the Mercer Family Foundation. The family part-owns Breitbart News and has given more than $35M to Republican candidates and super PACs since 2010, per the Washington Post.",
  ["https://hyperallergic.com/544448/rebekah-mercer/","https://www.influencewatch.org/non-profit/mercer-family-foundation/"]),
]
def right_basis(label):
    for rid,lab,rx,tx,basis,urls in RIGHT:
        if rx.search(label): return {'id':rid,'b':basis,'u':urls}
    return None
def cat_of(tok):
    if FOUND.search(tok) and not re.search(r"\b(state|city|government|ministry)\b",tok,re.I): return 'found'
    if GOV.search(tok): return 'gov'
    if FOUND.search(tok): return 'found'
    return 'corp'
def clean(tok):
    tok=tok.strip(" .\t\n'\"()[]")
    tok=PREFIX.sub('',tok).strip(" .")
    m=re.match(r"^.*\b(?:members|include|includes|including|sponsors|donors|partners|supporters)\s+(?=[A-Z])",tok)
    if m and len(tok)>m.end(): tok=tok[m.end():]
    tok=re.sub(r"\s*\(.*?\)\s*"," ",tok).strip(" .")
    # "62% government", "City 51%", "about 85% public": the share is dropped and the body kept.
    tok=re.sub(r"^(?:about|around|roughly|some|over|nearly)?\s*\d[\d.,]*\s?%\s*(?:of\s+(?:it|the budget|its budget|income|revenue)\s+)?(?:from\s+)?","",tok,flags=re.I)
    tok=re.sub(r"\s+\d[\d.,]*\s?%$","",tok)
    # "Hyundai Motor since 2014": the date is not part of the name.
    tok=re.sub(r"\s+(?:since|from|until|in|between)\s+(?:19|20)\d\d\b.*$","",tok,flags=re.I)
    # "Municipal kunsthalle run by the City of Malmö": the funder is what follows "by".
    m2=re.search(r"\b(?:funded|financed|supported|run|owned|operated|backed|seeded|subsidi[sz]ed|paid for|co-funded)\s+(?:\w+\s+)?by\s+",tok,re.I)
    if m2: tok=tok[m2.end():].strip(" .")
    # "the Glass-House Trust": the article would fail the capital-letter test below, so it goes; keys never held it.
    tok=re.sub(r"^the\s+","",tok,flags=re.I).strip(" .")
    # "Statutory body under the Ministry of Cultural Affairs": the funder is what follows "under".
    m3=re.search(r"\bunder (?:the\s+|a\s+|an\s+)?(?=[A-Z])",tok)
    if m3: tok=tok[m3.end():].strip(" .")
    # "Astana Motors pays running costs", "Pinault bought Palazzo Grassi": a lowercase verb ends the name. Case matters:
    # "Pays de Montbéliard" is a name.
    m4=re.search(r"\s(?:owns|owned|bought|pays|paid|supervised|cites|co-funds|funds|funded|financed|runs|ran|run|set up|took over|gave|donated|holds|cost|covers|provides|provided|manages|operates|operated|backs|backed|sponsors|sponsored|supports|supported|produces|lists|contributing|contributed|is|are|was|were|comes|traces|relying|returns|oversees|publishes|owns|drew|pledged|overseeing|sits|who|which|whose|that)\b",tok)
    if m4:
        head=tok[:m4.start()].strip(" .,")
        tok=head if re.search(r"[A-Z]",head) else ''
    tok=re.sub(r"'s$","",tok).strip(" .")
    # A description beginning with an article or a size word is not a name.
    if re.match(r"^(?:an?|its|his|her|their|no|tiny|small|large|independent|about|us arm|mostly|mainly|public funders|site logos|partners listed|institutional funding|family money|joint shows|board leadership|self-funding)\b",tok,re.I): return ''
    return tok
GOVGEN={'the city':'City government','city':'City government','the state':'State government','state':'State government','the region':'Regional government','the government':'Government','government':'Government','the ministry':'Ministry of Culture','the county':'County government','local authority':'Local authority','the federal government':'Federal government'}
GOVGEN.update({'canton':'Canton','the canton':'Canton','federal':'Federal government','the federal government':'Federal government','county':'County government','the county':'County government',
  'province':'Provincial government','the province':'Provincial government','provincial government':'Provincial government','municipality':'Municipal government','the municipality':'Municipal government',
  'commune':'Municipal government','the commune':'Municipal government','regional government':'Regional government','the regional government':'Regional government','crown':'Crown','the crown':'Crown','eu':'European Union','the eu':'European Union'})
def parse_funding(text):
    out=[];seen=set()
    if not text: return out
    text=re.sub(r"\d{1,3}(?:,\d{3})+\s*(?:visits|visitors)","",text)
    text=re.sub(r"\s*\([^)]*\)","",text)
    text=re.sub(r"\s+\.",".",text)
    for sent in re.split(r"(?<=[A-Za-z0-9\)])\.\s+(?=[A-Z$£€0-9])",text):
        s0=PREFIX.sub('',sent.strip())
        for raw in SPLIT.split(s0):
            m=MONEY.search(raw); tok=clean(raw)
            if tok.lower() in GOVGEN: tok=GOVGEN[tok.lower()]
            if not tok or len(tok)<3 or len(tok.split())>9: continue
            if not (tok[0].isupper() or tok[0].isdigit()): continue
            if tok.lower() in GENERIC: continue
            if re.search(r"\b(museum|gallery|galleries|centre|center|house|building|institution|school|library|archive|collection|theatre|theater)$",tok,re.I) and not FOUND.search(tok): continue
            if re.fullmatch(r"[\d$£€.,\sMBKkmb%]+",tok) or re.search(r"\b(visitors?|visits|sq\s?m|employees|staff|opened|founded|since|built|per cent|percent|revenue|budget|income)\b",tok,re.I) : 
                continue
            nm=MONEY.sub('',tok).strip(" .,;-–—")
            nm=re.sub(r"\s{2,}"," ",nm)
            if len(nm)<3 or nm.lower() in GENERIC: continue
            nm=clean_label(nm)
            if not nm: continue
            k=norm(nm)
            if not k or k in seen: continue
            seen.add(k); out.append({'label':nm,'cat':cat_of(nm),'money':m.group(0).strip() if m else '', 'key':k})
    return out[:14]
id2={x['id']:x for x in d}
nodes_by_inst={}
for x in d:
    ns=[]; keys=set()
    for f in parse_funding(x.get('funding','')):
        ns.append(dict(label=f['label'],cat=f['cat'],tier=3 if f['money'] else 2,note=('Stated amount '+f['money']) if f['money'] else '',key=f['key'],src='funding')); keys.add(f['key'])
    for fl in x.get('funder_links',[]):
        k=norm(fl['funder'])
        if k in keys:
            for n in ns:
                if n['key']==k: n['tier']=3; n['note']=(n['note']+'; ' if n['note'] else '')+f"Also named on {fl['institutions']} atlas records"
            continue
        fc=cat_of(fl['funder'])
        if fc=='corp' and re.fullmatch(r"[A-Z][a-z]+(?: [A-Z]\.)?(?: [A-Z][a-z]+){1,2}",fl['funder']) and not re.search(r"\b(card|motor|motors|bank|air|airlines|cars|group|capital|energy|oil|gas|bros|brothers|company|systems|labs?|media|studios?|partners|holdings|international|global|industries|petroleum|brewery|wines?)\b",fl['funder'],re.I): fc='found'
        ns.append(dict(label=fl['funder'],cat=fc,tier=3,note=f"Named on {fl['institutions']} atlas records",key=k,src='links')); keys.add(k)
    flags=x.get('flags') or []
    why=(x.get('why_flagged') or '').strip()
    for i,fg in enumerate(flags):
        ns.append(dict(label=fg,cat='flag',tier=2,note=why if i==0 and why else 'Flag recorded on this record',key='',src='flag'))
    for e in x.get('epstein_records') or []:
        ns.append(dict(label=e.get('person','Epstein record'),cat='flag',tier=3,note=(e.get('link','')+': ' if e.get('link') else '')+(e.get('summary','') or '')[:420],key='',src='epstein'))
    for w in (x.get('wikileaks_records') or [])[:3]:
        ns.append(dict(label='WikiLeaks '+str(w.get('doc_id','cable')),cat='flag',tier=1,note=(w.get('what_shows','') or '')[:300],key='',src='wikileaks'))
    nodes_by_inst[x['id']]=ns
# shared funder index
idx=collections.defaultdict(set)
for iid,ns in nodes_by_inst.items():
    for n in ns:
        if n['key'] and n['cat']!='gov' or (n['key'] and n['src']=='links'): idx[n['key']].add(iid)
tr={'A':3,'B':2,'U':1}
out=[]
for x in d:
    ns=[dict(n) for n in nodes_by_inst[x['id']]]
    # dedupe by label
    seen=set(); u=[]
    for n in ns:
        k=(n['label'].lower(),n['cat'])
        if k in seen: continue
        seen.add(k); u.append(n)
    ns=u[:22]
    nodes=[];edges=[]
    for i,n in enumerate(ns):
        nodes.append([n['label'],n['cat'],n['tier'],n['note'],0,(('right:'+right_basis(n['label'])['id']) if right_basis(n['label']) else merge_key(n['label'],n['cat'],x['country'],x['id'])) if n['cat'] in ('gov','corp','found') else ''] + ([right_basis(n['label'])] if n['cat'] in ('gov','corp','found') and right_basis(n['label']) else [])); edges.append([0,i+1,{'flag':'flag recorded','epstein':'documented tie','wikileaks':'cable'}.get(n['src'],'funding')])
    taken={x['id']}; added=0
    for i,n in enumerate(ns):
        if not n['key']: continue
        others=[o for o in idx.get(n['key'],()) if o!=x['id'] and o not in taken]
        if not others: continue
        others.sort(key=lambda o:(id2[o]['country']!=x['country'],-tr.get(id2[o]['tier'],0),o))
        for o in others[:3]:
            if added>=12: break
            taken.add(o); added+=1
            oi=id2[o]; nodes.append([oi['name'],'link',2,oi['location'],o]); edges.append([i+1,len(nodes),'also funds'])
    rec=dict(id=x['id'],n=x['name'],c=x['location'],co=x['country'],t=x['tier'],s=x.get('size') or '',lat=x['lat'],lon=x['lon'],
        f=x.get('funding') or '',w=x.get('watch') or '',fl=x.get('flags') or [],why=(x.get('why_flagged') or '')[:300],tn=(x.get('tier_note') or '')[:200],
        u=(x.get('sources') or [])[:6],ep=[{'p':e.get('person',''),'l':e.get('link',''),'s':e.get('status',''),'t':(e.get('summary','') or '')[:320]} for e in (x.get('epstein_records') or [])],web=x.get('website') or '',nodes=nodes,edges=edges)
    out.append(rec)
# A donor named only in a record's own text (not parsed as a sponsor) still becomes a node on that record.
src_by_id={x['id']:x for x in d}
for rec in out:
    x=src_by_id[rec['id']]; text=' '.join(str(x.get(k) or '') for k in ('funding','watch','why_flagged','highlight'))
    for rid,lab,rx,tx,basis,urls in RIGHT:
        if any(len(n)>6 and n[6].get('id')==rid for n in rec['nodes']): continue
        m=tx.search(text)
        if not m: continue
        note='Named in the record: \u201c'+text[max(0,m.start()-60):m.end()+60].strip().replace('\n',' ')+'\u201d'
        rec['nodes'].append([lab,'found',3,note,0,'right:'+rid,{'id':rid,'b':basis,'u':urls}]); rec['edges'].append([0,len(rec['nodes']),'named in record'])
with open(OUT,'w',encoding='utf-8') as fh:
    json.dump(out,fh,ensure_ascii=False,separators=(',',':'))
print(len(out),'records written to',os.path.relpath(OUT,ROOT),str(os.path.getsize(OUT)//1024)+' KB')
print('records with no node:',sum(1 for r in out if len(r['nodes'])==0))
