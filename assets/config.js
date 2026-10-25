// The report API for whistleblower reviews (server/, hosted on Fly.io; see "Hosting the report API on Fly.io" in the README).
// Reviews are read from it and written to it only through the review form on a place's record. Empty means the record
// shows no reviews and no form.
window.ATLAS_REPORT_API_URL = 'https://culture-atlas-reports.fly.dev';

// The address of the chat endpoint (the Worker in worker/, path /chat). With it set, visitors get live Claude answers without
// entering a key; the Anthropic key stays in the Worker as the secret ANTHROPIC_API_KEY. Empty means the chat answers from
// the records, or from a visitor's own key if they add one in settings.
window.ATLAS_AI_PROXY_URL = '';
