# Culture Atlas

> **Ethically funded cultural institutions across the world**

An interactive 3D geospatial globe, ledger, and analysis tool mapping cultural institutions globally based on ethical funding transparency. Every institution is evaluated against corporate underwriting records, annual reports, partner pages, and public disclosures.

---

## 🌟 Features

- **🤖 Built-in AI Concierge & Conversational Experience**:
  - **Instant Offline Intelligence**: Natural language question answering and recommendation engine over all 197 institutions with zero setup or API keys required.
  - **Interactive Map Control**: Conversational responses generate interactive action chips (`[📍 Fly to Tokyo]`, `[🏛️ Inspect Te Papa]`, `[🟢 Filter Tier A]`) that manipulate the live 3D globe and filters.
  - **Google Gemini API Integration (Optional / BYOK)**: Connect your Google AI Studio API key in settings (⚙️) to unlock full multi-turn conversational reasoning, comparative analyses, and custom travel itineraries powered by **Gemini 2.5 Flash**.
  - **🎙️ Voice Input**: Dictate questions hands-free via the Web Speech API mic button.
  - **⌨️ Keyboard Shortcut**: Press `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux) anytime to toggle the concierge.

- **🌍 Interactive 3D D3 Globe**:
  - Physics-based rotation with inertial momentum deceleration.
  - Multi-touch pinch-to-zoom and mouse wheel exponential scaling.
  - Atmospheric bloom shader (`feGaussianBlur` + `feMerge`), ocean radial gradients, and rim light shaders.
  - Country polygon boundaries rendered from TopoJSON with hover highlights.
  - Interactive city pills and institution markers.
  - Kinetic flight transitions (`flyTo`) when selecting any institution, city, or country.
  - Keyboard navigation (arrow keys to rotate, `+`/`-` to zoom, `Esc` to deselect).

- **🏛️ 197 Cultural Institutions Mapped**:
  - **Tier A (🟢 Verified - 125 institutions)**: Fully verified clean funding roster, municipal/endowment backing, strict ethical gift-acceptance policies.
  - **Tier B (🔵 One name to know - 55 institutions)**: Flagged for a specific corporate sponsor to note (e.g., fossil finance, corporate surveillance).
  - **Tier U (⚪ Roster unverified - 17 institutions)**: Pending updated disclosures.

- **🔍 Search & Filtering**:
  - Real-time instant search across institutions, cities, and countries.
  - Filter by funding tier and institution size (Large: >$20M budget / >500k visitors vs. Small & Mid).
  - One-click geographic filtering by city or country.

- **📊 Dual View Modes**:
  - **Globe View**: 3D interactive spatial globe visualization with a live detail inspection drawer.
  - **City List / Table View**: Comprehensive tabular breakdown with budgets, watch notes, and direct links to official annual reports and disclosures.

- **📱 Progressive Web App (PWA)**:
  - Installable on desktop, iOS, and Android.
  - Service worker caching for 100% offline capability.
  - Standalone fullscreen display mode.

---

## 🚀 Quick Start

### Option 1: Python HTTP Server (Zero Dependencies)

Run the included server script:

```bash
cd app
python3 serve.py
```

Or using Python's built-in module:

```bash
cd app
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

---

### Option 2: Node.js / npx

```bash
cd app
npx serve . -p 8080
```

---

## 🤖 Using the Atlas Concierge

1. Click the glowing **Atlas Concierge** orb in the lower right corner, or press `Cmd+K` / `Ctrl+K`.
2. Try asking:
   - *"What ethically funded museums are in Tokyo?"*
   - *"Why is Te Papa categorized as Tier B?"*
   - *"Show me large Tier A verified institutions"*
   - *"How is funding transparency evaluated?"*
   - *"Recommend a hidden gem in Scandinavia"*
3. Click any returned action chip (`[📍 View on Globe]`, `[🏛️ Inspect Dossier]`) to fly the 3D globe to that destination.
4. *(Optional)* Click the gear icon (⚙️) in the concierge header to enter your **Google Gemini API Key** for open-ended conversational reasoning.

---

## 📁 Project Structure

```
sponsor-atlas/
├── app/
│   ├── index.html              # Main application entry point
│   ├── manifest.json           # Web app manifest for PWA installation
│   ├── icon.svg                # Vector app icon
│   ├── sw.js                   # Service worker for offline caching (v2)
│   ├── world-topo.json         # TopoJSON world geometry for the globe
│   ├── institutions.json       # Clean JSON dataset of all 197 institutions
│   ├── serve.py                # Standalone Python local web server
│   └── assets/
│       ├── index-Crf6FBR0.js   # Compiled React + D3 Geo application bundle
│       ├── index-i96-xYS5.css  # Cyberpunk/dark theme stylesheet
│       ├── chat.js             # AI Concierge engine (Offline + Gemini API + Map bridge)
│       └── chat.css            # Translucent neon chat UI styling
├── institutions.json           # Root dataset copy for easy access
├── parse_to_json.py           # Script that parses raw data into JSON
└── README.md                   # This documentation
```

---

## 📊 Dataset Schema

Each entry in `institutions.json` has the following fields:

```json
{
  "name": "ARoS",
  "location": "Aarhus, Denmark",
  "tier": "A",
  "size": "L",
  "funding": "DKK 125M budget, 600k visitors. Aarhus Municipal Council, Danish Ministry of Culture, ticket sales, and Salling Foundations.",
  "watch": "Major Danish art museum topped by Olafur Eliasson's 'Your rainbow panorama'. Financed primarily by municipal funds and the philanthropic Salling Fondene; clean ethical sponsorship policy.",
  "sources": [
    "https://www.aros.dk/en/about-aros/",
    "https://sallingfondene.dk"
  ],
  "lat": 56.153,
  "lon": 10.2
}
```

---

## 🛠️ Verification & Methodology

- **Clean Status (Tier A)**: Institutions with no current fossil fuel, weapons/defense, opioid, tobacco, gambling, or sanctioned state sponsorship.
- **Data Cutoff**: Verified against annual reports, partner listings, and public disclosures up to late September 2026.
