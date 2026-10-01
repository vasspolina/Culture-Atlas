#!/usr/bin/env python3
"""
enforce_pure_pp_telegraf_3_sizes.py
Ensures ONLY PP Telegraf Regular is used for everything, and ONLY 3 font sizes (14px, 18px, 24px) exist.
"""
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Remove Google Fonts links
    text = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*', '\n', text)
    text = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com"[^>]*>\s*', '\n', text)
    text = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/css2\?family=JetBrains\+Mono[^>]*>\s*', '\n', text)

    # 2. Tailwind fontFamily: set both sans and mono to PP Telegraf
    old_tw_font = """          fontFamily: {{
            sans: ['"PP Telegraph"', '"PP Telegraf"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }},"""
    new_tw_font = """          fontFamily: {{
            sans: ['"PP Telegraf"', '"PP Telegraph"', 'sans-serif'],
            mono: ['"PP Telegraf"', '"PP Telegraph"', 'sans-serif'],
          }},"""
    if old_tw_font in text:
        text = text.replace(old_tw_font, new_tw_font)
    else:
        # regex replace
        text = re.sub(r'fontFamily:\s*\{\{[^\}]*\}\},', new_tw_font.strip(), text)

    # 3. Replace .font-mono rule
    text = re.sub(r'\.font-mono\s*\{\{\s*font-family:\s*[\x27\x22]JetBrains Mono[\x27\x22][^;]*;\s*\}\}', 
                  '.font-mono {{\\n      font-family: \'PP Telegraf\', \'PP Telegraph\', sans-serif !important;\\n      letter-spacing: -0.01em;\\n    }}', 
                  text)

    # 4. Strict CSS universal rule forcing PP Telegraf Regular 400 and strict 3 sizes
    strict_css = """    /* ========================================================= */
    /* STRICT EXCLUSIVITY: ONLY PP TELEGRAF REGULAR FOR EVERYTHING */
    /* STRICT 3-TYPE-SIZE SYSTEM: 14px Floor/Body, 18px Mid, 24px Headline */
    /* ========================================================= */
    *, *::before, *::after, html, body, input, button, select, textarea, p, span, div, li, a, h1, h2, h3, h4, h5, h6, strong, b, code, pre, kbd, samp, .font-mono, [class*="font-mono"], [class*="font-"] {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 400 !important;
      font-synthesis: none !important;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    *, *::before, *::after {{
      font-size: 14px;
    }}
    html, body {{
      font-size: 14px !important;
      line-height: 1.45;
    }}
    input, button, select, textarea, p, span, div, li, a {{
      font-size: 14px;
    }}

    /* Size 1: 14px (Floor / Default) */
    .type-14, .text-14, .text-[14px],
    [class*="text-\\[8"], [class*="text-\\[9"], [class*="text-\\[10"], 
    [class*="text-\\[11"], [class*="text-\\[12"], [class*="text-\\[13"],
    [class*="text-\\[14px\\]"], .text-xs, .text-sm {{
      font-size: 14px !important;
      line-height: 1.45 !important;
    }}

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-[18px], .text-md, .text-base, .text-lg,
    [class*="text-\\[15"], [class*="text-\\[16"], [class*="text-\\[17"], [class*="text-\\[18"], [class*="text-\\[19"], [class*="text-\\[20"],
    [class*="text-\\[18px\\]"] {{
      font-size: 18px !important;
      line-height: 1.35 !important;
    }}

    /* Size 3: 24px (Main Brand Title, Modal Headlines, Large Dossier Titles) */
    .type-24, .text-24, .text-xl, .text-2xl, .text-3xl, .text-4xl,
    [class*="text-\\[21"], [class*="text-\\[22"], [class*="text-\\[23"], [class*="text-\\[24"], [class*="text-\\[25"], [class*="text-\\[26"], [class*="text-\\[28"], [class*="text-\\[30"], [class*="text-\\[32"],
    [class*="text-\\[24px\\]"] {{
      font-size: 24px !important;
      line-height: 1.25 !important;
    }}"""

    # Replace from /* ========================================================= */ down to Size 3 block
    pattern = r'/\* ========================================================= \*/\s*/\* STRICT 3-TYPE-SIZE SYSTEM.*?(?=/\* Canvas & 3D Math|\@font-face)'
    if re.search(pattern, text, re.DOTALL):
        text = re.sub(pattern, strict_css + "\n\n    ", text, count=1, flags=re.DOTALL)
        print(f"Replaced strict CSS block in {filepath}")

    # 5. Canvas ctx.font: set to strictly 14px "PP Telegraf", "PP Telegraph", sans-serif
    text = re.sub(r'ctx\.font\s*=\s*[\x27\x22][^\x27\x22]*[\x27\x22];?',
                  'ctx.font = \'14px "PP Telegraf", "PP Telegraph", sans-serif\';',
                  text)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Updated {filepath}")

process_file('build_conversational_atlas.py')
process_file('build_conversational_widget.py')
print("Applied pure PP Telegraf Regular and strict 3 type sizes!")
