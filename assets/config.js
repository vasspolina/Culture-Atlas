// Where Share information sends notes: the address of the submissions Worker (see worker/ and the README).
// Empty means information and gossip stay in the browser; whistleblower reports are not saved until the API is configured.
window.ATLAS_SUBMIT_URL = '';

// The report API for whistleblower notes (server/, hosted on Fly.io; see "Hosting the report API on Fly.io" in the README).
window.ATLAS_REPORT_API_URL = 'https://culture-atlas-reports.fly.dev';

// The address of the chat endpoint (the same Worker, path /chat). With it set, visitors get live Claude answers without
// entering a key; the Anthropic key stays in the Worker as the secret ANTHROPIC_API_KEY. Empty means the chat answers from
// the records, or from a visitor's own key if they add one in settings.
window.ATLAS_AI_PROXY_URL = 'https://culture-atlas-submissions.vasilievapolli.workers.dev/chat';
