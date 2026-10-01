#!/usr/bin/env python3
"""
apply_pp_telegraph.py
Applies 'PP Telegraph Regular' (and Medium for weights) to:
- build_conversational_atlas.py
- build_conversational_widget.py

Loads authentic PPTelegraf-Regular.otf and PPTelegraf-Medium.otf as base64 data URIs
with local font fallbacks, ensuring crisp, authentic typography everywhere.
"""

import base64
import os

font_reg_path = 'app/fonts/PPTelegraf-Regular.otf'
font_med_path = 'app/fonts/PPTelegraf-Medium.otf'

if not os.path.exists(font_reg_path):
    raise FileNotFoundError(f"Missing font file: {font_reg_path}")

# =========================================================
# 1. Update build_conversational_atlas.py
# =========================================================
with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    atlas_code = f.read()

# Add font loading code before f"""<!DOCTYPE html>
load_fonts_code = '''    import base64
    b64_reg = base64.b64encode(open('app/fonts/PPTelegraf-Regular.otf', 'rb').read()).decode('ascii')
    b64_med = base64.b64encode(open('app/fonts/PPTelegraf-Medium.otf', 'rb').read()).decode('ascii')

    html = f"""<!DOCTYPE html>'''

atlas_code = atlas_code.replace('    html = f"""<!DOCTYPE html>', load_fonts_code)

# Replace head styles and font definition
old_head_atlas = '''  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'''

new_head_atlas = '''  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"PP Telegraph"', '"PP Telegraf"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }}
        }}
      }}
    }};
  </script>
  <style>
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}

    body {{
      font-family: 'PP Telegraph', 'PP Telegraf', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'''

if old_head_atlas in atlas_code:
    atlas_code = atlas_code.replace(old_head_atlas, new_head_atlas)
    print("Updated head styles and @font-face in build_conversational_atlas.py!")
else:
    print("Warning: old_head_atlas not found!")

# Replace canvas font
atlas_code = atlas_code.replace(
    'ctx.font = \'500 13px "Inter", sans-serif\';',
    'ctx.font = \'500 13px "PP Telegraph", "PP Telegraf", sans-serif\';'
)

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(atlas_code)


# =========================================================
# 2. Update build_conversational_widget.py
# =========================================================
with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
    widget_code = f.read()

load_fonts_widget = '''    import base64
    b64_reg = base64.b64encode(open('app/fonts/PPTelegraf-Regular.otf', 'rb').read()).decode('ascii')
    b64_med = base64.b64encode(open('app/fonts/PPTelegraf-Medium.otf', 'rb').read()).decode('ascii')

    widget_html = f"""<!DOCTYPE html>'''

widget_code = widget_code.replace('    widget_html = f"""<!DOCTYPE html>', load_fonts_widget)

old_head_widget = '''  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'''

new_head_widget = '''  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"PP Telegraph"', '"PP Telegraf"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }}
        }}
      }}
    }};
  </script>
  <style>
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_med}') format('opentype'),
           local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}

    body {{
      font-family: 'PP Telegraph', 'PP Telegraf', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'''

if old_head_widget in widget_code:
    widget_code = widget_code.replace(old_head_widget, new_head_widget)
    print("Updated head styles and @font-face in build_conversational_widget.py!")
else:
    print("Warning: old_head_widget not found!")

with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
    f.write(widget_code)

print("Both build scripts updated for PP Telegraph Regular!")
