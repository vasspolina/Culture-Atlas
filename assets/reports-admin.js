(function () {
  const API = (window.ATLAS_REPORT_API_URL || '').replace(/\/+$/, '');
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
  let token = '';

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

  async function loadPending() {
    $('status').textContent = 'Loading reports…';
    $('list').replaceChildren();
    try {
      const reports = await api('/api/admin/reports/pending');
      $('status').textContent = reports.length
        ? `${reports.length} report${reports.length === 1 ? '' : 's'} waiting for review.`
        : 'No submissions are waiting for review.';
      $('list').innerHTML = reports.map(report => `
        <article data-id="${esc(report.id)}">
          <p><strong>${esc(report.city)}</strong>${report.institution ? ` | ${esc(report.institution)}` : ''} · ${esc(new Date(report.createdAt).toLocaleString())}</p>
          <p>${esc(report.content)}</p>
          <div class="actions">
            <button type="button" class="btn approve" data-status="APPROVED">Approve &amp; Post to Map</button>
            <button type="button" class="btn reject" data-status="REJECTED">Reject</button>
          </div>
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
    loadPending();
  });

  $('refreshBtn').addEventListener('click', loadPending);
  $('signOutBtn').addEventListener('click', () => signOut());
  $('list').addEventListener('click', async event => {
    const button = event.target.closest('button[data-status]');
    if (!button) return;
    const article = button.closest('article');
    const buttons = article.querySelectorAll('button');
    buttons.forEach(item => { item.disabled = true; });
    try {
      await api(`/api/admin/reports/${encodeURIComponent(article.dataset.id)}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: button.dataset.status })
      });
      article.remove();
      $('status').textContent = 'Report updated.';
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
    loadPending();
  }
})();
