import re

def update_build_conversational_atlas():
    with open("build_conversational_atlas.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update curatorSettingsBtn in sheetOpenControls
    old_btn = """            <!-- Settings Button -->
            <button id="curatorSettingsBtn" class="p-1.5 bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#a1a1aa] hover:text-white rounded-lg text-[14px] transition shrink-0" title="Curator Settings">
              <span>⚙️</span>
            </button>"""

    new_btn = """            <!-- Live AI / Critical Engine Status & Settings Button -->
            <button id="curatorSettingsBtn" class="flex items-center gap-1.5 px-2.5 py-1 bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white rounded-xl text-[14px] transition shrink-0 shadow-sm" title="Curator Intelligence Settings & API Status">
              <span id="curatorStatusDot" class="w-2 h-2 rounded-full bg-amber-400"></span>
              <span id="curatorStatusLabel" class="hidden sm:inline font-mono text-[14px]">Offline Engine</span>
              <span class="text-[14px]">⚙️</span>
            </button>"""

    if old_btn in content:
        content = content.replace(old_btn, new_btn, 1)
        print("Updated curatorSettingsBtn in header bar")
    else:
        print("Warning: old curatorSettingsBtn not found")

    # 2. Update curatorInquiryRow prompt suggestions
    old_prompts_match = re.search(r'(<div id="curatorInquiryRow".*?)(<div class="p-2 sm:p-3 bg-\[#171717\] shrink-0 border-t border-\[#222222\]">)', content, re.DOTALL)
    if old_prompts_match:
        new_prompts = """<div id="curatorInquiryRow" class="max-w-3xl mx-auto w-full px-3 sm:px-6 py-1.5 flex items-center gap-2 overflow-x-auto custom-scrollbar shrink-0 text-[14px] whitespace-nowrap">
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Tell me about London's art scene, independent spaces, and divestment history" data-city="London">
            <span>London art scene</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="What is Beyond Objecthood and how did the exhibition become a critical form?">
            <span>Beyond Objecthood</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="What does e-flux say about the museum as a factory and duty-free art?">
            <span>e-flux: Museum as factory</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Explain the three waves of institutional critique from Hans Haacke to Nan Goldin and Strike MoMA">
            <span>3 Waves of Critique</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Why is MoMA excluded from Culture Atlas?">
            <span>Why MoMA is excluded</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Which cultural spaces offer always free admission?">
            <span>Free admission</span>
          </button>
        </div>
        """
        content = content[:old_prompts_match.start()] + new_prompts + content[old_prompts_match.start(2):]
        print("Updated prompt suggestion chips")

    # 3. Update Settings Modal HTML
    old_modal_pattern = r'<!-- ⚙️ CURATOR SETTINGS MODAL.*?</script>\s*<script>\s*// Embedded Data Sources'
    # Let's inspect where the modal ends
    old_modal_start = content.find('<!-- ⚙️ CURATOR SETTINGS MODAL')
    old_modal_end = content.find('// Embedded Data Sources (Enriched by Researcher Pipeline)')
    if old_modal_start != -1 and old_modal_end != -1:
        # We replace the modal and the script tag opening
        new_modal = """<!-- ⚙️ CURATOR INTELLIGENCE SETTINGS MODAL (Multi-Provider API Support) -->
  <!-- ========================================================================= -->
  <div id="curatorSettingsModal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
    <div class="bg-[#18181b] border border-[#2e2e2e] rounded-3xl max-w-lg w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[92vh] overflow-y-auto custom-scrollbar">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#2e2e2e] pb-3 shrink-0">
        <div class="flex items-center gap-2.5">
          <span class="text-[24px]">🏛️</span>
          <div>
            <h3 class="font-medium text-white text-[18px]">Curator Intelligence Settings</h3>
            <p class="text-[14px] text-[#a1a1aa]">Power conversational reasoning with live AI or use the built-in critical engine</p>
          </div>
        </div>
        <button id="closeSettingsModalBtn" class="text-[#a1a1aa] hover:text-white text-[18px] p-1.5 hover:bg-[#262626] rounded-xl transition">✕</button>
      </div>

      <!-- Provider Tabs -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-medium">AI Intelligence Provider</label>
        <div class="grid grid-cols-3 gap-2">
          <button id="providerClaudeBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#3e3e3e] bg-[#27272a] text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🟣</span> <span>Claude</span>
          </button>
          <button id="providerOpenAIBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🟢</span> <span>OpenAI</span>
          </button>
          <button id="providerGeminiBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🔵</span> <span>Gemini</span>
          </button>
        </div>
        <div id="providerTip" class="text-[14px] text-[#a1a1aa] pt-1">
          Recommended: <strong>Claude 3.5 / Haiku 4.5</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and nuanced institutional analysis.
        </div>
      </div>

      <!-- API Key Input -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label class="block text-[14px] text-[#a1a1aa] font-medium">API Key</label>
          <span id="keyDetectBadge" class="text-[14px] font-mono text-[#a1a1aa]">Auto-detecting provider...</span>
        </div>
        <div class="relative flex items-center">
          <input 
            type="password" 
            id="aiApiKeyInput" 
            placeholder="Paste sk-ant-... or sk-... or AIzaSy..." 
            class="w-full bg-[#212121] border border-[#333333] text-[14px] text-white px-3.5 py-2.5 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono pr-10"
          />
          <button id="toggleKeyVisibilityBtn" class="absolute right-3 text-[#71717a] hover:text-white text-[14px] p-1" title="Toggle visibility">👁️</button>
        </div>
        <div class="text-[14px] text-[#71717a] flex items-center justify-between">
          <span>Tip: You can also paste your API key straight into the chat box anytime!</span>
        </div>
      </div>

      <!-- Model Selector -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-medium">Model</label>
        <select id="aiModelSelect" class="w-full bg-[#212121] border border-[#333333] text-white text-[14px] px-3.5 py-2 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono">
          <option value="claude-haiku-4-5-20251001">claude-haiku-4-5-20251001 (Fast & Articulate - Recommended)</option>
          <option value="claude-sonnet-4-5-20250929">claude-sonnet-4-5-20250929 (Deep Critical Reasoning)</option>
        </select>
      </div>

      <!-- Connection Test Status Box -->
      <div id="connectionTestBox" class="hidden p-3 rounded-xl text-[14px] border flex items-center gap-2">
        <span id="testStatusIcon">⏳</span>
        <span id="testStatusMsg" class="font-mono">Testing connection...</span>
      </div>

      <!-- Privacy Assurance -->
      <div class="p-3 bg-[#212121] border border-[#2e2e2e] rounded-xl text-[14px] text-[#a1a1aa] leading-relaxed">
        <p>
          🔒 <strong>100% Client-Side Privacy:</strong> Your key is saved strictly in your local browser's <code class="text-white font-mono text-[14px]">localStorage</code>. Requests are sent directly from your browser to the provider's API. No intermediate backend logs your keys.
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-2.5 pt-2 border-t border-[#2e2e2e]">
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <button id="testConnectionBtn" class="px-3.5 py-2 bg-[#27272a] hover:bg-[#333338] border border-[#3e3e3e] text-white text-[14px] rounded-xl transition flex-1 sm:flex-initial">
            Test Connection
          </button>
          <button id="clearApiKeyBtn" class="px-3 py-2 text-[#f87171] hover:bg-rose-500/10 rounded-xl text-[14px] transition flex-1 sm:flex-initial">
            Disconnect
          </button>
        </div>
        <button id="saveApiKeyBtn" class="w-full sm:w-auto px-5 py-2 bg-white hover:bg-neutral-200 text-black text-[14px] font-medium rounded-xl transition shadow-sm">
          Save & Connect
        </button>
      </div>

    </div>
  </div>

  <script>
    """
        content = content[:old_modal_start] + new_modal + content[old_modal_end:]
        print("Updated Settings Modal HTML")
    else:
        print("Warning: Could not find settings modal boundaries")

    with open("build_conversational_atlas.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Saved build_conversational_atlas.py (Phase 1)!")

if __name__ == "__main__":
    update_build_conversational_atlas()
