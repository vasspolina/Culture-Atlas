// Files sent with a whistleblower note: photos, screenshots and PDFs, attached the way a chat takes them: the Attach
// button, a drop onto the note box, or a paste. Each file shows as a chip above the box and can be taken off again.
//
// Photos are drawn again in this browser before they are sent, which leaves only the picture: the camera, the time and
// the place a phone writes into a photo do not survive. The report API removes the same data a second time. PDFs are
// sent as they are; the form says that their document properties can carry a name. No file name is sent.
//
// The note form reads the files with window.atlasNoteFiles.payload() when it sends, and calls clear() once it is sent.
(function () {
  const LIMITS = { count: 4, bytes: 5 * 1024 * 1024, total: 12 * 1024 * 1024, side: 2560 };
  const PHOTO = /^image\//;
  const $ = (id) => document.getElementById(id);
  const files = [];   // { id, kind: 'image' | 'pdf', blob, url, label }
  let nextId = 1;
  let busy = 0;

  const inNoteMode = () => document.body.classList.contains('chat-input-mode-active');
  const size = (n) => n >= 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
  const total = () => files.reduce((n, f) => n + f.blob.size, 0);

  function say(text) {
    const box = $('noteFileInfo');
    if (!box) return;
    box.textContent = text || '';
    box.hidden = !text;
  }

  // What the line under the chips says while nothing has gone wrong: what happens to the files, and the PDF caution.
  function sayDefault() {
    if (!files.length) return say('');
    const parts = [];
    if (files.some(f => f.kind === 'image')) parts.push('Location and camera details are removed from photos. Check what the picture itself shows.');
    if (files.some(f => f.kind === 'pdf')) parts.push('A PDF is sent as it is: its document properties can hold the name of whoever made it.');
    parts.push('Approved files are shown with the review.');
    say(parts.join(' '));
  }

  function render() {
    const list = $('noteFileList');
    if (!list) return;
    list.replaceChildren(...files.map(f => {
      const li = document.createElement('li');
      li.className = 'note-file';
      if (f.kind === 'image') {
        const img = document.createElement('img');
        img.src = f.url;
        img.alt = '';
        li.appendChild(img);
      } else {
        const tile = document.createElement('span');
        tile.className = 'note-file-tile';
        tile.textContent = 'PDF';
        li.appendChild(tile);
      }
      const text = document.createElement('span');
      text.className = 'note-file-text';
      const name = document.createElement('span');
      name.className = 'note-file-name';
      name.textContent = f.label;
      const meta = document.createElement('span');
      meta.className = 'note-file-meta';
      meta.textContent = `${f.kind === 'image' ? 'Photo' : 'PDF'}, ${size(f.blob.size)}`;
      text.append(name, meta);
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'note-file-remove';
      remove.dataset.fileId = String(f.id);
      remove.setAttribute('aria-label', `Remove ${f.label}`);
      remove.title = 'Remove';
      remove.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>';
      li.append(text, remove);
      return li;
    }));
    list.hidden = !files.length;
    const btn = $('noteAttachBtn');
    if (btn) btn.disabled = files.length >= LIMITS.count;
  }

  // Draws a photo onto a canvas and returns the canvas's own file, which has no metadata. A photo the browser cannot
  // read (a HEIC photo in Chrome, say) is refused with a reason rather than sent unread.
  async function redraw(file) {
    let source;
    try {
      source = await createImageBitmap(file, { imageOrientation: 'from-image' });
    } catch (e) {
      source = await new Promise((resolve, reject) => {
        const img = new Image();
        const url = URL.createObjectURL(file);
        img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
        img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('unreadable')); };
        img.src = url;
      });
    }
    const w = source.width || source.naturalWidth;
    const h = source.height || source.naturalHeight;
    if (!w || !h) throw new Error('unreadable');
    const scale = Math.min(1, LIMITS.side / Math.max(w, h));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(w * scale);
    canvas.height = Math.round(h * scale);
    const ctx = canvas.getContext('2d');
    // A screenshot (PNG) keeps sharp text as PNG while it stays small enough; everything else becomes a JPEG.
    const png = file.type === 'image/png';
    if (!png) { ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height); }
    ctx.drawImage(source, 0, 0, canvas.width, canvas.height);
    if (source.close) source.close();
    const encode = (type, q) => new Promise((resolve) => canvas.toBlob(resolve, type, q));
    let blob = png ? await encode('image/png') : null;
    if (!blob || blob.size > LIMITS.bytes) {
      if (png) { ctx.globalCompositeOperation = 'destination-over'; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height); }
      blob = await encode('image/jpeg', 0.88);
    }
    if (!blob) throw new Error('unreadable');
    return blob;
  }

  async function add(list) {
    const incoming = [...(list || [])];
    if (!incoming.length) return;
    let problem = '';
    for (const file of incoming) {
      if (files.length + busy >= LIMITS.count) { problem = `A note can carry at most ${LIMITS.count} files.`; break; }
      const isPdf = file.type === 'application/pdf' || /\.pdf$/i.test(file.name || '');
      if (!isPdf && !PHOTO.test(file.type)) { problem = `${file.name || 'That file'} is not a photo or a PDF.`; continue; }
      busy += 1;
      say('Preparing…');
      try {
        let blob;
        if (isPdf) {
          blob = file;
        } else {
          try { blob = await redraw(file); } catch (e) { problem = `This browser cannot read ${file.name || 'that photo'}. Send it as a JPEG or PNG.`; continue; }
        }
        if (blob.size > LIMITS.bytes) { problem = `${file.name || 'That file'} is larger than 5 MB.`; continue; }
        if (total() + blob.size > LIMITS.total) { problem = 'The files together would be larger than 12 MB.'; continue; }
        const kind = isPdf ? 'pdf' : 'image';
        files.push({ id: nextId++, kind, blob, url: kind === 'image' ? URL.createObjectURL(blob) : '', label: file.name || (kind === 'image' ? 'Pasted image' : 'Document') });
        render();
      } finally {
        busy -= 1;
      }
    }
    if (problem) say(problem); else sayDefault();
  }

  function removeFile(id) {
    const i = files.findIndex(f => f.id === id);
    if (i < 0) return;
    if (files[i].url) URL.revokeObjectURL(files[i].url);
    files.splice(i, 1);
    render();
    sayDefault();
  }

  const toBase64 = (blob) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).replace(/^data:[^,]*,/, ''));
    reader.onerror = () => reject(reader.error || new Error('read failed'));
    reader.readAsDataURL(blob);
  });

  window.atlasNoteFiles = {
    count: () => files.length,
    busy: () => busy > 0,
    // Only the bytes: no name, no claimed type. The API reads the type from the file itself.
    payload: () => Promise.all(files.map(async f => ({ data: await toBase64(f.blob) }))),
    clear() {
      files.splice(0).forEach(f => { if (f.url) URL.revokeObjectURL(f.url); });
      render();
      say('');
    }
  };

  const input = $('noteFileInput');
  const btn = $('noteAttachBtn');
  if (!input || !btn) return;

  btn.addEventListener('click', () => input.click());
  input.addEventListener('change', () => { add(input.files); input.value = ''; });
  $('noteFileList').addEventListener('click', (e) => {
    const b = e.target.closest('.note-file-remove');
    if (b) removeFile(Number(b.dataset.fileId));
  });

  // A paste of an image into the note box attaches it; pasted text goes in as text, as before.
  $('workInput').addEventListener('paste', (e) => {
    if (!inNoteMode()) return;
    const pasted = [...((e.clipboardData && e.clipboardData.files) || [])];
    if (!pasted.length) return;
    e.preventDefault();
    add(pasted);
  });

  // A drop anywhere on the note card attaches what was dropped.
  const card = $('workInputCard');
  let depth = 0;
  const hasFiles = (e) => e.dataTransfer && [...(e.dataTransfer.types || [])].includes('Files');
  card.addEventListener('dragenter', (e) => { if (!inNoteMode() || !hasFiles(e)) return; e.preventDefault(); depth += 1; card.classList.add('is-file-over'); });
  card.addEventListener('dragover', (e) => { if (!inNoteMode() || !hasFiles(e)) return; e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
  card.addEventListener('dragleave', () => { depth = Math.max(0, depth - 1); if (!depth) card.classList.remove('is-file-over'); });
  card.addEventListener('drop', (e) => {
    depth = 0;
    card.classList.remove('is-file-over');
    if (!inNoteMode() || !hasFiles(e)) return;
    e.preventDefault();
    add(e.dataTransfer.files);
  });
})();
