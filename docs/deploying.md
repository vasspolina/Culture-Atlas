# Deploying

How the site reaches GitHub Pages. Back to the [README](../README.md).

## Deploying

`main` is the source of truth. Every push to `main` runs
`.github/workflows/deploy.yml`, which copies `index.html`,
`reports-admin.html`, `sw.js`, `manifest.json`, `assets/` and `fonts/` to the `gh-pages` branch that GitHub
Pages serves. Do not push to `gh-pages` by hand. If the live site looks stale,
check the **Actions** tab for a failed "Deploy to GitHub Pages" run.
