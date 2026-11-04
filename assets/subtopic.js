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
        : 'The record text holds nothing on it. Say so plainly in one or two sentences, for example that the Atlas has no record on the ' + topic.label + ' of ' + inst.name + '. Do not give the space\'s grade, funding or general record in its place, and never invent a funder, amount or claim.') +
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

  var api = { detectSubTopic: detectSubTopic, heldSentences: heldSentences, subTopicBlock: subTopicBlock, subTopicRecordAnswer: subTopicRecordAnswer };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.AtlasSubTopic = api;
})(typeof window !== 'undefined' ? window : globalThis);
