export type Tier = 'A' | 'B' | 'U';
export type Size = 'S' | 'L';

export interface Institution {
  n: string;   // Name
  c: string;   // City, Country
  t: Tier;     // Tier: A = Clean/Verified, B = One flag/name to know, U = Roster unverified
  s: Size;     // S = Small/mid, L = Large ($20M+ budget or 500k+ visitors)
  f: string;   // Funding breakdown & sponsors
  w: string;   // Note, flag details, or controversy context
  u: string[]; // Source URLs
  la: number;  // Latitude
  lo: number;  // Longitude
}

export interface TierInfo {
  c: string; // CSS color var
  colorHex: string;
  l: string; // Label
}

export const TIER: Record<Tier, TierInfo> = {
  A: { c: 'var(--clean)', colorHex: '#24a148', l: 'Verified' },
  B: { c: 'var(--flag)', colorHex: '#4589ff', l: 'One name to know' },
  U: { c: 'var(--open)', colorHex: '#8d8d8d', l: 'Roster unverified' },
};
