import json
import urllib.request
import ssl
import re
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def check_url(url, timeout=10):
    if not url:
        return {'status': 'empty', 'error': 'No URL provided'}
    clean_url = url.strip()
    if not clean_url.startswith('http'):
        clean_url = 'https://' + clean_url
        
    try:
        req = urllib.request.Request(clean_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            final_url = resp.url
            status_code = resp.status
            sample = resp.read(16384).decode('utf-8', errors='ignore')
            title_m = re.search(r'<title[^>]*>(.*?)</title>', sample, re.IGNORECASE | re.DOTALL)
            title = re.sub(r'\s+', ' ', title_m.group(1)).strip() if title_m else ''
            
            flags = []
            final_lower = final_url.lower()
            sample_lower = sample.lower()

            if 'suspendedpage' in final_lower or 'cgi-sys' in final_lower or 'suspended' in final_lower:
                flags.append('suspended_hosting')
            if any(term in final_lower for term in ['godaddy', 'sedo', 'dan.com', 'hugedomains', 'parking', 'domainmarket']):
                flags.append('domain_parked')
            if any(term in sample_lower for term in ['this domain is for sale', 'buy this domain', 'domain has expired', 'account suspended', 'website suspended', 'domain is parked']):
                flags.append('domain_expired_or_suspended')
            if any(term in sample_lower for term in ['permanently closed', 'has closed permanently', 'closing permanently', 'we have closed our doors', 'permanently closed to the public']):
                flags.append('permanently_closed_notice')
            if '404 not found' in sample_lower and status_code == 200:
                flags.append('soft_404')
                
            return {
                'status': 'ok' if not flags else 'flagged',
                'code': status_code,
                'orig_url': url,
                'final_url': final_url,
                'title': title[:120],
                'flags': flags
            }
    except urllib.error.HTTPError as e:
        return {'status': 'http_error', 'code': e.code, 'orig_url': url, 'error': str(e)}
    except urllib.error.URLError as e:
        return {'status': 'url_error', 'orig_url': url, 'error': str(e.reason)}
    except socket.timeout:
        return {'status': 'timeout', 'orig_url': url, 'error': 'Connection timed out'}
    except Exception as e:
        return {'status': 'error', 'orig_url': url, 'error': str(e)}

def main():
    with open('institutions.json', 'r', encoding='utf-8') as f:
        institutions = json.load(f)

    print(f"Loaded {len(institutions)} institutions. Starting concurrent verification...")

    results = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_inst = {
            executor.submit(check_url, inst.get('website')): inst
            for inst in institutions
        }
        
        completed = 0
        for future in as_completed(future_to_inst):
            inst = future_to_inst[future]
            try:
                res = future.result()
            except Exception as exc:
                res = {'status': 'exception', 'orig_url': inst.get('website'), 'error': str(exc)}
            
            results[inst['name']] = {
                'institution': inst['name'],
                'city': inst.get('city'),
                'country': inst.get('country'),
                'tier': inst.get('tier'),
                'check': res
            }
            completed += 1
            if completed % 50 == 0 or completed == len(institutions):
                print(f"Progress: {completed}/{len(institutions)} checked...")

    with open('website_verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    issues = [r for r in results.values() if r['check']['status'] != 'ok']
    print(f"\nVerification Complete! Found {len(issues)} issues out of {len(institutions)} institutions.")

    # Breakdown by tier
    tier_a_issues = [r for r in issues if r.get('tier') == 'A']
    print(f"Tier A (Verified Clean Sanctuaries) with issues: {len(tier_a_issues)}")

    print("\n--- TIER A INSTITUTIONS WITH WEBSITE ISSUES ---")
    for item in tier_a_issues:
        chk = item['check']
        print(f"[{item['country']} - {item['city']}] {item['institution']}")
        print(f"   URL: {chk.get('orig_url')}")
        print(f"   Status: {chk.get('status')} | Code: {chk.get('code')} | Error: {chk.get('error')} | Flags: {chk.get('flags')}")
        if chk.get('final_url') and chk.get('final_url') != chk.get('orig_url'):
            print(f"   Final URL: {chk.get('final_url')}")
        print()

if __name__ == '__main__':
    main()
