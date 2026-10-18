import { useCallback, useEffect, useState } from 'react';

const API = (window.ATLAS_REPORT_API_URL || '').replace(/\/+$/, '');

export function AdminModerator() {
  const [token, setToken] = useState(() => {
    try { return sessionStorage.getItem('atlas-report-admin-token') || ''; } catch { return ''; }
  });
  const [reports, setReports] = useState([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');
  const [loading, setLoading] = useState(false);

  const loadPending = useCallback(async () => {
    if (!API || !token) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(API + '/api/admin/reports/pending', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || `Request failed (${response.status}).`);
      setReports(body);
      try { sessionStorage.setItem('atlas-report-admin-token', token); } catch {}
    } catch (err) {
      setError(err.message || 'Could not load reports.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadPending(); }, [loadPending]);

  async function handleDecision(id, status) {
    setBusy(id);
    setError('');
    try {
      const response = await fetch(`${API}/api/admin/reports/${encodeURIComponent(id)}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || `Request failed (${response.status}).`);
      setReports(current => current.filter(report => report.id !== id));
    } catch (err) {
      setError(err.message || 'Could not update this report.');
    } finally {
      setBusy('');
    }
  }

  return (
    <main className="report-moderator">
      <h1>Pending whistleblower reports</h1>
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
      <button type="button" onClick={loadPending} disabled={!API || !token || loading}>
        {loading ? 'Loading…' : 'Refresh queue'}
      </button>
      {error && <p role="alert">{error}</p>}
      {!loading && reports.length === 0 && <p>No submissions are waiting for review.</p>}
      <ul>
        {reports.map(report => (
          <li key={report.id}>
            <p>
              <strong>{report.city}</strong>
              {report.institution ? ` | ${report.institution}` : ''}
              {' · '}{new Date(report.createdAt).toLocaleString()}
            </p>
            <p>{report.content}</p>
            <button
              type="button"
              disabled={busy === report.id}
              onClick={() => handleDecision(report.id, 'APPROVED')}
            >
              Approve &amp; Post to Map
            </button>
            <button
              type="button"
              disabled={busy === report.id}
              onClick={() => handleDecision(report.id, 'REJECTED')}
            >
              Reject
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
