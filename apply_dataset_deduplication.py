import json
import re

def deduplicate_sentences(text):
    if not text or not isinstance(text, str):
        return text
    
    m = re.match(r'^([A-Z\s/]+:\s*)(.*)$', text)
    if m and any(m.group(1).startswith(p) for p in ['WATCH', 'EXCLUDED', 'UNVERIFIED', 'AUDITED', 'NOTICE']):
        prefix = m.group(1)
        body = m.group(2)
    else:
        prefix = ''
        body = text

    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', body) if s.strip()]
    seen = set()
    cleaned_sentences = []
    for s in raw_sentences:
        norm = re.sub(r'\s+', ' ', s).strip()
        if norm not in seen:
            seen.add(norm)
            cleaned_sentences.append(s)
            
    res = prefix + ' '.join(cleaned_sentences)
    return res.strip()

def clean_file(filepath):
    print(f"Cleaning {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_count = 0
    for inst in data:
        for k, v in inst.items():
            if isinstance(v, str) and len(v) > 15:
                cleaned = deduplicate_sentences(v)
                if cleaned != v:
                    inst[k] = cleaned
                    cleaned_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Cleaned {cleaned_count} fields in {filepath}")

if __name__ == '__main__':
    clean_file('institutions.json')
