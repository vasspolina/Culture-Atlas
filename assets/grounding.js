// What the model is told about a record, and about a place, before it answers.
//
// A record on the atlas holds far more than its one-line funding and watch lines: the researched overview, the funding verdict and
// its points, the audited figures for the year, the legal form and its controls, every reported case with its date and sources,
// the Epstein and WikiLeaks records, the employee and visitor accounts, the critics quoted on it, hours, prices, transit and
// access. The chat answers from the records alone, so an answer can only be as specific as the record it was given. This file
// writes the whole record out in labelled sections, the parts the question is most often about first, within a character budget.
//
// Pure functions, no DOM; index.html calls formatRecord from queryAI and placeSummary for a question about a city or country, and
// tests/grounding.test.mjs loads the file in Node.
(function (root) {
  var FULL = 14000;     // the record the question is about
  var SHORT = 3200;     // every other record sent with it

  function clean(t) { return String(t == null ? '' : t).replace(/\s+/g, ' ').trim(); }
  function cut(t, n) { t = clean(t); return t.length > n ? t.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : t; }
  function has(v) { return v != null && v !== '' && !(Array.isArray(v) && !v.length) && !(typeof v === 'object' && !Array.isArray(v) && !Object.keys(v).length); }
  function urls(list, n) { return (list || []).map(function (s) { return typeof s === 'string' ? s : (s && s.url) || ''; }).filter(Boolean).slice(0, n || 6).join(' ; '); }
  function money(n, cur) {
    if (typeof n !== 'number' || !isFinite(n)) return '';
    var abs = Math.abs(n), s;
    if (abs >= 1e9) s = (n / 1e9).toFixed(2).replace(/\.?0+$/, '') + ' billion';
    else if (abs >= 1e6) s = (n / 1e6).toFixed(1).replace(/\.0$/, '') + ' million';
    else if (abs >= 1e3) s = (n / 1e3).toFixed(0) + ' thousand';
    else s = String(n);
    return (cur ? cur + ' ' : '') + s;
  }
  function pct(part, whole) { return typeof part === 'number' && typeof whole === 'number' && whole > 0 ? ' (' + Math.round(part / whole * 100) + '%)' : ''; }

  // One labelled section: a heading and its lines. An empty section is left out.
  function section(title, lines) {
    var out = (lines || []).filter(function (l) { return l && clean(l); });
    return out.length ? '  ' + title + ':\n' + out.map(function (l) { return '    ' + clean(l); }).join('\n') : '';
  }

  // The record of one space, written out for the model. opts.status is the record's status line (the page's tierName);
  // opts.watchGossip says whether the watch line reports something or records a clean result; opts.full gives the long budget.
  function formatRecord(i, opts) {
    opts = opts || {};
    var budget = opts.full ? FULL : SHORT;
    var d = (i.details && typeof i.details === 'object') ? i.details : {};
    var f = (i.finance && typeof i.finance === 'object') ? i.finance : null;
    var b = (i.bureaucracy && typeof i.bureaucracy === 'object') ? i.bureaucracy : null;
    var parts = [];

    var head = '- INSTITUTION: ' + i.name + (i.aliases && i.aliases.length ? ' (also: ' + i.aliases.slice(0, 4).join(', ') + ')' : '') +
      '\n  Place: ' + [i.city, i.country].filter(Boolean).join(', ') + (i.address ? ' — ' + i.address : '') + (i.neighborhood ? ' — ' + cut(i.neighborhood, 160) : '') +
      (i.year_founded ? '\n  Founded: ' + i.year_founded : '') +
      (i.size ? '\n  Size: ' + ({ S: 'small', M: 'medium', L: 'large', XL: 'very large' }[i.size] || i.size) : '') +
      (i.website ? '\n  Website: ' + i.website : '');
    parts.push(head);

    parts.push(section('STATUS', [
      'Governance Classification: ' + (opts.status || i.tier || 'not stated'),
      'Grade Basis: ' + (i.grade && i.grade_basis ? i.grade_basis : 'none recorded'),
      i.tier_note ? 'Tier note: ' + cut(i.tier_note, 400) : '',
      'Recorded Flags: ' + ((i.flags || []).join(', ') || 'none recorded'),
      i.why_flagged ? 'Why flagged: ' + i.why_flagged : '',
      'Watch Line: ' + (i.watch ? i.watch + ' (Watch Line Is Gossip: ' + (opts.watchGossip ? 'yes' : 'no, a clean result or a description') + ')' : 'none recorded')
    ]));

    var fin = [
      'Funding on record: ' + (i.funding || 'not stated'),
      d.funding_verdict ? 'Funding verdict: ' + d.funding_verdict : ''
    ];
    (d.funding || []).slice(0, 8).forEach(function (p) { fin.push('- ' + cut(p, 500)); });
    if (i.finances_note) fin.push('Finances: ' + i.finances_note);
    if (f && (f.income || f.expenditure)) {
      fin.push('Audited figures' + (f.fy ? ' FY' + f.fy : '') + (f.source_kind ? ' (' + f.source_kind + ')' : '') + ': income ' + money(f.income, f.currency) +
        (f.expenditure ? ', expenditure ' + money(f.expenditure, f.currency) : '') +
        (f.public ? '; public ' + money(f.public, f.currency) + pct(f.public, f.income) : '') +
        (f.private ? '; private ' + money(f.private, f.currency) + pct(f.private, f.income) : '') +
        (f.earned ? '; earned ' + money(f.earned, f.currency) + pct(f.earned, f.income) : '') +
        (f.sponsorship ? '; sponsorship ' + money(f.sponsorship, f.currency) + pct(f.sponsorship, f.income) : '') +
        (f.net_assets ? '; net assets ' + money(f.net_assets, f.currency) : '') +
        (f.url ? '. Source: ' + f.url : ''));
    }
    if (i.funder_links && i.funder_links.length) fin.push('Funders also named at other spaces on the atlas: ' + i.funder_links.filter(function (x) { return x && x.funder; }).map(function (x) { return x.funder + ' (' + x.institutions + ' spaces)'; }).join(', '));
    if (i.records_note) fin.push('What it publishes: ' + i.records_note);
    if (i.statutory_filings_url) fin.push('Statutory filings: ' + i.statutory_filings_url);
    else if (i.audit_dossier_url) fin.push('Statutory filings: ' + i.audit_dossier_url);
    parts.push(section('FUNDING AND FINANCES', fin));

    if (b || i.affiliations_note || i.red_tape) {
      var gov = [];
      if (b) {
        gov.push('Legal form: ' + (b.legal_form || 'not stated') + (b.parent ? '; parent: ' + b.parent : '') + (b.budget_set_by ? '; budget set by ' + b.budget_set_by : '') + (b.year ? ' (' + b.year + ')' : ''));
        if (b.controls && b.controls.length) gov.push('Public controls it is under: ' + b.controls.join('; '));
        if (b.level_basis) gov.push('Administration rating basis: ' + b.level_basis);
      }
      if (i.red_tape && i.red_tape.note) gov.push('Red tape: ' + i.red_tape.note + (i.red_tape.date ? ' (' + i.red_tape.date + ')' : ''));
      if (i.affiliations_note) gov.push('Affiliations: ' + i.affiliations_note);
      parts.push(section('GOVERNANCE', gov));
    }

    var about = [];
    (d.overview || []).slice(0, opts.full ? 10 : 4).forEach(function (p) { about.push('- ' + cut(p, 500)); });
    if (i.highlight) about.push('Collections and site: ' + i.highlight);
    if (i.curatorial_focus) about.push('Curatorial focus: ' + i.curatorial_focus);
    (d.wider_context || []).slice(0, 3).forEach(function (p) { about.push('Context: ' + cut(p, 400)); });
    if (d.bottom_line) about.push('Bottom line of the research: ' + d.bottom_line);
    parts.push(section('ABOUT', about));

    // The gossip items (notes/gossip-criteria.md): talk collected from the internet, each with who says it, where, when, the
    // response and its sources. Newest first, stale ones last, as the attach tool orders them. Before the reported items: in
    // Gossip mode the chat answers from these first.
    var gos = ((i.gossip_data || {}).gossip || []).slice(0, opts.full ? 8 : 1).map(function (g) {
      return 'Gossip ' + (g.id || '') + ' [' + [g.kind, g.status].filter(Boolean).join(', ') + ']: ' + clean(g.headline) + ' — ' + cut(g.said, opts.full ? 700 : 160) +
        ' Who says it: ' + (g.who_says || '') + ' (' + (g.where || '') + (g.when ? ', ' + g.when : '') + ').' +
        (opts.full && g.response ? ' Response: ' + cut(g.response, 300) : '') + (opts.full && g.outcome ? ' Outcome: ' + cut(g.outcome, 300) : '') +
        (opts.full && g.urls && g.urls.length ? ' Sources: ' + urls(g.urls, 3) : '');
    });
    parts.push(section(opts.full ? 'GOSSIP (talk collected from the internet by the atlas\'s rules; state who says each item, never an item of status talk as fact; unverified unless confirmed or resolved)' : 'GOSSIP (internet talk; say who says it; unverified)', gos));

    var rep = [];
    (d.red_flags || []).forEach(function (r) { if (r && (r.heading || (r.points || []).length)) rep.push((r.heading ? r.heading + ': ' : '') + (r.points || []).slice(0, 4).map(function (p) { return cut(p, 300); }).join(' ')); });
    if (d.press && (d.press.overall || (d.press.items || []).length)) {
      rep.push('Press: ' + (d.press.overall || '') + ' ' + (d.press.items || []).slice(0, 4).map(function (p) { return typeof p === 'string' ? cut(p, 250) : cut([p.title, p.outlet, p.date, p.summary || p.text].filter(Boolean).join(', '), 250); }).join(' | '));
    }
    ((i.gossip_data || {}).real_cases || []).slice(0, opts.full ? 6 : 2).forEach(function (c) {
      rep.push('Case file ' + (c.case_id || '') + (c.event_date ? ' (' + c.event_date + ')' : '') + ': ' + clean(c.title) + ' — ' + cut((c.facts || []).join(' '), 500) +
        ((c.claims || []).length ? ' Claim: ' + cut(c.claims.join(' '), 300) : '') + (c.response ? ' Response: ' + cut(c.response, 300) : '') + (c.outcome ? ' Outcome: ' + cut(c.outcome, 300) : '') +
        (c.status ? ' Status: ' + String(c.status).replace(/_/g, ' ') : '') + (c.sources && c.sources.length ? ' Sources: ' + urls(c.sources, 2) : ''));
    });
    (i.case_notes || []).slice(0, opts.full ? 8 : 3).forEach(function (c) { rep.push('Case: ' + [c.title, c.meta].filter(Boolean).join(', ') + ' — ' + cut(c.text, 500) + (c.sources && c.sources.length ? ' Sources: ' + urls(c.sources, 2) : '')); });
    (i.epstein_records || []).forEach(function (e) { rep.push('Epstein record: ' + [e.person, e.tie, e.status, e.consequence].filter(Boolean).join('; ') + (e.summary ? ' — ' + cut(e.summary, 400) : '') + (e.sources && e.sources.length ? ' Sources: ' + urls(e.sources, 2) : '')); });
    (i.wikileaks_records || []).forEach(function (w) { rep.push('WikiLeaks record' + (w.date ? ' ' + w.date : '') + (w.doc_id ? ' (' + w.doc_id + ')' : '') + ': ' + cut(w.what_shows, 400) + (w.flags_added ? ' Flags added: ' + w.flags_added : '') + (w.sources && w.sources.length ? ' Sources: ' + urls(w.sources, 2) : '')); });
    (i.propaganda || []).forEach(function (p) { rep.push('Propaganda record' + (p.period ? ' (' + p.period + ')' : '') + ': ' + [p.kind, p.mechanism].filter(Boolean).join('; ') + ' — ' + cut(p.summary, 400)); });
    if (i.other_findings) rep.push('Other findings: ' + cut(i.other_findings, 600));
    if (d.not_related && d.not_related.length) rep.push('Not related to this space (do not attribute): ' + d.not_related.slice(0, 4).map(function (p) { return cut(p, 200); }).join(' | '));
    parts.push(section('REPORTED ON THE RECORD (each item names its source)', rep));

    var acc = ((i.gossip_data || {}).accounts || []).slice(0, opts.full ? 6 : 2).map(function (a) {
      return 'Account ' + (a.id || '') + (a.scope ? ' [' + a.scope + ']' : '') + ': ' + (a.fields || []).map(function (kv) { return Array.isArray(kv) ? kv[0] + ' — ' + cut(kv[1], 300) : cut(kv, 300); }).join('; ') + (a.sources && a.sources.length ? ' Source: ' + urls(a.sources, 1) : '');
    });
    parts.push(section('EMPLOYEE AND VISITOR ACCOUNTS (unverified platform posts by self-described reviewers; say so when citing one)', acc));

    var crit = [];
    if (i.critique_note) crit.push('Published critics on the record: ' + cut(i.critique_note, opts.full ? 1200 : 500));
    (i.visual_critiques || []).forEach(function (v) {
      if (!v) return;
      if (v.kind === 'theory' && v.quotes && v.quotes.length) crit.push('Critical frame (' + (v.strategy || 'theory') + ', about this type of museum, not a finding on this space): ' + v.quotes.slice(0, opts.full ? 4 : 2).map(function (q) { return [q.author, q.title, q.publication, q.date].filter(Boolean).join(', ') + ': ' + cut(q.text, 260); }).join(' | '));
      else if (v.artwork || v.artist) crit.push('Artist critique attached (a lens, not reception of this space): ' + [v.artist, v.artwork, v.year, v.target].filter(Boolean).join(', ') + (v.summary ? ' — ' + cut(v.summary, 220) : ''));
    });
    (i.study_notes || []).forEach(function (s) { crit.push('Study: ' + [s.authors, s.title, s.journal, s.year].filter(Boolean).join(', ') + (s.text ? ' — ' + cut(s.text, 400) : '')); });
    if (i.case_study && i.case_study.title) crit.push('Case study on the atlas: ' + i.case_study.title + (i.case_study.kick ? ' — ' + cut(i.case_study.kick, 300) : ''));
    parts.push(section('CRITICS AND STUDIES', crit));

    parts.push(section('VISITING', [
      i.opening_hours ? 'Opening hours: ' + i.opening_hours : '',
      (i.admission_fee || i.admission_details || i.admission_policy) ? 'Admission: ' + [i.admission_policy, i.admission_fee, i.admission_details].filter(Boolean).join('; ') : '',
      i.visit_duration ? 'Typical visit: ' + i.visit_duration : '',
      i.transit_tips ? 'Getting there: ' + i.transit_tips : '',
      i.accessibility ? 'Accessibility: ' + i.accessibility : '',
      i.amenities ? 'Amenities: ' + i.amenities : '',
      i.scale && i.scale.visitors ? 'Visitors: ' + i.scale.visitors.toLocaleString('en-GB') + (i.scale.visitors_year ? ' in ' + i.scale.visitors_year : '') : '',
      i.visit_url ? 'Visitor page: ' + i.visit_url : ''
    ]));

    var src = urls((i.sources || []).concat(d.sources || []), opts.full ? 10 : 5);
    parts.push(section('SOURCES', [src ? src : 'none recorded']));

    // Over budget, the longest section loses its last line, again and again, so the head, the visiting lines and the sources all
    // stay and no section is lost whole; a shortened section says so once.
    parts = parts.filter(Boolean);
    var length = function () { return parts.join('\n').length; };
    var guard = 400;
    while (length() > budget && guard-- > 0) {
      var at = -1, max = 0;
      for (var k = 1; k < parts.length - 1; k++) { var ls = parts[k].split('\n'); if (ls.length > 2 && !(ls.length === 3 && /more on the page/.test(ls[2])) && parts[k].length > max) { max = parts[k].length; at = k; } }
      if (at < 0) break;
      var lines = parts[at].split('\n');
      if (lines[lines.length - 1].indexOf('[more on the page]') >= 0) lines.pop();
      lines.pop();
      lines.push('    [more on the page]');
      parts[at] = lines.join('\n');
    }
    return parts.join('\n');
  }

  // The grade letter of a record, from the page's grade table when given.
  function letter(i, GRADE) { return i.grade && GRADE && GRADE[i.grade] ? GRADE[i.grade].letter : (i.grade ? String(i.grade) : ''); }

  // A question about a city or country as a whole is answered from every record in it, not the dozen the name search finds:
  // the count, the grade tally, each flagged space with its reason, the funders named most, the largest figures on record.
  function placeSummary(placeName, insts, GRADE) {
    if (!placeName || !insts || !insts.length) return '';
    var tally = {}, flagged = [], funders = {}, figs = [];
    insts.forEach(function (i) {
      var k = i.grade ? 'Grade ' + letter(i, GRADE) : 'ungraded';
      tally[k] = (tally[k] || 0) + 1;
      if (i.why_flagged || (i.flags || []).length) flagged.push(i);
      (i.funder_links || []).forEach(function (x) { if (x && x.funder) funders[x.funder] = (funders[x.funder] || 0) + 1; });
      if (i.finance && typeof i.finance.income === 'number' && i.finance.income > 0) figs.push(i);
    });
    var lines = [
      'Place: ' + placeName,
      'Spaces on the atlas: ' + insts.length,
      'Grades: ' + Object.keys(tally).sort().map(function (k) { return tally[k] + ' ' + k; }).join(', '),
      'All spaces (grade): ' + insts.slice().sort(function (a, b) { return (a.grade || 9) - (b.grade || 9) || a.name.localeCompare(b.name); }).map(function (i) { return i.name + (i.grade ? ' (' + letter(i, GRADE) + ')' : ''); }).slice(0, 80).join('; ') + (insts.length > 80 ? ' …' : '')
    ];
    if (flagged.length) lines.push('Flagged, with the reason on record: ' + flagged.slice(0, 25).map(function (i) { return i.name + ' — ' + cut(i.why_flagged || (i.flags || []).join(', '), 160); }).join(' | '));
    var top = Object.keys(funders).sort(function (a, b) { return funders[b] - funders[a]; }).slice(0, 8);
    if (top.length) lines.push('Funders named on more than one record here: ' + top.map(function (k) { return k + ' (' + funders[k] + ')'; }).join(', '));
    figs.sort(function (a, b) { return b.finance.income - a.finance.income; });
    if (figs.length) lines.push('Largest audited incomes on record: ' + figs.slice(0, 6).map(function (i) { return i.name + ' ' + money(i.finance.income, i.finance.currency) + (i.finance.fy ? ' (FY' + i.finance.fy + ')' : ''); }).join('; '));
    return '<place_summary>\n' + lines.join('\n') + '\n</place_summary>';
  }

  var api = { formatRecord: formatRecord, placeSummary: placeSummary, FULL: FULL, SHORT: SHORT };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.AtlasGrounding = api;
})(typeof window !== 'undefined' ? window : globalThis);
