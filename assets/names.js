// A space named in another language: "Jewish museum berlin" is the Jüdisches Museum Berlin, "german history museum" the
// Deutsches Historisches Museum, "musee d'orsay" the Musée d'Orsay. Pure functions, no DOM; index.html calls them from the
// name resolvers and the test loads this file in Node.
(function (root) {
  // Each word of a name is folded (accents off, lower case) and then mapped to one English stem, so the two spellings meet.
  var STEM = {
    // German
    judisch: 'jewish', judische: 'jewish', judisches: 'jewish', juedisch: 'jewish', juedisches: 'jewish',
    deutsch: 'german', deutsche: 'german', deutsches: 'german', deutschen: 'german',
    staatlich: 'state', staatliche: 'state', staatliches: 'state', staatlichen: 'state', landes: 'state',
    stadtisch: 'city', stadtische: 'city', stadtisches: 'city', stadt: 'city',
    museen: 'museum', museums: 'museum',
    kunst: 'art', kunste: 'art', kunsthalle: 'kunsthalle', kunstmuseum: 'art museum', kunstverein: 'kunstverein',
    galerie: 'gallery', galerien: 'gallery', nationalgalerie: 'national gallery',
    geschichte: 'history', historisch: 'history', historische: 'history', historisches: 'history', historischen: 'history',
    naturkunde: 'natural history', naturkundemuseum: 'natural history museum', technik: 'technology',
    moderne: 'modern', modernen: 'modern', zeitgenossisch: 'contemporary', zeitgenossische: 'contemporary', zeitgenossischen: 'contemporary', gegenwart: 'contemporary', gegenwartskunst: 'contemporary art',
    sammlung: 'collection', stiftung: 'foundation', haus: 'house', schloss: 'palace', palais: 'palace',
    fotografie: 'photography', photographie: 'photography', architektur: 'architecture', gestaltung: 'design',
    fur: 'of', fuer: 'of', der: 'the', die: 'the', das: 'the', des: 'the', dem: 'the', und: 'and', zu: 'of', im: 'in', am: 'at',
    // French
    musee: 'museum', musees: 'museum', beaux: 'fine', nationale: 'national', nationaux: 'national',
    histoire: 'history', contemporain: 'contemporary', contemporaine: 'contemporary',
    juif: 'jewish', juive: 'jewish', judaisme: 'jewish',
    du: 'of', de: 'of', la: 'the', le: 'the', les: 'the', et: 'and',
    // Spanish, Italian, Portuguese
    museo: 'museum', museu: 'museum', nacional: 'national', nazionale: 'national', nazionali: 'national',
    arte: 'art', arti: 'art', artes: 'art', moderno: 'modern', moderna: 'modern', contemporaneo: 'contemporary', contemporanea: 'contemporary',
    historia: 'history', storia: 'history', judio: 'jewish', judia: 'jewish', ebraico: 'jewish',
    fundacion: 'foundation', fondazione: 'foundation', fundacao: 'foundation', galleria: 'gallery', galeria: 'gallery',
    palacio: 'palace', palazzo: 'palace', casa: 'house', bellas: 'fine', belle: 'fine',
    del: 'of', della: 'of', dell: 'of', degli: 'of', delle: 'of', dos: 'of', el: 'the', il: 'the', lo: 'the', y: 'and', e: 'and',
    // Dutch
    joods: 'jewish', joodse: 'jewish', nationaal: 'national', rijksmuseum: 'rijksmuseum', stedelijk: 'municipal',
    geschiedenis: 'history', kunsten: 'art', hedendaagse: 'contemporary', van: 'of', het: 'the', en: 'and',
    // English variants
    centre: 'center', theatre: 'theater', jewish: 'jewish', hebrew: 'hebrew'
  };
  var STOP = { the: 1, of: 1, and: 1, in: 1, at: 1, a: 1, an: 1, for: 1, to: 1, on: 1 };

  function fold(s) {
    return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ß/g, 'ss').toLowerCase();
  }
  // The content words of a name or a question, each translated to its English stem; "museum" stays, articles go.
  function stems(s) {
    var out = [];
    fold(s).split(/[^a-z0-9]+/).forEach(function (w) {
      if (!w) return;
      var m = STEM[w];
      if (m === undefined) m = w;
      m.split(' ').forEach(function (p) { if (p && !STOP[p]) out.push(p); });
    });
    return out;
  }
  // A question that only puts the words of a space's name in another order or language ("Jewish museum berlin",
  // "berlin jewish museum") resolves to that one space. Every content word of the question must be in the name,
  // and the name's own words must mostly be in the question, so "museum berlin" never picks one of many.
  var ASK_WORDS = /^(?:(?:please|can you|could you|now)\s+)*(?:(?:what about|tell me about|about|show me|show|how about|go to|go back to|take me to|bring me to|fly me to|fly to|move to|jump to|head to|navigate to|zoom(?: back)?(?: in| out)?(?: to| on| onto| into| over)?|center on|centre on|focus on|open|find|visit|who funds|what is|where is)\s+)+/;
  // Words that name a kind of space rather than one space; a question made only of these and a place names no one record.
  var GENERIC = { museum: 1, gallery: 1, art: 1, arts: 1, modern: 1, contemporary: 1, national: 1, state: 1, city: 1, center: 1, house: 1,
    foundation: 1, institute: 1, collection: 1, history: 1, fine: 1, new: 1, old: 1, kunsthalle: 1, kunstverein: 1, palace: 1, design: 1,
    photography: 1, architecture: 1, natural: 1, technology: 1, science: 1, culture: 1, cultural: 1, jewish: 0 };
  function findNamedSpace(text, institutions) {
    if (!text || !institutions || !institutions.length) return null;
    var q = fold(text).trim().replace(ASK_WORDS, '').replace(/[?!.,\s]+$/, '').replace(/^the\s+/, '');
    var qs = stems(q);
    if (qs.length < 2) return null;
    // At least one word must be the space's own: not a kind of space, not a city or country on the map.
    var places = {};
    institutions.forEach(function (i) { if (i) stems([i.city, i.country].filter(Boolean).join(' ')).forEach(function (w) { places[w] = 1; }); });
    if (!qs.some(function (w) { return !GENERIC[w] && !places[w]; })) return null;
    var hits = [], exact = [];
    for (var k = 0; k < institutions.length; k++) {
      var inst = institutions[k];
      if (!inst || !inst.name) continue;
      // The record's own city and country may follow the name ("neue nationalgalerie berlin"); they are not part of it.
      var place = stems([inst.city, inst.country].filter(Boolean).join(' '));
      var asked = qs.filter(function (w) { return place.indexOf(w) === -1; });
      if (asked.length < 1) continue;
      var names = [inst.name].concat(inst.aliases || []);
      for (var a = 0; a < names.length; a++) {
        var ns = stems(names[a]);
        if (ns.length < 2) continue;
        var allAsked = asked.every(function (w) { return ns.indexOf(w) !== -1; });
        if (!allAsked) continue;
        var covered = ns.filter(function (w) { return asked.indexOf(w) !== -1; }).length;
        // The name's words must be at least two thirds covered, and the name must not be more than one word longer.
        if (covered >= Math.ceil(ns.length * 2 / 3) && ns.length - covered <= 1) {
          hits.push(inst);
          if (ns.join(' ') === asked.join(' ')) exact.push(inst);
          break;
        }
      }
    }
    if (hits.length === 1) return hits[0];
    // Several: the one spelled out in full and in order ("Deutsches Historisches Museum" over "Museum für Deutsche Geschichte").
    if (exact.length === 1) return exact[0];
    return null;
  }

  var api = { fold: fold, stems: stems, findNamedSpace: findNamedSpace };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.AtlasNames = api;
})(typeof window !== 'undefined' ? window : globalThis);
