#!/usr/bin/env python3
"""
fix_fstring_braces.py
Ensures all curly braces inside the CSS block of build_conversational_atlas.py
and build_conversational_widget.py are properly escaped as {{ and }} for Python f-string.
"""

def fix_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    # The block we inserted in css_3_sizes:
    old_css_single = '''    /* ========================================================= */
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
    .type-14, .text-14, .text-[14px], .text-[14px],
    [class*="text-\[8"], [class*="text-\[9"], [class*="text-\[10"], 
    [class*="text-\[11"], [class*="text-\[12"], [class*="text-\[13"],
    [class*="text-\[14px\]"] {
      font-size: 14px !important;
      line-height: 1.45 !important;
    }

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-[18px], .text-[18px], .text-md,
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
    }'''

    new_css_double = '''    /* ========================================================= */
    /* STRICT 3-TYPE-SIZE SYSTEM (14px Floor, 18px Medium, 24px Large) */
    /* ========================================================= */
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
    [class*="text-\[8"], [class*="text-\[9"], [class*="text-\[10"], 
    [class*="text-\[11"], [class*="text-\[12"], [class*="text-\[13"],
    [class*="text-\[14px\]"] {{
      font-size: 14px !important;
      line-height: 1.45 !important;
    }}

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-[18px], .text-md,
    [class*="text-\[15"], [class*="text-\[16"], [class*="text-\[17"], [class*="text-\[18"], [class*="text-\[19"], [class*="text-\[20"],
    [class*="text-\[18px\]"] {{
      font-size: 18px !important;
      line-height: 1.35 !important;
    }}

    /* Size 3: 24px (Main Brand Title, Modal Headlines, Large Dossier Titles) */
    .type-24, .text-24, .text-xl, .text-2xl, .text-3xl,
    [class*="text-\[22"], [class*="text-\[24"], [class*="text-\[25"], [class*="text-\[26"], [class*="text-\[28"], [class*="text-\[30"],
    [class*="text-\[24px\]"] {{
      font-size: 24px !important;
      line-height: 1.25 !important;
    }}'''

    if old_css_single in text:
        text = text.replace(old_css_single, new_css_double)
        print(f"Fixed double braces in {filename}")

    # Fix tailwind.config fontSize single braces
    old_tw = '''          fontSize: {
            'xs': ['14px', '1.45'],
            'sm': ['14px', '1.45'],
            'base': ['18px', '1.35'],
            'md': ['18px', '1.35'],
            'lg': ['18px', '1.35'],
            'xl': ['24px', '1.25'],
            '2xl': ['24px', '1.25'],
            '3xl': ['24px', '1.25'],
          }'''

    new_tw = '''          fontSize: {{
            'xs': ['14px', '1.45'],
            'sm': ['14px', '1.45'],
            'base': ['18px', '1.35'],
            'md': ['18px', '1.35'],
            'lg': ['18px', '1.35'],
            'xl': ['24px', '1.25'],
            '2xl': ['24px', '1.25'],
            '3xl': ['24px', '1.25'],
          }}'''

    if old_tw in text:
        text = text.replace(old_tw, new_tw)
        print(f"Fixed tailwind.config braces in {filename}")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

fix_file('build_conversational_atlas.py')
fix_file('build_conversational_widget.py')
