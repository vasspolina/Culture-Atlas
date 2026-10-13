#!/usr/bin/env python3
"""Embed the Gossip Mode research (data/gossip_research.md) and the visual
critique reference list (data/visual_critique_refs.json) into index.html.
Nothing is added to the text: sections are the file's own '##' sections."""
import json, re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
md = (root / 'data/gossip_research.md').read_text(encoding='utf8')
refs = json.loads((root / 'data/visual_critique_refs.json').read_text(encoding='utf8'))

parts = re.split(r'^## ', md, flags=re.M)
head = parts[0].split('\n', 1)
sections = [{'title': head[0].lstrip('# ').strip(), 'md': head[1].strip(), 'open': True}]
for p in parts[1:]:
    t, _, body = p.partition('\n')
    sections.append({'title': t.strip(), 'md': body.strip()})

block = '/*RESEARCH_STUDIES_START*/const GOSSIP_RESEARCH=%s;const VISUAL_CRITIQUE_REFS=%s;/*RESEARCH_STUDIES_END*/' % (
    json.dumps(sections, ensure_ascii=False).replace('</', '<\\/'),
    json.dumps(refs, ensure_ascii=False).replace('</', '<\\/'))

idx = root / 'index.html'
html = idx.read_text(encoding='utf8')
pat = re.compile(r'/\*RESEARCH_STUDIES_START\*/.*?/\*RESEARCH_STUDIES_END\*/', re.S)
if pat.search(html):
    html = pat.sub(lambda m: block, html)
else:
    k = html.index('const ACADEMIC_RESEARCH')
    html = html[:k] + block + '\n    ' + html[k:]
idx.write_text(html, encoding='utf8')
print(len(sections), 'sections,', len(refs), 'references')
