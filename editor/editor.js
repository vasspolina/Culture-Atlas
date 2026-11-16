/* The data editor (tools/editor.py serves it). Every record of institutions.json, one field at a time, under a plain label,
   with lists drawn as lists and nested records as cards, so a record reads as what it says rather than as a string of JSON.

   With tools/editor.py running, Save writes the record back to institutions.json and each field is checked against the
   wording rules of tools/lint_text.py as it is typed. Opened as a plain file or from a static server, the page still reads
   and edits, and Save downloads a whole institutions.json to put in the repository by hand. */
(() => {
  'use strict';

  // ---- What each field is called, what it is for, and how it is grouped -------------------------------------------------

  const GROUPS = [
    ['Identity', ['name', 'shortName', 'id', 'former_ids', 'aliases', 'category', 'tier', 'tier_note', 'size', 'year_founded']],
    ['Place and visit', ['location', 'city', 'country', 'address', 'lat', 'lon', 'website', 'visit_url', 'opening_hours',
      'admission_fee', 'admission_policy', 'admission_details', 'accessibility', 'architecture_status', 'highlight']],
    ['Funding', ['grade', 'grade_basis', 'funding', 'flags', 'why_flagged', 'watch', 'funder_links', 'propaganda',
      'epstein_records', 'wikileaks_records']],
    ['Records and accounts', ['records_note', 'finances_note', 'affiliations_note', 'finance', 'scale', 'bureaucracy',
      'red_tape', 'audit_dossier_url', 'statutory_filings_url']],
    ['Dossier', ['details']],
    ['Reports and critique', ['gossip_data', 'case_notes', 'other_findings', 'critique_note', 'visual_critiques',
      'study_notes', 'case_study']],
    ['Sources', ['sources', 'field_sources', 'research_retrieved', 'links']],
  ];

  // Labels by key, wherever the key sits. A key not named here is shown with its underscores turned to spaces.
  const LABELS = {
    name: 'Name', shortName: 'Short name', id: 'Record id', former_ids: 'Former ids', aliases: 'Other names', category: 'Category',
    tier: 'Tier', tier_note: 'Tier note', size: 'Size', year_founded: 'Founded', location: 'Location line', city: 'City',
    country: 'Country', address: 'Address', lat: 'Latitude', lon: 'Longitude', website: 'Website', visit_url: 'Visit page',
    opening_hours: 'Opening hours', admission_fee: 'Admission', admission_policy: 'Admission policy',
    admission_details: 'Admission details', accessibility: 'Accessibility', architecture_status: 'Building',
    highlight: 'Highlight', grade: 'Funding grade', grade_basis: 'Why this grade', funding: 'Who funds it', flags: 'Flags',
    why_flagged: 'Why flagged', watch: 'Description', funder_links: 'Shared funders', propaganda: 'Propaganda record',
    epstein_records: 'Epstein files', wikileaks_records: 'WikiLeaks documents', records_note: 'What it publishes',
    finances_note: 'Finances', affiliations_note: 'Affiliations', finance: 'Accounts in figures', scale: 'Scale',
    bureaucracy: 'Governance', red_tape: 'Official review', audit_dossier_url: 'Audit dossier',
    statutory_filings_url: 'Statutory filings', details: 'Dossier', gossip_data: 'Reports', case_notes: 'Case notes',
    other_findings: 'Other findings', critique_note: 'Critique note', visual_critiques: 'Critiques', study_notes: 'Studies',
    case_study: 'Case study', sources: 'Sources', field_sources: 'Where each field comes from',
    research_retrieved: 'Research checked on', links: 'Links',
    // nested
    overview: 'Overview', funding_verdict: 'Funding verdict', red_flags: 'Red flags', not_related: 'Not related',
    wider_context: 'Wider context', bottom_line: 'Bottom line', retrieved: 'Checked on', press: 'Press', overall: 'Overall',
    items: 'Items', headline: 'Headline', said: 'What is said', who_says: 'Who says it', where: 'Where', when: 'When',
    urls: 'Addresses', kind: 'Kind', status: 'Status', response: 'Reply', outcome: 'Outcome', retrieved_on: 'Checked on',
    rule: 'Rule', title: 'Title', meta: 'Dates', text: 'Text', period: 'Period', mechanism: 'Mechanism', summary: 'Summary',
    authors: 'Authors', year: 'Year', journal: 'Journal', doi: 'DOI', date: 'Date', doc_id: 'Document', what_shows: 'What it shows',
    flags_added: 'Flags added', person: 'Person', link: 'Link', tie: 'Tie', consequence: 'Consequence', note: 'Note',
    url: 'Address', funder: 'Funder', institutions: 'Spaces it funds', fy: 'Financial year', currency: 'Currency',
    income: 'Income', expenditure: 'Spending', public: 'Public money', private: 'Private money', earned: 'Earned income',
    net_assets: 'Net assets', source_kind: 'Source', visitors: 'Visitors', visitors_year: 'Visitors in', legal_form: 'Legal form',
    budget_set_by: 'Budget set by', controls: 'Controls', level: 'Level', level_basis: 'Why this level', basis: 'Basis',
    strategy: 'Frame', strategy_id: 'Frame id', target: 'Applies to', quotes: 'Quotes', author: 'Author',
    publication: 'Publication', historical_impact: 'Question it asks', real_cases: 'Case files', accounts: 'Staff and visitor posts',
    gossip: 'Press reports', case_id: 'Case', topics: 'Topics', event_date: 'Event date', latest_source_date: 'Latest source',
    facts: 'Facts', claims: 'Claims', limits: 'Limits', follow_up: 'Follow up', publisher: 'Publisher', published: 'Published',
    scope: 'About', fields: 'Fields', kick: 'Kicker', bullets: 'Points', stats: 'Figures', coordinates: 'Coordinates',
  };

  const HELP = {
    name: 'As the space calls itself. The map, the chat and the search all match on it.',
    id: 'Other files point to this id, so it is not changed here.',
    former_ids: 'Old ids that still lead here. Kept so old links work.',
    aliases: 'Other spellings the search and the chat should find it by. One per line.',
    tier: 'A, clean: a source is cited. B, flagged: there is a recorded reason. U: unverified. Rebuild turns A into U when no independent source backs it, and B into U when no reason is recorded.',
    size: 'S, M or L.',
    location: 'The line under the name: city, country.',
    grade: 'Worked out from the funding text, the flags and the sources by tools/grade_funding.py on every rebuild.',
    funding: 'Who pays for it, named. Kept under 30 words; amounts and shares if the record has them.',
    flags: 'One flag per line, with the spelling the filters use (Fossil fuels, Tobacco, Arms…).',
    why_flagged: 'The sentence that says what the flag rests on.',
    watch: 'The short description at the head of the record. Kept under 25 words.',
    records_note: 'What the space itself publishes: reports, accounts, a board, a sponsor list.',
    other_findings: 'Each finding on its own line. Stored as one text, the findings joined by a vertical bar.',
    sources: 'One address per line. Only what backs a field the record shows.',
  };

  // Fields that a tool writes. They are shown, not edited, with where to change them instead.
  const READONLY = [
    [p => p === 'id' || p === 'former_ids', 'Other files and links point to it.'],
    [p => p === 'grade' || p === 'grade_basis', 'Worked out by tools/grade_funding.py on every rebuild. Change the funding, the flags or the sources instead.'],
    [p => p === 'gossip_data.gossip', 'Written from data/gossip_items.json by tools/attach_gossip.py. Edit the item there.'],
    [p => p === 'gossip_data.real_cases', 'Written from the case findings by tools/import_gossip_findings.py.'],
    [p => p === 'funder_links', 'Worked out from the funding text across all records.'],
  ];
  const readonlyItem = (path, v) => (path === 'visual_critiques' && v && v.kind === 'theory')
    ? 'A critical frame, written by tools/attach_critiques.py from data/research_attach/institutional_critiques.json.' : null;

  // Strings stored joined, shown as a list.
  const JOINED = { other_findings: ' | ' };
  // Keys whose text is prose: set in a reading face and checked for wording.
  const PROSE_KEYS = new Set(['funding', 'watch', 'why_flagged', 'records_note', 'finances_note', 'affiliations_note',
    'critique_note', 'other_findings', 'highlight', 'tier_note', 'grade_basis', 'funding_verdict', 'bottom_line', 'overview',
    'red_flags', 'not_related', 'wider_context', 'overall', 'text', 'summary', 'said', 'response', 'outcome', 'what_shows',
    'tie', 'consequence', 'note', 'historical_impact', 'level_basis', 'facts', 'claims', 'limits', 'follow_up', 'bullets', 'kick']);
  // Keys with a short list of values; the page suggests the ones already in use.
  const SUGGEST_KEYS = new Set(['tier', 'size', 'country', 'flags', 'status', 'who_says', 'kind', 'legal_form', 'budget_set_by',
    'source_kind', 'currency', 'mechanism', 'category', 'basis', 'link', 'topics']);
  const WORD_LIMIT = { funding: 30, watch: 25 };

  // What each wording rule of tools/lint_text.py means, in a sentence.
  const RULES = {
    'dash': 'A dash in prose. The atlas uses a comma or a full stop instead.',
    'quote-mix': 'Curly and straight quotation marks in one text.',
    'semicolon-chain': 'Two or more semicolons in a row of clauses. Split it into sentences.',
    'hedge': 'A hedge. Say what the source says, or leave it out.',
    'filler': 'Praise or filler. Name the thing instead.',
    'empty': 'An empty phrase that adds no fact.',
    'verdict': 'A verdict of the editor’s own. Report what was said and by whom.',
    'frame': 'A framing phrase. Say what the criticism is.',
    'vague': 'A funder left unnamed. Name them, or say the record does not.',
    'over': 'Longer than this field allows.',
    'visitor count in funding': 'A visitor count in the funding text. It belongs in Scale.',
    'no-site boilerplate': 'Boilerplate about the site. Say what it publishes, or leave the note out.',
    'lower-case start': 'The text starts with a small letter.',
  };

  // ---- State -------------------------------------------------------------------------------------------------------------

  const $ = (s, el = document) => el.querySelector(s);
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else if (k in n && typeof v !== 'string') n[k] = v;
      else n.setAttribute(k, v === true ? '' : v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) n.append(c);
    return n;
  };
  const clone = v => JSON.parse(JSON.stringify(v));
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  let records = [];          // as loaded (or as last saved)
  let byId = new Map();
  const drafts = new Map();  // id -> edited copy, only for records opened
  let problems = {};         // id -> [{field, problem}]
  let live = false;          // tools/editor.py is serving the page
  let current = null;        // id of the open record
  let view = 'fields';       // 'fields' | 'raw'
  let suggestions = {};      // key -> [values]
  let topKeys = [];          // every top-level key in the file, for Add field
  let lintTimer = 0;

  const draft = id => drafts.get(id) || byId.get(id);
  const isChanged = id => drafts.has(id) && !same(drafts.get(id), byId.get(id));

  // ---- Loading -----------------------------------------------------------------------------------------------------------

  async function load() {
    try {
      const r = await fetch('/api/records', { cache: 'no-store' });
      if (!r.ok) throw new Error(r.status);
      records = await r.json();
      live = true;
    } catch {
      const r = await fetch('../institutions.json', { cache: 'no-store' });
      records = await r.json();
      live = false;
    }
    index();
    $('#mode').textContent = live
      ? `${records.length} records from institutions.json. Save writes to the file.`
      : `${records.length} records, read only from this page. Save downloads institutions.json; run python3 tools/editor.py to save in place and check wording.`;
    $('#rebuild').hidden = !live;
    if (live) {
      fetch('/api/problems').then(r => r.json()).then(p => { problems = p; renderList(); if (current) renderRecord(); });
    }
    renderList();
    const want = decodeURIComponent(location.hash.slice(1));
    if (byId.has(want)) open(want);
  }

  function index() {
    byId = new Map(records.map(r => [r.id, r]));
    const sug = {};
    const keys = new Map();
    const walk = (v, key) => {
      if (Array.isArray(v)) return v.forEach(x => walk(x, key));
      if (v && typeof v === 'object') return Object.entries(v).forEach(([k, x]) => walk(x, k));
      if (typeof v === 'string' && SUGGEST_KEYS.has(key) && v.length < 60) (sug[key] ||= new Set()).add(v);
    };
    for (const r of records) {
      for (const [k, v] of Object.entries(r)) { if (!keys.has(k)) keys.set(k, v); walk(v, k); }
    }
    suggestions = Object.fromEntries(Object.entries(sug).map(([k, s]) => [k, [...s].sort()]));
    topKeys = [...keys.entries()];
  }

  // ---- The list of records -----------------------------------------------------------------------------------------------

  const fold = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

  function renderList() {
    const q = fold($('#q').value.trim());
    const show = document.querySelector('input[name=show]:checked').value;
    const hits = records.filter(r => {
      if (show === 'problems' && !(problems[r.id] || []).length) return false;
      if (show === 'changed' && !isChanged(r.id)) return false;
      if (!q) return true;
      return [r.name, r.city, r.country, r.id, ...(r.aliases || [])].some(s => fold(s).includes(q));
    }).sort((a, b) => a.name.localeCompare(b.name));
    const list = $('#list');
    list.replaceChildren(...hits.slice(0, 400).map(r => {
      const n = (problems[r.id] || []).length;
      return el('li', {}, el('button', {
        type: 'button', 'aria-current': r.id === current ? 'true' : 'false', onclick: () => open(r.id),
      }, el('span', { class: 'nm' }, r.name,
        n ? el('span', { class: 'tag', title: `${n} wording ${n === 1 ? 'point' : 'points'} to check` }, String(n)) : null,
        isChanged(r.id) ? el('span', { class: 'tag chg' }, 'changed') : null),
      el('span', { class: 'sub' }, [r.city, r.country].filter(Boolean).join(', '))));
    }));
    $('#count').textContent = hits.length > 400 ? `${hits.length} records, the first 400 shown. Search to narrow.`
      : `${hits.length} ${hits.length === 1 ? 'record' : 'records'}`;
  }

  // ---- One record --------------------------------------------------------------------------------------------------------

  function open(id) {
    if (!byId.has(id)) return;
    current = id;
    if (!drafts.has(id)) drafts.set(id, clone(byId.get(id)));
    history.replaceState(null, '', '#' + encodeURIComponent(id));
    renderList();
    renderRecord();
    $('#main').scrollTop = 0;
    $('#main').focus({ preventScroll: true });
  }

  function renderRecord(statusText, statusKind) {
    const rec = draft(current);
    const main = $('#main');
    const changed = isChanged(current);
    const issues = problems[current] || [];
    const head = el('div', { class: 'rec-head' },
      el('h2', {}, rec.name || '(no name)', el('span', { class: 'meta' },
        [rec.location || [rec.city, rec.country].filter(Boolean).join(', '), rec.id].filter(Boolean).join(' · '))),
      el('div', { class: 'acts' },
        el('button', { type: 'button', disabled: !changed, onclick: revert }, 'Undo changes'),
        el('button', { type: 'button', class: 'primary', disabled: !changed, onclick: save },
          live ? 'Save' : 'Download institutions.json')),
      el('p', { class: 'status' + (statusKind ? ' ' + statusKind : ''), id: 'status', role: 'status' },
        statusText || (changed ? 'Unsaved changes.' : '')));
    const tablist = el('div', { class: 'tabs', role: 'tablist', 'aria-label': 'View' },
      ...[['fields', 'Fields'], ['raw', 'JSON']].map(([v, label]) => el('button', {
        type: 'button', role: 'tab', 'aria-selected': String(view === v),
        onclick: () => { if (view === 'raw' && v !== 'raw' && !applyRaw()) return; view = v; renderRecord(); },
      }, label)));
    const body = view === 'raw' ? renderRaw(rec) : renderFields(rec, issues);
    main.replaceChildren(head, tablist, body);
  }

  function setStatus(text, kind) {
    const s = $('#status');
    if (s) { s.textContent = text; s.className = 'status' + (kind ? ' ' + kind : ''); }
  }

  function changedAfterEdit() {
    const changed = isChanged(current);
    const [undo, saveBtn] = document.querySelectorAll('.rec-head .acts button');
    undo.disabled = saveBtn.disabled = !changed;
    setStatus(changed ? 'Unsaved changes.' : '');
    renderList();
    if (live) { clearTimeout(lintTimer); lintTimer = setTimeout(lintNow, 500); }
  }

  async function lintNow() {
    const id = current;
    try {
      const r = await fetch('/api/lint', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(draft(id)) });
      const found = await r.json();
      if (id !== current) return;
      if (same(found, problems[id] || [])) return;
      if (found.length) problems[id] = found; else delete problems[id];
      drawIssues();
      renderList();
    } catch { /* the lint is advice; a failed check changes nothing */ }
  }

  // ---- Fields view -------------------------------------------------------------------------------------------------------

  function renderFields(rec, issues) {
    const wrap = el('div', { class: 'fields' });
    if (issues.length) wrap.append(el('div', { class: 'summary', id: 'summary' }));
    const placed = new Set();
    for (const [title, keys] of GROUPS) {
      const present = keys.filter(k => k in rec);
      present.forEach(k => placed.add(k));
      if (!present.length) continue;
      wrap.append(el('section', { class: 'group' }, el('h3', {}, title), ...present.map(k => fieldRow(rec, [k]))));
    }
    const rest = Object.keys(rec).filter(k => !placed.has(k));
    if (rest.length) wrap.append(el('section', { class: 'group' }, el('h3', {}, 'Other fields'), ...rest.map(k => fieldRow(rec, [k]))));

    const missing = topKeys.filter(([k]) => !(k in rec) && !READONLY.some(([t]) => t(k)));
    if (missing.length) {
      const sel = el('select', { class: 'txt', id: 'addkey' }, el('option', { value: '' }, 'Choose a field…'),
        ...missing.sort((a, b) => label(a[0]).localeCompare(label(b[0])))
          .map(([k]) => el('option', { value: k }, `${label(k)} (${k})`)));
      wrap.append(el('div', { class: 'add-field' }, el('label', { for: 'addkey' }, 'Add a field'), sel,
        el('button', { type: 'button', onclick: () => {
          const k = sel.value; if (!k) return;
          draft(current)[k] = blank(topKeys.find(([x]) => x === k)[1]);
          renderRecord(); changedAfterEdit();
          const row = document.querySelector(`[data-path="${CSS.escape(k)}"]`);
          if (row) { row.scrollIntoView({ block: 'center' }); row.querySelector('input,textarea,select,button')?.focus(); }
        } }, 'Add')));
    }
    queueMicrotask(drawIssues);
    return wrap;
  }

  const label = k => LABELS[k] || (k.charAt(0).toUpperCase() + k.slice(1)).replace(/_/g, ' ');
  const pathStr = path => path.filter(p => typeof p === 'string').join('.');
  const getAt = (obj, path) => path.reduce((o, k) => (o == null ? o : o[k]), obj);
  const setAt = (obj, path, v) => { getAt(obj, path.slice(0, -1))[path[path.length - 1]] = v; };

  // An empty value of the same shape, for a new field or a new item in a list.
  function blank(example) {
    if (Array.isArray(example)) return [];
    if (example && typeof example === 'object') return Object.fromEntries(Object.entries(example).map(([k, v]) => [k, blank(v)]));
    if (typeof example === 'number') return null;
    if (typeof example === 'boolean') return false;
    return '';
  }

  function fieldRow(rec, path) {
    const key = path[path.length - 1];
    const p = pathStr(path);
    const value = getAt(rec, path);
    const ro = READONLY.find(([t]) => t(p));
    const row = el('div', { class: 'field', 'data-path': p });
    const orig = getAt(byId.get(current), path);
    if (!same(orig, value)) row.classList.add('changed');
    const id = 'f-' + p.replace(/[^\w-]/g, '_') + '-' + path.length;
    const name = path.length > 1 && key === 'id' ? 'Id' : label(key);
    const lab = el('div', { class: 'lab' }, el('label', { for: id }, name), path.length === 1 ? el('span', { class: 'key' }, p) : null);
    const val = el('div', { class: 'val' });
    if (ro) val.append(readonly(value, ro[1], key));
    else val.append(control(rec, path, value, id));
    if (HELP[p] && !ro) val.append(el('p', { class: 'help' }, HELP[p]));
    val.append(el('ul', { class: 'issues', 'data-issues': p }));
    if (path.length === 1 && !ro && !['name', 'location', 'lat', 'lon', 'city', 'country', 'tier', 'sources'].includes(key)) {
      val.append(el('div', { class: 'add-row' }, el('button', { type: 'button', class: 'link small', onclick: () => {
        delete draft(current)[key]; renderRecord(); changedAfterEdit();
      } }, `Remove ${label(key).toLowerCase()} from this record`)));
    }
    row.append(lab, val);
    return row;
  }

  function onEdit(path, v, row) {
    setAt(draft(current), path, v);
    const orig = getAt(byId.get(current), path);
    row?.classList.toggle('changed', !same(orig, v));
    changedAfterEdit();
  }

  function control(rec, path, value, id) {
    const key = path[path.length - 1];
    const row = () => document.querySelector(`[data-path="${CSS.escape(pathStr(path))}"]`);
    if (JOINED[key] && typeof value === 'string') {
      const sep = JOINED[key];
      return stringList(value ? value.split(sep) : [], key, id, list => onEdit(path, list.filter(s => s.trim()).join(sep), row()));
    }
    if (Array.isArray(value)) return arrayControl(rec, path, value, id);
    if (value && typeof value === 'object') return objectControl(rec, path, value);
    if (value === null) {
      return el('div', {}, el('span', { class: 'help' }, 'Empty. '),
        el('button', { type: 'button', class: 'small', id, onclick: () => { setAt(draft(current), path, ''); renderRecord(); changedAfterEdit(); } }, 'Write a value'));
    }
    if (typeof value === 'number' || ['lat', 'lon', 'year_founded', 'grade', 'level', 'income', 'expenditure', 'public',
      'private', 'earned', 'net_assets', 'visitors', 'institutions'].includes(key)) {
      return el('input', { class: 'txt num', type: 'number', step: 'any', id, value: value ?? '', oninput: e => {
        const t = e.target.value; onEdit(path, t === '' ? null : Number(t), row());
      } });
    }
    if (typeof value === 'boolean') {
      return el('input', { type: 'checkbox', id, checked: value, onchange: e => onEdit(path, e.target.checked, row()) });
    }
    return textControl(value, key, id, v => onEdit(path, v, row()));
  }

  const isUrl = s => /^https?:\/\/\S+$/.test(s || '');

  function textControl(value, key, id, commit) {
    const s = String(value ?? '');
    if (key === 'tier') {
      const opts = [['A', 'A, clean'], ['B', 'B, flagged'], ['U', 'U, unverified']];
      if (!opts.some(([v]) => v === s)) opts.push([s, s]);
      return el('select', { class: 'txt', id, style: 'max-width:14em', onchange: e => commit(e.target.value) },
        ...opts.map(([v, t]) => el('option', { value: v, selected: v === s }, t)));
    }
    if (isUrl(s) || /url|website/.test(key)) {
      const input = el('input', { class: 'txt url', type: 'url', id, value: s, spellcheck: 'false' });
      const a = el('a', { href: s, target: '_blank', rel: 'noopener', hidden: !isUrl(s) }, 'Open');
      input.addEventListener('input', () => { a.href = input.value; a.hidden = !isUrl(input.value); commit(input.value); });
      return el('div', { class: 'url-row' }, input, a);
    }
    const prose = PROSE_KEYS.has(key) || s.length > 90 || s.includes('\n');
    if (!prose) {
      const list = suggestions[key] ? 'dl-' + key : null;
      const input = el('input', { class: 'txt', type: 'text', id, value: s, list, oninput: e => commit(e.target.value) });
      if (list && !document.getElementById(list)) {
        document.body.append(el('datalist', { id: list }, ...suggestions[key].map(v => el('option', { value: v }))));
      }
      return input;
    }
    const ta = el('textarea', { class: 'prose', id, rows: 2, lang: 'en', spellcheck: 'true' });
    ta.value = s;
    const words = el('div', { class: 'words' });
    const count = () => {
      const n = ta.value.trim() ? ta.value.trim().split(/\s+/).length : 0;
      const lim = WORD_LIMIT[key];
      words.textContent = `${n} ${n === 1 ? 'word' : 'words'}` + (lim ? ` of ${lim}` : '');
    };
    ta.addEventListener('input', () => { count(); grow(ta); commit(ta.value); });
    count();
    queueMicrotask(() => grow(ta));
    return el('div', {}, ta, words);
  }

  // `field-sizing: content` does this where it is supported; elsewhere the box grows with its text.
  function grow(ta) {
    if (CSS.supports('field-sizing', 'content')) return;
    ta.style.height = 'auto';
    ta.style.height = ta.scrollHeight + 2 + 'px';
  }

  function stringList(items, key, id, commit) {
    const list = el('ol', { class: 'items' });
    const values = [...items];
    const draw = () => {
      list.replaceChildren(...values.map((v, i) => {
        const c = textControl(v, key, i === 0 ? id : `${id}-${i}`, nv => { values[i] = nv; commit(values); });
        const inputEl = c.matches?.('input,textarea,select') ? c : c.querySelector('input,textarea,select');
        inputEl?.setAttribute('aria-label', `${label(key)} ${i + 1}`);
        return el('li', {}, c, el('div', { class: 'row-acts' },
          el('button', { type: 'button', class: 'small', title: 'Move up', 'aria-label': `Move ${i + 1} up`, disabled: i === 0,
            onclick: () => { [values[i - 1], values[i]] = [values[i], values[i - 1]]; commit(values); draw(); } }, '↑'),
          el('button', { type: 'button', class: 'small', title: 'Move down', 'aria-label': `Move ${i + 1} down`, disabled: i === values.length - 1,
            onclick: () => { [values[i + 1], values[i]] = [values[i], values[i + 1]]; commit(values); draw(); } }, '↓'),
          el('button', { type: 'button', class: 'small', title: 'Remove', 'aria-label': `Remove ${i + 1}`,
            onclick: () => { values.splice(i, 1); commit(values); draw(); } }, '×')));
      }));
    };
    draw();
    return el('div', {}, list, el('div', { class: 'add-row' }, el('button', { type: 'button', class: 'small', onclick: () => {
      values.push(''); draw(); list.lastElementChild?.querySelector('input,textarea')?.focus();
    } }, values.length ? 'Add another' : 'Add one')));
  }

  function arrayControl(rec, path, value, id) {
    const key = path[path.length - 1];
    const row = () => document.querySelector(`[data-path="${CSS.escape(pathStr(path))}"]`);
    const objects = value.some(v => v && typeof v === 'object');
    if (value.length && value.every(isPair)) return pairsControl(path, value);
    if (!objects) {
      return stringList(value.map(v => v == null ? '' : String(v)), key, id, list => onEdit(path, list, row()));
    }
    const wrap = el('div', {});
    value.forEach((item, i) => {
      const roWhy = readonlyItem(pathStr(path), item);
      const card = el('details', { class: 'card', open: value.length <= 3 && !roWhy });
      card.append(el('summary', {}, el('span', { class: 'ttl' }, cardTitle(item, i), roWhy ? el('small', {}, 'written by a tool') : null)));
      const body = el('div', { class: 'body' });
      if (roWhy || !item || typeof item !== 'object' || Array.isArray(item)) body.append(readonly(item, roWhy || '', key));
      else {
        body.append(objectControl(rec, [...path, i], item));
        body.append(el('div', { class: 'card-acts' },
          el('button', { type: 'button', class: 'small', disabled: i === 0, onclick: () => move(path, i, -1) }, 'Move up'),
          el('button', { type: 'button', class: 'small', disabled: i === value.length - 1, onclick: () => move(path, i, 1) }, 'Move down'),
          el('button', { type: 'button', class: 'small', onclick: () => {
            if (!confirm(`Remove “${cardTitle(item, i)}”?`)) return;
            getAt(draft(current), path).splice(i, 1); renderRecord(); changedAfterEdit();
          } }, 'Remove')));
      }
      card.append(body);
      wrap.append(card);
    });
    const example = value.find(v => v && typeof v === 'object' && !readonlyItem(pathStr(path), v));
    if (example) {
      wrap.append(el('div', { class: 'add-row' }, el('button', { type: 'button', class: 'small', id, onclick: () => {
        const item = blank(example);
        delete item.id;
        getAt(draft(current), path).push(item); renderRecord(); changedAfterEdit();
      } }, 'Add an entry')));
    }
    return wrap;
  }

  // A list of [label, text] pairs (a staff account's fields): the label is shown as the field's name, the text edited beside it.
  const isPair = v => Array.isArray(v) && v.length === 2 && typeof v[0] === 'string' && typeof v[1] === 'string';

  function pairsControl(path, value) {
    const wrap = el('div', { class: 'obj' });
    value.forEach(([name, text], i) => {
      const id = 'f-' + pathStr(path).replace(/[^\w-]/g, '_') + '-p' + i + '-' + path.length;
      const row = el('div', { class: 'field' });
      row.append(el('div', { class: 'lab' }, el('label', { for: id }, name)),
        el('div', { class: 'val' }, textControl(text, 'text', id, v => onEdit([...path, i, 1], v, row))));
      wrap.append(row);
    });
    return wrap;
  }

  function move(path, i, by) {
    const arr = getAt(draft(current), path);
    [arr[i], arr[i + by]] = [arr[i + by], arr[i]];
    renderRecord(); changedAfterEdit();
  }

  function cardTitle(item, i) {
    if (!item || typeof item !== 'object') return String(item ?? '');
    const t = item.headline || item.title || item.strategy || item.person || item.funder || item.doc_id || item.name ||
      item.summary || item.text || item.note || item.scope ||
      (Array.isArray(item.fields) && isPair(item.fields.find(isPair)) ? item.fields.find(isPair)[1] : null) || item.kind;
    const when = item.when || item.date || item.period || item.event_date || item.year || item.meta;
    const s = t ? String(t) : `Entry ${i + 1}`;
    return (s.length > 110 ? s.slice(0, 107) + '…' : s) + (when ? ` · ${when}` : '');
  }

  function objectControl(rec, path, value) {
    const wrap = el('div', { class: 'obj' });
    for (const k of Object.keys(value)) wrap.append(fieldRow(rec, [...path, k]));
    return wrap;
  }

  // A value a tool writes: shown as it reads, with why it is not edited here.
  function readonly(value, why, key) {
    const box = el('div', { class: 'ro' });
    if (why) box.append(el('p', { class: 'why' }, why));
    box.append(readable(value, key));
    return box;
  }

  function readable(v, key) {
    if (v == null || v === '') return el('p', {}, '(empty)');
    if (Array.isArray(v)) {
      if (!v.length) return el('p', {}, '(none)');
      if (v.every(isPair)) {
        return el('div', { class: 'obj' }, ...v.map(([k, x]) => el('div', { class: 'field' },
          el('div', { class: 'lab' }, k), el('div', { class: 'val' }, readable(x, 'text')))));
      }
      if (v.every(x => x == null || typeof x !== 'object')) {
        return el('ul', {}, ...v.map(x => el('li', {}, isUrl(String(x)) ? el('a', { href: x, target: '_blank', rel: 'noopener' }, x) : String(x))));
      }
      return el('div', {}, ...v.map((x, i) => el('details', { class: 'card' }, el('summary', {}, el('span', { class: 'ttl' }, cardTitle(x, i))),
        el('div', { class: 'body' }, readable(x)))));
    }
    if (typeof v === 'object') {
      return el('div', { class: 'obj' }, ...Object.entries(v).map(([k, x]) => el('div', { class: 'field' },
        el('div', { class: 'lab' }, label(k)), el('div', { class: 'val' }, readable(x, k)))));
    }
    const s = String(v);
    if (isUrl(s)) return el('p', {}, el('a', { href: s, target: '_blank', rel: 'noopener' }, s));
    return el('p', { class: PROSE_KEYS.has(key) || s.length > 90 ? 'prose' : '' }, s);
  }

  // ---- Wording points from tools/lint_text.py ----------------------------------------------------------------------------

  function explain(problem) {
    const [kind, ...rest] = problem.split(':');
    const base = kind.startsWith('over ') ? 'over' : kind.trim();
    return { kind: base, word: rest.join(':').trim(), text: RULES[base] || problem, raw: problem };
  }

  function drawIssues() {
    const list = problems[current] || [];
    document.querySelectorAll('[data-issues]').forEach(u => u.replaceChildren());
    const byField = {};
    for (const { field, problem } of list) (byField[field] ||= []).push(problem);
    for (const [field, ps] of Object.entries(byField)) {
      const u = document.querySelector(`[data-issues="${CSS.escape(field)}"]`);
      if (!u) continue;
      u.replaceChildren(...ps.map(p => {
        const e = explain(p);
        return el('li', {}, el('b', {}, e.word ? `“${e.word}”` : e.raw), el('span', {}, e.text),
          e.kind === 'dash' ? el('button', { type: 'button', class: 'small', onclick: () => fixDashes(field) }, 'Replace the dashes') : null);
      }));
    }
    const s = $('#summary');
    if (s) {
      if (!list.length) { s.remove(); return; }
      s.replaceChildren(el('strong', {}, `${list.length} wording ${list.length === 1 ? 'point' : 'points'} to check`),
        el('ul', {}, ...Object.entries(byField).map(([f, ps]) => el('li', {},
          el('button', { type: 'button', class: 'link', onclick: () => {
            const row = document.querySelector(`[data-path="${CSS.escape(f)}"]`);
            row?.scrollIntoView({ block: 'center' }); row?.querySelector('textarea,input')?.focus({ preventScroll: true });
          } }, label(f.split('.').pop())), `: ${ps.map(p => explain(p).word || explain(p).raw).join(', ')}`))));
    }
  }

  // The mechanical repair of tools/lint_text.py: a range of figures takes "to", a dash between words a comma.
  function fixDashes(field) {
    const path = field.split('.');
    const v = getAt(draft(current), path);
    if (typeof v !== 'string') return;
    const fixed = v.replace(/(?<=\d)–(?=\d)/g, ' to ').replace(/\s+[—–]\s+/g, ', ').replace(/(?<=\w)—(?=\w)/g, ', ');
    setAt(draft(current), path, fixed);
    renderRecord(); changedAfterEdit();
  }

  // ---- JSON view ---------------------------------------------------------------------------------------------------------

  function renderRaw(rec) {
    const ta = el('textarea', { id: 'raw', spellcheck: 'false', 'aria-label': 'The record as JSON' });
    ta.value = JSON.stringify(rec, null, 2);
    return el('div', { class: 'raw' },
      el('p', { class: 'help' }, 'The whole record as stored. Changes here are applied when you go back to Fields or save.'),
      ta, el('p', { class: 'err', id: 'raw-err', role: 'alert' }));
  }

  function applyRaw() {
    const ta = $('#raw');
    if (!ta) return true;
    try {
      const obj = JSON.parse(ta.value);
      if (!obj || typeof obj !== 'object' || Array.isArray(obj)) throw new Error('The record must be one object.');
      if (obj.id !== current) throw new Error(`The id must stay ${current}.`);
      drafts.set(current, obj);
      return true;
    } catch (e) {
      $('#raw-err').textContent = 'Not applied: ' + e.message;
      return false;
    }
  }

  // ---- Saving ------------------------------------------------------------------------------------------------------------

  function revert() {
    if (!confirm('Undo every unsaved change to this record?')) return;
    drafts.set(current, clone(byId.get(current)));
    renderRecord(); changedAfterEdit();
  }

  async function save() {
    if (view === 'raw' && !applyRaw()) return;
    const id = current;
    const rec = drafts.get(id);
    if (!live) return download();
    setStatus('Saving…');
    try {
      const r = await fetch('/api/records/' + encodeURIComponent(id), {
        method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ record: rec, base: byId.get(id) }),
      });
      const out = await r.json();
      if (r.status === 409) {
        if (confirm(out.error + '\n\nLoad the version on disk? Your unsaved changes to this record will be lost.')) {
          replace(id, out.current); drafts.set(id, clone(out.current)); renderRecord('Loaded the version on disk.', 'ok');
        } else setStatus(out.error + ' Not saved.', 'err');
        return;
      }
      if (!r.ok) return setStatus(out.error || 'Not saved.', 'err');
      replace(id, out.record);
      drafts.set(id, clone(out.record));
      if (out.problems.length) problems[id] = out.problems; else delete problems[id];
      renderList();
      if (id === current) renderRecord(`Saved to institutions.json at ${new Date().toLocaleTimeString()}. Rebuild page data to see it on the atlas.`, 'ok');
    } catch (e) {
      setStatus('Not saved: the editor server did not answer. ' + e.message, 'err');
    }
  }

  function replace(id, rec) {
    const i = records.findIndex(r => r.id === id);
    records[i] = rec;
    byId.set(id, rec);
  }

  function download() {
    const all = records.map(r => (drafts.has(r.id) ? drafts.get(r.id) : r));
    const blob = new Blob([JSON.stringify(all, null, 2).replace(/[\u007f-￿]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'))],
      { type: 'application/json' });
    const a = el('a', { href: URL.createObjectURL(blob), download: 'institutions.json' });
    document.body.append(a); a.click(); a.remove();
    setStatus('Downloaded institutions.json with every change made in this window. Put it in the repository root, then run tools/clean_data.py and tools/embed_data.py.', 'ok');
  }

  async function rebuild() {
    const unsaved = records.filter(r => isChanged(r.id)).length;
    if (unsaved && !confirm(`${unsaved} ${unsaved === 1 ? 'record has' : 'records have'} unsaved changes, which the rebuild will not include. Rebuild anyway?`)) return;
    const btn = $('#rebuild');
    btn.disabled = true; btn.textContent = 'Rebuilding…';
    const dlg = $('#log');
    try {
      const r = await fetch('/api/rebuild', { method: 'POST' });
      const out = await r.json();
      $('#log-title').textContent = r.ok ? 'Rebuilt: institutions.json cleaned and assets/institutions.js written' : out.error;
      $('#log-text').textContent = out.log || '';
      // The clean pass can change records (spellings, tiers, grades), so the page reloads them.
      const fresh = await (await fetch('/api/records', { cache: 'no-store' })).json();
      records = fresh; index();
      for (const [id, d] of [...drafts]) if (!isChanged(id) || !byId.has(id)) drafts.delete(id);
      problems = await (await fetch('/api/problems')).json();
      renderList(); if (current && byId.has(current)) renderRecord();
    } catch (e) {
      $('#log-title').textContent = 'The rebuild did not finish';
      $('#log-text').textContent = String(e);
    }
    btn.disabled = false; btn.textContent = 'Rebuild page data';
    dlg.showModal();
  }

  // ---- Wiring ------------------------------------------------------------------------------------------------------------

  $('#q').addEventListener('input', renderList);
  document.querySelectorAll('input[name=show]').forEach(r => r.addEventListener('change', renderList));
  $('#rebuild').addEventListener('click', rebuild);
  addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') { e.preventDefault(); if (current && isChanged(current)) save(); }
  });
  addEventListener('beforeunload', e => { if (records.some(r => isChanged(r.id))) { e.preventDefault(); e.returnValue = ''; } });
  addEventListener('hashchange', () => { const id = decodeURIComponent(location.hash.slice(1)); if (id !== current && byId.has(id)) open(id); });

  load().catch(e => { $('#mode').textContent = 'The records could not be loaded: ' + e.message; });
})();
