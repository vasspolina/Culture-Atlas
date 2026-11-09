// Sub-topic of a space: "tell me about the archive at MoMA" asks about the archive, not about MoMA.
// Pure functions, no DOM; index.html calls them from queryAI and from the record answers, and the test loads this file in Node.
(function (root) {
  var TOPICS = [
    { key: 'archive', label: 'archive', ask: /\b(archives?|archival)\b/i, held: /\barchiv/i },
    { key: 'library', label: 'library', ask: /\b(librar(?:y|ies))\b/i, held: /\blibrar/i },
    { key: 'collection', label: 'collection', ask: /\b(collections?|holdings)\b/i, held: /\b(collections?|holdings?)\b/i },
    { key: 'education', label: 'education programme', ask: /\b(education|learning programmes?|schools? programmes?)\b/i, held: /\beducation/i },
    { key: 'shop', label: 'shop', ask: /\b(shop|store|gift shop)\b/i, held: /\b(shop|store)\b/i },
    { key: 'cafe', label: 'café', ask: /\b(caf[eé]|restaurant)\b/i, held: /\b(caf[eé]|restaurant)\b/i },
    { key: 'garden', label: 'garden', ask: /\b(gardens?|sculpture park)\b/i, held: /\b(gardens?|sculpture park)\b/i }
  ];
  var FIELDS = ['highlight', 'funding', 'watch', 'why_flagged', 'curatorial_focus', 'governance_details', 'architecture_status', 'description'];

  // The sub-topic the question names next to the space, or null. The space's own name is cut out first, so "Wiener Library" is not a
  // question about a library; a bare "the collection" with no other noun still counts.
  function detectSubTopic(query, inst) {
    var q = String(query || '');
    var names = [];
    if (inst && inst.name) {
      names.push(inst.name);
      var m = /\(([^)]+)\)/.exec(inst.name);
      if (m) names.push(m[1]);
      names.push(inst.name.replace(/\s*\([^)]*\)/, ''));
    }
    names.forEach(function (n) {
      if (n && n.length > 2) q = q.replace(new RegExp(n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'ig'), ' ');
    });
    for (var i = 0; i < TOPICS.length; i++) if (TOPICS[i].ask.test(q)) return TOPICS[i];
    return null;
  }

  // Any other thing asked about a space ("symbol of the museum", "who is the director at MoMA"): the words left once the space's
  // name and the question's own words are cut out. Only the record answer's last branch uses it, after funding, hours, flags and
  // the rest have had their turn, so the visitor gets an answer to what was asked and not the whole record again (user, 4 Nov 2026).
  // A question with nothing left ("tell me about it", "what is this museum") is about the space as a whole and gets null.
  var STOP = new Set(('a an the of at in on for to from by with and or about tell me us more show give find what whats what\'s who whos ' +
    'is are was were be does do did has have had can could would should will it its it\'s this that these those there here please ' +
    'info information detail details record records overview summary story history describe explain know learn say says said ' +
    'museum museums space spaces gallery galleries institution institutions place venue foundation centre center kunsthalle ' +
    'how where when why which any some their they them his her i you your my our we').split(' '));
  var SYNONYMS = { symbol: 'symbol|logo|emblem|insignia|mascot', logo: 'symbol|logo|emblem|insignia', emblem: 'symbol|logo|emblem|insignia' };
  function stripNames(query, inst) {
    var q = String(query || '');
    var names = [];
    if (inst && inst.name) {
      names.push(inst.name);
      var m = /\(([^)]+)\)/.exec(inst.name);
      if (m) names.push(m[1]);
      names.push(inst.name.replace(/\s*\([^)]*\)/, ''));
    }
    names.sort(function (a, b) { return b.length - a.length; }).forEach(function (n) {
      if (n && n.length > 2) q = q.replace(new RegExp(n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'ig'), ' ');
    });
    return q;
  }
  function detectFreeTopic(query, inst) {
    var words = stripNames(query, inst).toLowerCase().replace(/[’']s\b/g, '').match(/[a-zÀ-ɏ][a-zÀ-ɏ-]*/g) || [];
    words = words.filter(function (w) { return w.length > 2 && !STOP.has(w); });
    if (!words.length || words.length > 4) return null;
    var stems = words.map(function (w) { return SYNONYMS[w] || (w.length > 5 ? w.slice(0, w.length - 2) : w); });
    return { key: 'free', label: words.join(' '), ask: new RegExp('\\b(' + stems.join('|') + ')', 'i'), held: new RegExp('\\b(' + stems.join('|') + ')', 'i') };
  }

  // The sentences of the record that mention the sub-topic: all the model, or the record answer, may say about it.
  function heldSentences(topic, inst) {
    if (!topic || !inst) return [];
    var out = [];
    FIELDS.forEach(function (f) {
      var v = inst[f];
      if (typeof v !== 'string') return;
      v.split(/(?<=[.!?])\s+/).forEach(function (s) { if (topic.held.test(s) && out.indexOf(s) < 0) out.push(s.trim()); });
    });
    return out;
  }

  // The <sub_topic> block for the grounded prompt.
  function subTopicBlock(topic, inst) {
    if (!topic || !inst) return '';
    var held = heldSentences(topic, inst);
    return '<sub_topic>\nThe visitor asked about the ' + topic.label + ' of ' + inst.name + ', not about the space as a whole. Answer about the ' + topic.label + ' in the first sentence. ' +
      (held.length
        ? 'The record text that mentions it, and all you may say about it:\n' + held.map(function (s) { return '- ' + s; }).join('\n') + '\nDo not add funders, amounts, dates or claims that these lines do not hold, and do not fall back on the space\'s grade or general record.'
        : 'The record text holds nothing on it. Say so in one sentence (the atlas has no record on the ' + topic.label + ' of ' + inst.name + '), then answer about the ' + topic.label + ' from your own knowledge, opening that part with the words "From general knowledge," and giving no figure, date or name you are not sure of (user, 9 Nov 2026: the model fills the gap). Do not give the space\'s grade, funding or general record in its place.') +
      '\n</sub_topic>\n\n';
  }

  // The no-model answer: plain text, or null when the question names no sub-topic.
  function subTopicRecordAnswer(topic, inst) {
    if (!topic || !inst) return null;
    var held = heldSentences(topic, inst);
    return held.length
      ? { held: true, text: held.join(' ') }
      : { held: false, text: 'The Atlas holds no record on the ' + topic.label + ' of ' + inst.name + '.' };
  }

  var api = { detectSubTopic: detectSubTopic, detectFreeTopic: detectFreeTopic, heldSentences: heldSentences, subTopicBlock: subTopicBlock, subTopicRecordAnswer: subTopicRecordAnswer };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.AtlasSubTopic = api;
})(typeof window !== 'undefined' ? window : globalThis);
