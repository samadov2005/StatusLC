# StatusLC Docker

Local Docker stack:

```bash
docker compose up --build
```

Services:


Before production deploy, replace these values in `docker-compose.yml` or environment variables:


Environment variables
---------------------

Copy `.env.example` to `.env` and fill in secrets before running `docker-compose`:

```bash
cp .env.example .env
# edit .env to set DJANGO_SECRET_KEY and POSTGRES_PASSWORD
```

`docker-compose.yml` is configured to read variables from `.env` (via `env_file`). Do not commit `.env` to git.

CI / Deploy with Render
-----------------------

This repo includes a GitHub Actions workflow that triggers a Render deploy whenever you push to `main`:

- File: `.github/workflows/render-deploy.yml`
- Required repository secrets (set in GitHub Settings → Secrets):
  - `RENDER_API_KEY` — your Render API key (service account / API key)
  - `RENDER_SERVICE_ID` — the Render service ID for your web service

To set up automatic deploys on Render:
1. Create a Render account and connect your GitHub repository (or create a new Web Service and choose Docker).
2. In Render, provision a Managed Postgres (optional) and set environment variables there, or set `DATABASE_URL` and other secrets in GitHub Secrets.
3. Add `RENDER_API_KEY` and `RENDER_SERVICE_ID` to GitHub repository secrets.
4. Push to `main` — the workflow will call Render's deploy API and kick off a deploy.

If you prefer, you can also connect Render directly to your GitHub repo and use Render's automatic deploys without the workflow.
API token login for API clients:

```bash
curl -X POST http://127.0.0.1:8001/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"your-password\"}"
```

Use the returned token as:

```text
Authorization: Token <token>
```
