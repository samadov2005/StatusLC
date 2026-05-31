**Render Deployment Guide**

- **Purpose:** Steps to provision Render services (Managed Postgres + Web Service) and connect GitHub for auto-deploy.

Prerequisites
- A Render account (https://render.com). GitHub connected to Render for repo access.
- Repository pushed to GitHub (already done).
- A secure `DJANGO_SECRET_KEY` value and production `TELEGRAM_BOT_TOKEN`.

Quick steps (manual)

1. Create Managed Postgres on Render
- In Render dashboard: New -> PostgreSQL
- Choose plan (Free for testing), set DB name `statuslc`, user `statuslc`, and a strong password.
- When ready, copy the `DATABASE_URL` value (postgres://user:pass@host:5432/dbname).

2. Create a Web Service for the backend
- In Render dashboard: New -> Web Service
- Connect your GitHub repo `samadov2005/StatusLC` and select branch `main`.
- Environment: Docker
- Dockerfile Path: `/Dockerfile`
- Add environment variables (Render dashboard -> Environment):
  - `DATABASE_URL` = the value from Managed Postgres
  - `DJANGO_SECRET_KEY` = (your secret)
  - `TELEGRAM_BOT_TOKEN` = (your token)
  - `DEBUG` = `False`
  - `ALLOWED_HOSTS` = your domain(s) or `*` for testing

3. (Optional) Create a second Web Service for the frontend
- Build using `frontend/Dockerfile.prod` or serve static via a CDN. If creating a service, set Dockerfile Path to `/frontend/Dockerfile.prod`.
- Set environment variables as needed and configure a health check path `/`.

4. Deploy & Verify
- Trigger a deploy from Render or push to GitHub `main` to auto-deploy.
- Confirm the backend is reachable; check logs for migrations and collectstatic (entrypoint runs them).
- On success, update DNS for custom domain (Render provides HTTPS automatically).

Automation via `render.yaml`
- This repo contains a sample `render.yaml`. Edit values (secrets, repo) and upload it in Render dashboard under "Create from render.yaml" or use it when creating services programmatically.

Setting GitHub secrets (for GitHub Actions)
- In your GitHub repo: Settings -> Secrets -> Actions, add:
  - `RENDER_API_KEY` (if you want CI to trigger Render deploy)
  - `RENDER_SERVICE_ID` (optional, from Render service settings)
  - `DJANGO_SECRET_KEY` (or set in Render directly)
  - `DATABASE_URL` (if you prefer setting DB via GitHub rather than Render UI)

Local notes / troubleshooting
- If `docker-compose up` fails with bind/permission errors, ensure host ports are free. This repo now maps:
  - Postgres host port -> `5433:5432` (use `PGPORT=5433` to connect locally)
  - Frontend host port -> `8080:80`
  - Backend host port -> `8001:8000`

Commands to run locally

```bash
# build and run locally
docker-compose up --build
# access frontend at http://localhost:8080
# access backend at http://localhost:8001
```

If you want, I can provision Render automatically — you'll need to provide a Render API key with permission to create services. If you'd rather do it yourself, follow the steps above and tell me when to continue with GitHub secrets or verification.
