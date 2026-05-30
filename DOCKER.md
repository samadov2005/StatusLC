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
