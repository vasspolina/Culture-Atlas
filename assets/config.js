// Where Share information sends notes: the address of the submissions Worker (see worker/ and the README).
// Empty means information and gossip stay in the browser; whistleblower reports are not saved until the API is configured.
window.ATLAS_SUBMIT_URL = '';

// Optional Express + Prisma endpoint for whistleblower reports.
window.ATLAS_REPORT_API_URL = '';

// The address of the chat endpoint (the same Worker, path /chat). With it set, visitors get live Claude answers without
// entering a key; the Anthropic key stays in the Worker as the secret ANTHROPIC_API_KEY. Empty means the chat answers from
// the records, or from a visitor's own key if they add one in settings.
window.ATLAS_AI_PROXY_URL = '';
