import { readFileSync } from 'node:fs';

export const LIMITS = { content: 2000, minContent: 10, label: 40, placeId: 120, placeName: 120, minPlaceName: 2, city: 80, address: 200 };

// Plain text only. Tags (and what a script or style tag holds), control characters and stray angle brackets are
// removed, runs of spaces collapse, and no more than one blank line survives. The page escapes the text again.
export function cleanText(value) {
  if (typeof value !== 'string') return '';
  return value
    .normalize('NFC')
    .replace(/<(script|style)\b[\s\S]*?<\/\1\s*>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<\/?[a-z!?][^>]*>/gi, ' ')
    .replace(/[<>]/g, '')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F​-‏‪-‮⁠﻿]/g, '')
    .replace(/\r\n?/g, '\n')
    .replace(/[^\S\n]+/g, ' ')
    .replace(/ *\n */g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// The places a review may be about, read from the atlas data so a review always names a real record.
export function loadInstitutions(file) {
  const rows = JSON.parse(readFileSync(file, 'utf8'));
  if (!Array.isArray(rows) || !rows.length) throw new Error(`No institutions found in ${file}.`);
  const byId = new Map();
  const byName = new Map();
  for (const row of rows) {
    if (!row || typeof row.id !== 'string' || typeof row.name !== 'string') continue;
    const place = { id: row.id, name: row.name, city: row.city || '' };
    byId.set(row.id, place);
    byName.set(nameKey(row.name), place);
  }
  if (!byId.size) throw new Error(`No institutions with an id found in ${file}.`);
  return { byId, byName };
}

// Names compared without case, accents or punctuation, so "Musée d'Orsay" and "musee dorsay" are the same place.
export function nameKey(name) {
  return String(name || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '');
}

export function findPlace(placeId, institutions) {
  if (typeof placeId !== 'string' || !placeId || placeId.length > LIMITS.placeId) return null;
  return institutions.byId.get(placeId) || null;
}

// Returns { error } or { data } ready for the database. Nothing from the sender but the text, an optional display
// label and the place the review is filed under.
export function validateReview(body, place) {
  const source = body && typeof body === 'object' ? body : {};
  const content = cleanText(source.content);
  if (!content) return { error: 'Write the review first.' };
  if (content.length < LIMITS.minContent) return { error: `The review must be at least ${LIMITS.minContent} characters.` };
  if (content.length > LIMITS.content) return { error: `The review cannot be longer than ${LIMITS.content} characters.` };

  let authorLabel = null;
  if (source.authorLabel != null && source.authorLabel !== '') {
    if (typeof source.authorLabel !== 'string' || source.authorLabel.length > LIMITS.label * 4) {
      return { error: `The name must be text no longer than ${LIMITS.label} characters.` };
    }
    authorLabel = cleanText(source.authorLabel).replace(/\s+/g, ' ');
    if (authorLabel.length > LIMITS.label) return { error: `The name must be text no longer than ${LIMITS.label} characters.` };
    authorLabel = authorLabel || null;
  }

  return { data: { kind: 'review', content, authorLabel, placeId: place.id, institution: place.name, city: place.city || 'Unspecified' } };
}

function oneLine(value) {
  return cleanText(typeof value === 'string' ? value.slice(0, 1000) : '').replace(/\s+/g, ' ');
}

// A place the atlas is missing (user, 18 Nov 2026). The sender names it and its city; the note says what they know.
// A name the atlas already has is refused with that record's id, so the note goes on the record instead.
// Returns { error, status?, placeId? } or { data }.
export function validateNewPlace(body, institutions) {
  const source = body && typeof body === 'object' ? body : {};
  const name = oneLine(source.placeName);
  if (name.length < LIMITS.minPlaceName) return { error: 'Write the name of the place.' };
  if (name.length > LIMITS.placeName) return { error: `The name of the place cannot be longer than ${LIMITS.placeName} characters.` };
  const city = oneLine(source.city);
  if (!city) return { error: 'Write the city or town the place is in.' };
  if (city.length > LIMITS.city) return { error: `The city cannot be longer than ${LIMITS.city} characters.` };
  // The street address is optional (user, 19 Nov 2026), so the editor can find the place.
  const address = oneLine(source.address);
  if (address.length > LIMITS.address) return { error: `The address cannot be longer than ${LIMITS.address} characters.` };
  const known = institutions.byName && institutions.byName.get(nameKey(name));
  if (known) return { error: `${known.name} is on the atlas already. Choose it from the list to add to its record.`, status: 409, placeId: known.id };
  const result = validateReview(source, { id: null, name, city });
  if (result.error) return result;
  return { data: { ...result.data, kind: 'new-place', placeId: null, address: address || null } };
}
