import json

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

inst_json = json.dumps(institutions)

widget_html = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    #widgetGlobeCanvas {
      cursor: grab;
      touch-action: none;
    }
    #widgetGlobeCanvas.dragging {
      cursor: grabbing;
    }
    .custom-scrollbar::-webkit-scrollbar {
      width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
    }
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-2 selection:bg-cyan-500 selection:text-white">
  
  <div class="bg-slate-950 text-slate-100 border border-cyan-500/30 rounded-2xl p-3 shadow-2xl overflow-hidden flex flex-col gap-2.5 max-h-[480px]">
    
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-800 pb-2 px-1">
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#00ff87] animate-pulse"></span>
        <h2 class="text-xs font-bold tracking-wider text-white flex items-center gap-1.5 uppercase">
          Culture Atlas <span class="text-cyan-400 font-normal">AI Concierge</span>
        </h2>
      </div>
      <div class="flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
        <span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
          197 Institutions Mapped
        </span>
      </div>
    </div>

    <!-- Main 2-Column Interface -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 flex-1 min-h-[340px] overflow-hidden">
      
      <!-- Left Column: Interactive 3D Canvas Globe -->
      <div class="sm:col-span-5 bg-slate-900/80 rounded-xl border border-slate-800 p-2 flex flex-col items-center justify-center relative overflow-hidden">
        <canvas id="widgetGlobeCanvas" width="220" height="220" class="max-w-full"></canvas>
        
        <div class="absolute bottom-2 left-2 flex items-center gap-1 text-[10px] text-slate-400 font-mono">
          <button id="widgetSpinBtn" class="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition">↻ Spin</button>
          <button id="widgetResetBtn" class="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition">◎ Center</button>
        </div>

        <div class="absolute top-2 right-2 text-[10px] font-mono text-cyan-400 bg-slate-950/70 px-1.5 py-0.5 rounded border border-slate-800" id="globeHoverLabel">
          Drag to rotate
        </div>
      </div>

      <!-- Right Column: Conversational Concierge & Dossier -->
      <div class="sm:col-span-7 bg-slate-900/60 rounded-xl border border-slate-800 flex flex-col overflow-hidden">
        
        <!-- Tab Bar -->
        <div class="flex items-center justify-between bg-slate-950/60 border-b border-slate-800 px-3 py-1.5 text-[11px]">
          <div class="flex gap-2">
            <button id="tabChatBtn" class="font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5">Concierge Chat</button>
            <button id="tabDossierBtn" class="font-medium text-slate-400 hover:text-white pb-0.5">Dossier Card</button>
          </div>
          <span class="text-[10px] text-slate-500">Offline Instant Engine</span>
        </div>

        <!-- Chat View -->
        <div id="widgetChatView" class="flex-1 flex flex-col overflow-hidden p-2">
          
          <!-- Message history -->
          <div id="widgetChatHistory" class="flex-1 overflow-y-auto custom-scrollbar space-y-2 text-xs pr-1">
            <div class="bg-slate-800/80 p-2.5 rounded-xl text-slate-300 leading-relaxed border border-slate-700/60">
              <p class="font-semibold text-white mb-1">Welcome! How can I assist your exploration?</p>
              <p class="text-[11px] text-slate-400">Click a preset below or type any museum or city to fly the 3D globe directly there:</p>
              <div class="mt-2 flex flex-wrap gap-1">
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-emerald-950 border border-slate-700 hover:border-emerald-500/50 text-[10.5px] text-slate-300 hover:text-white transition">
                  🟢 Verified in Tokyo
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-emerald-950 border border-slate-700 hover:border-emerald-500/50 text-[10.5px] text-slate-300 hover:text-white transition">
                  🏛️ Te Papa Dossier
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-emerald-950 border border-slate-700 hover:border-emerald-500/50 text-[10.5px] text-slate-300 hover:text-white transition">
                  ⚖️ Ethical Criteria
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-emerald-950 border border-slate-700 hover:border-emerald-500/50 text-[10.5px] text-slate-300 hover:text-white transition">
                  ✨ Surprise Me
                </button>
              </div>
            </div>
          </div>

          <!-- Input bar -->
          <div class="mt-2 flex items-center gap-1.5 pt-1.5 border-t border-slate-800">
            <input type="text" id="widgetChatInput" placeholder="Ask: 'Museums in London' or 'Audain Art Museum'..." class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400" />
            <button id="widgetChatSend" class="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow transition">
              Ask
            </button>
          </div>

        </div>

        <!-- Dossier View -->
        <div id="widgetDossierView" class="hidden flex-1 overflow-y-auto custom-scrollbar p-3 text-xs space-y-2.5">
          <div id="widgetDossierEmpty" class="text-center py-10 text-slate-500">
            <p class="text-xl mb-1">🏛️</p>
            <p>Click any dot on the 3D globe to inspect its ethical funding dossier.</p>
          </div>
          <div id="widgetDossierBody" class="hidden space-y-2">
            <div class="flex items-center justify-between">
              <h3 id="dossierName" class="font-bold text-white text-sm"></h3>
              <span id="dossierTier" class="text-[10px] px-2 py-0.5 rounded-full border"></span>
            </div>
            <p id="dossierLoc" class="text-[11px] text-cyan-400"></p>
            <div class="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block mb-0.5">Funding</span>
              <p id="dossierFunding" class="text-[11px] text-slate-300 leading-relaxed"></p>
            </div>
            <div id="dossierWatchBox" class="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block mb-0.5">Watch Notes</span>
              <p id="dossierWatch" class="text-[11px] text-slate-300 leading-relaxed"></p>
            </div>
            <div id="dossierSources" class="pt-1 text-[11px]"></div>
          </div>
        </div>

      </div>

    </div>

  </div>

  <script>
    const DATA = ''' + inst_json + ''';

    // 3D Globe Projection
    const canvas = document.getElementById('widgetGlobeCanvas');
    const ctx = canvas.getContext('2d');
    let rotLon = 0;
    let rotLat = 20;
    let targetRotLon = 0;
    let targetRotLat = 20;
    let isFlying = false;
    let flightProgress = 0;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let hoveredInst = null;
    let selectedInst = null;

    function project(lon, lat, r, cx, cy) {
      const rad = Math.PI / 180;
      const lambda = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda);
      if (cosC < 0) return null;

      const x = cx + r * Math.cos(phi) * Math.sin(lambda);
      const y = cy - r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda));
      return { x, y, depth: cosC };
    }

    function render() {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const r = Math.min(w, h) * 0.44;

      ctx.clearRect(0, 0, w, h);

      if (isFlying) {
        flightProgress += 0.05;
        if (flightProgress >= 1) {
          flightProgress = 1;
          isFlying = false;
        }
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      } else if (isAutoSpinning && !isDragging) {
        rotLon = (rotLon + 0.3) % 360;
      }

      // Outer glow
      const glow = ctx.createRadialGradient(cx, cy, r * 0.8, cx, cy, r * 1.25);
      glow.addColorStop(0, 'rgba(0, 242, 254, 0.25)');
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, r * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Sphere base
      const ocean = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
      ocean.addColorStop(0, '#002b5c');
      ocean.addColorStop(0.7, '#00142e');
      ocean.addColorStop(1, '#000714');
      ctx.fillStyle = ocean;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Graticule
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();
      ctx.strokeStyle = 'rgba(0, 255, 135, 0.15)';
      ctx.lineWidth = 0.8;
      [-45, 0, 45].forEach(lat => {
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 8) {
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      });
      for (let lon = -180; lon < 180; lon += 45) {
        ctx.beginPath();
        let first = true;
        for (let lat = -80; lat <= 80; lat += 6) {
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      }
      ctx.restore();

      // Rim
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.45)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Dots
      DATA.forEach(inst => {
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (!pt) return;

        const isSel = selectedInst && selectedInst.name === inst.name;
        const isHov = hoveredInst && hoveredInst.name === inst.name;
        const dotR = (isSel ? 6 : isHov ? 5 : inst.size === 'L' ? 4 : 2.5) * Math.min(1.5, Math.max(0.7, pt.depth));

        let col = '#24a148';
        if (inst.tier === 'B') col = '#4589ff';
        if (inst.tier === 'U') col = '#8d8d8d';

        if (isSel) {
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 2.2, 0, Math.PI * 2);
          ctx.strokeStyle = '#00ff87';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
      });

      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);

    function flyTo(lon, lat) {
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }

    function showDossier(inst) {
      selectedInst = inst;
      flyTo(inst.lon, inst.lat);

      document.getElementById('dossierName').textContent = inst.name;
      document.getElementById('dossierLoc').textContent = `📍 ${inst.location} (${inst.size === 'L' ? 'Large' : 'Small/Mid'})`;
      
      const tierBadge = document.getElementById('dossierTier');
      tierBadge.textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      tierBadge.className = `text-[10px] px-2 py-0.5 rounded-full border ${inst.tier === 'A' ? 'bg-emerald-950 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-600'}`;

      document.getElementById('dossierFunding').textContent = inst.funding;

      const watchBox = document.getElementById('dossierWatchBox');
      if (inst.watch) {
        document.getElementById('dossierWatch').textContent = inst.watch;
        watchBox.classList.remove('hidden');
      } else {
        watchBox.classList.add('hidden');
      }

      const sourcesDiv = document.getElementById('dossierSources');
      sourcesDiv.innerHTML = (inst.sources || []).map(u => {
        let domain = u;
        try { domain = new URL(u).hostname.replace(/^www\\./, ''); } catch(e){}
        return `<a href="${u}" target="_blank" class="inline-block mr-2 text-cyan-400 hover:underline">↗ ${domain}</a>`;
      }).join('');

      document.getElementById('widgetDossierEmpty').classList.add('hidden');
      document.getElementById('widgetDossierBody').classList.remove('hidden');
      
      // Switch tab to dossier
      tabDossierBtn.click();
    }

    // Pointer events
    canvas.addEventListener('pointerdown', e => {
      isDragging = true;
      canvas.classList.add('dragging');
      lastX = e.clientX;
      lastY = e.clientY;
      isFlying = false;
      isAutoSpinning = false;
    });

    window.addEventListener('pointermove', e => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      if (isDragging) {
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;

        rotLon = (rotLon - dx * 0.6) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.6));
      } else {
        // Hit test
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const r = Math.min(canvas.width, canvas.height) * 0.44;

        let hit = null;
        for (let i = 0; i < DATA.length; i++) {
          const inst = DATA[i];
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 9) {
            hit = inst;
            break;
          }
        }
        hoveredInst = hit;
        const lbl = document.getElementById('globeHoverLabel');
        if (hit) {
          lbl.textContent = hit.name;
          lbl.className = 'absolute top-2 right-2 text-[10px] font-mono text-emerald-400 bg-slate-950/90 px-1.5 py-0.5 rounded border border-emerald-600/50 shadow';
        } else {
          lbl.textContent = 'Drag to rotate';
          lbl.className = 'absolute top-2 right-2 text-[10px] font-mono text-cyan-400 bg-slate-950/70 px-1.5 py-0.5 rounded border border-slate-800';
        }
      }
    });

    window.addEventListener('pointerup', () => {
      if (isDragging) {
        isDragging = false;
        canvas.classList.remove('dragging');
      }
    });

    canvas.addEventListener('click', () => {
      if (hoveredInst) {
        showDossier(hoveredInst);
      }
    });

    document.getElementById('widgetSpinBtn').addEventListener('click', () => {
      isAutoSpinning = !isAutoSpinning;
    });
    document.getElementById('widgetResetBtn').addEventListener('click', () => {
      flyTo(0, 20);
    });

    // Tabs
    const tabChatBtn = document.getElementById('tabChatBtn');
    const tabDossierBtn = document.getElementById('tabDossierBtn');
    const widgetChatView = document.getElementById('widgetChatView');
    const widgetDossierView = document.getElementById('widgetDossierView');

    tabChatBtn.addEventListener('click', () => {
      tabChatBtn.className = 'font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5';
      tabDossierBtn.className = 'font-medium text-slate-400 hover:text-white pb-0.5';
      widgetChatView.classList.remove('hidden');
      widgetDossierView.classList.add('hidden');
    });

    tabDossierBtn.addEventListener('click', () => {
      tabDossierBtn.className = 'font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5';
      tabChatBtn.className = 'font-medium text-slate-400 hover:text-white pb-0.5';
      widgetDossierView.classList.remove('hidden');
      widgetChatView.classList.add('hidden');
    });

    // Chat processing
    const chatHistory = document.getElementById('widgetChatHistory');
    const chatInput = document.getElementById('widgetChatInput');
    const chatSend = document.getElementById('widgetChatSend');

    function appendChat(role, text, actions = []) {
      const div = document.createElement('div');
      div.className = role === 'user' ? 'flex justify-end' : 'flex justify-start';

      let actionsHtml = '';
      if (actions.length > 0) {
        actionsHtml = `<div class="mt-2 flex flex-wrap gap-1">` +
          actions.map((act, i) => `
            <button class="widget-act px-2 py-0.5 rounded text-[10px] font-semibold border ${act.tier === 'A' ? 'bg-emerald-950 text-emerald-300 border-emerald-600' : 'bg-slate-900 text-cyan-300 border-slate-700'} hover:scale-105 transition" data-idx="${i}">
              ${act.label}
            </button>
          `).join('') + `</div>`;
      }

      div.innerHTML = `
        <div class="${role === 'user' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-200 border border-slate-700'} p-2.5 rounded-xl max-w-[88%] text-[11.5px] leading-relaxed shadow">
          ${text}
          ${actionsHtml}
        </div>
      `;

      if (actions.length > 0) {
        div.querySelectorAll('.widget-act').forEach(btn => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          btn.addEventListener('click', () => actions[idx].handler());
        });
      }

      chatHistory.appendChild(div);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function processQuery(query) {
      appendChat('user', query);
      const q = query.toLowerCase().trim();

      // Check specific institution
      const match = DATA.find(i => q.includes(i.name.toLowerCase()) || (i.name.toLowerCase().includes(q) && q.length > 3));
      if (match) {
        appendChat('bot', `
          <strong>${match.name}</strong> · <span class="${match.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}">${match.tier === 'A' ? 'Verified' : 'One Name'}</span><br>
          📍 ${match.location}<br>
          <span class="text-slate-300">${match.funding}</span>
        `, [{
          label: `📍 Inspect on Globe`,
          tier: match.tier,
          handler: () => showDossier(match)
        }]);
        showDossier(match);
        return;
      }

      // Check city
      const geo = DATA.filter(i => i.location.toLowerCase().includes(q) || q.includes(i.location.split(',')[0].toLowerCase()));
      if (geo.length > 0) {
        const city = geo[0].location.split(',')[0];
        appendChat('bot', `
          Found <strong>${geo.length}</strong> institutions in <strong>${city}</strong>:<br>
          ${geo.slice(0, 3).map(i => `• ${i.name} (${i.tier === 'A' ? 'Verified' : 'One Name'})`).join('<br>')}
        `, [{
          label: `Fly to ${city}`,
          handler: () => flyTo(geo[0].lon, geo[0].lat)
        }, {
          label: `View ${geo[0].name}`,
          tier: geo[0].tier,
          handler: () => showDossier(geo[0])
        }]);
        flyTo(geo[0].lon, geo[0].lat);
        return;
      }

      // Criteria / methodology
      if (q.includes('criter') || q.includes('method') || q.includes('tier') || q.includes('ethic')) {
        appendChat('bot', `
          <strong>Culture Atlas Screening Criteria:</strong><br>
          • <strong>Tier A (Verified · 125):</strong> Zero controversial underwriters (fossil fuel, arms, opioids, tobacco). Public or endowed.<br>
          • <strong>Tier B (One Name · 55):</strong> Corporate sponsor to note (e.g. fossil-finance banks).<br>
          • <strong>Tier U (17):</strong> Disclosures pending.
        `);
        return;
      }

      // Surprise me
      if (q.includes('surprise') || q.includes('random') || q.includes('recommend')) {
        const pick = DATA[Math.floor(Math.random() * DATA.length)];
        appendChat('bot', `
          ✨ <strong>${pick.name}</strong> (${pick.location})<br>
          ${pick.funding}
        `, [{
          label: `📍 Inspect`,
          tier: pick.tier,
          handler: () => showDossier(pick)
        }]);
        showDossier(pick);
        return;
      }

      // Default fallback
      appendChat('bot', `
        Ask about any museum or city (e.g., <em>"Te Papa"</em>, <em>"Tokyo"</em>, <em>"Berlin"</em>, or <em>"Large verified spaces"</em>).
      `);
    }

    chatSend.addEventListener('click', () => {
      const v = chatInput.value.trim();
      if (v) {
        chatInput.value = '';
        processQuery(v);
      }
    });

    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const v = chatInput.value.trim();
        if (v) {
          chatInput.value = '';
          processQuery(v);
        }
      }
    });

    document.querySelectorAll('.widget-preset').forEach(btn => {
      btn.addEventListener('click', () => {
        processQuery(btn.textContent.trim());
      });
    });

  </script>
</body>
</html>
'''

with open('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html', 'w') as f:
    f.write(widget_html)

print("Generated concierge_widget.html successfully!")
