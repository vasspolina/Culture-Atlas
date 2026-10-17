// Where Share information sends notes: the address of the submissions Worker (see worker/ and the README).
// Empty means nothing is sent and notes stay in the reader's browser, as before.
window.ATLAS_SUBMIT_URL = '';

// The address of the chat endpoint (the same Worker, path /chat). With it set, visitors get live Claude answers without
// entering a key; the Anthropic key stays in the Worker as the secret ANTHROPIC_API_KEY. Empty means the chat answers from
// the records, or from a visitor's own key if they add one in settings.
window.ATLAS_AI_PROXY_URL = '';
