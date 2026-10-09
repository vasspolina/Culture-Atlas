import re

with open("build_conversational_atlas.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update font-face block
font_face_block_old = re.search(r"@font-face\s*\{\{\s*font-family:\s*'PP Telegraph';.*?body\s*\{\{", text, re.DOTALL)
if font_face_block_old:
    print("Found old font-face block, replacing with universal extra thin declarations...")
    new_font_faces = """@font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_ultralight}') format('opentype'),
           url('fonts/PPTelegraf-Ultralight.otf') format('opentype'),
           local('PP Telegraf Ultralight'), local('PP Telegraf Extra Thin'), local('PPTelegraf-Ultralight');
      font-weight: 100 900;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_ultralight}') format('opentype'),
           url('fonts/PPTelegraf-Ultralight.otf') format('opentype'),
           local('PP Telegraf Ultralight'), local('PP Telegraf Extra Thin'), local('PPTelegraf-Ultralight');
      font-weight: 100 900;
      font-style: normal;
      font-display: swap;
    }}

    *, *::before, *::after {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 200 !important;
    }}

    body, button, input, select, textarea, div, span, p, h1, h2, h3, h4, h5, h6, a, label, li, ul, ol, td, th, strong, b, em, i {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 200 !important;
    }}

    .font-mono, monospace, code, pre, .font-bold, .font-semibold, .font-medium, strong, b {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 250 !important;
    }}

    body {{"""
    text = text[:font_face_block_old.start()] + new_font_faces + text[font_face_block_old.end():]
    print("Replaced font-face block!")
else:
    print("Warning: font-face block regex didn't match directly.")

# 2. Update canvas ctx.font weights: convert bold, 600, 700 to 200
text = re.sub(r"ctx\.font\s*=\s*'bold\s+", "ctx.font = '200 ", text)
text = re.sub(r'ctx\.font\s*=\s*"bold\s+', 'ctx.font = "200 ', text)
text = re.sub(r"ctx\.font\s*=\s*'600\s+", "ctx.font = '200 ", text)
text = re.sub(r'ctx\.font\s*=\s*"600\s+', 'ctx.font = "200 ', text)
text = re.sub(r"ctx\.font\s*=\s*'700\s+", "ctx.font = '200 ", text)
text = re.sub(r'ctx\.font\s*=\s*"700\s+', 'ctx.font = "200 ', text)

with open("build_conversational_atlas.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated build_conversational_atlas.py with PP Telegraf Extra Thin for all fonts!")
