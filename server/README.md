# server/

The whistleblower report API: an Express app over SQLite through Prisma. Sites send a review to it,
it holds the review as waiting (or a suggested new place, `POST /api/new-places`), and a note shows on the atlas only after the editor approves it on
`reports-admin.html`. Endpoints, limits and hosting (Fly.io) are in [docs/api.md](../docs/api.md).

| File | Role |
|---|---|
| `index.js` | Starts the server: reads the environment, opens Prisma, listens on `PORT`. |
| `app.js` | `createApp(...)`: the routes and middleware. Built without a port so tests run it in-process. |
| `validate.js` | Checks a submission and loads the atlas records it may refer to (`institutions.json`). |
| `files.js` | Attached photos, screenshots and PDFs: type read from the file's own bytes, size limits, metadata stripped from photos. |
| `test/api.test.mjs` | API tests against a throwaway SQLite file. |

Run: `npm install`, set the variables in `.env.example` (`ADMIN_SECRET_KEY`, `ALLOWED_ORIGINS`,
`DATABASE_URL`), `npm run db:push`, then `npm run dev`. Tests: `npm test` from the repository root.
The database file is git-ignored; the schema is `prisma/schema.prisma`.
