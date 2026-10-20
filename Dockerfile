# The whistleblower report API (server/ + prisma/), for Fly.io or any container host. See "Hosting the report API" in the README.
FROM node:22-slim
RUN apt-get update -y && apt-get install -y --no-install-recommends openssl ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json ./
COPY prisma ./prisma
RUN npm install --no-audit --no-fund && npx prisma generate
COPY server ./server
COPY institutions.json ./
ENV NODE_ENV=production PORT=4000
EXPOSE 4000
# Creates the table on first start and leaves existing notes alone; then starts the API.
CMD ["sh", "-c", "npx prisma db push --skip-generate && node server/index.js"]
