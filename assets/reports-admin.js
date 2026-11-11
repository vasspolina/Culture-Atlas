(function () {
  const API = (window.ATLAS_REPORT_API_URL || '').replace(/\/+$/, '');
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
  let token = '';
  let view = 'PENDING';
  const EMPTY = { PENDING: 'No notes are waiting for review.', APPROVED: 'No notes are on the atlas.', REJECTED: 'No notes were rejected.' };
  const WORD = { PENDING: 'waiting for review', APPROVED: 'on the atlas', REJECTED: 'rejected' };

  try { token = sessionStorage.getItem('atlas-report-admin-token') || ''; } catch {}

  function setVisible(id, visible) {
    $(id).classList.toggle('hidden', !visible);
  }

  async function api(path, options = {}) {
    const response = await fetch(API + path, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
      }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401) signOut('The admin token was not accepted.');
      throw new Error(body.error || `Request failed (${response.status}).`);
    }
    return body;
  }

  function signOut(message = '') {
    token = '';
    try { sessionStorage.removeItem('atlas-report-admin-token'); } catch {}
    $('tokenInput').value = '';
    setVisible('queue', false);
    setVisible('loginForm', true);
    $('loginError').textContent = message;
    setVisible('loginError', !!message);
  }

  const fileSize = n => n >= 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
  const objectUrls = [];

  // The files sent with a note. They are fetched with the token (a pending file is not public) and shown from memory.
  function filesFor(report) {
    const files = report.files || [];
    if (!files.length) return '';
    return `<p>${files.length} file${files.length === 1 ? '' : 's'} attached. Approved files are shown with the review; remove any that should not be.</p>
      <div class="files">${files.map(file => `
        <figure data-file="${esc(file.id)}" data-type="${esc(file.type)}">
          <a class="file-open" href="#" target="_blank" rel="noopener">${file.type.startsWith('image/') ? '<img alt="Attached photo">' : '<span class="pdf">PDF</span>'}</a>
          <figcaption>${file.type.startsWith('image/') ? 'Photo' : 'PDF'}, ${fileSize(file.size)}
            <button type="button" class="btn" data-remove-file="1">Remove file</button></figcaption>
        </figure>`).join('')}</div>`;
  }

  async function showFiles() {
    for (const figure of document.querySelectorAll('#list figure[data-file]')) {
      try {
        const response = await fetch(`${API}/api/admin/files/${encodeURIComponent(figure.dataset.file)}`, { headers: { Authorization: `Bearer ${token}` } });
        if (!response.ok) throw new Error(String(response.status));
        const url = URL.createObjectURL(await response.blob());
        objectUrls.push(url);
        figure.querySelector('a').href = url;
        const img = figure.querySelector('img');
        if (img) img.src = url;
      } catch {
        figure.querySelector('figcaption').prepend('Could not load this file. ');
      }
    }
  }

  function actionsFor(status) {
    return [
      status !== 'APPROVED' ? '<button type="button" class="btn approve" data-status="APPROVED">Approve</button>' : '',
      status === 'PENDING' ? '<button type="button" class="btn reject" data-status="REJECTED">Reject</button>' : '',
      status === 'APPROVED' ? '<button type="button" class="btn" data-status="PENDING">Take off the atlas</button>' : '',
      '<button type="button" class="btn delete" data-delete="1">Delete</button>'
    ].join('');
  }

  async function load() {
    $('status').textContent = 'Loading notes…';
    $('list').replaceChildren();
    objectUrls.splice(0).forEach(url => URL.revokeObjectURL(url));
    document.querySelectorAll('[data-view]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.view === view));
    });
    try {
      const reports = await api('/api/admin/reports?status=' + view);
      $('status').textContent = reports.length
        ? `${reports.length} note${reports.length === 1 ? '' : 's'} ${WORD[view]}.`
        : EMPTY[view];
      $('list').innerHTML = reports.map(report => `
        <article data-id="${esc(report.id)}">
          <p><strong>${esc(report.institution || report.city)}</strong>${report.institution ? ` | ${esc(report.city)}` : ''} · ${esc(new Date(report.createdAt).toLocaleString())}</p>
          <p>${report.authorLabel ? `shown as “${esc(report.authorLabel)}”` : 'shown as Whistleblower'}</p>
          <p style="white-space:pre-wrap">${esc(report.content)}</p>
          ${filesFor(report)}
          <div class="actions">${actionsFor(report.status)}</div>
        </article>
      `).join('');
      showFiles();
    } catch (error) {
      $('status').textContent = error.message;
    }
  }

  $('loginForm').addEventListener('submit', event => {
    event.preventDefault();
    token = $('tokenInput').value.trim();
    if (!token) return;
    setVisible('loginError', false);
    try { sessionStorage.setItem('atlas-report-admin-token', token); } catch {}
    setVisible('loginForm', false);
    setVisible('queue', true);
    load();
  });

  $('refreshBtn').addEventListener('click', load);
  document.querySelector('[data-view]').closest('div').addEventListener('click', event => {
    const button = event.target.closest('button[data-view]');
    if (!button) return;
    view = button.dataset.view;
    load();
  });
  $('signOutBtn').addEventListener('click', () => signOut());
  $('list').addEventListener('click', async event => {
    const removeFile = event.target.closest('button[data-remove-file]');
    if (removeFile) {
      const figure = removeFile.closest('figure');
      if (!window.confirm('Remove this file for good? The note stays.')) return;
      removeFile.disabled = true;
      try {
        await api(`/api/admin/files/${encodeURIComponent(figure.dataset.file)}`, { method: 'DELETE' });
        figure.remove();
        $('status').textContent = 'File removed.';
      } catch (error) {
        $('status').textContent = error.message;
        removeFile.disabled = false;
      }
      return;
    }
    const button = event.target.closest('button[data-status], button[data-delete]');
    if (!button) return;
    const article = button.closest('article');
    const id = encodeURIComponent(article.dataset.id);
    const removing = button.hasAttribute('data-delete');
    if (removing && !window.confirm('Delete this note for good? It cannot be brought back.')) return;
    const buttons = article.querySelectorAll('button');
    buttons.forEach(item => { item.disabled = true; });
    try {
      if (removing) await api(`/api/admin/reports/${id}`, { method: 'DELETE' });
      else await api(`/api/admin/reports/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status: button.dataset.status }) });
      article.remove();
      $('status').textContent = removing ? 'Note deleted.' : 'Note updated.';
    } catch (error) {
      $('status').textContent = error.message;
      buttons.forEach(item => { item.disabled = false; });
    }
  });

  if (!API) {
    setVisible('noBackend', true);
    $('loginForm').querySelector('button').disabled = true;
  } else if (token) {
    $('tokenInput').value = token;
    setVisible('loginForm', false);
    setVisible('queue', true);
    load();
  }
})();
