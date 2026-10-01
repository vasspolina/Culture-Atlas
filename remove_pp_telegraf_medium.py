#!/usr/bin/env python3
"""
remove_pp_telegraf_medium.py
Strictly removes PP Telegraf Medium everywhere, ensuring only PP Telegraf Regular is used.
"""
import os
import re

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Remove b64_med line
    text = re.sub(r"[ \t]*b64_med = base64\.b64encode\(open\('app/fonts/PPTelegraf-Medium\.otf', 'rb'\)\.read\(\)\)\.decode\('ascii'\)\n?", "", text)

    # 2. In @font-face, replace b64_med with b64_reg and remove Medium local references
    text = text.replace("{b64_med}", "{b64_reg}")
    text = text.replace("local('PP Telegraf Medium'), local('PPTelegraf-Medium'), local('PP Telegraph Medium')", "local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular')")

    # 3. Canvas font weights: change 600 14px and 500 14px to 400 14px
    text = text.replace("ctx.font = '600 14px \"PP Telegraph\"", "ctx.font = '400 14px \"PP Telegraph\"")
    text = text.replace("ctx.font = '500 14px \"PP Telegraph\"", "ctx.font = '400 14px \"PP Telegraph\"")

    # 4. Comments: change (14px Floor, 18px Medium, 24px Large) to (14px Floor, 18px Mid, 24px Large)
    text = text.replace("18px Medium", "18px Mid")

    # 5. Add font-synthesis: none; to prevent browser from synthesizing fake medium/bold
    if "font-synthesis: none;" not in text:
        text = text.replace("*, *::before, *::after {{", "*, *::before, *::after {{\n      font-synthesis: none;\n      -webkit-font-smoothing: antialiased;")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Updated {filepath}")

clean_file('build_conversational_atlas.py')
clean_file('build_conversational_widget.py')

# Remove the file from app/fonts if it exists
med_font_path = 'app/fonts/PPTelegraf-Medium.otf'
if os.path.exists(med_font_path):
    try:
        os.remove(med_font_path)
        print(f"Deleted {med_font_path}")
    except Exception as e:
        print(f"Could not remove {med_font_path}: {e}")

print("Done cleaning PP Telegraf Medium!")
