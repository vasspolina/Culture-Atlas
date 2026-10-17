// Review page for notes sent with Share information. Talks to the submissions Worker (worker/index.js).
(function () {
  const API = (window.ATLAS_SUBMIT_URL || '').replace(/\/+$/, '');
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const KIND = { information: 'Information', gossip: 'Gossip', whistleblower: 'Whistleblower' };
  let token = '';
  try { token = sessionStorage.getItem('atlas-review-token') || ''; } catch (e) {}
  let view = 'pending';

  $('themeBtn').addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('atlas-theme', next); } catch (e) {}
  });

  async function api(path, opts = {}) {
    const res = await fetch(API + path, { ...opts, headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token, ...(opts.headers || {}) } });
    const body = await res.json().catch(() => ({}));
    if (res.status === 401) { signOut('That password did not work.'); throw new Error('Wrong password.'); }
    if (!res.ok) throw new Error(body.error || 'The server said no (' + res.status + ').');
    return body;
  }

  function show(id, on) { $(id).classList.toggle('hidden', !on); }

  function signOut(message) {
    token = '';
    try { sessionStorage.removeItem('atlas-review-token'); } catch (e) {}
    show('queue', false); show('signOutBtn', false); show('loginForm', true);
    $('loginError').textContent = message || '';
    show('loginError', !!message);
  }

  async function load() {
    $('status').textContent = 'Loading…';
    $('list').innerHTML = '';
    try {
      if (view === 'pending') {
        const { submissions } = await api('/admin/pending');
        $('status').textContent = submissions.length ? `${submissions.length} waiting, oldest first.` : 'Nothing is waiting.';
        $('list').innerHTML = submissions.map(pendingHtml).join('');
      } else {
        const { notes } = await api('/admin/approved');
        $('status').textContent = notes.length ? `${notes.length} on the atlas, newest first.` : 'Nothing has been approved yet.';
        $('list').innerHTML = notes.map(approvedHtml).join('');
      }
    } catch (err) {
      $('status').textContent = err.message;
    }
  }

  const when = (iso) => iso ? new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : '';

  function pendingHtml(s) {
    return `<article class="item" data-id="${esc(s.id)}">
      <div class="meta"><span class="kind kind-${esc(s.kind)}">${esc(KIND[s.kind] || s.kind)}</span><span>Received ${esc(when(s.receivedAt))}</span></div>
      <label for="text-${esc(s.id)}">Text</label>
      <textarea id="text-${esc(s.id)}" data-field="text">${esc(s.text)}</textarea>
      <label for="space-${esc(s.id)}">Space it belongs to (exact name on the atlas, or empty)</label>
      <input id="space-${esc(s.id)}" data-field="spaceName" value="${esc(s.spaceName)}">
      <label for="src-${esc(s.id)}">Source link (optional)</label>
      <input id="src-${esc(s.id)}" data-field="sourceUrl" type="url" value="${esc(s.sourceUrl)}" placeholder="https://">
      <div class="actions">
        <button type="button" class="btn approve" data-act="approve">Approve and publish</button>
        <button type="button" class="btn reject" data-act="reject">Reject and delete</button>
      </div>
    </article>`;
  }

  function approvedHtml(n) {
    return `<article class="item" data-id="${esc(n.id)}">
      <div class="meta"><span class="kind kind-${esc(n.kind)}">${esc(KIND[n.kind] || n.kind)}</span><span>${n.spaceName ? esc(n.spaceName) : 'No space'}</span><span>Approved ${esc(when(n.approvedAt))}</span></div>
      <p class="t-lead no-indent">${esc(n.text)}</p>
      ${n.sourceUrl ? `<p class="no-indent meta"><a href="${esc(n.sourceUrl)}" target="_blank" rel="noopener noreferrer">${esc(n.sourceUrl)}</a></p>` : ''}
      <div class="actions"><button type="button" class="btn" data-act="unpublish">Take down</button></div>
    </article>`;
  }

  $('list').addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-act]');
    if (!btn) return;
    const item = btn.closest('.item');
    const id = item.dataset.id;
    const act = btn.dataset.act;
    if (act === 'reject' && !confirm('Delete this note for good?')) return;
    if (act === 'unpublish' && !confirm('Take this note off the atlas? It is deleted, not sent back to the queue.')) return;
    const body = {};
    item.querySelectorAll('[data-field]').forEach(f => { body[f.dataset.field] = f.value; });
    item.querySelectorAll('button').forEach(b => { b.disabled = true; });
    try {
      await api(`/admin/submissions/${encodeURIComponent(id)}/${act}`, { method: 'POST', body: JSON.stringify(body) });
      item.remove();
      const left = $('list').children.length;
      $('status').textContent = (act === 'approve' ? 'Approved. It shows on the atlas within a minute. ' : act === 'reject' ? 'Deleted. ' : 'Taken down. ')
        + (view === 'pending' ? (left ? `${left} still waiting.` : 'Nothing else is waiting.') : '');
    } catch (err) {
      $('status').textContent = err.message;
      item.querySelectorAll('button').forEach(b => { b.disabled = false; });
    }
  });

  function setView(v) {
    view = v;
    $('tabPending').setAttribute('aria-selected', String(v === 'pending'));
    $('tabApproved').setAttribute('aria-selected', String(v === 'approved'));
    load();
  }
  $('tabPending').addEventListener('click', () => setView('pending'));
  $('tabApproved').addEventListener('click', () => setView('approved'));
  $('refreshBtn').addEventListener('click', load);
  $('signOutBtn').addEventListener('click', () => signOut(''));

  $('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    token = $('tokenInput').value.trim();
    if (!token) return;
    try { sessionStorage.setItem('atlas-review-token', token); } catch (err) {}
    start();
  });

  function start() {
    show('loginForm', false); show('loginError', false);
    show('queue', true); show('signOutBtn', true);
    setView('pending');
  }

  if (!API) show('noBackend', true);
  else if (token) start();
  else show('loginForm', true);
})();
