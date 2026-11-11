// Files attached to a review: photos, screenshots and PDFs. The type is read from the file's own first bytes, never from
// what the sender says it is, and only four kinds pass. Photos lose everything but the picture: camera, time, place
// (GPS) and editing software are all held in metadata blocks, and those blocks are removed here before anything is
// stored. The page already removes them in the browser; this is the second pass, for a sender whose browser did not.
// PDFs are stored as sent: their document properties (author, software) are not rewritten, and the form says so.
// No original file name is kept, since a file name can carry a person's name.

export const FILE_LIMITS = { count: 4, bytes: 5 * 1024 * 1024, total: 12 * 1024 * 1024 };
export const FILE_TYPES = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
  'application/pdf': 'pdf'
};

const BASE64 = /^[A-Za-z0-9+/]*={0,2}$/;

export function sniffType(buf) {
  if (buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return 'image/jpeg';
  if (buf.length >= 8 && buf.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return 'image/png';
  if (buf.length >= 12 && buf.toString('latin1', 0, 4) === 'RIFF' && buf.toString('latin1', 8, 12) === 'WEBP') return 'image/webp';
  if (buf.length >= 5 && buf.toString('latin1', 0, 5) === '%PDF-') return 'application/pdf';
  return null;
}

// JPEG: keeps the segments that draw the picture (tables, frame, scan) and three that change how it looks: JFIF (APP0),
// an ICC colour profile (APP2 "ICC_PROFILE") and Adobe's colour transform (APP14). EXIF and XMP (APP1), every other APPn
// block and comments go. From the start of the scan on, the bytes are copied as they are.
export function stripJpeg(buf) {
  const out = [buf.subarray(0, 2)];
  let i = 2;
  while (i < buf.length) {
    if (buf[i] !== 0xff) throw new Error('bad jpeg');
    const marker = buf[i + 1];
    if (marker === 0xff) { i += 1; continue; }                       // fill byte
    if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { out.push(buf.subarray(i, i + 2)); i += 2; continue; }
    if (marker === 0xd9) { out.push(buf.subarray(i, i + 2)); break; } // end of image
    if (i + 4 > buf.length) throw new Error('bad jpeg');
    const len = buf.readUInt16BE(i + 2);
    if (len < 2 || i + 2 + len > buf.length) throw new Error('bad jpeg');
    const segment = buf.subarray(i, i + 2 + len);
    if (marker === 0xda) { out.push(buf.subarray(i)); break; }        // start of scan: the rest is picture
    const isApp = marker >= 0xe0 && marker <= 0xef;
    const keep = !isApp && marker !== 0xfe
      || marker === 0xe0
      || marker === 0xee
      || (marker === 0xe2 && segment.toString('latin1', 4, 15) === 'ICC_PROFILE');
    if (keep) out.push(segment);
    i += 2 + len;
  }
  return Buffer.concat(out);
}

// PNG: keeps the chunks that draw the picture and set its colour, size and animation. Text chunks (tEXt, zTXt, iTXt),
// EXIF (eXIf), the time (tIME) and anything unknown go.
const PNG_KEEP = new Set(['IHDR', 'PLTE', 'IDAT', 'IEND', 'tRNS', 'gAMA', 'cHRM', 'sRGB', 'iCCP', 'sBIT', 'bKGD', 'pHYs', 'acTL', 'fcTL', 'fdAT']);
export function stripPng(buf) {
  const out = [buf.subarray(0, 8)];
  let i = 8;
  let ended = false;
  while (i + 12 <= buf.length) {
    const len = buf.readUInt32BE(i);
    const type = buf.toString('latin1', i + 4, i + 8);
    const end = i + 12 + len;
    if (end > buf.length) throw new Error('bad png');
    if (PNG_KEEP.has(type)) out.push(buf.subarray(i, end));
    i = end;
    if (type === 'IEND') { ended = true; break; }
  }
  if (!ended) throw new Error('bad png');
  return Buffer.concat(out);
}

// WebP: drops the EXIF and XMP chunks and clears their flags in the VP8X header, then writes the new RIFF size.
export function stripWebp(buf) {
  const chunks = [];
  let i = 12;
  while (i + 8 <= buf.length) {
    const fourcc = buf.toString('latin1', i, i + 4);
    const size = buf.readUInt32LE(i + 4);
    const end = i + 8 + size + (size % 2);
    if (i + 8 + size > buf.length) throw new Error('bad webp');
    if (fourcc !== 'EXIF' && fourcc !== 'XMP ') {
      const chunk = Buffer.from(buf.subarray(i, Math.min(end, buf.length)));
      if (fourcc === 'VP8X' && size >= 1) chunk[8] &= ~(0x08 | 0x04);
      chunks.push(chunk);
    }
    i = end;
  }
  if (!chunks.length) throw new Error('bad webp');
  const body = Buffer.concat(chunks);
  const head = Buffer.alloc(12);
  head.write('RIFF', 0, 'latin1');
  head.writeUInt32LE(body.length + 4, 4);
  head.write('WEBP', 8, 'latin1');
  return Buffer.concat([head, body]);
}

const STRIP = { 'image/jpeg': stripJpeg, 'image/png': stripPng, 'image/webp': stripWebp };

// Returns { error } or { files: [{ type, size, data }] }. `list` is what the client sent: an array of { data } with the
// file as base64. Anything else on an entry (a name, a claimed type) is ignored.
export function validateFiles(list) {
  if (list == null) return { files: [] };
  if (!Array.isArray(list)) return { error: 'Files must be sent as a list.' };
  if (list.length > FILE_LIMITS.count) return { error: `Attach at most ${FILE_LIMITS.count} files.` };
  const files = [];
  let total = 0;
  for (const [n, entry] of list.entries()) {
    const which = list.length > 1 ? ` (file ${n + 1})` : '';
    const raw = entry && typeof entry === 'object' ? entry.data : null;
    if (typeof raw !== 'string' || !raw || raw.length > Math.ceil(FILE_LIMITS.bytes / 3) * 4 + 4 || !BASE64.test(raw)) {
      return { error: `A file could not be read${which}, or it is larger than 5 MB.` };
    }
    const buf = Buffer.from(raw, 'base64');
    if (!buf.length) return { error: `A file is empty${which}.` };
    if (buf.length > FILE_LIMITS.bytes) return { error: `A file is larger than 5 MB${which}.` };
    const type = sniffType(buf);
    if (!type) return { error: `Only photos (JPEG, PNG, WebP) and PDFs can be attached${which}.` };
    let data = buf;
    if (STRIP[type]) {
      try { data = STRIP[type](buf); } catch { return { error: `That image could not be read${which}.` }; }
    } else if (!buf.subarray(Math.max(0, buf.length - 1024)).toString('latin1').includes('%%EOF')) {
      return { error: `That PDF is incomplete${which}.` };
    }
    total += data.length;
    if (total > FILE_LIMITS.total) return { error: 'The files together are larger than 12 MB.' };
    files.push({ type, size: data.length, data });
  }
  return { files };
}
