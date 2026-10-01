import json

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

inst_json = json.dumps(institutions)

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Culture Atlas — Conversational 3D Experience</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
      --bg: #030712;
      --card-bg: rgba(15, 23, 42, 0.85);
      --accent: #00ff87;
      --cyan: #00f2fe;
      --tier-a: #24a148;
      --tier-b: #4589ff;
      --tier-u: #8d8d8d;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: #f1f5f9;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Glow utilities */
    .glow-cyan {
      box-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
    }
    .glow-green {
      box-shadow: 0 0 20px rgba(0, 255, 135, 0.25);
    }
    .text-glow {
      text-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
    }

    /* Glassmorphism */
    .glass-panel {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.2);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 9999px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.25);
    }

    /* Globe canvas cursor */
    #globeCanvas {
      cursor: grab;
      touch-action: none;
    }
    #globeCanvas.dragging {
      cursor: grabbing;
    }

    @keyframes pulse-ring {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.1); opacity: 0.4; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    .pulsing {
      animation: pulse-ring 2.5s infinite ease-in-out;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col bg-slate-950 text-slate-100">

  <!-- TOP HEADER / NAV -->
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-4 py-3">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Brand & Description -->
      <div class="flex items-center gap-3">
        <div>
          <h1 class="text-base font-bold tracking-wide text-white flex items-center gap-2">
            CULTURE ATLAS
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
              Conversational 3D
            </span>
          </h1>
          <p class="text-xs text-slate-400 hidden sm:block">Ethically funded cultural institutions across the world</p>
        </div>
      </div>

      <!-- Controls & View Mode -->
      <div class="flex items-center gap-2 flex-wrap">
        <!-- View toggle -->
        <div class="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700 text-xs">
          <button id="viewGlobeBtn" class="px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow">
            3D Globe
          </button>
          <button id="viewListBtn" class="px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white">
            Ledger Table
          </button>
        </div>

        <!-- Chat Concierge Toggle -->
        <button id="headerChatToggle" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-600/50 text-xs text-emerald-300 font-medium transition glow-green">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Atlas AI Concierge</span>
          <span class="hidden md:inline text-[10px] opacity-75 font-mono">⌘K</span>
        </button>
      </div>

    </div>
  </header>

  <!-- FILTER & SEARCH BAR -->
  <section class="border-b border-slate-800/80 bg-slate-900/50 px-4 py-2 text-xs">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Tier Filters -->
      <div class="flex items-center gap-2 flex-wrap" role="group" aria-label="Filter by Tier">
        <span class="text-slate-400 text-xs mr-1 font-medium">Tiers:</span>
        <button id="tierABtn" class="tier-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-emerald-500/40 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/60 transition" data-tier="A">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Verified</span>
          <span class="font-mono text-[11px] opacity-75 ml-0.5" id="countTierA">125</span>
        </button>
        <button id="tierBBtn" class="tier-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-blue-500/40 bg-blue-950/40 text-blue-300 hover:bg-blue-900/60 transition" data-tier="B">
          <span class="w-2 h-2 rounded-full bg-blue-400"></span>
          <span>One Name to Know</span>
          <span class="font-mono text-[11px] opacity-75 ml-0.5" id="countTierB">55</span>
        </button>
        <button id="tierUBtn" class="tier-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-slate-500/40 bg-slate-900/40 text-slate-300 hover:bg-slate-800 transition" data-tier="U">
          <span class="w-2 h-2 rounded-full bg-slate-400"></span>
          <span>Unverified</span>
          <span class="font-mono text-[11px] opacity-75 ml-0.5" id="countTierU">17</span>
        </button>
      </div>

      <!-- Size Filters & Search -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-1 bg-slate-800/80 px-1 py-0.5 rounded-lg border border-slate-700 text-xs">
          <button id="sizeAllBtn" class="px-2 py-0.5 rounded text-white bg-slate-700 font-medium">All</button>
          <button id="sizeLargeBtn" class="px-2 py-0.5 rounded text-slate-400 hover:text-white">Large (&gt;$20M)</button>
          <button id="sizeSmallBtn" class="px-2 py-0.5 rounded text-slate-400 hover:text-white">Small/Mid</button>
        </div>

        <div class="relative w-48 sm:w-64">
          <input type="text" id="searchInput" placeholder="Search institutions, cities..." class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1 text-xs text-white focus:outline-none focus:border-cyan-400 transition" />
          <button id="clearSearchBtn" class="hidden absolute right-2.5 top-1 text-slate-400 hover:text-white text-xs">✕</button>
        </div>
      </div>

    </div>
  </section>

  <!-- MAIN VIEWPORT -->
  <main class="flex-1 flex flex-col relative overflow-hidden">
    
    <!-- 3D GLOBE VIEW -->
    <div id="globeViewContainer" class="flex-1 flex flex-col md:flex-row h-full min-h-[550px] relative">
      
      <!-- Globe canvas wrapper -->
      <div class="relative flex-1 bg-slate-950 flex items-center justify-center overflow-hidden min-h-[400px]">
        <canvas id="globeCanvas" class="w-full h-full max-h-[85vh]"></canvas>

        <!-- Globe Tools Overlay -->
        <div class="absolute bottom-5 left-5 flex flex-col gap-2 bg-slate-900/80 border border-slate-800 p-1.5 rounded-xl shadow-xl backdrop-blur z-20">
          <button id="zoomInBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center font-bold transition" title="Zoom In">+</button>
          <button id="zoomOutBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center font-bold transition" title="Zoom Out">−</button>
          <button id="resetViewBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center transition" title="Reset View">◎</button>
          <button id="spinToggleBtn" class="w-8 h-8 rounded-lg bg-emerald-950/70 border border-emerald-600/50 hover:bg-emerald-900 text-emerald-300 flex items-center justify-center transition" title="Toggle Auto-Spin">↻</button>
        </div>

        <!-- Coordinates / Status Info -->
        <div class="absolute bottom-5 right-5 hidden sm:flex items-center gap-3 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl text-[11px] font-mono text-slate-400 backdrop-blur z-20">
          <span id="globeStatus">Drag to turn · Scroll to zoom</span>
          <span class="text-slate-600">|</span>
          <span id="visibleCount" class="text-cyan-400">197 visible</span>
        </div>

        <!-- Tooltip -->
        <div id="globeTooltip" class="absolute pointer-events-none hidden z-30 bg-slate-900/95 border border-cyan-500/50 text-white px-3 py-2 rounded-lg shadow-xl text-xs max-w-xs backdrop-blur">
          <div id="tooltipName" class="font-semibold text-white"></div>
          <div id="tooltipMeta" class="text-[11px] text-slate-300"></div>
        </div>

      </div>

      <!-- Detail & Inspection Side Drawer -->
      <aside id="detailDrawer" class="w-full md:w-96 border-t md:border-t-0 md:border-l border-slate-800 bg-slate-900/95 flex flex-col z-30 max-h-[50vh] md:max-h-none overflow-y-auto">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-400">Institution Dossier</h2>
          <span id="dossierTierBadge" class="hidden text-[10px] font-bold px-2 py-0.5 rounded-full border"></span>
        </div>

        <div id="dossierContent" class="p-4 flex-1 flex flex-col justify-center text-slate-400 text-xs">
          <div class="text-center py-8">
            <div class="w-12 h-12 mx-auto rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-xl mb-3 text-cyan-400">
              🏛️
            </div>
            <p class="font-medium text-slate-300">No institution selected</p>
            <p class="text-[11px] text-slate-500 mt-1 max-w-[200px] mx-auto">
              Click any dot on the 3D globe, search above, or ask the AI Concierge.
            </p>
          </div>
        </div>
      </aside>

    </div>

    <!-- TABLE / LIST VIEW -->
    <div id="listViewContainer" class="hidden flex-1 overflow-auto p-4 max-w-7xl mx-auto w-full">
      <div class="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-2xl">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="bg-slate-800/90 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-700">
            <tr>
              <th class="p-3.5">Institution</th>
              <th class="p-3.5">Location</th>
              <th class="p-3.5">Tier</th>
              <th class="p-3.5">Size</th>
              <th class="p-3.5">Funding Breakdown</th>
              <th class="p-3.5">Watch / Notes</th>
              <th class="p-3.5">Sources</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-slate-800/60 font-sans">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- CONVERSATIONAL AI CONCIERGE FLOATING DRAWER -->
  <div id="chatDrawer" class="fixed bottom-5 right-5 w-96 max-w-[calc(100vw-2rem)] h-[580px] max-h-[85vh] bg-slate-900/95 border border-cyan-500/40 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col z-50 transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-none">
    
    <!-- Chat Header -->
    <div class="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/70 rounded-t-2xl">
      <div class="flex items-center gap-2.5">
        <div class="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-xs">
          ✨
        </div>
        <div>
          <h3 class="text-xs font-semibold text-white tracking-wide">Atlas AI Concierge</h3>
          <span id="chatModeTag" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
            Offline Engine
          </span>
        </div>
      </div>
      <div class="flex items-center gap-1.5">
        <button id="chatSettingsBtn" class="text-slate-400 hover:text-white p-1 rounded" title="Settings / API Key">⚙️</button>
        <button id="chatClearBtn" class="text-slate-400 hover:text-white p-1 rounded" title="Clear chat">🗑️</button>
        <button id="chatCloseBtn" class="text-slate-400 hover:text-white p-1 rounded text-base" title="Close">✕</button>
      </div>
    </div>

    <!-- Messages Container -->
    <div id="chatMessages" class="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
      
      <!-- Welcome message -->
      <div class="flex flex-col gap-1 items-start">
        <div class="bg-slate-800/90 border border-slate-700/80 text-slate-200 p-3.5 rounded-2xl rounded-tl-sm max-w-[92%] leading-relaxed shadow-md">
          <p class="font-semibold text-white mb-1">Hello! I am your Culture Atlas Concierge.</p>
          <p class="text-slate-300">
            Ask me about any of the <strong>197 cultural institutions</strong>, funding models, or city collections. I can rotate the 3D globe and inspect dossiers directly for you!
          </p>
          <div class="mt-3 flex flex-col gap-1.5">
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🧭 What ethically funded museums are in Tokyo?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🟢 Show me large Tier A verified institutions
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🔍 Why is Te Papa categorized as Tier B?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              ⚖️ How is funding transparency evaluated?
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- Settings Overlay -->
    <div id="settingsOverlay" class="absolute inset-0 bg-slate-950/95 backdrop-blur-md p-4 rounded-2xl hidden flex-col gap-3 z-20">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2">
        <h4 class="text-xs font-semibold text-white uppercase tracking-wider">Concierge Settings</h4>
        <button id="closeSettingsOverlay" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <div class="flex flex-col gap-1 text-xs">
        <label class="text-slate-300 font-medium">Google Gemini API Key (Optional)</label>
        <input type="password" id="geminiApiKeyInput" placeholder="AIzaSy..." class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400" />
        <p class="text-[11px] text-slate-500 mt-1">
          Leave blank for the built-in offline engine. Add your key from <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-cyan-400 underline">Google AI Studio</a> for advanced open-ended reasoning.
        </p>
      </div>
      <button id="saveSettingsBtn" class="mt-2 w-full py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition">
        Save Settings
      </button>
    </div>

    <!-- Chat Input Bar -->
    <div class="p-3 border-t border-slate-800 bg-slate-950/80 rounded-b-2xl flex items-center gap-2">
      <input type="text" id="chatInput" placeholder="Ask about a museum, city, or sponsor..." class="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-400 transition" />
      <button id="chatVoiceBtn" class="p-2 text-slate-400 hover:text-cyan-400 rounded-lg border border-slate-800 hover:border-slate-700 transition" title="Voice Input">
        🎙️
      </button>
      <button id="chatSendBtn" class="p-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg transition shadow-md" title="Send">
        ➤
      </button>
    </div>

  </div>

  <!-- FLOATING CHAT BUTTON (BOTTOM RIGHT) -->
  <button id="floatingChatBtn" class="fixed bottom-5 right-5 z-40 flex items-center gap-2 px-3.5 py-2 rounded-full bg-gradient-to-r from-slate-900 to-slate-950 border border-emerald-500/50 text-white text-xs font-semibold shadow-2xl hover:scale-105 transition glow-green">
    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#00ff87] animate-pulse"></span>
    <span>Atlas Concierge</span>
  </button>

  <script>
    const ALL_INSTITUTIONS = ''' + inst_json + ''';

    // State
    let activeTiers = new Set(['A', 'B', 'U']);
    let activeSize = 'all';
    let searchQuery = '';
    let selectedInstitution = null;
    let activeView = 'globe';

    // Globe Physics & Projection State
    let rotLon = 0;
    let rotLat = 20;
    let targetRotLon = 0;
    let targetRotLat = 20;
    let isFlying = false;
    let flightProgress = 0;
    let startRotLon = 0, startRotLat = 0;

    let zoom = 1.0;
    let targetZoom = 1.0;
    let isDragging = false;
    let lastMouseX = 0, lastMouseY = 0;
    let velLon = 0.2; // auto-spin velocity
    let velLat = 0;
    let isAutoSpinning = true;

    // Hover state
    let hoveredInstitution = null;

    // Canvas & Context
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('globeTooltip');
    const tooltipName = document.getElementById('tooltipName');
    const tooltipMeta = document.getElementById('tooltipMeta');

    // Resize canvas
    function resizeCanvas() {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // 3D Orthographic projection
    function project(lon, lat, r, cx, cy) {
      const rad = Math.PI / 180;
      const lambda = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda);
      if (cosC < 0) return null; // Behind sphere

      const x = cx + r * Math.cos(phi) * Math.sin(lambda);
      const y = cy - r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda));
      return { x, y, depth: cosC };
    }

    // Filter institutions
    function getFilteredInstitutions() {
      return ALL_INSTITUTIONS.filter(i => {
        if (!activeTiers.has(i.tier)) return false;
        if (activeSize === 'L' && i.size !== 'L') return false;
        if (activeSize === 'S' && i.size !== 'S') return false;
        if (searchQuery) {
          const q = searchQuery.toLowerCase();
          const match = i.name.toLowerCase().includes(q) || i.location.toLowerCase().includes(q);
          if (!match) return false;
        }
        return true;
      });
    }

    // Render loop
    function renderGlobe() {
      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;
      const cx = w / 2;
      const cy = h / 2;
      const radius = Math.min(w, h) * 0.42 * zoom;

      ctx.clearRect(0, 0, w, h);

      // Animation & Inertia
      if (isFlying) {
        flightProgress += 0.035;
        if (flightProgress >= 1) {
          flightProgress = 1;
          isFlying = false;
        }
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
        rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        zoom += (targetZoom - zoom) * 0.1;
      } else if (isAutoSpinning && !isDragging) {
        rotLon = (rotLon + velLon) % 360;
      } else if (!isDragging) {
        // Friction
        rotLon = (rotLon + velLon) % 360;
        rotLat = Math.max(-80, Math.min(80, rotLat + velLat));
        velLon *= 0.94;
        velLat *= 0.94;
      }

      // Outer Glow
      const glowGrad = ctx.createRadialGradient(cx, cy, radius * 0.85, cx, cy, radius * 1.25);
      glowGrad.addColorStop(0, 'rgba(0, 242, 254, 0.22)');
      glowGrad.addColorStop(0.5, 'rgba(0, 255, 135, 0.08)');
      glowGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Globe Base Sphere
      const oceanGrad = ctx.createRadialGradient(cx - radius * 0.3, cy - radius * 0.3, radius * 0.1, cx, cy, radius);
      oceanGrad.addColorStop(0, '#00264d');
      oceanGrad.addColorStop(0.7, '#001124');
      oceanGrad.addColorStop(1, '#00050d');
      ctx.fillStyle = oceanGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe for graticules
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();

      // Draw Parallels (Latitudes)
      ctx.strokeStyle = 'rgba(0, 255, 135, 0.12)';
      ctx.lineWidth = 1;
      [-60, -30, 0, 30, 60].forEach(lat => {
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 6) {
          const pt = project(lon, lat, radius, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else {
            first = true;
          }
        }
        ctx.stroke();
      });

      // Draw Meridians (Longitudes)
      for (let lon = -180; lon < 180; lon += 30) {
        ctx.beginPath();
        let first = true;
        for (let lat = -80; lat <= 80; lat += 4) {
          const pt = project(lon, lat, radius, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else {
            first = true;
          }
        }
        ctx.stroke();
      }

      ctx.restore();

      // Sphere Rim Highlight
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.5)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Render Institutions Dots
      const filtered = getFilteredInstitutions();
      document.getElementById('visibleCount').textContent = `${filtered.length} visible`;

      filtered.forEach(inst => {
        const pt = project(inst.lon, inst.lat, radius, cx, cy);
        if (!pt) return;

        const isSelected = selectedInstitution && selectedInstitution.name === inst.name;
        const isHovered = hoveredInstitution && hoveredInstitution.name === inst.name;

        // Size
        const baseR = inst.size === 'L' ? 5.5 : 3.5;
        const dotR = (isSelected ? baseR * 1.6 : isHovered ? baseR * 1.3 : baseR) * Math.min(1.8, Math.max(0.6, pt.depth));

        // Color by tier
        let dotColor = '#24a148';
        if (inst.tier === 'B') dotColor = '#4589ff';
        if (inst.tier === 'U') dotColor = '#8d8d8d';

        // Glowing outer halo
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR * 2, 0, Math.PI * 2);
        ctx.fillStyle = inst.tier === 'A' ? 'rgba(0, 255, 135, 0.25)' : inst.tier === 'B' ? 'rgba(0, 242, 254, 0.25)' : 'rgba(255, 255, 255, 0.15)';
        ctx.fill();

        // Selected pulsing ring
        if (isSelected) {
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 3, 0, Math.PI * 2);
          ctx.strokeStyle = '#00ff87';
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        // Core dot
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = dotColor;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      requestAnimationFrame(renderGlobe);
    }
    requestAnimationFrame(renderGlobe);

    // Kinetic Fly To Location
    function flyTo(lon, lat, targetZ = 1.3) {
      isAutoSpinning = false;
      document.getElementById('spinToggleBtn').classList.remove('bg-emerald-950/70', 'text-emerald-300');
      document.getElementById('spinToggleBtn').classList.add('bg-slate-800', 'text-slate-400');

      startRotLon = rotLon;
      startRotLat = rotLat;
      
      // Compute shortest angle
      let dLon = (lon - startRotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = startRotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      targetZoom = targetZ;

      flightProgress = 0;
      isFlying = true;
    }

    // Inspect Institution in Detail Drawer
    function selectInstitution(inst) {
      selectedInstitution = inst;
      const drawer = document.getElementById('dossierContent');
      const badge = document.getElementById('dossierTierBadge');

      const tierLabels = { A: 'Verified', B: 'One Name To Know', U: 'Unverified' };
      const tierColors = {
        A: 'bg-emerald-950 text-emerald-400 border-emerald-600',
        B: 'bg-blue-950 text-blue-400 border-blue-600',
        U: 'bg-slate-800 text-slate-300 border-slate-600'
      };

      badge.className = `text-[10px] font-bold px-2 py-0.5 rounded-full border ${tierColors[inst.tier]}`;
      badge.textContent = tierLabels[inst.tier];
      badge.classList.remove('hidden');

      drawer.innerHTML = `
        <div class="space-y-4">
          <div>
            <h3 class="text-base font-bold text-white">${inst.name}</h3>
            <p class="text-xs text-cyan-400 flex items-center gap-1 mt-0.5">
              <span>📍</span> <span>${inst.location}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400">${inst.size === 'L' ? 'Large Institution' : 'Small/Mid-sized'}</span>
            </p>
          </div>

          <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
            <h4 class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1">Funding & Governance</h4>
            <p class="text-xs text-slate-200 leading-relaxed">${inst.funding}</p>
          </div>

          ${inst.watch ? `
            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <h4 class="text-[10px] font-bold uppercase tracking-wider text-cyan-400 mb-1">Watch Notes</h4>
              <p class="text-xs text-slate-300 leading-relaxed">${inst.watch}</p>
            </div>
          ` : ''}

          <div>
            <h4 class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Verified Sources</h4>
            <div class="flex flex-col gap-1.5">
              ${(inst.sources || []).map(url => {
                let domain = url;
                try { domain = new URL(url).hostname.replace(/^www\\./, ''); } catch(e){}
                return `
                  <a href="${url}" target="_blank" rel="noopener noreferrer" class="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-[11px] text-cyan-300 hover:text-white transition">
                    <span class="truncate">${domain}</span>
                    <span>↗</span>
                  </a>
                `;
              }).join('')}
            </div>
          </div>
        </div>
      `;

      flyTo(inst.lon, inst.lat, Math.max(zoom, 1.4));
    }

    // Pointer Interactions for Globe
    canvas.addEventListener('pointerdown', e => {
      isDragging = true;
      canvas.classList.add('dragging');
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      velLon = 0;
      velLat = 0;
      isFlying = false;
    });

    window.addEventListener('pointermove', e => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (isDragging) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;

        const sens = 0.35 / zoom;
        rotLon = (rotLon - dx * sens) % 360;
        rotLat = Math.max(-80, Math.min(80, rotLat + dy * sens));
        velLon = -dx * sens * 0.4;
        velLat = dy * sens * 0.4;
      } else {
        // Hit test dots
        const cx = rect.width / 2;
        const cy = rect.height / 2;
        const radius = Math.min(rect.width, rect.height) * 0.42 * zoom;

        let hit = null;
        const filtered = getFilteredInstitutions();
        for (let i = 0; i < filtered.length; i++) {
          const inst = filtered[i];
          const pt = project(inst.lon, inst.lat, radius, cx, cy);
          if (pt) {
            const dist = Math.hypot(pt.x - mouseX, pt.y - mouseY);
            if (dist < 12) {
              hit = inst;
              break;
            }
          }
        }

        hoveredInstitution = hit;
        if (hit) {
          tooltip.style.left = `${mouseX + 12}px`;
          tooltip.style.top = `${mouseY + 12}px`;
          tooltipName.textContent = hit.name;
          tooltipMeta.textContent = `${hit.location} · ${hit.tier === 'A' ? 'Verified' : hit.tier === 'B' ? 'One Name to Know' : 'Unverified'}`;
          tooltip.classList.remove('hidden');
        } else {
          tooltip.classList.add('hidden');
        }
      }
    });

    window.addEventListener('pointerup', e => {
      if (isDragging) {
        isDragging = false;
        canvas.classList.remove('dragging');
      }
    });

    canvas.addEventListener('click', e => {
      if (hoveredInstitution) {
        selectInstitution(hoveredInstitution);
      }
    });

    // Zoom on wheel
    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      zoom = Math.max(0.6, Math.min(3.5, zoom * factor));
    }, { passive: false });

    // Controls
    document.getElementById('zoomInBtn').addEventListener('click', () => { zoom = Math.min(3.5, zoom * 1.25); });
    document.getElementById('zoomOutBtn').addEventListener('click', () => { zoom = Math.max(0.6, zoom / 1.25); });
    document.getElementById('resetViewBtn').addEventListener('click', () => { flyTo(0, 20, 1.0); });
    document.getElementById('spinToggleBtn').addEventListener('click', () => {
      isAutoSpinning = !isAutoSpinning;
      const btn = document.getElementById('spinToggleBtn');
      if (isAutoSpinning) {
        btn.classList.add('bg-emerald-950/70', 'text-emerald-300');
        btn.classList.remove('bg-slate-800', 'text-slate-400');
        velLon = 0.2;
      } else {
        btn.classList.remove('bg-emerald-950/70', 'text-emerald-300');
        btn.classList.add('bg-slate-800', 'text-slate-400');
      }
    });

    // Tier filter buttons
    ['A', 'B', 'U'].forEach(t => {
      const btn = document.getElementById(`tier${t}Btn`);
      btn.addEventListener('click', () => {
        if (activeTiers.has(t)) {
          if (activeTiers.size > 1) activeTiers.delete(t);
        } else {
          activeTiers.add(t);
        }
        btn.classList.toggle('opacity-40', !activeTiers.has(t));
        renderTable();
      });
    });

    // Size filters
    const sizeButtons = {
      all: document.getElementById('sizeAllBtn'),
      L: document.getElementById('sizeLargeBtn'),
      S: document.getElementById('sizeSmallBtn'),
    };
    Object.keys(sizeButtons).forEach(sz => {
      sizeButtons[sz].addEventListener('click', () => {
        activeSize = sz;
        Object.keys(sizeButtons).forEach(k => {
          sizeButtons[k].classList.toggle('bg-slate-700', k === sz);
          sizeButtons[k].classList.toggle('text-white', k === sz);
          sizeButtons[k].classList.toggle('text-slate-400', k !== sz);
        });
        renderTable();
      });
    });

    // Search input
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    searchInput.addEventListener('input', e => {
      searchQuery = e.target.value.trim();
      clearSearchBtn.classList.toggle('hidden', !searchQuery);
      renderTable();
    });
    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      renderTable();
    });

    // View mode toggle
    const viewGlobeBtn = document.getElementById('viewGlobeBtn');
    const viewListBtn = document.getElementById('viewListBtn');
    const globeViewContainer = document.getElementById('globeViewContainer');
    const listViewContainer = document.getElementById('listViewContainer');

    viewGlobeBtn.addEventListener('click', () => {
      activeView = 'globe';
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white';
      globeViewContainer.classList.remove('hidden');
      listViewContainer.classList.add('hidden');
      resizeCanvas();
    });

    viewListBtn.addEventListener('click', () => {
      activeView = 'list';
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white';
      listViewContainer.classList.remove('hidden');
      globeViewContainer.classList.add('hidden');
      renderTable();
    });

    // Render Table View
    function renderTable() {
      const tbody = document.getElementById('tableBody');
      const filtered = getFilteredInstitutions();

      tbody.innerHTML = filtered.map(inst => `
        <tr class="hover:bg-slate-800/40 transition cursor-pointer" onclick="selectAndShow('${inst.name.replace(/'/g, "\\\\'")}')">
          <td class="p-3.5 font-semibold text-white">${inst.name}</td>
          <td class="p-3.5 text-slate-300 whitespace-nowrap">${inst.location}</td>
          <td class="p-3.5 whitespace-nowrap">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${inst.tier === 'A' ? 'bg-emerald-950 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-600'}">
              ${inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified'}
            </span>
          </td>
          <td class="p-3.5 text-slate-400">${inst.size === 'L' ? 'Large' : 'Small/Mid'}</td>
          <td class="p-3.5 max-w-xs text-slate-300">${inst.funding}</td>
          <td class="p-3.5 max-w-xs text-slate-400">${inst.watch || '—'}</td>
          <td class="p-3.5 whitespace-nowrap">
            ${(inst.sources || []).slice(0, 1).map(u => `
              <a href="${u}" target="_blank" onclick="event.stopPropagation()" class="text-cyan-400 hover:underline">Link ↗</a>
            `).join('')}
          </td>
        </tr>
      `).join('');
    }
    renderTable();

    window.selectAndShow = function(name) {
      const inst = ALL_INSTITUTIONS.find(i => i.name === name);
      if (inst) {
        viewGlobeBtn.click();
        selectInstitution(inst);
      }
    };

    // ==========================================
    // AI CONCIERGE CHAT ENGINE
    // ==========================================
    const chatDrawer = document.getElementById('chatDrawer');
    const floatingChatBtn = document.getElementById('floatingChatBtn');
    const headerChatToggle = document.getElementById('headerChatToggle');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatSettingsBtn = document.getElementById('chatSettingsBtn');
    const settingsOverlay = document.getElementById('settingsOverlay');
    const closeSettingsOverlay = document.getElementById('closeSettingsOverlay');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const geminiApiKeyInput = document.getElementById('geminiApiKeyInput');
    const chatModeTag = document.getElementById('chatModeTag');

    let geminiApiKey = localStorage.getItem('atlas_gemini_key') || '';
    if (geminiApiKey) {
      chatModeTag.textContent = 'Gemini 2.5';
      chatModeTag.className = 'text-[9px] uppercase px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono';
    }

    function toggleChatDrawer() {
      const isOpen = chatDrawer.classList.contains('opacity-100');
      if (isOpen) {
        chatDrawer.classList.remove('opacity-100', 'translate-y-0', 'pointer-events-auto');
        chatDrawer.classList.add('opacity-0', 'translate-y-4', 'pointer-events-none');
      } else {
        chatDrawer.classList.remove('opacity-0', 'translate-y-4', 'pointer-events-none');
        chatDrawer.classList.add('opacity-100', 'translate-y-0', 'pointer-events-auto');
        setTimeout(() => chatInput.focus(), 150);
      }
    }

    floatingChatBtn.addEventListener('click', toggleChatDrawer);
    headerChatToggle.addEventListener('click', toggleChatDrawer);
    chatCloseBtn.addEventListener('click', toggleChatDrawer);

    window.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleChatDrawer();
      }
    });

    chatSettingsBtn.addEventListener('click', () => {
      geminiApiKeyInput.value = geminiApiKey;
      settingsOverlay.classList.remove('hidden');
      settingsOverlay.classList.add('flex');
    });

    closeSettingsOverlay.addEventListener('click', () => {
      settingsOverlay.classList.add('hidden');
      settingsOverlay.classList.remove('flex');
    });

    saveSettingsBtn.addEventListener('click', () => {
      geminiApiKey = geminiApiKeyInput.value.trim();
      localStorage.setItem('atlas_gemini_key', geminiApiKey);
      if (geminiApiKey) {
        chatModeTag.textContent = 'Gemini 2.5';
        chatModeTag.className = 'text-[9px] uppercase px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono';
        appendBotMessage('Connected to Google Gemini! Enhanced conversational reasoning is now enabled.');
      } else {
        chatModeTag.textContent = 'Offline Engine';
        chatModeTag.className = 'text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono';
        appendBotMessage('Switched to Built-in Offline Intelligence Engine.');
      }
      settingsOverlay.classList.add('hidden');
      settingsOverlay.classList.remove('flex');
    });

    chatClearBtn.addEventListener('click', () => {
      chatMessages.innerHTML = '';
      appendBotMessage('Conversation cleared. How can I help you explore Culture Atlas?');
    });

    // Preset buttons
    chatMessages.addEventListener('click', e => {
      const preset = e.target.closest('.chat-preset');
      if (preset) {
        handleUserQuery(preset.textContent.trim());
      }
    });

    function appendUserMessage(text) {
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1 items-end';
      div.innerHTML = `
        <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-3 rounded-2xl rounded-tr-sm max-w-[85%] shadow-md">
          ${text}
        </div>
      `;
      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendBotMessage(html, actions = []) {
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1 items-start';

      let actionsHtml = '';
      if (actions.length > 0) {
        actionsHtml = `
          <div class="mt-2.5 flex flex-wrap gap-1.5">
            ${actions.map((act, i) => `
              <button class="chat-act-btn px-2.5 py-1 rounded-full text-[11px] font-semibold flex items-center gap-1 border transition ${act.tier === 'A' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600 hover:bg-emerald-900' : act.tier === 'B' ? 'bg-blue-950/80 text-blue-300 border-blue-600 hover:bg-blue-900' : 'bg-slate-800 text-cyan-300 border-slate-700 hover:bg-slate-700'}" data-act-idx="${i}">
                ${act.icon || '📍'} ${act.label}
              </button>
            `).join('')}
          </div>
        `;
      }

      div.innerHTML = `
        <div class="bg-slate-800/90 border border-slate-700/80 text-slate-200 p-3 rounded-2xl rounded-tl-sm max-w-[90%] leading-relaxed shadow-md">
          ${html}
          ${actionsHtml}
        </div>
      `;

      if (actions.length > 0) {
        div.querySelectorAll('.chat-act-btn').forEach(btn => {
          const idx = parseInt(btn.getAttribute('data-act-idx'), 10);
          btn.addEventListener('click', () => {
            if (actions[idx] && actions[idx].handler) {
              actions[idx].handler();
            }
          });
        });
      }

      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function handleUserQuery(query) {
      appendUserMessage(query);

      // Typing indicator
      const typing = document.createElement('div');
      typing.id = 'typingIndicator';
      typing.className = 'flex gap-1.5 p-2 bg-slate-800/60 rounded-xl w-14';
      typing.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>';
      chatMessages.appendChild(typing);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      if (geminiApiKey) {
        callGemini(query).catch(err => {
          typing.remove();
          runOfflineLogic(query, `*(Gemini error: ${err.message}. Showing offline answer)*<br><br>`);
        });
      } else {
        setTimeout(() => {
          typing.remove();
          runOfflineLogic(query);
        }, 300);
      }
    }

    function runOfflineLogic(query, prefix = '') {
      const q = query.toLowerCase().trim();
      const actions = [];
      let response = '';

      // 1. Specific institution check
      const matchInst = ALL_INSTITUTIONS.find(i => {
        const n = i.name.toLowerCase();
        return q.includes(n) || (n.includes(q) && q.length > 3);
      });

      if (matchInst) {
        response = `
          <p class="font-bold text-white">${matchInst.name} <span class="text-xs ${matchInst.tier === 'A' ? 'text-emerald-400' : matchInst.tier === 'B' ? 'text-blue-400' : 'text-slate-400'}">· ${matchInst.tier === 'A' ? 'Verified' : matchInst.tier === 'B' ? 'One Name to Know' : 'Unverified'}</span></p>
          <p class="text-xs text-cyan-300 mt-0.5">📍 ${matchInst.location} (${matchInst.size === 'L' ? 'Large' : 'Small/Mid'})</p>
          <p class="text-xs text-slate-300 mt-2"><strong>Funding:</strong> ${matchInst.funding}</p>
          ${matchInst.watch ? `<p class="text-xs text-slate-400 mt-1"><strong>Watch Notes:</strong> ${matchInst.watch}</p>` : ''}
        `;
        actions.push({
          label: `Inspect ${matchInst.name}`,
          icon: '🌍',
          tier: matchInst.tier,
          handler: () => {
            viewGlobeBtn.click();
            selectInstitution(matchInst);
          }
        });
        appendBotMessage(prefix + response, actions);
        viewGlobeBtn.click();
        selectInstitution(matchInst);
        return;
      }

      // 2. City or country search
      const geoMatches = ALL_INSTITUTIONS.filter(i => {
        const loc = i.location.toLowerCase();
        return q.includes(loc) || loc.split(',').some(p => q.includes(p.trim().toLowerCase()) && p.trim().length > 2);
      });

      if (geoMatches.length > 0) {
        const cityName = geoMatches[0].location.split(',')[0].trim();
        response = `
          <p class="font-bold text-white">Found ${geoMatches.length} institution${geoMatches.length > 1 ? 's' : ''} in ${cityName}:</p>
          <ul class="mt-1.5 space-y-1 text-slate-300 text-xs">
            ${geoMatches.slice(0, 4).map(i => `
              <li><strong>${i.name}</strong> <span class="${i.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}">(${i.tier === 'A' ? 'Verified' : 'One Name'})</span></li>
            `).join('')}
          </ul>
        `;
        actions.push({
          label: `Fly to ${cityName}`,
          icon: '📍',
          handler: () => {
            viewGlobeBtn.click();
            flyTo(geoMatches[0].lon, geoMatches[0].lat, 1.8);
          }
        });
        geoMatches.slice(0, 2).forEach(inst => {
          actions.push({
            label: inst.name,
            icon: '🏛️',
            tier: inst.tier,
            handler: () => {
              viewGlobeBtn.click();
              selectInstitution(inst);
            }
          });
        });
        appendBotMessage(prefix + response, actions);
        viewGlobeBtn.click();
        flyTo(geoMatches[0].lon, geoMatches[0].lat, 1.6);
        return;
      }

      // 3. Methodology & criteria
      if (q.includes('method') || q.includes('criteria') || q.includes('evaluat') || q.includes('tier')) {
        response = `
          <p class="font-bold text-white">Ethical Funding Methodology:</p>
          <p class="text-xs text-slate-300 mt-1">Institutions are evaluated on their corporate sponsorship records up to late 2026:</p>
          <ul class="mt-1.5 space-y-1 text-slate-300 text-xs">
            <li><strong class="text-emerald-400">Tier A (Verified · 125):</strong> Zero controversy. Endowed, public benefit, or strict ethical gift policies.</li>
            <li><strong class="text-blue-400">Tier B (One Name · 55):</strong> Transparent, but has a corporate partner to note (e.g. fossil finance, defense).</li>
            <li><strong class="text-slate-400">Tier U (Unverified · 17):</strong> Disclosures pending.</li>
          </ul>
          <p class="text-xs text-slate-400 mt-1">Excluded: institutions sponsored by weapons/defense, fossil fuel extraction, tobacco, gambling, or opioids.</p>
        `;
        actions.push({
          label: 'Filter Tier A Only',
          tier: 'A',
          icon: '🟢',
          handler: () => {
            activeTiers = new Set(['A']);
            document.getElementById('tierABtn').classList.remove('opacity-40');
            document.getElementById('tierBBtn').classList.add('opacity-40');
            document.getElementById('tierUBtn').classList.add('opacity-40');
            renderTable();
          }
        });
        appendBotMessage(prefix + response, actions);
        return;
      }

      // 4. Fallback
      response = `
        <p class="font-bold text-white">Culture Atlas Concierge</p>
        <p class="text-xs text-slate-300 mt-1">I can guide you through all 197 cultural institutions. Try asking:</p>
        <ul class="mt-1 space-y-1 text-xs text-cyan-300">
          <li>• "Tell me about ARoS or Te Papa"</li>
          <li>• "What museums are in London or Tokyo?"</li>
          <li>• "Show large Tier A institutions"</li>
        </ul>
      `;
      actions.push({
        label: 'Surprise Me',
        icon: '✨',
        handler: () => {
          const pick = ALL_INSTITUTIONS[Math.floor(Math.random() * ALL_INSTITUTIONS.length)];
          runOfflineLogic(`Tell me about ${pick.name}`);
        }
      });
      appendBotMessage(prefix + response, actions);
    }

    async function callGemini(query) {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiApiKey}`;
      const systemInstruction = `
You are the Culture Atlas AI Concierge.
You guide users exploring 197 globally mapped cultural institutions evaluated on ethical funding transparency.
Tier A = 125 verified clean, Tier B = 55 one name to know, Tier U = 17 unverified.
Data summary: ${JSON.stringify(ALL_INSTITUTIONS.slice(0, 40))}
When mentioning an institution from the list, format its action button as [[SELECT:ExactInstitutionName]].
Keep answers concise, cultured, and insightful.
`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: query }] }],
          systemInstruction: { parts: [{ text: systemInstruction }] },
          generationConfig: { maxOutputTokens: 600, temperature: 0.7 }
        })
      });

      document.getElementById('typingIndicator')?.remove();
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      let text = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response.';

      const actions = [];
      const selRegex = /\\[\\[SELECT:([^\\]]+)\\]\\]/g;
      let m;
      while ((m = selRegex.exec(text)) !== null) {
        const name = m[1].trim();
        const inst = ALL_INSTITUTIONS.find(i => i.name.toLowerCase() === name.toLowerCase());
        if (inst) {
          actions.push({
            label: `Inspect ${inst.name}`,
            icon: '🏛️',
            tier: inst.tier,
            handler: () => {
              viewGlobeBtn.click();
              selectInstitution(inst);
            }
          });
        }
      }
      text = text.replace(selRegex, '');

      appendBotMessage(text.replace(/\\n/g, '<br>'), actions);
    }

    chatSendBtn.addEventListener('click', () => {
      const val = chatInput.value.trim();
      if (val) {
        chatInput.value = '';
        handleUserQuery(val);
      }
    });

    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const val = chatInput.value.trim();
        if (val) {
          chatInput.value = '';
          handleUserQuery(val);
        }
      }
    });

    // Voice recognition
    const voiceBtn = document.getElementById('chatVoiceBtn');
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
      const rec = new SpeechRec();
      rec.onresult = e => {
        const t = e.results[0][0].transcript;
        chatInput.value = t;
        handleUserQuery(t);
      };
      voiceBtn.addEventListener('click', () => {
        try { rec.start(); } catch(e){}
      });
    } else {
      voiceBtn.style.display = 'none';
    }

  </script>
</body>
</html>
'''

# Write to artifact directory for instant viewing and inline embedding
with open('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html', 'w') as f:
    f.write(html_template)

# Also write to app directory
with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/standalone.html', 'w') as f:
    f.write(html_template)

print("Created self-contained Culture Atlas application successfully!")
