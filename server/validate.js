import { readFileSync } from 'node:fs';

export const LIMITS = { content: 2000, minContent: 10, label: 40, placeId: 120 };

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
  for (const row of rows) {
    if (!row || typeof row.id !== 'string' || typeof row.name !== 'string') continue;
    byId.set(row.id, { id: row.id, name: row.name, city: row.city || '' });
  }
  if (!byId.size) throw new Error(`No institutions with an id found in ${file}.`);
  return { byId };
}

export function findPlace(placeId, institutions) {
  if (typeof placeId !== 'string' || !placeId || placeId.length > LIMITS.placeId) return null;
  return institutions.byId.get(placeId) || null;
}

// Returns { error } or { data } ready for the database. Nothing from the sender but the text, an optional star
// rating, an optional display label and the place the review is filed under.
export function validateReview(body, place) {
  const source = body && typeof body === 'object' ? body : {};
  const content = cleanText(source.content);
  if (!content) return { error: 'Write the review first.' };
  if (content.length < LIMITS.minContent) return { error: `The review must be at least ${LIMITS.minContent} characters.` };
  if (content.length > LIMITS.content) return { error: `The review cannot be longer than ${LIMITS.content} characters.` };

  let rating = null;
  if (source.rating != null && source.rating !== '') {
    if (!Number.isInteger(source.rating) || source.rating < 1 || source.rating > 5) {
      return { error: 'The rating must be a whole number from 1 to 5, or left out.' };
    }
    rating = source.rating;
  }

  let authorLabel = null;
  if (source.authorLabel != null && source.authorLabel !== '') {
    if (typeof source.authorLabel !== 'string' || source.authorLabel.length > LIMITS.label * 4) {
      return { error: `The name must be text no longer than ${LIMITS.label} characters.` };
    }
    authorLabel = cleanText(source.authorLabel).replace(/\s+/g, ' ');
    if (authorLabel.length > LIMITS.label) return { error: `The name must be text no longer than ${LIMITS.label} characters.` };
    authorLabel = authorLabel || null;
  }

  return { data: { content, rating, authorLabel, placeId: place.id, institution: place.name, city: place.city || 'Unspecified' } };
}
