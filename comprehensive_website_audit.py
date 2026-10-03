import json
import socket
import ssl
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

with open('institutions.json', 'r', encoding='utf-8') as f:
    institutions = json.load(f)

print(f"Loaded {len(institutions)} institutions for audit.")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

PARKING_KEYWORDS = [
    'suspendedpage', 'cgi-sys/suspendedpage', 'domain has expired', 'domain is parked',
    'renew your domain', 'this domain may be for sale', 'buy this domain', 'hugedomains',
    'sedoparking', 'parkingcrew', 'dan.com', 'bodis.com', 'godaddy.com/parking'
]

def audit_institution(inst):
    name = inst.get('name', '')
    url = inst.get('website', '')
    tier = inst.get('tier', '')
    city = inst.get('city', '')
    country = inst.get('country', '')

    result = {
        'name': name,
        'tier': tier,
        'city': city,
        'country': country,
        'url': url,
        'dns_ok': False,
        'http_status': None,
        'final_url': None,
        'content_type': None,
        'is_working': False,
        'issue': None,
        'parked_or_suspended': False
    }

    if not url:
        result['issue'] = 'Missing website URL'
        return result

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        result['issue'] = 'Invalid URL format'
        return result

    # 1. DNS Resolution check
    try:
        addrinfo = socket.getaddrinfo(hostname, None)
        result['dns_ok'] = True
    except Exception as e:
        result['issue'] = f"DNS NXDOMAIN: {e}"
        return result

    # 2. HTTP Request check
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            result['http_status'] = response.status
            result['final_url'] = response.geturl()
            result['content_type'] = response.headers.get_content_type()
            
            # Read first 8KB to check for parking/suspension keywords
            try:
                body_chunk = response.read(8192).decode('utf-8', errors='ignore').lower()
                for kw in PARKING_KEYWORDS:
                    if kw in body_chunk or kw in result['final_url'].lower():
                        result['parked_or_suspended'] = True
                        result['issue'] = f"Detected parked/suspended page keyword: {kw}"
                        return result
            except Exception:
                pass

            result['is_working'] = True
            return result

    except urllib.error.HTTPError as e:
        result['http_status'] = e.code
        # 403 / 401 / 429 are standard bot challenge protections on major cultural sites (Cloudflare, Akamai, CloudFront)
        if e.code in [401, 403, 429]:
            # DNS resolved and server responded with valid HTTP challenge
            result['is_working'] = True
            result['issue'] = f"Bot challenge ({e.code}) - server active and reachable"
        elif e.code == 404:
            result['issue'] = f"HTTP 404 Not Found"
        elif e.code >= 500:
            result['issue'] = f"Server Error {e.code}"
        else:
            result['issue'] = f"HTTP Error {e.code}"
        return result

    except urllib.error.URLError as e:
        result['issue'] = f"Connection URL error: {e.reason}"
        return result

    except socket.timeout:
        result['issue'] = "Connection timed out"
        return result

    except Exception as e:
        result['issue'] = f"Error: {e}"
        return result

with ThreadPoolExecutor(max_workers=35) as executor:
    audit_results = list(executor.map(audit_institution, institutions))

with open('audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(audit_results, f, indent=2, ensure_ascii=False)

working = [r for r in audit_results if r['is_working']]
failed = [r for r in audit_results if not r['is_working']]

print(f"Audit completed: {len(working)} working, {len(failed)} issues.")
for f in failed:
    print(f"FAILED: {f['name']} ({f['tier']}) - {f['url']} -> {f['issue']}")
