import { readFileSync } from 'node:fs';

export const LIMITS = { content: 2000, minContent: 10, name: 200 };

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

const fold = value => cleanText(value).toLowerCase().replace(/\s+/g, ' ');

// The institutions and cities a note may be about, read from the atlas data so a note always names a real record.
export function loadInstitutions(file) {
  const rows = JSON.parse(readFileSync(file, 'utf8'));
  if (!Array.isArray(rows) || !rows.length) throw new Error(`No institutions found in ${file}.`);
  const byName = new Map();
  const cities = new Map();
  for (const row of rows) {
    if (!row || typeof row.name !== 'string') continue;
    const entry = { name: row.name, city: row.city || '' };
    byName.set(fold(row.name), entry);
    if (row.city) cities.set(fold(row.city), row.city);
  }
  return { byName, cities };
}

// Returns { error } or { data } ready for the database. Nothing from the sender but the text and the place.
export function validateReport(body, institutions) {
  const source = body && typeof body === 'object' ? body : {};
  const content = cleanText(source.content);
  if (!content) return { error: 'Write the note first.' };
  if (content.length < LIMITS.minContent) return { error: `The note must be at least ${LIMITS.minContent} characters.` };
  if (content.length > LIMITS.content) return { error: `The note cannot be longer than ${LIMITS.content} characters.` };

  for (const field of ['institution', 'city']) {
    const value = source[field];
    if (value != null && value !== '' && (typeof value !== 'string' || value.length > LIMITS.name * 2)) {
      return { error: `${field === 'city' ? 'City' : 'Institution'} must be text no longer than ${LIMITS.name} characters.` };
    }
  }
  const institutionName = cleanText(source.institution);
  const cityName = cleanText(source.city);
  if (!institutionName && !cityName) return { error: 'Name the institution this note is about.' };

  if (institutionName) {
    const match = institutions.byName.get(fold(institutionName));
    if (!match) return { error: 'That institution is not on the atlas. Use the name as the record gives it.' };
    return { data: { content, institution: match.name, city: match.city || 'Unspecified' } };
  }
  const city = institutions.cities.get(fold(cityName));
  if (!city) return { error: 'That city is not on the atlas.' };
  return { data: { content, institution: null, city } };
}
