import { useCallback, useEffect, useState } from 'react';

const API = (window.ATLAS_REPORT_API_URL || '').replace(/\/+$/, '');
const fileSize = n => n >= 1048576 ? `${(n / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;

// One attached file, fetched with the token (a pending file is not public) and shown from memory.
function AttachedFile({ file, token, onRemove, disabled }) {
  const [url, setUrl] = useState('');
  useEffect(() => {
    let made = '';
    fetch(`${API}/api/admin/files/${encodeURIComponent(file.id)}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(response => (response.ok ? response.blob() : Promise.reject()))
      .then(blob => { made = URL.createObjectURL(blob); setUrl(made); })
      .catch(() => {});
    return () => { if (made) URL.revokeObjectURL(made); };
  }, [file.id, token]);
  const image = file.type.startsWith('image/');
  return (
    <figure>
      <a href={url || undefined} target="_blank" rel="noopener">
        {image ? <img src={url || undefined} alt="Attached photo" width="180" height="180" style={{ objectFit: 'cover' }} /> : 'PDF'}
      </a>
      <figcaption>
        {image ? 'Photo' : 'PDF'}, {fileSize(file.size)}{' '}
        <button type="button" disabled={disabled} onClick={onRemove}>Remove file</button>
      </figcaption>
    </figure>
  );
}

const VIEWS = [
  ['PENDING', 'Waiting'],
  ['APPROVED', 'On the atlas'],
  ['REJECTED', 'Rejected']
];

export function AdminModerator() {
  const [token, setToken] = useState(() => {
    try { return sessionStorage.getItem('atlas-report-admin-token') || ''; } catch { return ''; }
  });
  const [view, setView] = useState('PENDING');
  const [reports, setReports] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');
  const [loading, setLoading] = useState(false);

  const request = useCallback(async (path, options = {}) => {
    const response = await fetch(API + path, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        Authorization: `Bearer ${token}`
      }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `Request failed (${response.status}).`);
    return body;
  }, [token]);

  const load = useCallback(async () => {
    if (!API || !token) return;
    setLoading(true);
    setError('');
    try {
      setReports(await request(`/api/admin/reports?status=${view}`));
      try { sessionStorage.setItem('atlas-report-admin-token', token); } catch {}
    } catch (err) {
      setError(err.message || 'Could not load notes.');
    } finally {
      setLoading(false);
    }
  }, [request, token, view]);

  useEffect(() => { load(); }, [load]);

  async function act(id, run) {
    setBusy(id);
    setError('');
    try {
      await run();
      setReports(current => current.filter(report => report.id !== id));
    } catch (err) {
      setError(err.message || 'Could not update this note.');
    } finally {
      setBusy('');
    }
  }

  const setStatus = (id, status) => act(id, () => request(`/api/admin/reports/${encodeURIComponent(id)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  }));

  async function removeFile(reportId, fileId) {
    if (!window.confirm('Remove this file for good? The note stays.')) return;
    setBusy(reportId);
    setError('');
    try {
      await request(`/api/admin/files/${encodeURIComponent(fileId)}`, { method: 'DELETE' });
      setReports(current => current.map(report => report.id === reportId
        ? { ...report, files: (report.files || []).filter(file => file.id !== fileId) }
        : report));
    } catch (err) {
      setError(err.message || 'Could not remove this file.');
    } finally {
      setBusy('');
    }
  }

  const remove = id => {
    if (!window.confirm('Delete this note for good? It cannot be brought back.')) return;
    return act(id, () => request(`/api/admin/reports/${encodeURIComponent(id)}`, { method: 'DELETE' }));
  };

  return (
    <main className="report-moderator">
      <h1>Whistleblower reviews</h1>
      {!API && <p role="alert">Set ATLAS_REPORT_API_URL in assets/config.js to connect the report API.</p>}
      <label>
        Admin bearer token
        <input
          type="password"
          autoComplete="current-password"
          value={token}
          onChange={event => setToken(event.target.value)}
        />
      </label>
      <div role="group" aria-label="Show notes">
        {VIEWS.map(([status, label]) => (
          <button key={status} type="button" aria-pressed={view === status} onClick={() => setView(status)}>
            {label}
          </button>
        ))}
      </div>
      <button type="button" onClick={load} disabled={!API || !token || loading}>
        {loading ? 'Loading…' : 'Refresh'}
      </button>
      {error && <p role="alert">{error}</p>}
      {!loading && reports.length === 0 && <p>No notes here.</p>}
      <ul>
        {reports.map(report => (
          <li key={report.id}>
            <p>
              <strong>{report.institution || report.city}</strong>
              {report.institution ? ` | ${report.city}` : ''}
              {' · '}{new Date(report.createdAt).toLocaleString()}
            </p>
            <p>{report.authorLabel ? `shown as “${report.authorLabel}”` : 'shown as Whistleblower'}</p>
            <p style={{ whiteSpace: 'pre-wrap' }}>{report.content}</p>
            {(report.files || []).map(file => (
              <AttachedFile
                key={file.id}
                file={file}
                token={token}
                disabled={busy === report.id}
                onRemove={() => removeFile(report.id, file.id)}
              />
            ))}
            {report.status !== 'APPROVED' && (
              <button type="button" disabled={busy === report.id} onClick={() => setStatus(report.id, 'APPROVED')}>
                Approve
              </button>
            )}
            {report.status === 'PENDING' && (
              <button type="button" disabled={busy === report.id} onClick={() => setStatus(report.id, 'REJECTED')}>
                Reject
              </button>
            )}
            {report.status === 'APPROVED' && (
              <button type="button" disabled={busy === report.id} onClick={() => setStatus(report.id, 'PENDING')}>
                Take off the atlas
              </button>
            )}
            <button type="button" disabled={busy === report.id} onClick={() => remove(report.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
