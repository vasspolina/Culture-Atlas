#!/usr/bin/env python3
"""
apply_3_type_sizes.py
Strictly enforces:
- Fonts start at 14px (minimum floor is 14px, nothing smaller)
- Exactly 3 type sizes used across the entire application:
    Size 1: 14px (All body text, badges, buttons, chips, inputs, metadata, chat, list items, scale)
    Size 2: 18px (Card titles, subheaders, museum names, section headers, city labels)
    Size 3: 24px (Main title 'CULTURE ATLAS', modal main headlines, large dossier headers)
"""

import re

# =========================================================
# 1. Process build_conversational_atlas.py
# =========================================================
with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    atlas = f.read()

# Replace Tailwind config fontSize map
atlas = re.sub(
    r'tailwind\.config\s*=\s*\{.*?theme:\s*\{.*?extend:\s*\{.*?fontFamily:\s*\{.*?\}\s*(?:,\s*fontSize:\s*\{.*?\})?',
    '''tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['"PP Telegraph"', '"PP Telegraf"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          fontSize: {
            'xs': ['14px', '1.45'],
            'sm': ['14px', '1.45'],
            'base': ['18px', '1.35'],
            'md': ['18px', '1.35'],
            'lg': ['18px', '1.35'],
            'xl': ['24px', '1.25'],
            '2xl': ['24px', '1.25'],
            '3xl': ['24px', '1.25'],
          }''',
    atlas,
    flags=re.DOTALL
)

# CSS Rules for strict 3-type-size enforcement
css_3_sizes = '''    /* ========================================================= */
    /* STRICT 3-TYPE-SIZE SYSTEM (14px Floor, 18px Medium, 24px Large) */
    /* ========================================================= */
    *, *::before, *::after {
      font-size: 14px;
    }
    html, body {
      font-size: 14px !important;
      line-height: 1.45;
    }
    input, button, select, textarea, p, span, div, li, a {
      font-size: 14px;
    }

    /* Size 1: 14px (Floor / Default) */
    .type-14, .text-14, .text-sm, .text-xs,
    [class*="text-\[8"], [class*="text-\[9"], [class*="text-\[10"], 
    [class*="text-\[11"], [class*="text-\[12"], [class*="text-\[13"],
    [class*="text-\[14px\]"] {
      font-size: 14px !important;
      line-height: 1.45 !important;
    }

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-base, .text-lg, .text-md,
    [class*="text-\[15"], [class*="text-\[16"], [class*="text-\[17"], [class*="text-\[18"], [class*="text-\[19"], [class*="text-\[20"],
    [class*="text-\[18px\]"] {
      font-size: 18px !important;
      line-height: 1.35 !important;
    }

    /* Size 3: 24px (Main Brand Title, Modal Headlines, Large Dossier Titles) */
    .type-24, .text-24, .text-xl, .text-2xl, .text-3xl,
    [class*="text-\[22"], [class*="text-\[24"], [class*="text-\[25"], [class*="text-\[26"], [class*="text-\[28"], [class*="text-\[30"],
    [class*="text-\[24px\]"] {
      font-size: 24px !important;
      line-height: 1.25 !important;
    }
'''

# Insert css_3_sizes right after <style> in atlas
atlas = atlas.replace('<style>', '<style>\n' + css_3_sizes)

# Update Main Brand Title to Size 3 (24px)
atlas = atlas.replace(
    '<span class="text-[11px] sm:text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>',
    '<span class="text-[24px] font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>'
)
atlas = atlas.replace(
    '<span class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>',
    '<span class="text-[24px] font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>'
)

# Floating Card: Title to Size 2 (18px), meta to Size 1 (14px)
atlas = atlas.replace(
    'id="floatingCardTitle" class="font-bold text-[12px] sm:text-[13px] text-slate-950 leading-tight truncate"',
    'id="floatingCardTitle" class="font-bold text-[18px] text-slate-950 leading-tight truncate"'
)
atlas = atlas.replace(
    'max-w-[240px] sm:max-w-[280px]',
    'max-w-[300px] sm:max-w-[340px]'
)

# Modal titles to Size 3 (24px)
atlas = atlas.replace(
    '<h3 class="font-bold text-white text-xs sm:text-sm">EXCLUSION AUDIT · Why MoMA is Excluded</h3>',
    '<h3 class="font-bold text-white text-[24px]">EXCLUSION AUDIT · Why MoMA is Excluded</h3>'
)
atlas = atlas.replace(
    '<h3 class="font-semibold text-white text-sm">Curator Intelligence Settings</h3>',
    '<h3 class="font-semibold text-white text-[24px]">Curator Intelligence Settings</h3>'
)
atlas = atlas.replace(
    '<h2 id="detailTitle" class="font-bold text-white text-base sm:text-lg leading-tight truncate"></h2>',
    '<h2 id="detailTitle" class="font-bold text-white text-[24px] leading-tight truncate"></h2>'
)

# Modal subheadings to Size 2 (18px)
atlas = atlas.replace('text-xs flex items-center gap-1.5', 'text-[18px] flex items-center gap-1.5')

# Canvas fonts in atlas: 14px floor
atlas = re.sub(r'ctx\.font\s*=\s*[\'"][^\'"]*monospace[\'"]', "ctx.font = '600 14px \"JetBrains Mono\", monospace'", atlas)
atlas = re.sub(r'ctx\.font\s*=\s*[\'"][^\'"]*sans-serif[\'"]', "ctx.font = '500 14px \"PP Telegraph\", \"PP Telegraf\", sans-serif'", atlas)

# Replace all micro text-[...px] under 14px with text-[14px]
def replace_micro_atlas(m):
    val = float(m.group(1))
    if val < 16:
        return 'text-[14px]'
    elif val < 22:
        return 'text-[18px]'
    else:
        return 'text-[24px]'

atlas = re.sub(r'text-\[([0-9.]+)px\]', replace_micro_atlas, atlas)

# Replace text-xs with text-[14px]
atlas = re.sub(r'\btext-xs\b', 'text-[14px]', atlas)
atlas = re.sub(r'\btext-sm\b', 'text-[14px]', atlas)
atlas = re.sub(r'\btext-base\b', 'text-[18px]', atlas)
atlas = re.sub(r'\btext-lg\b', 'text-[18px]', atlas)

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(atlas)

print("Updated build_conversational_atlas.py with 3 type sizes (14px, 18px, 24px)!")


# =========================================================
# 2. Process build_conversational_widget.py
# =========================================================
with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
    widget = f.read()

# Replace Tailwind config fontSize map
widget = re.sub(
    r'tailwind\.config\s*=\s*\{.*?theme:\s*\{.*?extend:\s*\{.*?fontFamily:\s*\{.*?\}\s*(?:,\s*fontSize:\s*\{.*?\})?',
    '''tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            sans: ['"PP Telegraph"', '"PP Telegraf"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          fontSize: {
            'xs': ['14px', '1.45'],
            'sm': ['14px', '1.45'],
            'base': ['18px', '1.35'],
            'md': ['18px', '1.35'],
            'lg': ['18px', '1.35'],
            'xl': ['24px', '1.25'],
            '2xl': ['24px', '1.25'],
            '3xl': ['24px', '1.25'],
          }''',
    widget,
    flags=re.DOTALL
)

# Insert css_3_sizes right after <style> in widget
widget = widget.replace('<style>', '<style>\n' + css_3_sizes)

# Brand Title in widget to Size 2 / 3
widget = widget.replace(
    '<span class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>',
    '<span class="text-[18px] font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>'
)

# Card Title in widget to Size 2 (18px)
widget = widget.replace(
    'id="wCardTitle">Plug In ICA</div>',
    'class="text-[18px] font-bold text-slate-950 leading-tight truncate" id="wCardTitle">Plug In ICA</div>'
)
widget = widget.replace(
    'class="font-bold text-[11px] text-slate-950 leading-tight truncate" id="wCardTitle">Plug In ICA</div>',
    'class="font-bold text-[18px] text-slate-950 leading-tight truncate" id="wCardTitle">Plug In ICA</div>'
)

# Canvas fonts in widget: 14px floor
widget = re.sub(r'ctx\.font\s*=\s*[\'"][^\'"]*monospace[\'"]', "ctx.font = '600 14px \"JetBrains Mono\", monospace'", widget)
widget = re.sub(r'ctx\.font\s*=\s*[\'"][^\'"]*sans-serif[\'"]', "ctx.font = '500 14px \"PP Telegraph\", \"PP Telegraf\", sans-serif'", widget)

# Replace all micro text-[...px] in widget
widget = re.sub(r'text-\[([0-9.]+)px\]', replace_micro_atlas, widget)
widget = re.sub(r'\btext-xs\b', 'text-[14px]', widget)
widget = re.sub(r'\btext-sm\b', 'text-[14px]', widget)
widget = re.sub(r'\btext-base\b', 'text-[18px]', widget)
widget = re.sub(r'\btext-lg\b', 'text-[18px]', widget)

with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
    f.write(widget)

print("Updated build_conversational_widget.py with 3 type sizes (14px, 18px, 24px)!")
