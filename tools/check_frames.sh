#!/bin/bash
# tools/check_frames.sh hosts.tsv headers.tsv (see tools/frame_refusers.py). For each host<TAB>url line: fetch the page headers (following redirects) and print host, status, x-frame-options, frame-ancestors.
check() {
  host="${1%%	*}"; url="${1#*	}"
  h=$(curl -s -L --max-redirs 5 -D - -o /dev/null --max-time 12 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" "$url" 2>/dev/null | tr -d '\r')
  # keep only the last response block (after redirects)
  last=$(printf '%s\n' "$h" | awk '/^HTTP\//{b=""} {b=b $0 "\n"} END{printf "%s", b}')
  st=$(printf '%s' "$last" | head -1 | awk '{print $2}')
  xfo=$(printf '%s' "$last" | grep -i '^x-frame-options:' | head -1 | cut -d: -f2- | sed 's/^ *//')
  fa=$(printf '%s' "$last" | grep -i '^content-security-policy:' | grep -io 'frame-ancestors[^;]*' | head -1)
  printf '%s\t%s\t%s\t%s\n' "$host" "${st:-ERR}" "$xfo" "$fa"
}
export -f check
cat "$1" | tr '\n' '\0' | xargs -0 -P 48 -n 1 bash -c 'check "$1"' _ > "$2"
echo CHECK-DONE $(wc -l < "$2")
