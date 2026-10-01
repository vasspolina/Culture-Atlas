#!/usr/bin/env python3
"""
fix_retina_blur.py
Upgrades the 3D globe canvas in build_conversational_atlas.py and build_conversational_widget.py
to full native Retina / High-DPI hardware resolution (using window.devicePixelRatio),
removing object-contain and setting crisp vector stroke geometry.
"""
import re

# 1. FIX build_conversational_atlas.py
with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace canvas tag
text = text.replace(
    '<canvas id="globeCanvas" width="900" height="700" class="w-full h-full object-contain cursor-grab"></canvas>',
    '<canvas id="globeCanvas" class="w-full h-full block cursor-grab"></canvas>'
)

# Replace CSS for #globeCanvas
old_css_canvas = """    #globeCanvas {{
      cursor: grab;
      touch-action: none;
    }}"""
new_css_canvas = """    #globeCanvas {{
      cursor: grab;
      touch-action: none;
      display: block;
      width: 100%;
      height: 100%;
      image-rendering: -webkit-optimize-contrast;
    }}"""
if old_css_canvas in text:
    text = text.replace(old_css_canvas, new_css_canvas)

# Replace Canvas & 3D Math Setup and resizeCanvas
old_setup = """    // Canvas & 3D Math Setup
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.clientWidth;
    let height = canvas.height = canvas.parentElement.clientHeight;

    function getBaseRadius() {{
      const minDim = Math.min(width, height);
      return window.innerWidth < 768 ? Math.max(120, minDim * 0.38) : Math.max(160, minDim * 0.33);
    }}
    let baseRadius = getBaseRadius();
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;

    function getMinRadius() {{ return baseRadius * 0.7; }}
    function getMaxRadius() {{ return baseRadius * 4.5; }}

    // Slower Cinematic Motion Physics
    let rotLon = -45;
    let rotLat = 35;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let pointerStartX = 0, pointerStartY = 0;
    let pointerDownTime = 0;

    let isFlying = false;
    let flightProgress = 0;
    let startRotLon = 0, startRotLat = 0;
    let targetRotLon = 0, targetRotLat = 0;

    function resizeCanvas() {{
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
      baseRadius = getBaseRadius();
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius));
    }}
    window.addEventListener('resize', resizeCanvas);"""

new_setup = """    // Canvas & 3D Math Setup with Native Retina / High-DPI Support
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d', {{ alpha: false }});
    
    let dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    let width = 800;
    let height = 600;

    function getBaseRadius() {{
      const minDim = Math.min(width, height);
      return window.innerWidth < 768 ? Math.max(120, minDim * 0.38) : Math.max(160, minDim * 0.33);
    }}
    let baseRadius = 200;
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;

    function getMinRadius() {{ return baseRadius * 0.7; }}
    function getMaxRadius() {{ return baseRadius * 4.5; }}

    // Slower Cinematic Motion Physics
    let rotLon = -45;
    let rotLat = 35;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let pointerStartX = 0, pointerStartY = 0;
    let pointerDownTime = 0;

    let isFlying = false;
    let flightProgress = 0;
    let startRotLon = 0, startRotLat = 0;
    let targetRotLon = 0, targetRotLat = 0;

    function resizeCanvas() {{
      if (!canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
      
      width = Math.round(rect.width) || canvas.parentElement.clientWidth || 800;
      height = Math.round(rect.height) || canvas.parentElement.clientHeight || 600;

      // Double/triple buffer dimensions for razor-sharp Retina displays
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);

      // Logical layout display dimensions
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      baseRadius = getBaseRadius();
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius));
    }}
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);"""

if old_setup in text:
    text = text.replace(old_setup, new_setup)
    print("Replaced atlas canvas setup and resizeCanvas")
else:
    print("Warning: old_setup not found in atlas")

# Update render() in atlas to apply ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
old_render_start = """    function render() {{
      ctx.clearRect(0, 0, width, height);"""

new_render_start = """    function render() {{
      // Scale coordinates to high-DPI hardware buffer for crystal-clear Retina rendering
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';"""

if old_render_start in text:
    text = text.replace(old_render_start, new_render_start)
    print("Replaced atlas render() start with Retina transform")

# Sharpen globe sphere border and country borders
text = text.replace("ctx.strokeStyle = '#182030';\n      ctx.lineWidth = 1;", "ctx.strokeStyle = '#223048';\n      ctx.lineWidth = 1.2;")
text = text.replace("ctx.strokeStyle = isCActive ? '#60a5fa' : '#040b17';\n            ctx.lineWidth = isCActive ? 1.5 : 0.4;", "ctx.strokeStyle = isCActive ? '#60a5fa' : '#050c18';\n            ctx.lineWidth = isCActive ? 2.0 : 0.75;")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(text)

# 2. FIX build_conversational_widget.py
with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
    wtext = f.read()

# Replace canvas tag
wtext = wtext.replace(
    '<canvas id="widgetCanvas" width="500" height="200" class="w-full h-full object-contain"></canvas>',
    '<canvas id="widgetCanvas" class="w-full h-full block cursor-grab"></canvas>'
)

# Replace setup in widget
old_w_setup = """    const canvas = document.getElementById('widgetCanvas');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.clientWidth || 460;
    let height = canvas.height = canvas.parentElement.clientHeight || 360;

    let baseRadius = Math.min(width, height) * 0.35;
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;"""

new_w_setup = """    const canvas = document.getElementById('widgetCanvas');
    const ctx = canvas.getContext('2d', {{ alpha: false }});
    
    let dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    let width = 460;
    let height = 360;

    function resizeCanvas() {{
      if (!canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
      width = Math.round(rect.width) || canvas.parentElement.clientWidth || 460;
      height = Math.round(rect.height) || canvas.parentElement.clientHeight || 360;

      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      baseRadius = Math.min(width, height) * 0.35;
      targetRadius = baseRadius;
    }}
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    let baseRadius = Math.min(width, height) * 0.35;
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;"""

if old_w_setup in wtext:
    wtext = wtext.replace(old_w_setup, new_w_setup)
    print("Replaced widget canvas setup and resizeCanvas")

# Replace render start in widget
old_w_render = """    function render() {{
      ctx.clearRect(0, 0, width, height);"""

new_w_render = """    function render() {{
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';"""

if old_w_render in wtext:
    wtext = wtext.replace(old_w_render, new_w_render)
    print("Replaced widget render() start with Retina transform")

with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
    f.write(wtext)

print("Both files updated for high-DPI Retina sharpness!")
