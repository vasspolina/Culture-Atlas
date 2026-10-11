#!/usr/bin/env python3
"""
apply_code_html_mobile_design.py
Applies the exact mobile design from code.html and media_1791625755099_5e95dfd6.png
to build_conversational_atlas.py while preserving desktop layout, automated tests,
and universal PP Museum typography.
"""

import os
import sys

def main():
    path = "build_conversational_atlas.py"
    # Always start from fresh backup
    if os.path.exists("build_conversational_atlas.py.bak"):
        with open("build_conversational_atlas.py.bak", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

    # 1. Update tailwind.config with atlas colors and box shadows
    target_font_family = "sans: ['\"PP Museum\"', '\"PP Telegraf\"', '\"PP Telegraph\"', 'sans-serif'],"
    replacement_colors = """sans: ['\"PP Museum\"', '\"PP Telegraf\"', '\"PP Telegraph\"', 'sans-serif'],
            mono: ['\"PP Museum\"', '\"PP Telegraf\"', '\"PP Telegraph\"', 'sans-serif'],
          }},
          colors: {{
            atlas: {{
              black: '#05070B',
              card: 'rgba(13, 20, 31, 0.78)',
              border: 'rgba(34, 211, 238, 0.18)',
              teal: '#14b8a6',
              emerald: '#10b981',
              cyan: '#06b6d4',
              gossip: '#f59e0b',
              glow: 'rgba(16, 185, 129, 0.25)'
            }}
          }},
          boxShadow: {{
            'glow-teal': '0 0 25px -3px rgba(20, 184, 166, 0.4)',
            'glow-node': '0 0 12px 2px rgba(45, 212, 191, 0.65)',
            'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.6)'
          """
    content = content.replace("mono: ['\"PP Museum\"', '\"PP Telegraf\"', '\"PP Telegraph\"', 'sans-serif'],", "")
    content = content.replace(target_font_family, replacement_colors, 1)
    print("Updated tailwind.config with atlas colors and shadows!")

    # 2. Add Mobile CSS Rules to <style>
    mobile_css = """
    /* iOS notch padding support */
    .pb-safe {
      padding-bottom: env(safe-area-inset-bottom, 16px);
    }
    .pt-safe {
      padding-top: env(safe-area-inset-top, 44px);
    }

    /* Subtle Starfield & Globe Glow */
    .space-background {
      background-color: #05070B;
      background-image: 
        radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 80px 140px, #38bdf8, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 220px 70px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.2px 1.2px at 320px 220px, #a7f3d0, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 150px 310px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 280px 420px, #67e8f9, rgba(0,0,0,0)),
        radial-gradient(circle at 50% 38%, rgba(13, 148, 136, 0.15) 0%, rgba(5, 7, 11, 0.95) 75%);
      background-repeat: repeat;
      background-size: 350px 350px, 400px 400px, 300px 300px, 450px 450px, 280px 280px, 320px 320px, 100% 100%;
    }

    /* Hide scrollbars for pill bars */
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }

    /* Globe Pulse Rings */
    @keyframes pulseRing {
      0% { transform: scale(0.96); opacity: 0.8; }
      50% { transform: scale(1.03); opacity: 0.4; }
      100% { transform: scale(0.96); opacity: 0.8; }
    }
    .globe-ring {
      animation: pulseRing 5s ease-in-out infinite;
    }
    .shadow-glow-teal {
      box-shadow: 0 0 25px -3px rgba(20, 184, 166, 0.4) !important;
    }
    .shadow-glow-node {
      box-shadow: 0 0 12px 2px rgba(45, 212, 191, 0.65) !important;
    }
    .shadow-glass {
      box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6) !important;
    }
    """
    mobile_css_escaped = mobile_css.replace("{", "{{").replace("}", "}}")
    insert_marker = "/* Unified Split-Screen Architecture: Desktop Vertical Half-and-Half / Mobile Stacked */"
    content = content.replace(insert_marker, mobile_css_escaped + "\n    " + insert_marker, 1)

    # 3. Add space-background to body
    content = content.replace('<body class="bg-black text-slate-100', '<body class="bg-black text-slate-100 space-background')

    # 4. Add Mobile Top Bar above Desktop Header
    desktop_header_tag = '<header class="w-full h-14 bg-black border-b border-[#1c1c1f]'
    new_desktop_header_tag = '<header class="hidden md:flex w-full h-14 bg-black border-b border-[#1c1c1f]'

    mobile_top_header = """  <!-- ========================================================= -->
  <!-- 📱 MOBILE TOP BAR (Matches code.html & media_1791625755099_5e95dfd6.png) -->
  <!-- ========================================================= -->
  <header class="pt-safe px-3.5 pb-2.5 z-40 bg-[#05070B]/80 backdrop-blur-md border-b border-cyan-950/40 flex md:hidden items-center justify-between gap-2 shrink-0 select-none">
    <!-- Left: Logo & Space Count Pill -->
    <button id="mobileTopBrandBtn" type="button" class="flex items-center space-x-2 text-left bg-transparent border-0 p-0 cursor-pointer focus:outline-none" onclick="if (typeof window.resetGlobeZoom === 'function') window.resetGlobeZoom();" title="Reset Globe View">
      <div class="relative flex items-center justify-center w-7 h-7 rounded-full bg-emerald-950/60 border border-emerald-400/80 shadow-glow-teal shrink-0">
        <span class="w-3.5 h-3.5 rounded-full border-2 border-emerald-400"></span>
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-semibold tracking-tight text-white flex items-center gap-1.5 leading-none">
          Culture Atlas
        </span>
        <span class="inline-flex items-center mt-1 text-[10px] font-medium text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded-full border border-emerald-800/60 leading-none">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1"></span>
          444 Clean spaces
        </span>
      </div>
    </button>
    <!-- Right: Action Switchers & Controls -->
    <div class="flex items-center space-x-1.5 shrink-0">
      <!-- Yellow Gossip Mode Badge Button -->
      <button class="flex items-center space-x-1 px-2 py-1 rounded-full text-[11px] font-medium border border-amber-500/50 bg-amber-950/30 text-amber-300 transition-all active:scale-95 hover:bg-amber-900/40 cursor-pointer" data-purpose="toggle-gossip-mode" id="gossip-mode-btn" onclick="window.toggleGossipMode();">
        <span class="w-2 h-2 rounded-full bg-amber-400"></span>
        <span>Gossip Mode</span>
      </button>
      <!-- New Chat / Reset Quick Actions -->
      <button aria-label="New chat or reset" class="px-2 py-1 rounded-full text-[11px] text-slate-400 hover:text-slate-200 border border-slate-800 bg-slate-900/50 active:scale-95 transition cursor-pointer" id="reset-state-btn" onclick="window.resetToNewChat(); if (typeof window.setActiveMobileTab === 'function') window.setActiveMobileTab('chat');">
        + Chat
      </button>
    </div>
  </header>

"""
    content = content.replace(desktop_header_tag, mobile_top_header + "  " + new_desktop_header_tag, 1)

    # 5. Insert Floating Filter Category Chips Bar & Celestial Rings inside globeViewport
    globe_top_html = """
      <!-- BEGIN: FloatingFilterCategoryChips (Mobile Bar matching code.html & media_1791625755099_5e95dfd6.png) -->
      <section class="absolute top-0 inset-x-0 z-20 pt-2 px-3 flex md:hidden items-center justify-between pointer-events-auto bg-[#05070B]/80 backdrop-blur-sm" data-purpose="map-filter-chips" id="mobileFilterChipsSection">
        <div class="flex items-center space-x-1.5 overflow-x-auto no-scrollbar py-1 text-[11px] w-full">
          <button type="button" onclick="window.openFiscalAnalyticsHUD();" class="px-2.5 py-1 rounded-full font-medium bg-teal-950/90 text-teal-300 border border-teal-500/60 whitespace-nowrap shadow-sm cursor-pointer">Fiscal</button>
          <button type="button" onclick="window.openResistanceTimelineModal();" class="px-2.5 py-1 rounded-full font-medium bg-purple-950/70 text-purple-300 border border-purple-800/60 whitespace-nowrap cursor-pointer">Victories</button>
          <button type="button" onclick="window.openStatutoryFilingsModal();" class="px-2.5 py-1 rounded-full font-medium bg-cyan-950/70 text-cyan-300 border border-cyan-500/50 whitespace-nowrap cursor-pointer">990s</button>
          <button type="button" onclick="window.openTrusteeConflictNetworkModal();" class="px-2.5 py-1 rounded-full font-medium bg-cyan-900/40 text-cyan-200/90 border border-cyan-700 whitespace-nowrap cursor-pointer">Boards</button>
          <button type="button" onclick="window.openCuratorialItineraryModal();" class="px-2.5 py-1 rounded-full font-medium bg-rose-950/60 text-rose-300 border border-rose-800/40 whitespace-nowrap cursor-pointer">Crawls</button>
          <button type="button" onclick="window.toggleRailCorridors(event);" class="px-2.5 py-1 rounded-full font-medium bg-slate-900 text-slate-300 border border-slate-700 whitespace-nowrap cursor-pointer">Rail</button>
        </div>
      </section>
      <!-- END: FloatingFilterCategoryChips -->

      <!-- Outer Celestial Orbit Lines (Mobile Matching code.html) -->
      <div class="absolute w-[330px] h-[330px] rounded-full border border-cyan-500/10 globe-ring pointer-events-none md:hidden"></div>
      <div class="absolute w-[300px] h-[300px] rounded-full border border-teal-500/20 pointer-events-none md:hidden"></div>
"""
    content = content.replace('<canvas id="globeCanvas" class="w-full h-full block cursor-grab"></canvas>',
                              '<canvas id="globeCanvas" class="w-full h-full block cursor-grab"></canvas>' + globe_top_html, 1)

    # 6. Insert Space Detail Card Bottom Sheet (#dossier-bottom-sheet) and Curator Chat Drawer (#curator-chat-drawer)
    mobile_cards_html = """
      <!-- BEGIN: SpaceDetailCardBottomSheet (Mobile Sliding Sheet Matching code.html & media_1791625755099_5e95dfd6.png) -->
      <section class="absolute bottom-0 inset-x-0 z-30 max-h-[52vh] flex md:hidden flex-col bg-slate-950/90 border-t border-cyan-500/30 rounded-t-2xl backdrop-blur-xl shadow-glass transition-all duration-300" data-purpose="space-dossier-sheet" id="dossier-bottom-sheet">
        <!-- Grab Handle & Header Bar -->
        <div class="pt-2 pb-1 px-4 flex flex-col items-center cursor-pointer" id="sheet-drag-handle">
          <div class="w-10 h-1 rounded-full bg-slate-700/80 mb-2"></div>
        </div>
        <div class="px-4 pb-2 flex items-start justify-between border-b border-slate-800/60">
          <div>
            <div class="flex items-center space-x-2">
              <h2 class="text-base font-bold text-white tracking-tight" id="dossier-sheet-name">Green Papaya Art Projects</h2>
              <span class="inline-flex items-center px-1.5 py-0.2 text-[10px] font-semibold text-emerald-300 bg-emerald-950 border border-emerald-600 rounded" id="dossier-sheet-tier">
                Verified
              </span>
            </div>
            <p class="text-xs text-slate-400 font-mono mt-0.5" id="dossier-sheet-meta">Quezon City / Manila, Philippines · Artist-Run</p>
          </div>
          <button aria-label="Minimize space details" class="p-1 rounded-full text-slate-400 hover:text-white bg-slate-800/60 border border-slate-700 text-xs cursor-pointer" id="close-sheet-btn">
            ✕
          </button>
        </div>
        <!-- Mode Toggle Tabs (Verified Info vs Gossip Mode) -->
        <div class="px-4 pt-2.5 flex space-x-2">
          <button id="dossier-tab-info" type="button" class="flex-1 py-1 text-xs font-semibold rounded-md bg-teal-900/90 text-teal-200 border border-teal-300 text-center shadow-inner cursor-pointer">Verified Info</button>
          <button id="dossier-tab-gossip" type="button" class="flex-1 py-1 text-xs font-semibold rounded-md bg-slate-900/90 text-amber-300 border border-amber-500/50 text-center hover:bg-amber-950/40 cursor-pointer">Yellow Gossip Mode</button>
        </div>
        <!-- Scrollable Card Body Details -->
        <div class="overflow-y-auto px-4 py-3 space-y-3 text-xs leading-relaxed no-scrollbar pb-6" id="dossier-sheet-scrollable-body">
          <!-- Verified Pane -->
          <div id="dossier-sheet-verified-pane" class="space-y-3">
            <!-- Financial Metrics & Budget Badge -->
            <div class="p-2.5 rounded-lg bg-slate-900/80 border border-cyan-900/40 space-y-2">
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Budget Band</span>
                  <span class="font-bold text-slate-100 text-xs" id="dossier-sheet-budget-val">€250K – €850K Grassroots Budget</span>
                </div>
                <span class="px-2 py-0.5 text-[10px] font-medium text-cyan-300 bg-cyan-950 border border-cyan-700 rounded-full" id="dossier-sheet-budget-badge">
                  Lean Non-Profit
                </span>
              </div>
              <!-- Funding breakdown pills -->
              <div class="grid grid-cols-4 gap-1 pt-1 font-mono text-[10px] text-center" id="dossier-sheet-pills">
                <div class="p-1 rounded bg-emerald-950/70 border border-emerald-800/60 text-emerald-300 font-semibold" id="dossier-sheet-pill-public">
                  58% Public
                </div>
                <div class="p-1 rounded bg-purple-950/70 border border-purple-800/60 text-purple-300" id="dossier-sheet-pill-grants">
                  14% Grants
                </div>
                <div class="p-1 rounded bg-cyan-950/70 border border-cyan-800/60 text-cyan-300" id="dossier-sheet-pill-earned">
                  28% Earned
                </div>
                <div class="p-1 rounded bg-amber-950/70 border border-amber-800/60 text-amber-300 font-semibold" id="dossier-sheet-pill-ratio">
                  84% Ratio
                </div>
              </div>
              <p class="text-[11px] text-slate-300 pt-1">
                <strong class="text-teal-400">Funding Source:</strong> <span id="dossier-sheet-funding-text">Collective self-funding, Arts Collaboratory, independent foundations. 100% free of corporate defense/oil capture.</span>
              </p>
              <p class="text-[11px] text-slate-400">
                <strong class="text-slate-300">Access:</strong> <span id="dossier-sheet-access-text">Nomadic research &amp; residency; free admission.</span>
              </p>
            </div>
            <!-- Current Exhibition Box -->
            <div class="p-2.5 rounded-lg bg-teal-950/20 border border-emerald-500/30 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[10px] uppercase font-mono tracking-wider text-emerald-400 font-bold">Current Exhibition</span>
                <span class="text-[9px] bg-emerald-900 text-emerald-200 border border-emerald-500 px-1.5 py-0.2 rounded font-semibold">Now On View</span>
              </div>
              <p class="font-bold text-slate-100 text-xs" id="dossier-sheet-exhibit-title">Featured Exhibition: In Focus with Green Papaya</p>
              <p class="text-[11px] text-slate-300" id="dossier-sheet-exhibit-curator">Green Papaya Curatorial Cohort &amp; Guest Artists · On View Autumn 2026 – Spring 2027</p>
              <div class="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px]">
                <span class="text-slate-400 font-mono" id="dossier-sheet-exhibit-vernissage">Vernissage: Fri, Oct 23 (18:00–21:30)</span>
                <span class="text-emerald-400 font-semibold cursor-pointer" id="dossier-sheet-exhibit-rsvp">Free / RSVP →</span>
              </div>
            </div>
            <!-- Action Buttons Bar -->
            <div class="grid grid-cols-2 gap-2 pt-1">
              <button id="dossier-sheet-audit-btn" type="button" class="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-teal-900/90 hover:bg-teal-950 text-teal-200 font-bold text-xs border border-teal-300 shadow-glow-teal active:scale-95 transition cursor-pointer">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                <span>Audit Dossier</span>
              </button>
              <button id="dossier-sheet-plan-btn" type="button" class="flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-cyan-950/70 border border-cyan-400 text-cyan-300 font-medium text-xs hover:bg-cyan-950 active:scale-95 transition cursor-pointer">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
                <span>Plan Visit in Chat</span>
              </button>
            </div>
            <!-- Secondary Link Row -->
            <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1 px-1">
              <a id="dossier-sheet-link-web" class="hover:text-cyan-300 flex items-center space-x-1 cursor-pointer" href="#" target="_blank" rel="noopener noreferrer">
                <span>🌐 website</span>
              </a>
              <button id="dossier-sheet-link-3d" type="button" class="hover:text-cyan-300 flex items-center space-x-1 cursor-pointer bg-transparent border-0 text-slate-400 p-0 text-[11px]">
                <span>📍 Google 3D</span>
              </button>
              <button id="dossier-sheet-link-photos" type="button" class="hover:text-cyan-300 flex items-center space-x-1 cursor-pointer bg-transparent border-0 text-slate-400 p-0 text-[11px]">
                <span>🖼️ Archive Photos</span>
              </button>
            </div>
          </div>
          <!-- Gossip Pane -->
          <div id="dossier-sheet-gossip-pane" class="hidden space-y-2.5">
            <div class="p-2.5 rounded-lg bg-[#181404] border border-amber-500/50 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-amber-400 uppercase tracking-wider block">Field Intel &amp; Whispers</span>
                <span class="px-2 py-0.5 text-[10px] font-medium text-amber-300 bg-amber-950 border border-amber-600 rounded-full" id="dossier-sheet-gossip-badge">Documented</span>
              </div>
              <p id="dossier-sheet-gossip-headline" class="text-xs font-bold text-amber-200 leading-snug">Union organizing and artist fee disputes surface during biennial planning</p>
              <div class="p-2 rounded bg-black/40 border border-amber-900/40 text-[11px] text-slate-300 space-y-1">
                <div class="flex items-center gap-1 text-[10px] font-mono text-amber-400"><span>r/art Community:</span></div>
                <p id="dossier-sheet-gossip-reddit">Staff organizing update: negotiations stall over independent curator compensation.</p>
              </div>
              <div class="p-2 rounded bg-black/40 border border-amber-900/40 text-[11px] text-slate-300 space-y-1">
                <div class="flex items-center gap-1 text-[10px] font-mono text-sky-400"><span>X / Twitter:</span></div>
                <p id="dossier-sheet-gossip-twitter">Open letter signed by 45 exhibiting artists demanding W.A.G.E. certified honorariums.</p>
              </div>
              <button id="dossier-sheet-full-gossip-btn" type="button" class="w-full py-1.5 px-3 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-semibold text-xs flex items-center justify-center gap-1.5 transition cursor-pointer shadow-md">
                <span>Full Dossier &amp; Leaks →</span>
              </button>
            </div>
          </div>
        </div>
      </section>
      <!-- END: SpaceDetailCardBottomSheet -->

      <!-- BEGIN: CuratorChatDrawer (Mobile Collapsible AI Chat Panel Matching code.html) -->
      <section class="hidden absolute inset-0 z-30 flex-1 bg-slate-950/95 flex md:hidden flex-col overflow-hidden border-t border-cyan-900/50 backdrop-blur-2xl" data-purpose="ai-curator-chat" id="curator-chat-drawer">
        <!-- AI Thinking / Status Header -->
        <div class="px-4 py-2 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/60 shrink-0">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span class="text-[11px] text-slate-300 font-mono">Thought for 3s</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-teal-950 text-teal-300 border border-teal-700/60">
              Clean Sanctuary
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <button id="curatorDrawerListenBtn" type="button" class="text-[11px] text-slate-400 hover:text-white px-2 py-0.5 rounded border border-slate-700 cursor-pointer">Listen</button>
            <button class="text-xs text-slate-400 hover:text-white px-1 cursor-pointer" id="close-chat-view-btn" type="button">✕</button>
          </div>
        </div>
        <!-- Chat Transcript Message Area -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3 text-xs leading-relaxed" id="curatorDrawerChatBody">
          <div class="bg-slate-900/90 border border-cyan-900/40 p-3 rounded-2xl rounded-tl-sm text-slate-200">
            <p>
              I’d love to help you find independent art spaces nearby—operating strictly without corporate capture, defense contractor ties, or fossil fuel underwriting.
            </p>
            <p class="mt-2 text-slate-300 font-medium">
              Where are you currently located, or would you like me to map Manila, Tokyo, or Berlin?
            </p>
          </div>
          <div class="pt-2">
            <p class="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">Suggested Inquiries</p>
            <div class="flex flex-wrap gap-1.5">
              <button class="curator-suggest-chip text-[11px] bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700/80 px-2.5 py-1.5 rounded-lg text-left cursor-pointer" data-query="Find independent art spaces near me" type="button">
                ↳ Find independent art spaces near me
              </button>
              <button class="curator-suggest-chip text-[11px] bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700/80 px-2.5 py-1.5 rounded-lg text-left cursor-pointer" data-query="Who funds this museum?" type="button">
                Who funds this museum?
              </button>
              <button class="curator-suggest-chip text-[11px] bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700/80 px-2.5 py-1.5 rounded-lg text-left cursor-pointer" data-query="Tell me about W.A.G.E. certification, fair pay, and museum unionization" type="button">
                W.A.G.E. fair pay certified spaces
              </button>
              <button class="curator-suggest-chip text-[11px] bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700/80 px-2.5 py-1.5 rounded-lg text-left cursor-pointer" data-query="Which museums and galleries are free to enter?" type="button">
                Free admission spaces today
              </button>
            </div>
          </div>
          <div id="curatorDrawerLiveStream" class="space-y-3 pt-2"></div>
        </div>
      </section>
      <!-- END: CuratorChatDrawer -->
"""
    floating_close = '<!-- Floating Active Map Filter Pill Banner -->'
    content = content.replace(floating_close, mobile_cards_html + "\n      " + floating_close, 1)

    # 7. Add Sticky Curator Input Bar & Mobile Bottom Navigation Bar
    # On mobile, #mobileStickyInputBar is displayed when in map/split mode; when in chat mode, workBottomDock is at bottom of workViewContainer!
    sticky_nav_html = """
  <!-- ========================================================= -->
  <!-- 📌 STICKY CURATOR INPUT BAR (Mobile Matching code.html & media_1791625755099_5e95dfd6.png) -->
  <!-- ========================================================= -->
  <div class="z-40 bg-slate-950/95 border-t border-slate-800/80 px-3 py-2 flex md:hidden flex-col gap-1.5 backdrop-blur-lg shrink-0" data-purpose="ai-chat-input-bar" id="mobileStickyInputBar">
    <div class="relative flex items-center">
      <button id="mobileStickyPlusBtn" type="button" class="w-8 h-8 rounded-full bg-slate-800/90 hover:bg-slate-700 text-slate-200 flex items-center justify-center text-sm font-bold border border-slate-700 mr-2 shrink-0 cursor-pointer">
        +
      </button>
      <input class="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 pr-16" id="chat-input" placeholder="Ask about a museum or cultural space..." type="text">
      <button id="mobileStickySendBtn" type="button" class="absolute right-1.5 top-1.5 bottom-1.5 px-3 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs rounded-lg flex items-center space-x-1 active:scale-95 transition border border-cyan-300 cursor-pointer"><span class="">Send</span></button>
    </div>
    <div class="flex items-center justify-between text-[10px] text-slate-400 px-1">
      <span class="flex items-center space-x-1">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        <span>Anthropic · Live</span>
      </span>
      <div class="flex items-center space-x-2">
        <span id="mobileStickyVoiceBtn" class="text-slate-400 bg-slate-900 px-2 py-0.5 rounded-full border border-slate-800 cursor-pointer">Voice: ON</span>
        <span class="text-emerald-400">● Clean Funding (444)</span>
      </div>
    </div>
  </div>

  <!-- ========================================================= -->
  <!-- 📱 MOBILE BOTTOM NAVIGATION (4-Tab Matching code.html & media_1791625755099_5e95dfd6.png) -->
  <!-- ========================================================= -->
  <nav class="z-40 pb-safe bg-slate-950 border-t border-slate-800 px-4 pt-2 flex md:hidden items-center justify-around shrink-0 select-none" data-purpose="mobile-tab-bar" id="mobileBottomNav">
    <!-- Nav Item: Atlas Globe -->
    <button class="flex flex-col items-center space-y-1 text-cyan-400 focus:outline-none cursor-pointer" id="tab-atlas" type="button">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
      <span class="text-[10px] font-medium tracking-tight">Atlas</span>
    </button>
    <!-- Nav Item: Dossier -->
    <button class="flex flex-col items-center space-y-1 text-slate-400 hover:text-slate-200 focus:outline-none cursor-pointer" id="tab-dossier" type="button">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
      <span class="text-[10px] font-medium tracking-tight">Dossier</span>
    </button>
    <!-- Nav Item: Curator AI -->
    <button class="flex flex-col items-center space-y-1 text-slate-400 hover:text-slate-200 focus:outline-none relative cursor-pointer" id="tab-chat" type="button">
      <span class="absolute -top-1 right-2 w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
      <span class="text-[10px] font-medium tracking-tight">Curator</span>
    </button>
    <!-- Nav Item: Layers / Filters -->
    <button class="flex flex-col items-center space-y-1 text-slate-400 hover:text-slate-200 focus:outline-none cursor-pointer" id="tab-filters" type="button">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
      <span class="text-[10px] font-medium tracking-tight">Filters</span>
    </button>
  </nav>
"""
    main_app_close = '</div>\n\n  <!-- ========================================================= -->\n  <!-- 📋 CATALOG MODAL'
    content = content.replace(main_app_close, '</div>' + sticky_nav_html + '\n\n  <!-- ========================================================= -->\n  <!-- 📋 CATALOG MODAL', 1)

    # 8. Add Mobile Interaction Logic and update setMobileViewMode to coordinate sticky input dock
    js_update = """
    // Mobile Tab Navigation and Drawer State Controller (Matches code.html)
    function initMobileCodeDesign() {{
      const bottomSheet = document.getElementById('dossier-bottom-sheet');
      const chatDrawer = document.getElementById('curator-chat-drawer');
      const closeSheetBtn = document.getElementById('close-sheet-btn');
      const closeChatBtn = document.getElementById('close-chat-view-btn');
      const tabAtlas = document.getElementById('tab-atlas');
      const tabDossier = document.getElementById('tab-dossier');
      const tabChat = document.getElementById('tab-chat');
      const tabFilters = document.getElementById('tab-filters');
      const gossipBtn = document.getElementById('gossip-mode-btn');
      const chatInput = document.getElementById('chat-input');
      const sendBtn = document.getElementById('mobileStickySendBtn');
      const tabInfo = document.getElementById('dossier-tab-info');
      const tabGossip = document.getElementById('dossier-tab-gossip');
      const verifiedPane = document.getElementById('dossier-sheet-verified-pane');
      const gossipPane = document.getElementById('dossier-sheet-gossip-pane');
      const stickyDock = document.getElementById('mobileStickyInputBar');

      function setActiveMobileTab(activeEl) {{
        [tabAtlas, tabDossier, tabChat, tabFilters].forEach(el => {{
          if (!el) return;
          el.classList.remove('text-cyan-400');
          el.classList.add('text-slate-400');
        }});
        if (activeEl) {{
          activeEl.classList.remove('text-slate-400');
          activeEl.classList.add('text-cyan-400');
        }}
      }}
      window.setActiveMobileTab = function(name) {{
        if (name === 'atlas') tabAtlas?.click();
        else if (name === 'dossier') tabDossier?.click();
        else if (name === 'chat') tabChat?.click();
        else if (name === 'filters') tabFilters?.click();
      }};

      closeSheetBtn?.addEventListener('click', () => {{
        bottomSheet?.classList.add('hidden');
        setActiveMobileTab(tabAtlas);
      }});

      closeChatBtn?.addEventListener('click', () => {{
        chatDrawer?.classList.add('hidden');
        setActiveMobileTab(tabAtlas);
        if (typeof setMobileViewMode === 'function') setMobileViewMode('map');
      }});

      tabAtlas?.addEventListener('click', () => {{
        setActiveMobileTab(tabAtlas);
        chatDrawer?.classList.add('hidden');
        if (bottomSheet) {{
          bottomSheet.classList.toggle('hidden');
        }}
        if (stickyDock) stickyDock.classList.remove('hidden');
        if (typeof setMobileViewMode === 'function') setMobileViewMode('map');
      }});

      tabDossier?.addEventListener('click', () => {{
        setActiveMobileTab(tabDossier);
        chatDrawer?.classList.add('hidden');
        bottomSheet?.classList.remove('hidden');
        if (stickyDock) stickyDock.classList.remove('hidden');
      }});

      tabChat?.addEventListener('click', () => {{
        setActiveMobileTab(tabChat);
        bottomSheet?.classList.add('hidden');
        chatDrawer?.classList.remove('hidden');
        if (typeof setBottomSheetSnap === 'function') setBottomSheetSnap('expanded');
        if (typeof setMobileViewMode === 'function') setMobileViewMode('chat');
        // When in expanded chat mode, workBottomDock handles input
        if (stickyDock && window.innerWidth < 768) stickyDock.classList.add('hidden');
      }});

      tabFilters?.addEventListener('click', () => {{
        setActiveMobileTab(tabFilters);
        if (typeof toggleFilterDrawer === 'function') toggleFilterDrawer(true);
      }});

      // Card Mode Tabs
      tabInfo?.addEventListener('click', () => {{
        tabInfo.classList.add('bg-teal-900/90', 'text-teal-200', 'border-teal-300');
        tabInfo.classList.remove('bg-slate-900/90', 'text-slate-400');
        tabGossip?.classList.remove('bg-teal-900/90', 'text-teal-200', 'border-teal-300');
        tabGossip?.classList.add('bg-slate-900/90', 'text-amber-300');
        verifiedPane?.classList.remove('hidden');
        gossipPane?.classList.add('hidden');
      }});

      tabGossip?.addEventListener('click', () => {{
        tabGossip.classList.add('bg-amber-950/80', 'text-amber-300', 'border-amber-500/80');
        tabGossip.classList.remove('bg-slate-900/90', 'text-slate-400');
        tabInfo?.classList.remove('bg-teal-900/90', 'text-teal-200', 'border-teal-300');
        tabInfo?.classList.add('bg-slate-900/90', 'text-slate-400');
        verifiedPane?.classList.add('hidden');
        gossipPane?.classList.remove('hidden');
      }});

      // Send Query from Mobile Sticky Input
      function handleMobileStickySend() {{
        if (!chatInput) return;
        const q = chatInput.value.trim();
        if (!q) return;
        chatInput.value = '';
        tabChat?.click();
        if (typeof handleCuratorQuery === 'function') {{
          handleCuratorQuery(q);
        }}
      }}

      sendBtn?.addEventListener('click', handleMobileStickySend);
      chatInput?.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') {{
          e.preventDefault();
          handleMobileStickySend();
        }}
      }});

      // Voice Toggle
      document.getElementById('mobileStickyVoiceBtn')?.addEventListener('click', () => {{
        if (typeof toggleCuratorVoice === 'function') toggleCuratorVoice();
      }});

      // Plus Menu
      document.getElementById('mobileStickyPlusBtn')?.addEventListener('click', () => {{
        if (typeof toggleFilterDrawer === 'function') toggleFilterDrawer();
      }});

      // Suggested Inquiry Chips inside Drawer
      document.querySelectorAll('.curator-suggest-chip').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const q = btn.getAttribute('data-query');
          if (q && typeof handleCuratorQuery === 'function') {{
            tabChat?.click();
            handleCuratorQuery(q);
          }}
        }});
      }});

      // Audit Dossier & Plan Visit buttons on Mobile Sheet
      document.getElementById('dossier-sheet-audit-btn')?.addEventListener('click', () => {{
        if (selectedInstitution && typeof openDossier === 'function') {{
          openDossier(selectedInstitution);
        }}
      }});
      document.getElementById('dossier-sheet-plan-btn')?.addEventListener('click', () => {{
        if (selectedInstitution && typeof atlasPlanVisit === 'function') {{
          atlasPlanVisit(selectedInstitution);
          tabChat?.click();
        }}
      }});
      document.getElementById('dossier-sheet-full-gossip-btn')?.addEventListener('click', () => {{
        if (selectedInstitution && typeof openGossipDossier === 'function') {{
          openGossipDossier(selectedInstitution);
        }}
      }});
      document.getElementById('dossier-sheet-link-3d')?.addEventListener('click', () => {{
        if (selectedInstitution && typeof zoomToBuilding === 'function') {{
          zoomToBuilding(selectedInstitution);
        }}
      }});
      document.getElementById('dossier-sheet-link-photos')?.addEventListener('click', () => {{
        if (selectedInstitution && typeof openArchiveHoldingsModal === 'function') {{
          openArchiveHoldingsModal(selectedInstitution);
        }}
      }});
    }}
    """
    content = content.replace("window.setBottomSheetSnap = setBottomSheetSnap;",
                              "window.setBottomSheetSnap = setBottomSheetSnap;\n" + js_update, 1)

    # 9. Update selectInstitution to dynamically update #dossier-bottom-sheet
    update_sheet_code = """
      // Update Mobile Space Detail Card Bottom Sheet (#dossier-bottom-sheet)
      const dsName = document.getElementById('dossier-sheet-name');
      const dsTier = document.getElementById('dossier-sheet-tier');
      const dsMeta = document.getElementById('dossier-sheet-meta');
      const dsBudgetVal = document.getElementById('dossier-sheet-budget-val');
      const dsBudgetBadge = document.getElementById('dossier-sheet-budget-badge');
      const dsPillPublic = document.getElementById('dossier-sheet-pill-public');
      const dsPillGrants = document.getElementById('dossier-sheet-pill-grants');
      const dsPillEarned = document.getElementById('dossier-sheet-pill-earned');
      const dsPillRatio = document.getElementById('dossier-sheet-pill-ratio');
      const dsFundingText = document.getElementById('dossier-sheet-funding-text');
      const dsAccessText = document.getElementById('dossier-sheet-access-text');
      const dsExTitle = document.getElementById('dossier-sheet-exhibit-title');
      const dsExCurator = document.getElementById('dossier-sheet-exhibit-curator');
      const dsExVernissage = document.getElementById('dossier-sheet-exhibit-vernissage');
      const dsWebLink = document.getElementById('dossier-sheet-link-web');
      const dsGossipHeadline = document.getElementById('dossier-sheet-gossip-headline');
      const dsGossipReddit = document.getElementById('dossier-sheet-gossip-reddit');
      const dsGossipTwitter = document.getElementById('dossier-sheet-gossip-twitter');

      if (dsName) dsName.textContent = inst.name || 'Green Papaya Art Projects';
      if (dsTier) dsTier.textContent = inst.tier_label || 'Verified';
      if (dsMeta) dsMeta.textContent = `${{inst.city || 'Quezon City / Manila'}}, ${{inst.country || 'Philippines'}} · ${{inst.governance_classification || 'Artist-Run'}}`;
      if (dsBudgetVal) dsBudgetVal.textContent = inst.financial_data?.operating_budget_display || '€250K – €850K Grassroots Budget';
      if (dsBudgetBadge) dsBudgetBadge.textContent = inst.financial_data?.budget_tier || 'Lean Non-Profit';
      if (dsPillPublic) dsPillPublic.textContent = `${{inst.financial_data?.public_subsidies_pct || 58}}% Public`;
      if (dsPillGrants) dsPillGrants.textContent = `${{inst.financial_data?.philanthropy_endowment_pct || 14}}% Grants`;
      if (dsPillEarned) dsPillEarned.textContent = `${{inst.financial_data?.earned_revenue_pct || 28}}% Earned`;
      if (dsPillRatio) dsPillRatio.textContent = `${{inst.financial_data?.program_expense_ratio_pct || 84}}% Ratio`;
      if (dsFundingText) dsFundingText.textContent = inst.governance_details || 'Collective self-funding, Arts Collaboratory, independent foundations. 100% free of corporate defense/oil capture.';
      if (dsAccessText) dsAccessText.textContent = inst.floor_plans?.[0]?.access_policy || 'Nomadic research & residency; free admission.';

      const curShow = inst.temporary_shows?.[0] || inst.floor_plans?.[0]?.current_shows?.[0];
      if (dsExTitle) dsExTitle.textContent = curShow?.title || `Featured Exhibition: In Focus with ${{inst.name}}`;
      if (dsExCurator) dsExCurator.textContent = `${{curShow?.curator_artists || 'Curatorial Cohort & Guest Artists'}} · ${{curShow?.dates || 'On View Autumn 2026 – Spring 2027'}}`;
      if (dsExVernissage) dsExVernissage.textContent = curShow?.opening_night ? `Vernissage: ${{curShow.opening_night.date}} (${{curShow.opening_night.hours}})` : 'Vernissage: Fri, Oct 23 (18:00–21:30)';
      if (dsWebLink) dsWebLink.href = getValidWebUrl(inst);

      if (inst.gossip_data && dsGossipHeadline) {{
        dsGossipHeadline.textContent = inst.gossip_data.headline || 'Field Intel & Whispers documented';
        if (dsGossipReddit) dsGossipReddit.textContent = inst.gossip_data.reddit?.snippet || 'Community Discussion documented on r/contemporaryart.';
        if (dsGossipTwitter) dsGossipTwitter.textContent = inst.gossip_data.twitter_x?.snippet || 'Field claim logged on X / Twitter.';
      }}
    """
    content = content.replace("selectedInstitution = inst;", "selectedInstitution = inst;\n" + update_sheet_code, 1)

    # 10. Hide legacy mobile handle bar and ensure map is default mobile mode
    content = content.replace('<div id="mobileSheetHandleBar" class="flex md:hidden', '<div id="mobileSheetHandleBar" class="hidden', 1)
    content = content.replace("let currentMobileMode = 'split';", "let currentMobileMode = 'map';", 1)

    # Replace mobile split trigger in selectInstitution with bottom sheet show
    old_split_trigger = """      if (window.innerWidth < 768 && typeof currentMobileMode !== 'undefined' && currentMobileMode === 'chat' && typeof setMobileViewMode === 'function') {{
        setMobileViewMode('split');
      }}"""
    new_split_trigger = """      if (window.innerWidth < 768) {{
        const bs = document.getElementById('dossier-bottom-sheet');
        if (bs) bs.classList.remove('hidden');
      }}"""
    content = content.replace(old_split_trigger, new_split_trigger, 1)

    # 11. Call initMobileCodeDesign and pre-populate Green Papaya Art Projects on load
    init_call = """
    // Initialize Mobile Code.html Design & Default Space
    try {{
      initMobileCodeDesign();
      const greenPapaya = (window.ALL_INSTITUTIONS || []).find(i => i.name && i.name.toLowerCase().includes('green papaya'));
      if (greenPapaya && !selectedInstitution) {{
        selectInstitution(greenPapaya, false);
      }}
    }} catch (e) {{
      console.warn('initMobileCodeDesign error:', e);
    }}
    """
    content = content.replace("initBuildingRooms3DEngine();", "initBuildingRooms3DEngine();\n" + init_call, 1)

    # 12. Coordinate setMobileViewMode so in 'chat' mode workBottomDock is inside workViewContainer at bottom, and mobileStickyInputBar is hidden
    old_chat_mode = """        if (workView) {{
          workView.style.display = 'flex';
          workView.style.height = '100%';
          workView.style.minHeight = '0px';
          workView.style.flex = '1 1 0%';
        }}"""
    new_chat_mode = """        if (workView) {{
          workView.style.display = 'flex';
          workView.style.height = '100%';
          workView.style.minHeight = '0px';
          workView.style.flex = '1 1 0%';
        }}
        const stickyDock = document.getElementById('mobileStickyInputBar');
        if (stickyDock && window.innerWidth < 768) stickyDock.classList.add('hidden');"""
    content = content.replace(old_chat_mode, new_chat_mode, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched build_conversational_atlas.py!")

if __name__ == "__main__":
    main()
