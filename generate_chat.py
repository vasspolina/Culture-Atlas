import json

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/institutions.json') as f:
    inst_data = json.load(f)

# Compact institutions data for fallback
compact_insts = []
for i in inst_data:
    compact_insts.append({
        'n': i['name'],
        'c': i['location'],
        't': i['tier'],
        's': i['size'],
        'f': i['funding'],
        'w': i['watch'],
        'u': i['sources'],
        'la': i['lat'],
        'lo': i['lon']
    })

insts_json = json.dumps(compact_insts)

chat_code = '''/**
 * Culture Atlas — AI Concierge & Conversational Experience
 * Complete Offline Intelligence + Gemini API Integration + 3D Globe Control
 */

(function () {
  'use strict';

  // Fallback institutions dataset (all 197 institutions embedded for 100% offline & file:// safety)
  const FALLBACK_INSTITUTIONS = ''' + insts_json + ''';

  let institutions = FALLBACK_INSTITUTIONS;
  let isChatOpen = false;
  let isMinimized = false;
  let isListening = false;
  let recognition = null;

  const STORAGE_KEY_API_KEY = 'atlas_gemini_api_key';
  const STORAGE_KEY_MODEL = 'atlas_gemini_model';

  function safeGetStorage(key, defVal = '') {
    try {
      return localStorage.getItem(key) || defVal;
    } catch (e) {
      return defVal;
    }
  }

  function safeSetStorage(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
  }

  let geminiApiKey = safeGetStorage(STORAGE_KEY_API_KEY, '');
  let geminiModel = safeGetStorage(STORAGE_KEY_MODEL, 'gemini-2.5-flash');

  // Tier info lookup
  const TIERS = {
    A: { label: 'Verified', color: '#24a148', desc: 'No controversial corporate underwriting. Endowed, public benefit, or strict ethical policy.' },
    B: { label: 'One name to know', color: '#4589ff', desc: 'Major public institution with a corporate partner to note on its roster.' },
    U: { label: 'Roster unverified', color: '#8d8d8d', desc: 'Pending updated annual report disclosure or under review.' }
  };

  function updateInstitutionsFromAtlas() {
    if (window.Atlas && window.Atlas.institutions && window.Atlas.institutions.length > 0) {
      institutions = window.Atlas.institutions;
    }
  }

  // Build UI
  function createChatUI() {
    if (document.getElementById('atlasConciergeToggle')) return;

    // 1. Toggle Button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'atlas-concierge-toggle';
    toggleBtn.id = 'atlasConciergeToggle';
    toggleBtn.setAttribute('type', 'button');
    toggleBtn.setAttribute('aria-label', 'Open Atlas AI Concierge');
    toggleBtn.innerHTML = `
      <div class="atlas-toggle-orb">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="m4.93 4.93 4.24 4.24"></path>
          <path d="m14.83 9.17 4.24-4.24"></path>
          <path d="m14.83 14.83 4.24 4.24"></path>
          <path d="m9.17 14.83-4.24 4.24"></path>
          <circle cx="12" cy="12" r="4"></circle>
        </svg>
      </div>
      <span>Atlas Concierge</span>
      <span class="atlas-toggle-badge">${navigator.platform && navigator.platform.includes('Mac') ? '⌘K' : 'Ctrl+K'}</span>
    `;
    toggleBtn.addEventListener('click', toggleChat);
    document.body.appendChild(toggleBtn);

    // 2. Chat Window
    const chatWindow = document.createElement('div');
    chatWindow.className = 'atlas-chat-window';
    chatWindow.id = 'atlasChatWindow';
    chatWindow.innerHTML = `
      <div class="atlas-chat-header">
        <div class="atlas-chat-title-group">
          <div class="atlas-toggle-orb" style="width:20px;height:20px;"></div>
          <h3>Atlas AI Concierge</h3>
          <span class="atlas-engine-tag ${geminiApiKey ? 'gemini' : ''}" id="atlasEngineTag">
            ${geminiApiKey ? 'Gemini 2.5' : 'Offline Engine'}
          </span>
        </div>
        <div class="atlas-chat-header-actions">
          <button class="atlas-icon-btn" id="atlasSettingsBtn" title="API Settings & Model" aria-label="Settings">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasClearBtn" title="Clear Chat" aria-label="Clear chat">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"></path>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasMinimizeBtn" title="Minimize" aria-label="Minimize">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasCloseBtn" title="Close" aria-label="Close">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages container -->
      <div class="atlas-chat-messages" id="atlasChatMessages">
        <div class="atlas-msg assistant">
          <div class="atlas-msg-bubble">
            <p><strong>Welcome to the Culture Atlas Concierge.</strong></p>
            <p>I can help you explore 197 ethically evaluated cultural institutions worldwide, analyze funding rosters, compare public and endowment models, or fly the 3D globe to any destination.</p>
            <div class="atlas-quick-suggestions">
              <button type="button" class="atlas-suggestion-btn" data-query="What ethically funded museums are in Tokyo?">
                🧭 What ethically funded museums are in Tokyo?
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Show me large Tier A verified institutions">
                🟢 Show me large Tier A verified institutions
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Why is Te Papa categorized as Tier B?">
                🔍 Why is Te Papa categorized as Tier B?
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Explain the ethical funding screening methodology">
                ⚖️ How is funding transparency evaluated?
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings overlay -->
      <div class="atlas-settings-modal" id="atlasSettingsModal" style="display:none;">
        <div class="atlas-settings-header">
          <h4>Concierge Settings</h4>
          <button class="atlas-icon-btn" id="atlasCloseSettingsBtn">✕</button>
        </div>
        <div class="atlas-setting-item">
          <label>Google Gemini API Key (Optional)</label>
          <input type="password" id="atlasApiKeyInput" placeholder="AIzaSy..." value="${escapeHtml(geminiApiKey)}">
          <p class="atlas-settings-desc">
            Leave blank to use the built-in offline intelligence engine. Add an API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00f2fe;text-decoration:underline;">Google AI Studio</a> to unlock full multi-turn conversational reasoning.
          </p>
        </div>
        <div class="atlas-setting-item">
          <label>Gemini Model</label>
          <select id="atlasModelSelect">
            <option value="gemini-2.5-flash" ${geminiModel === 'gemini-2.5-flash' ? 'selected' : ''}>Gemini 2.5 Flash (Recommended)</option>
            <option value="gemini-1.5-flash" ${geminiModel === 'gemini-1.5-flash' ? 'selected' : ''}>Gemini 1.5 Flash</option>
            <option value="gemini-1.5-pro" ${geminiModel === 'gemini-1.5-pro' ? 'selected' : ''}>Gemini 1.5 Pro</option>
          </select>
        </div>
        <button type="button" class="atlas-save-settings-btn" id="atlasSaveSettingsBtn">Save Settings</button>
      </div>

      <!-- Input Bar -->
      <div class="atlas-chat-input-bar">
        <input type="text" class="atlas-chat-input" id="atlasChatInput" placeholder="Ask about any museum, city, or sponsor...">
        <button type="button" class="atlas-voice-btn" id="atlasVoiceBtn" title="Voice Input" aria-label="Voice input">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="22"></line>
          </svg>
        </button>
        <button type="button" class="atlas-send-btn" id="atlasSendBtn" title="Send message" aria-label="Send message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(chatWindow);

    setupEventListeners();
    setupSpeechRecognition();
  }

  function toggleChat() {
    const win = document.getElementById('atlasChatWindow');
    if (!win) return;
    updateInstitutionsFromAtlas();
    isChatOpen = !isChatOpen;
    if (isChatOpen) {
      win.classList.add('open');
      isMinimized = false;
      win.classList.remove('minimized');
      setTimeout(() => document.getElementById('atlasChatInput')?.focus(), 200);
    } else {
      win.classList.remove('open');
    }
  }

  function setupEventListeners() {
    const win = document.getElementById('atlasChatWindow');
    const input = document.getElementById('atlasChatInput');
    const sendBtn = document.getElementById('atlasSendBtn');
    const closeBtn = document.getElementById('atlasCloseBtn');
    const minBtn = document.getElementById('atlasMinimizeBtn');
    const clearBtn = document.getElementById('atlasClearBtn');
    const settingsBtn = document.getElementById('atlasSettingsBtn');
    const closeSettingsBtn = document.getElementById('atlasCloseSettingsBtn');
    const saveSettingsBtn = document.getElementById('atlasSaveSettingsBtn');
    const messages = document.getElementById('atlasChatMessages');

    closeBtn?.addEventListener('click', () => {
      isChatOpen = false;
      win.classList.remove('open');
    });

    minBtn?.addEventListener('click', () => {
      isMinimized = !isMinimized;
      win.classList.toggle('minimized', isMinimized);
    });

    clearBtn?.addEventListener('click', () => {
      if (messages) {
        messages.innerHTML = '';
        appendAssistantMessage('Chat history cleared. How can I assist you with Culture Atlas today?');
      }
    });

    settingsBtn?.addEventListener('click', () => {
      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'flex';
    });

    closeSettingsBtn?.addEventListener('click', () => {
      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'none';
    });

    saveSettingsBtn?.addEventListener('click', () => {
      const keyInput = document.getElementById('atlasApiKeyInput');
      const modelSelect = document.getElementById('atlasModelSelect');
      const tag = document.getElementById('atlasEngineTag');

      geminiApiKey = keyInput ? keyInput.value.trim() : '';
      geminiModel = modelSelect ? modelSelect.value : 'gemini-2.5-flash';

      safeSetStorage(STORAGE_KEY_API_KEY, geminiApiKey);
      safeSetStorage(STORAGE_KEY_MODEL, geminiModel);

      if (tag) {
        tag.textContent = geminiApiKey ? 'Gemini 2.5' : 'Offline Engine';
        tag.classList.toggle('gemini', !!geminiApiKey);
      }

      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'none';
      appendAssistantMessage(
        geminiApiKey 
          ? `Connected to Google Gemini (${geminiModel})! Multi-turn conversational reasoning is now powered by Gemini.` 
          : 'Switched to Built-in Offline Intelligence Engine.'
      );
    });

    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleUserSend();
      }
    });

    sendBtn?.addEventListener('click', handleUserSend);

    messages?.addEventListener('click', (e) => {
      const btn = e.target.closest('.atlas-suggestion-btn');
      if (btn) {
        const query = btn.getAttribute('data-query');
        if (query) {
          handleQuery(query);
        }
      }
    });

    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleChat();
      }
    });
  }

  function setupSpeechRecognition() {
    const voiceBtn = document.getElementById('atlasVoiceBtn');
    const input = document.getElementById('atlasChatInput');
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRec) {
      if (voiceBtn) voiceBtn.style.display = 'none';
      return;
    }

    try {
      recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isListening = true;
        voiceBtn?.classList.add('listening');
      };

      recognition.onend = () => {
        isListening = false;
        voiceBtn?.classList.remove('listening');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (input) {
          input.value = transcript;
          handleUserSend();
        }
      };

      recognition.onerror = () => {
        isListening = false;
        voiceBtn?.classList.remove('listening');
      };

      voiceBtn?.addEventListener('click', () => {
        if (isListening) {
          recognition.stop();
        } else {
          try {
            recognition.start();
          } catch (e) {}
        }
      });
    } catch (e) {
      if (voiceBtn) voiceBtn.style.display = 'none';
    }
  }

  function appendUserMessage(text) {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return;
    const msg = document.createElement('div');
    msg.className = 'atlas-msg user';
    msg.innerHTML = `<div class="atlas-msg-bubble">${escapeHtml(text)}</div>`;
    container.appendChild(msg);
    scrollToBottom();
  }

  function appendAssistantMessage(htmlContent, actions = []) {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return;
    const msg = document.createElement('div');
    msg.className = 'atlas-msg assistant';

    let actionsHtml = '';
    if (actions && actions.length > 0) {
      actionsHtml = `<div class="atlas-actions-row">` +
        actions.map((act, idx) => `
          <button type="button" class="atlas-action-chip ${act.tier ? 'tier-' + act.tier.toLowerCase() : ''}" data-act-idx="${idx}">
            ${act.icon || '📍'} ${escapeHtml(act.label)}
          </button>
        `).join('') +
        `</div>`;
    }

    msg.innerHTML = `
      <div class="atlas-msg-bubble">
        ${htmlContent}
        ${actionsHtml}
      </div>
    `;

    if (actions && actions.length > 0) {
      const chips = msg.querySelectorAll('.atlas-action-chip');
      chips.forEach(chip => {
        const idx = parseInt(chip.getAttribute('data-act-idx'), 10);
        const action = actions[idx];
        if (action && action.handler) {
          chip.addEventListener('click', (e) => {
            e.stopPropagation();
            try {
              action.handler();
            } catch (err) {
              console.warn('Action failed', err);
            }
          });
        }
      });
    }

    container.appendChild(msg);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return null;
    const indicator = document.createElement('div');
    indicator.className = 'atlas-msg assistant typing';
    indicator.id = 'atlasTypingIndicator';
    indicator.innerHTML = `
      <div class="atlas-msg-bubble atlas-typing-indicator">
        <div class="atlas-typing-dot"></div>
        <div class="atlas-typing-dot"></div>
        <div class="atlas-typing-dot"></div>
      </div>
    `;
    container.appendChild(indicator);
    scrollToBottom();
    return indicator;
  }

  function removeTypingIndicator() {
    const ind = document.getElementById('atlasTypingIndicator');
    ind?.remove();
  }

  function scrollToBottom() {
    const container = document.getElementById('atlasChatMessages');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function handleUserSend() {
    const input = document.getElementById('atlasChatInput');
    if (!input) return;
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    handleQuery(q);
  }

  async function handleQuery(query) {
    appendUserMessage(query);
    showTypingIndicator();
    updateInstitutionsFromAtlas();

    if (geminiApiKey) {
      try {
        await handleGeminiQuery(query);
      } catch (err) {
        console.error('Gemini error, falling back to offline engine:', err);
        removeTypingIndicator();
        handleOfflineQuery(query, `*(Gemini error: ${err.message}. Showing offline results)*<br><br>`);
      }
    } else {
      setTimeout(() => {
        removeTypingIndicator();
        handleOfflineQuery(query);
      }, 300);
    }
  }

  // ==========================================
  // Offline Intelligence Engine
  // ==========================================
  function handleOfflineQuery(query, prefix = '') {
    const q = query.toLowerCase().trim();
    const actions = [];
    let responseHtml = '';

    updateInstitutionsFromAtlas();

    // 1. Methodology & Philosophy queries
    if (q.includes('method') || q.includes('criteria') || q.includes('how') && (q.includes('evaluate') || q.includes('tier') || q.includes('score') || q.includes('calculated') || q.includes('work'))) {
      responseHtml = `
        <p><strong>Culture Atlas Evaluation Methodology</strong></p>
        <p>Culture Atlas maps cultural institutions whose sponsors have never drawn an objection, evaluated by who funds them. Checked against official annual reports, partner listings, and public disclosures:</p>
        <ul>
          <li><strong>Tier A (Verified · 125 institutions)</strong>: Pure public benefit, municipal funding, or independent foundation endowment with strict ethical screening. Free of controversial underwriters.</li>
          <li><strong>Tier B (One name to know · 55 institutions)</strong>: High transparency, but has a corporate partner to note on its roster (e.g. fossil-finance banks, surveillance tech).</li>
          <li><strong>Tier U (Unverified · 17 institutions)</strong>: Public disclosures under review or awaiting updated partner indices.</li>
        </ul>
        <p>Excluded from the atlas entirely: institutions that retained sponsors linked to fossil fuel extraction, arms/defense manufacturing, opioids, tobacco, gambling, or sanctioned state entities.</p>
      `;
      actions.push({
        label: 'Show Verified (Tier A)',
        tier: 'A',
        icon: '🟢',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['A']));
          appendAssistantMessage('Filtered map to Tier A Verified institutions only.');
        }
      });
      actions.push({
        label: 'Show One Name To Know (Tier B)',
        tier: 'B',
        icon: '🔵',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['B']));
          appendAssistantMessage('Filtered map to Tier B institutions.');
        }
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 2. Specific Tier Filter queries
    if (q.includes('tier a') || q.includes('verified institutions')) {
      const tierA = institutions.filter(i => i.t === 'A');
      responseHtml = `
        <p><strong>Tier A: Verified Cultural Institutions (${tierA.length})</strong></p>
        <p>These institutions operate with transparent, ethically vetted funding models, primarily supported by civic municipal grants, national arts councils, or independent philanthropic trusts without corporate compromise.</p>
      `;
      actions.push({
        label: 'Filter Map to Tier A',
        tier: 'A',
        icon: '🟢',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['A']));
        }
      });
      tierA.slice(0, 3).forEach(inst => {
        actions.push({
          label: `Fly to ${inst.n} (${inst.c.split(',')[0]})`,
          icon: '📍',
          handler: () => triggerSelectInstitution(inst)
        });
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 3. Institution lookup by name
    const matchingInst = institutions.find(i => {
      const name = i.n.toLowerCase();
      return q.includes(name) || (name.includes(q) && q.length > 3);
    });

    if (matchingInst) {
      const tierInfo = TIERS[matchingInst.t] || TIERS.U;
      responseHtml = `
        <p><strong>${escapeHtml(matchingInst.n)}</strong> <span style="color:${tierInfo.color};font-weight:600;">· ${tierInfo.label}</span></p>
        <p>📍 <em>${escapeHtml(matchingInst.c)}</em> (${matchingInst.s === 'L' ? 'Large' : 'Small/Mid-sized'})</p>
        <p><strong>Funding & Governance:</strong><br>${escapeHtml(matchingInst.f)}</p>
        ${matchingInst.w ? `<p><strong>Watch Notes:</strong><br>${escapeHtml(matchingInst.w)}</p>` : ''}
      `;

      actions.push({
        label: `Inspect ${matchingInst.n} on Globe`,
        icon: '🌍',
        handler: () => triggerSelectInstitution(matchingInst)
      });

      if (matchingInst.u && matchingInst.u.length > 0) {
        actions.push({
          label: 'Official Source / Report',
          icon: '↗',
          handler: () => window.open(matchingInst.u[0], '_blank')
        });
      }

      appendAssistantMessage(prefix + responseHtml, actions);
      triggerSelectInstitution(matchingInst);
      return;
    }

    // 4. Geographic queries (cities & countries)
    const matchedInsts = institutions.filter(i => {
      const loc = i.c.toLowerCase();
      return q.includes(loc) || loc.split(',').some(part => q.includes(part.trim().toLowerCase()) && part.trim().length > 2);
    });

    if (matchedInsts.length > 0) {
      const cityName = matchedInsts[0].c.split(',')[0].trim();
      const countryName = matchedInsts[0].c.split(',')[1]?.trim() || '';
      responseHtml = `
        <p>Found <strong>${matchedInsts.length}</strong> institutions in <strong>${escapeHtml(cityName || countryName)}</strong>:</p>
        <ul>
          ${matchedInsts.slice(0, 5).map(i => `
            <li>
              <strong>${escapeHtml(i.n)}</strong> 
              <span style="color:${TIERS[i.t]?.color || '#888'}">(${TIERS[i.t]?.label})</span> — ${escapeHtml(i.s === 'L' ? 'Large' : 'Small/Mid')}
            </li>
          `).join('')}
        </ul>
        ${matchedInsts.length > 5 ? `<p><em>...and ${matchedInsts.length - 5} more.</em></p>` : ''}
      `;

      actions.push({
        label: `Filter by ${cityName}`,
        icon: '📍',
        handler: () => {
          if (window.Atlas?.filterCity) window.Atlas.filterCity(cityName);
          flyToCoordinates(matchedInsts[0].lo, matchedInsts[0].la, 4);
        }
      });

      matchedInsts.slice(0, 3).forEach(inst => {
        actions.push({
          label: inst.n,
          tier: inst.t,
          icon: '🏛️',
          handler: () => triggerSelectInstitution(inst)
        });
      });

      appendAssistantMessage(prefix + responseHtml, actions);
      flyToCoordinates(matchedInsts[0].lo, matchedInsts[0].la, 3.5);
      return;
    }

    // 5. Size queries
    if (q.includes('large') || q.includes('major') || q.includes('big') || q.includes('20m')) {
      const large = institutions.filter(i => i.s === 'L');
      responseHtml = `
        <p><strong>Large Cultural Institutions (${large.length})</strong></p>
        <p>Defined as institutions with annual budgets exceeding ~$20M or drawing over 500,000 visitors per year.</p>
        <p>Notable large ethical institutions include <em>ARoS (Aarhus)</em>, <em>Te Papa (Wellington)</em>, and <em>Museum of New Zealand</em>.</p>
      `;
      actions.push({
        label: 'Filter Large Only',
        icon: '🔍',
        handler: () => { if (window.Atlas?.selectSize) window.Atlas.selectSize('L'); }
      });
      actions.push({
        label: 'Show All Sizes',
        icon: '🌐',
        handler: () => { if (window.Atlas?.selectSize) window.Atlas.selectSize('all'); }
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 6. Surprise Me / Discovery
    if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('explore')) {
      const pick = institutions[Math.floor(Math.random() * institutions.length)];
      responseHtml = `
        <p>✨ <strong>Featured Institution: ${escapeHtml(pick.n)}</strong></p>
        <p>📍 <em>${escapeHtml(pick.c)}</em> · <span style="color:${TIERS[pick.t]?.color}">${TIERS[pick.t]?.label}</span></p>
        <p>${escapeHtml(pick.w || pick.f)}</p>
      `;
      actions.push({
        label: `Inspect ${pick.n}`,
        icon: '🌍',
        handler: () => triggerSelectInstitution(pick)
      });
      actions.push({
        label: 'Show Another',
        icon: '🎲',
        handler: () => handleOfflineQuery('surprise me')
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      triggerSelectInstitution(pick);
      return;
    }

    // 7. Fallback response
    responseHtml = `
      <p>I can help you search or analyze any of the <strong>197 cultural institutions</strong> on Culture Atlas.</p>
      <p>Try asking:</p>
      <ul>
        <li><em>"Find museums in Copenhagen"</em> or <em>"What's in Australia?"</em></li>
        <li><em>"Tell me about Audain Art Museum"</em></li>
        <li><em>"Which institutions have budgets over $20M?"</em></li>
        <li><em>"How do you evaluate corporate sponsorship?"</em></li>
      </ul>
      <p><small>💡 Tip: You can also tap the ⚙️ icon in the header to connect Google Gemini for deeper comparative reasoning.</small></p>
    `;

    actions.push({
      label: 'Surprise Me',
      icon: '✨',
      handler: () => handleOfflineQuery('surprise me')
    });
    actions.push({
      label: 'Switch to City List View',
      icon: '📋',
      handler: () => { if (window.Atlas?.toggleView) window.Atlas.toggleView('list'); }
    });

    appendAssistantMessage(prefix + responseHtml, actions);
  }

  // ==========================================
  // Google Gemini API Integration
  // ==========================================
  async function handleGeminiQuery(query) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${geminiApiKey}`;

    const summaryData = institutions.slice(0, 50).map(i => ({
      name: i.n,
      location: i.c,
      tier: i.t,
      size: i.s,
      funding: i.f,
      note: i.w,
      lat: i.la,
      lon: i.lo
    }));

    const systemInstruction = `
You are the Atlas AI Concierge, a brilliant assistant for "Culture Atlas".
Culture Atlas maps 197 cultural institutions across the globe evaluated by their ethical funding transparency and freedom from controversial sponsorship.
Tiers:
- Tier A (Verified): 125 institutions with clean funding, public benefit, or independent endowment.
- Tier B (One name to know): 55 institutions with notable corporate underwriting.
- Tier U (Unverified): 17 institutions awaiting updated disclosures.

Institutions Data Summary:
${JSON.stringify(summaryData)} (and 147 more available)

When relevant, you can include actionable commands in your response using special tags:
- [[FLY:longitude,latitude,zoom:Label]] to create a flight button to a location.
- [[SELECT:ExactInstitutionName]] to create an inspection button for an institution.
- [[FILTER:CityOrCountry]] to create a location filter button.
- [[TIER:A]] or [[TIER:B]] to filter by tier.

Keep responses engaging, informative, and formatted with clean markdown.
`;

    const body = {
      contents: [{ role: 'user', parts: [{ text: query }] }],
      systemInstruction: { parts: [{ text: systemInstruction }] },
      generationConfig: { temperature: 0.7, maxOutputTokens: 1000 }
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    removeTypingIndicator();

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.error?.message || `HTTP ${res.status}`);
    }

    const data = await res.json();
    let text = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response generated.';

    const actions = [];
    const flyRegex = /\\[\\[FLY:([-0-9.]+),([-0-9.]+),([0-9.]+):([^\\]]+)\\]\\]/g;
    let match;
    while ((match = flyRegex.exec(text)) !== null) {
      const [, lon, lat, zoom, label] = match;
      actions.push({
        label: label.trim(),
        icon: '📍',
        handler: () => flyToCoordinates(parseFloat(lon), parseFloat(lat), parseFloat(zoom))
      });
    }
    text = text.replace(flyRegex, '');

    const selectRegex = /\\[\\[SELECT:([^\\]]+)\\]\\]/g;
    while ((match = selectRegex.exec(text)) !== null) {
      const [, instName] = match;
      const inst = institutions.find(i => i.n.toLowerCase() === instName.trim().toLowerCase());
      if (inst) {
        actions.push({
          label: `Inspect ${inst.n}`,
          icon: '🏛️',
          handler: () => triggerSelectInstitution(inst)
        });
      }
    }
    text = text.replace(selectRegex, '');

    const filterRegex = /\\[\\[FILTER:([^\\]]+)\\]\\]/g;
    while ((match = filterRegex.exec(text)) !== null) {
      const [, loc] = match;
      actions.push({
        label: `Filter by ${loc.trim()}`,
        icon: '🔍',
        handler: () => { if (window.Atlas?.filterCity) window.Atlas.filterCity(loc.trim()); }
      });
    }
    text = text.replace(filterRegex, '');

    const tierRegex = /\\[\\[TIER:([ABU])\\]\\]/g;
    while ((match = tierRegex.exec(text)) !== null) {
      const [, t] = match;
      actions.push({
        label: `Show Tier ${t}`,
        tier: t,
        icon: t === 'A' ? '🟢' : t === 'B' ? '🔵' : '⚪',
        handler: () => { if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set([t])); }
      });
    }
    text = text.replace(tierRegex, '');

    appendAssistantMessage(formatMarkdown(text), actions);
  }

  function formatMarkdown(md) {
    let html = escapeHtml(md);
    html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    html = html.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 4px;border-radius:4px;font-size:12px;">$1</code>');
    html = html.replace(/\\n\\n+/g, '</p><p>');
    html = html.replace(/\\n/g, '<br>');
    html = `<p>${html}</p>`;
    html = html.replace(/<p><\\/p>/g, '');
    return html;
  }

  function triggerSelectInstitution(inst) {
    if (window.Atlas?.selectInstitution) {
      window.Atlas.selectInstitution(inst);
    }
    if (window.AtlasGlobe?.flyTo) {
      window.AtlasGlobe.flyTo(inst.lo, inst.la, 6);
    }
  }

  function flyToCoordinates(lon, lat, zoom = 4) {
    if (window.AtlasGlobe?.flyTo) {
      window.AtlasGlobe.flyTo(lon, lat, zoom);
    }
  }

  // Safe initialize
  function initConcierge() {
    createChatUI();
    updateInstitutionsFromAtlas();
  }

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initConcierge);
  } else {
    initConcierge();
  }

  window.AtlasConcierge = {
    open: () => { if (!isChatOpen) toggleChat(); },
    close: () => { if (isChatOpen) toggleChat(); },
    ask: handleQuery,
    setApiKey: (key) => {
      geminiApiKey = key;
      safeSetStorage(STORAGE_KEY_API_KEY, key);
      const tag = document.getElementById('atlasEngineTag');
      if (tag) {
        tag.textContent = key ? 'Gemini 2.5' : 'Offline Engine';
        tag.classList.toggle('gemini', !!key);
      }
    }
  };

})();
'''

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/assets/chat.js', 'w') as f:
    f.write(chat_code)

print("Generated robust chat.js with embedded data and storage safety!")
