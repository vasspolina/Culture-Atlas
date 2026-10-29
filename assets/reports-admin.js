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
          <div class="actions">${actionsFor(report.status)}</div>
        </article>
      `).join('');
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
