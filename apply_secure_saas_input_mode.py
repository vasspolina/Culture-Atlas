#!/usr/bin/env python3
"""
apply_secure_saas_input_mode.py
Implements:
1. Clear Visual Hierarchy:
   - Eliminates nested boxes and outer tracking borders around instructions and status bars.
   - Single primary container for input field with sophisticated dark slate (#0f172a) background.
   - Moves technical jargon (Zero-Knowledge, SHA-256) into subtle minimalist header/footer rather than screaming warning banners.
2. Clean Up Copy & Instructions:
   - Replaces the large instructional block card (VERIFICATION PROTOCOL) with a clean single-line helper and generous textarea placeholder.
   - Consolidates scattered repetitive Exit/Submit buttons into a single standard action bar inside the container.
3. Modern "Secure SaaS" Aesthetic:
   - Palette: #0f172a dark slate background, #334155 subtle slate border, off-white text (#f8fafc), emerald (#10b981 / #059669) strictly as accent for the active CTA and status dot.
   - Generous whitespace and padding giving the textarea room to breathe.
   - Strict 3-size typography (14px, 18px, 27px).
"""

import sys

def main():
    target = 'build_conversational_atlas.py'
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update chatInputModeHeader HTML markup (eliminate green gradient, screaming badges, duplicate exit button)
    old_header = """          <!-- Dedicated Input Mode Sticky / Top Header -->
          <div id="chatInputModeHeader" class="hidden w-full mb-3 p-3 sm:p-3.5 rounded-2xl bg-gradient-to-r from-[#061f15]/95 via-[#0b2b1e]/95 to-[#061f15]/95 border border-emerald-500/60 shadow-lg shadow-emerald-950/40 backdrop-blur-md flex items-center justify-between gap-3 text-slate-200">
            <div class="flex items-center gap-2.5 min-w-0">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
              <div class="min-w-0">
                <div class="text-[14px] sm:text-[14px] font-semibold text-emerald-300 flex items-center gap-2 truncate">
                  <span>Confidential Field Intel &amp; Whistleblower Vault</span>
                  <span class="text-[14px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60 uppercase">Zero-Knowledge</span>
                </div>
                <p class="text-[14px] font-mono text-emerald-400/80 truncate">Client-Side SHA-256 Hashing · No IP Logs · Ephemeral Pseudonyms</p>
              </div>
            </div>
            <button id="exitInputModeBtn" type="button" onclick="window.exitChatInputMode()" class="px-3 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-700 text-[14px] font-medium transition cursor-pointer flex items-center gap-1.5 shrink-0 shadow-sm" title="Exit Input Mode &amp; return to normal chat">
              <span>✕ Exit Input Mode</span>
            </button>
          </div>"""

    new_header = """          <!-- Dedicated Input Mode Header: Clean Minimalist SaaS Bar -->
          <div id="chatInputModeHeader" class="hidden w-full mb-3 py-2 px-3.5 rounded-xl bg-[#0f172a] border border-[#1e293b] flex items-center justify-between gap-3 text-slate-300 select-none">
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
              <span class="text-[14px] font-medium text-slate-100 truncate">Confidential Field Intel</span>
            </div>
            <div class="text-[14px] font-mono text-slate-400 truncate">
              <span>Zero-Knowledge · Client-Side SHA-256</span>
            </div>
          </div>"""

    assert old_header in content, "old_header not found in build_conversational_atlas.py"
    content = content.replace(old_header, new_header, 1)

    # 2. Update action bar inside workInputCard
    old_input_actions = """              <!-- Left: Plus action button & Input Mode Badge -->
              <div class="flex items-center gap-2 sm:gap-2.5">
                <button id="workPlusBtn" class="w-8.5 h-8.5 sm:w-9 sm:h-9 rounded-full bg-black hover:bg-[#1c1c1c] text-white border border-white/20 hover:border-white/40 flex items-center justify-center transition active:scale-95 cursor-pointer font-normal shrink-0 shadow-sm" title="Quick filters">
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                </button>
                <div id="workInputModeBadge" class="hidden items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/90 text-emerald-300 border border-emerald-700/70 text-[14px] font-mono shadow-sm">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Confidential Vault Active</span>
                </div>
              </div>"""

    new_input_actions = """              <!-- Left: Plus action button (normal chat) or Clean Cancel button (input mode) -->
              <div class="flex items-center gap-2 sm:gap-2.5">
                <button id="workPlusBtn" class="w-8.5 h-8.5 sm:w-9 sm:h-9 rounded-full bg-black hover:bg-[#1c1c1c] text-white border border-white/20 hover:border-white/40 flex items-center justify-center transition active:scale-95 cursor-pointer font-normal shrink-0 shadow-sm" title="Quick filters">
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                </button>
                <button id="inputModeCancelBtn" type="button" onclick="window.exitChatInputMode()" class="hidden px-3 py-1.5 rounded-xl bg-[#1e293b] hover:bg-[#334155] text-slate-300 hover:text-white border border-[#334155] text-[14px] font-normal transition cursor-pointer flex items-center gap-1 shrink-0" title="Cancel and return to chat">
                  <span>Cancel</span>
                </button>
                <div id="workInputModeBadge" class="hidden items-center gap-1.5 text-slate-400 text-[14px] font-mono">
                  <span>Zero-Knowledge · SHA-256</span>
                </div>
              </div>"""

    assert old_input_actions in content, "old_input_actions not found in build_conversational_atlas.py"
    content = content.replace(old_input_actions, new_input_actions, 1)

    # 3. Update enterChatInputMode() implementation
    old_enter_fn = """    function enterChatInputMode(defaultTopic = '') {{
      isChatInputMode = true;

      // 1. Activate whole-chat full-width mode via body class & collapse globe
      document.body.classList.add('chat-input-mode-active');
      if (window.innerWidth < 768 && typeof setMobileViewMode === 'function') {{
        setMobileViewMode('chat');
      }} else if (window.innerWidth >= 768) {{
        const g = document.getElementById('globeViewport');
        if (g) {{
          preInputModeGlobeWidth = g.style.width || '';
          setTimeout(resizeCanvas, 40);
        }}
      }}

      // 2. Expand input textarea & focus
      const workInput = document.getElementById('workInput');
      if (workInput) {{
        workInput.rows = 4;
        workInput.classList.add('min-h-[110px]');
        workInput.placeholder = '🔒 [Input Mode] Enter notes, queries, or confidential intel here...';
        if (defaultTopic) {{
          workInput.value = defaultTopic;
        }}
        workInput.focus();
      }}

      // 3. Update full-width input mode button state
      const fwBtn = document.getElementById('fullWidthInputModeBtn');
      const fwText = document.getElementById('fullWidthInputModeText');
      const fwDot = document.getElementById('fullWidthInputModeDot');
      if (fwBtn) {{
        fwBtn.classList.add('bg-[#072418]', 'border-emerald-500/70', 'text-emerald-300');
        fwBtn.classList.remove('bg-[#18181b]', 'text-white', 'border-white/20');
        fwBtn.setAttribute('title', 'Click to exit Input Mode');
      }}
      if (fwText) fwText.textContent = 'Exit Input Mode';
      if (fwDot) fwDot.classList.add('animate-ping');

      // 3. Hide suggestions & multi-row filter pills
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.add('hidden');

      const cityBar = document.getElementById('globeCityBar');
      if (cityBar) cityBar.classList.add('hidden');

      // 4. Show top sticky input mode header
      const inputModeHeader = document.getElementById('chatInputModeHeader');
      if (inputModeHeader) inputModeHeader.classList.remove('hidden');

      // 5. Style input card as dedicated secure vault
      const inputCard = document.getElementById('workInputCard');
      if (inputCard) {{
        inputCard.classList.add('border-emerald-500/80', 'bg-[#0a1e16]', 'shadow-emerald-950/70', 'ring-1', 'ring-emerald-500/40');
      }}

      // 6. Hide irrelevant AI model / voice buttons in input card
      const modelBtn = document.getElementById('workModelBtn');
      if (modelBtn) modelBtn.classList.add('hidden');

      const voiceToggleBtn = document.getElementById('curatorVoiceToggleBtn');
      if (voiceToggleBtn) voiceToggleBtn.classList.add('hidden');

      const inputBadge = document.getElementById('workInputModeBadge');
      if (inputBadge) {{
        inputBadge.classList.remove('hidden');
        inputBadge.classList.add('flex');
      }}

      // 7. Style Send button as dedicated emerald Submit Intel button
      const sendBtn = document.getElementById('workSendBtn');
      if (sendBtn) {{
        sendBtn.classList.remove('bg-black', 'hover:bg-[#1c1c1c]', 'border-white/20');
        sendBtn.classList.add('bg-gradient-to-r', 'from-emerald-600', 'to-teal-600', 'hover:from-emerald-500', 'hover:to-teal-500', 'shadow-emerald-900/60');
        sendBtn.innerHTML = `
          <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
          </svg>
          <span>Submit Intel</span>
        `;
        sendBtn.title = 'Cryptographically submit confidential intelligence';
      }}

      // 9. Inject dedicated Intake Workspace into curatorMessages if not already injected
      try {{
        if (!document.getElementById('inputModeIntakePanel') && typeof appendCuratorMessage === 'function') {{
          appendCuratorMessage(`
            <div id="inputModeIntakePanel" class="space-y-3.5 text-slate-200 bg-[#071f16]/95 border border-emerald-500/60 rounded-2xl sm:rounded-3xl p-4 sm:p-5 shadow-2xl backdrop-blur-md">
              <div class="flex items-center justify-between border-b border-emerald-800/60 pb-2.5">
                <div class="flex items-center gap-2.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
                  <h3 class="text-white font-semibold text-[14px] sm:text-[18px]">Confidential Field Intel &amp; Whistleblower Pipeline</h3>
                </div>
                <span class="text-[14px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/60">In-Chat Intake Active</span>
              </div>
              
              <p class="text-white text-[14px] sm:text-[14px] leading-relaxed">
                <strong>How to submit right here:</strong> Share non-public documents, unverified corporate sponsorships, board conflicts, or suggest unlisted independent art spaces directly in the chat below.
              </p>

              <div class="space-y-1.5 text-[14px] text-slate-300 bg-[#04140e]/80 p-3 rounded-xl border border-emerald-900/60">
                <div class="font-medium text-emerald-300 font-mono text-[14px] uppercase tracking-wider flex items-center gap-1.5">
                  <span>Verification Protocol (Zero-Knowledge)</span>
                </div>
                <ol class="list-decimal list-inside space-y-1 text-[14px] text-slate-300">
                  <li>Type or paste your information directly into the input vault below.</li>
                  <li>Include key details: Museum or institution name, trustee names, dates, or document excerpts.</li>
                  <li><strong>Cryptographic Receipt:</strong> Culture Atlas computes a native SHA-256 integrity hash locally in your browser and assigns an ephemeral pseudonym.</li>
                </ol>
              </div>


              <div class="pt-2 border-t border-emerald-900/60 flex items-center justify-between text-[14px] font-mono text-emerald-400/90 flex-wrap gap-2">
                <span class="flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>Input active below · Submit anytime via Enter or Send</span>
                </span>
                <span class="text-zinc-400">OpSec Tip: Use Tor or Brave for high-risk leaks</span>
              </div>
            </div>
          `);
        }}
      }} catch (err) {{
        console.warn('Could not inject intake panel:', err);
      }}

      scrollChatToBottom(true);
    }}"""

    new_enter_fn = """    function enterChatInputMode(defaultTopic = '') {{
      isChatInputMode = true;

      // 1. Activate whole-chat full-width mode via body class & collapse globe
      document.body.classList.add('chat-input-mode-active');
      if (window.innerWidth < 768 && typeof setMobileViewMode === 'function') {{
        setMobileViewMode('chat');
      }} else if (window.innerWidth >= 768) {{
        const g = document.getElementById('globeViewport');
        if (g) {{
          preInputModeGlobeWidth = g.style.width || '';
          setTimeout(resizeCanvas, 40);
        }}
      }}

      // 2. Expand input textarea with generous room to breathe & focused placeholder
      const workInput = document.getElementById('workInput');
      if (workInput) {{
        workInput.rows = 5;
        workInput.classList.remove('min-h-[34px]', 'sm:min-h-[42px]', 'max-h-36');
        workInput.classList.add('min-h-[120px]', 'sm:min-h-[140px]', 'max-h-60', 'text-slate-100', 'placeholder-slate-400', 'leading-relaxed');
        workInput.placeholder = 'Share confidential field intelligence, unverified sponsorships, or document excerpts. Submissions are processed with client-side zero-knowledge integrity...';
        if (defaultTopic) {{
          workInput.value = defaultTopic;
        }}
        workInput.focus();
      }}

      // 3. Hide redundant full-width input mode button underneath dock
      const fwBtn = document.getElementById('fullWidthInputModeBtn');
      if (fwBtn) fwBtn.classList.add('hidden');

      // 4. Hide suggestions & multi-row filter pills
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.add('hidden');

      const cityBar = document.getElementById('globeCityBar');
      if (cityBar) cityBar.classList.add('hidden');

      // 5. Show clean minimalist SaaS header
      const inputModeHeader = document.getElementById('chatInputModeHeader');
      if (inputModeHeader) inputModeHeader.classList.remove('hidden');

      // 6. Style primary input container with modern dark slate SaaS aesthetic (#0f172a)
      const inputCard = document.getElementById('workInputCard');
      if (inputCard) {{
        inputCard.classList.remove('bg-[#212121]', 'border-[#333333]');
        inputCard.classList.add('bg-[#0f172a]', 'border-[#334155]', 'shadow-2xl', 'shadow-slate-950/60', 'p-4', 'sm:p-5');
      }}

      // 7. Toggle action bar: show Cancel button & subtle metadata, hide plus button
      const plusBtn = document.getElementById('workPlusBtn');
      if (plusBtn) plusBtn.classList.add('hidden');

      const cancelBtn = document.getElementById('inputModeCancelBtn');
      if (cancelBtn) cancelBtn.classList.remove('hidden');

      const inputBadge = document.getElementById('workInputModeBadge');
      if (inputBadge) {{
        inputBadge.classList.remove('hidden');
        inputBadge.classList.add('flex');
      }}

      const modelBtn = document.getElementById('workModelBtn');
      if (modelBtn) modelBtn.classList.add('hidden');

      const voiceToggleBtn = document.getElementById('curatorVoiceToggleBtn');
      if (voiceToggleBtn) voiceToggleBtn.classList.add('hidden');

      // 8. Style primary CTA: clean emerald button as sole accent
      const sendBtn = document.getElementById('workSendBtn');
      if (sendBtn) {{
        sendBtn.classList.remove('bg-black', 'hover:bg-[#1c1c1c]', 'border-white/20', 'rounded-full');
        sendBtn.classList.add('bg-emerald-600', 'hover:bg-emerald-500', 'text-white', 'rounded-xl', 'px-4', 'py-2', 'shadow-sm');
        sendBtn.innerHTML = `
          <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
          </svg>
          <span>Submit Intel</span>
        `;
        sendBtn.title = 'Cryptographically submit confidential intelligence';
      }}

      // 9. Single-line clean helper prompt (no heavy nested boxes)
      try {{
        if (!document.getElementById('inputModeIntakePanel') && typeof appendCuratorMessage === 'function') {{
          appendCuratorMessage(`
            <div id="inputModeIntakePanel" class="py-2.5 px-3.5 rounded-xl bg-[#0f172a] border border-[#1e293b] text-[14px] text-slate-300 flex items-center justify-between gap-3 shadow-sm select-none">
              <span class="text-slate-200"><strong>Confidential Field Intel:</strong> Enter non-public filings, board disclosures, or suggested independent spaces below.</span>
              <span class="text-slate-400 font-mono text-[14px] shrink-0 hidden sm:inline">Zero-Knowledge · SHA-256</span>
            </div>
          `);
        }}
      }} catch (err) {{
        console.warn('Could not inject intake panel:', err);
      }}

      scrollChatToBottom(true);
    }}"""

    assert old_enter_fn in content, "old_enter_fn not found in build_conversational_atlas.py"
    content = content.replace(old_enter_fn, new_enter_fn, 1)

    # 4. Update exitChatInputMode() implementation
    old_exit_fn = """    function exitChatInputMode() {{
      isChatInputMode = false;

      // 1. Deactivate whole-chat full-width mode
      document.body.classList.remove('chat-input-mode-active');
      if (typeof resizeCanvas === 'function') {{
        setTimeout(resizeCanvas, 360);
      }}

      // 2. Reset full-width input mode button state
      const fwBtn = document.getElementById('fullWidthInputModeBtn');
      const fwText = document.getElementById('fullWidthInputModeText');
      const fwDot = document.getElementById('fullWidthInputModeDot');
      if (fwBtn) {{
        fwBtn.classList.remove('bg-[#072418]', 'border-emerald-500/70', 'text-emerald-300');
        fwBtn.classList.add('bg-[#18181b]', 'text-white', 'border-white/20');
        fwBtn.setAttribute('title', 'Switch whole chat to Input Mode');
      }}
      if (fwText) fwText.textContent = 'Input Mode';
      if (fwDot) fwDot.classList.remove('animate-ping');

      // 3. Hide sticky input mode header
      const inputModeHeader = document.getElementById('chatInputModeHeader');
      if (inputModeHeader) inputModeHeader.classList.add('hidden');

      // 4. Restore filter bar below input
      const cityBar = document.getElementById('globeCityBar');
      if (cityBar) cityBar.classList.remove('hidden');

      // 5. Restore input card styling & height
      const inputCard = document.getElementById('workInputCard');
      if (inputCard) {{
        inputCard.classList.remove('border-emerald-500/80', 'bg-[#0a1e16]', 'shadow-emerald-950/70', 'ring-1', 'ring-emerald-500/40');
      }}

      // 6. Restore AI controls
      const modelBtn = document.getElementById('workModelBtn');
      if (modelBtn) modelBtn.classList.remove('hidden');

      const voiceToggleBtn = document.getElementById('curatorVoiceToggleBtn');
      if (voiceToggleBtn) voiceToggleBtn.classList.remove('hidden');

      const inputBadge = document.getElementById('workInputModeBadge');
      if (inputBadge) {{
        inputBadge.classList.add('hidden');
        inputBadge.classList.remove('flex');
      }}

      // 7. Restore Send button
      const sendBtn = document.getElementById('workSendBtn');
      if (sendBtn) {{
        sendBtn.classList.remove('bg-gradient-to-r', 'from-emerald-600', 'to-teal-600', 'hover:from-emerald-500', 'hover:to-teal-500', 'shadow-emerald-900/60');
        sendBtn.classList.add('bg-black', 'hover:bg-[#1c1c1c]', 'border-white/20');
        sendBtn.innerHTML = `
          <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
          <span>Send</span>
        `;
        sendBtn.title = 'Send message';
      }}

      // 8. Restore placeholder & row height
      const workInput = document.getElementById('workInput');
      if (workInput) {{
        workInput.rows = 2;
        workInput.classList.remove('min-h-[110px]');
        workInput.placeholder = 'Ask about a museum or cultural space';
      }}

      // 9. Desktop split view restoration if previously minimized
      if (window.innerWidth >= 768) {{
        const g = document.getElementById('globeViewport');
        if (g && (g.style.width === '240px' || preInputModeGlobeWidth)) {{
          g.style.width = preInputModeGlobeWidth || '50%';
          g.style.flex = preInputModeGlobeWidth ? `1 1 ${{preInputModeGlobeWidth}}` : '1 1 50%';
          setTimeout(resizeCanvas, 40);
        }}
      }}

      appendCuratorMessage(`
        <div class="text-[14px] text-zinc-400 py-1 flex items-center justify-between border-y border-zinc-800">
          <span>Returned to Curator Chat. How can I help you explore cultural spaces?</span>
          <button type="button" onclick="window.enterChatInputMode()" class="text-emerald-400 hover:underline cursor-pointer font-mono text-[14px]">Re-open Intel Vault</button>
        </div>
      `);
      scrollChatToBottom(true);
    }}"""

    new_exit_fn = """    function exitChatInputMode() {{
      isChatInputMode = false;

      // 1. Deactivate whole-chat full-width mode
      document.body.classList.remove('chat-input-mode-active');
      if (typeof resizeCanvas === 'function') {{
        setTimeout(resizeCanvas, 360);
      }}

      // 2. Restore full-width input mode button below dock
      const fwBtn = document.getElementById('fullWidthInputModeBtn');
      const fwText = document.getElementById('fullWidthInputModeText');
      const fwDot = document.getElementById('fullWidthInputModeDot');
      if (fwBtn) {{
        fwBtn.classList.remove('hidden', 'bg-[#072418]', 'border-emerald-500/70', 'text-emerald-300');
        fwBtn.classList.add('bg-[#18181b]', 'text-white', 'border-white/20');
        fwBtn.setAttribute('title', 'Switch whole chat to Input Mode');
      }}
      if (fwText) fwText.textContent = 'Input Mode';
      if (fwDot) fwDot.classList.remove('animate-ping');

      // 3. Hide sticky input mode header
      const inputModeHeader = document.getElementById('chatInputModeHeader');
      if (inputModeHeader) inputModeHeader.classList.add('hidden');

      // 4. Restore filter bar below input
      const cityBar = document.getElementById('globeCityBar');
      if (cityBar) cityBar.classList.remove('hidden');

      // 5. Restore suggestions section
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.remove('hidden');

      // 6. Restore input card styling & padding
      const inputCard = document.getElementById('workInputCard');
      if (inputCard) {{
        inputCard.classList.remove('bg-[#0f172a]', 'border-[#334155]', 'shadow-2xl', 'shadow-slate-950/60', 'p-4', 'sm:p-5');
        inputCard.classList.add('bg-[#212121]', 'border-[#333333]');
      }}

      // 7. Toggle action bar: show plus, hide cancel & metadata
      const plusBtn = document.getElementById('workPlusBtn');
      if (plusBtn) plusBtn.classList.remove('hidden');

      const cancelBtn = document.getElementById('inputModeCancelBtn');
      if (cancelBtn) cancelBtn.classList.add('hidden');

      const inputBadge = document.getElementById('workInputModeBadge');
      if (inputBadge) {{
        inputBadge.classList.add('hidden');
        inputBadge.classList.remove('flex');
      }}

      // 8. Restore AI controls
      const modelBtn = document.getElementById('workModelBtn');
      if (modelBtn) modelBtn.classList.remove('hidden');

      const voiceToggleBtn = document.getElementById('curatorVoiceToggleBtn');
      if (voiceToggleBtn) voiceToggleBtn.classList.remove('hidden');

      // 9. Restore Send button
      const sendBtn = document.getElementById('workSendBtn');
      if (sendBtn) {{
        sendBtn.classList.remove('bg-emerald-600', 'hover:bg-emerald-500', 'text-white', 'rounded-xl', 'px-4', 'py-2');
        sendBtn.classList.add('bg-black', 'hover:bg-[#1c1c1c]', 'border-white/20', 'rounded-full');
        sendBtn.innerHTML = `
          <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
          <span>Send</span>
        `;
        sendBtn.title = 'Send message';
      }}

      // 10. Restore placeholder & row height
      const workInput = document.getElementById('workInput');
      if (workInput) {{
        workInput.rows = 2;
        workInput.classList.remove('min-h-[120px]', 'sm:min-h-[140px]', 'max-h-60', 'text-slate-100', 'placeholder-slate-400', 'leading-relaxed');
        workInput.classList.add('min-h-[34px]', 'sm:min-h-[42px]', 'max-h-36');
        workInput.placeholder = 'Ask about a museum or cultural space';
      }}

      // 11. Desktop split view restoration if previously minimized
      if (window.innerWidth >= 768) {{
        const g = document.getElementById('globeViewport');
        if (g && (g.style.width === '240px' || preInputModeGlobeWidth)) {{
          g.style.width = preInputModeGlobeWidth || '50%';
          g.style.flex = preInputModeGlobeWidth ? `1 1 ${{preInputModeGlobeWidth}}` : '1 1 50%';
          setTimeout(resizeCanvas, 40);
        }}
      }}

      appendCuratorMessage(`
        <div class="text-[14px] text-zinc-400 py-1.5 flex items-center justify-between border-y border-zinc-800">
          <span>Returned to Curator Chat. How can I help you explore cultural spaces?</span>
          <button type="button" onclick="window.enterChatInputMode()" class="text-emerald-400 hover:underline cursor-pointer font-mono text-[14px]">Re-open Intel Vault</button>
        </div>
      `);
      scrollChatToBottom(true);
    }}"""

    assert old_exit_fn in content, "old_exit_fn not found in build_conversational_atlas.py"
    content = content.replace(old_exit_fn, new_exit_fn, 1)

    # 5. Update whistleblower receipt card in processInChatWhistleblowerSubmission to dark slate SaaS palette
    old_receipt = """        <div class="p-3.5 rounded-2xl bg-[#092218] border border-emerald-500/60 space-y-2.5 text-slate-200 font-sans">
          <div class="flex items-center justify-between border-b border-emerald-500/30 pb-2">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
              <span class="text-white font-medium text-[14px]">Cryptographic Whistleblower Receipt</span>
            </div>
            <span class="text-[14px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60 shrink-0">SHA-256 VERIFIED</span>
          </div>
          <div class="text-[14px] font-mono space-y-1">
            <div class="text-emerald-300">Receipt Code: <span class="text-white">${{escapeHtml(cryptoReceipt.receipt)}}</span></div>
            <div class="text-slate-400 truncate">SHA-256 Digest: <span class="text-emerald-400">${{escapeHtml(cryptoReceipt.hash)}}</span></div>
          </div>
          <div class="pt-1.5 border-t border-emerald-500/20 text-[14px] text-slate-300 leading-relaxed">
            <strong class="text-emerald-400 block mb-0.5 font-mono uppercase text-[14px]">OpSec &amp; Whistleblower Precautions:</strong>
            Your lead is logged under anonymous pseudonym ${{escapeHtml(pseudonym)}}. Retain your receipt code.
          </div>
          <div class="pt-2 border-t border-emerald-900/60 flex items-center justify-between gap-2 flex-wrap">
            <button type="button" onclick="window.enterChatInputMode()" class="px-3 py-1.5 rounded-lg bg-emerald-800/80 hover:bg-emerald-700 text-emerald-200 hover:text-white border border-emerald-600/70 text-[14px] font-medium cursor-pointer transition">
              + Submit Another Report
            </button>
            <button type="button" onclick="window.exitChatInputMode()" class="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white border border-zinc-700 text-[14px] font-medium cursor-pointer transition">
              ✕ Return to Curator Chat
            </button>
          </div>
        </div>"""

    new_receipt = """        <div class="p-4 rounded-xl bg-[#0f172a] border border-[#334155] space-y-2.5 text-slate-200 font-sans shadow-lg">
          <div class="flex items-center justify-between border-b border-[#1e293b] pb-2">
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
              <span class="text-white font-medium text-[14px]">Cryptographic Whistleblower Receipt</span>
            </div>
            <span class="text-[14px] font-mono text-emerald-400 shrink-0">SHA-256 VERIFIED</span>
          </div>
          <div class="text-[14px] font-mono space-y-1 text-slate-300">
            <div>Receipt Code: <span class="text-white font-bold">${{escapeHtml(cryptoReceipt.receipt)}}</span></div>
            <div class="text-slate-400 truncate">SHA-256 Digest: <span class="text-slate-300">${{escapeHtml(cryptoReceipt.hash)}}</span></div>
          </div>
          <div class="pt-1.5 border-t border-[#1e293b] text-[14px] text-slate-300 leading-relaxed">
            <strong class="text-slate-200 block mb-0.5 font-mono uppercase text-[14px]">OpSec &amp; Whistleblower Precautions:</strong>
            Lead logged under pseudonym ${{escapeHtml(pseudonym)}}. Retain your cryptographic receipt code.
          </div>
          <div class="pt-2 border-t border-[#1e293b] flex items-center justify-between gap-2 flex-wrap">
            <button type="button" onclick="window.enterChatInputMode()" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[14px] font-medium cursor-pointer transition shadow-sm">
              + Submit Another Report
            </button>
            <button type="button" onclick="window.exitChatInputMode()" class="px-3 py-1.5 rounded-lg bg-[#1e293b] hover:bg-[#334155] text-slate-300 hover:text-white border border-[#334155] text-[14px] font-normal cursor-pointer transition">
              Return to Chat
            </button>
          </div>
        </div>"""

    assert old_receipt in content, "old_receipt not found in build_conversational_atlas.py"
    content = content.replace(old_receipt, new_receipt, 1)

    # 6. Update placeholder in processInChatWhistleblowerSubmission
    old_post_submit_ph = """          workInput.placeholder = '🔒 [Confidential Vault] Enter additional intel or paste document leak here...';"""
    new_post_submit_ph = """          workInput.placeholder = 'Share confidential field intelligence, unverified sponsorships, or document excerpts. Submissions are processed with client-side zero-knowledge integrity...';"""
    assert old_post_submit_ph in content, "old_post_submit_ph not found"
    content = content.replace(old_post_submit_ph, new_post_submit_ph, 1)

    with open(target, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Successfully patched build_conversational_atlas.py with Modern Secure SaaS aesthetic!")

if __name__ == '__main__':
    main()
