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
GOV=re.compile(r"\b(dcms|statutory|grant-in-aid|ministry|ministerio|ministère|government|govt|council|state|city|municipal|municipality|federal|national endowment|lottery|lotto|culture fund|cultural affairs|department|commission|agency|region|regional|province|county|kommune|länder|land |bund|crown|treasury|european union|\bEU\b|creative europe|arts council|heritage fund|canada council|ville de|stadt|gemeente|prefecture|republic|embassy|consulate|parliament|senate|congress)\b",re.I)
FOUND=re.compile(r"\b(foundations?|funds?|fonds|fondation|fondazione|stiftung|fundación|trusts?|family|philanthrop\w*|endowments?|society|friends|patrons?|board|trustees?|donors?|bequest|legacy|charit\w*|institute|association)\b",re.I)
GENERIC=set(x.lower() for x in """Admissions Admission Tickets Ticket Donations Donation Memberships Membership Sponsorship Sponsors Sponsor Visitors Earned income Individual donors Grants Grant Revenue Public funding Private donors Private funding Corporate sponsors Retail Shop Events Rentals Fundraising Income Budget Operating budget Endowment Mostly Mainly Plus Also Other Others Various Several Some Many Free Funding Support Supported Founded""".split('\n')[0].split())
GENERIC|={'admissions','tickets','donations','memberships','sponsors','visitors','earned income','individual donors','private donors','public funding','ticket sales','retail','shop','events','income','budget','endowment','revenue','grants'}
PREFIX=re.compile(r"^(?:paid for by|paid by|funded (?:mainly |mostly |largely )?by|financed by|supported (?:mainly |mostly )?by|funding (?:comes )?from|mainly|mostly|largely|plus|also|and|with|including|sponsors include|sponsors:|sponsored by|backed by|run by|owned by|operated by|founder|donors? include)\s+",re.I)
MONEY=re.compile(r"(?:US\$|[$£€¥]|CHF|JPY|RON|DKK|SEK|NOK|AUD|CAD|NZD|BRL|MXN|INR|CNY|RMB|KRW|PLN|CZK|HUF|ZAR|TRY|RUB)\s?\d[\d.,]*\s?(?:[MmBbKk]\b|million|billion|bn|m\b)?",re.I)
SPLIT=re.compile(r",|;|\band\b|\bplus\b|\bwith\b|\bvia\b|\bthrough\b|\bfrom\b| & |\bplus\b|:")
def norm(s):
    s=s.lower(); s=re.sub(r"\b(the|foundations?|funds?|fonds|stiftung|fondation|inc|ltd|llc|plc|co|corp|corporation|group|philanthropies)\b"," ",s); return re.sub(r"[^a-z0-9]","",s)
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
    return tok
GOVGEN={'the city':'City government','city':'City government','the state':'State government','state':'State government','the region':'Regional government','the government':'Government','government':'Government','the ministry':'Ministry of Culture','the county':'County government','local authority':'Local authority','the federal government':'Federal government'}
def parse_funding(text):
    out=[];seen=set()
    if not text: return out
    text=re.sub(r"\d{1,3}(?:,\d{3})+\s*(?:visits|visitors)","",text)
    text=re.sub(r"\s*\([^)]*\)","",text)
    text=re.sub(r"\s+\.",".",text)
    for sent in re.split(r"(?<=[A-Za-z0-9\)])\.\s+(?=[A-Z$£€])",text):
        s0=PREFIX.sub('',sent.strip())
        for raw in SPLIT.split(s0):
            m=MONEY.search(raw); tok=clean(raw)
            if tok.lower() in GOVGEN: tok=GOVGEN[tok.lower()]
            if not tok or len(tok)<3 or len(tok.split())>7: continue
            if not (tok[0].isupper() or tok[0].isdigit()): continue
            if tok.lower() in GENERIC: continue
            if re.search(r"\b(museum|gallery|galleries|centre|center|house|building|institution|school|library|archive|collection|theatre|theater)$",tok,re.I) and not FOUND.search(tok): continue
            if re.fullmatch(r"[\d$£€.,\sMBKkmb%]+",tok) or re.search(r"\b(visitors?|visits|sq\s?m|employees|staff|opened|founded|since|built|per cent|percent|revenue|budget|income)\b",tok,re.I) : 
                continue
            nm=MONEY.sub('',tok).strip(" .,;-–—")
            nm=re.sub(r"\s{2,}"," ",nm)
            if len(nm)<3 or nm.lower() in GENERIC: continue
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
        nodes.append([n['label'],n['cat'],n['tier'],n['note'],0]); edges.append([0,i+1,{'flag':'flag recorded','epstein':'documented tie','wikileaks':'cable'}.get(n['src'],'funding')])
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
        u=(x.get('sources') or [])[:6],web=x.get('website') or '',nodes=nodes,edges=edges)
    out.append(rec)
with open(OUT,'w',encoding='utf-8') as fh:
    json.dump(out,fh,ensure_ascii=False,separators=(',',':'))
print(len(out),'records written to',os.path.relpath(OUT,ROOT),str(os.path.getsize(OUT)//1024)+' KB')
print('records with no node:',sum(1 for r in out if len(r['nodes'])==0))
