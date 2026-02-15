# Money Manager

Personal finance manager with:
- Django web UI (legacy/transition)
- Versioned REST API (`/api/v1/*`)
- Financial chatbot module (RAG-ready integrations)

## Stack

- Python + Django
- Django REST Framework + SimpleJWT + drf-spectacular
- SQLite (dev) / PostgreSQL (recommended prod)
- Optional: Qdrant + Groq + HuggingFace for chatbot enrichment

## Project Structure

```text
config/                # URL routing + environment settings package
finanzas/              # Core financial domain (models/forms/views)
chatbot/               # Chat model + pipeline + providers
api/v1/                # Versioned API controllers/serializers
frontend/              # Django templates + static assets
frontend-web/          # Next.js scaffold for decoupled frontend migration
docs/                  # API and architecture documentation
```

## Local Setup

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Copy `.env.example` to `.env` and fill required values.

## Environment Settings

- `APP_ENV=development|production|test`
- Settings package:
  - `config.settings.dev`
  - `config.settings.prod`
  - `config.settings.test`

## API

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- API reference: `docs/API.md`

## Health Endpoints

- `GET /health/live/`
- `GET /health/ready/`

## Quality & CI

- Tooling config: `pyproject.toml`
- Pre-commit hooks: `.pre-commit-config.yaml`
- CI workflow: `.github/workflows/ci.yml`
- Baseline tests: `python manage.py test finanzas`

## Docker

```bash
docker compose up --build
```

Services:
- `web`: Django app
- `db`: PostgreSQL
- `redis`: Redis
