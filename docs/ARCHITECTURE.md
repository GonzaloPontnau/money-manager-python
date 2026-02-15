# Architecture - Money Manager

## Current Target State

- Backend: Django monolith with modular apps (`finanzas`, `chatbot`, `api`)
- API layer: DRF versioned under `/api/v1/*`
- Auth: JWT (SimpleJWT) + optional session auth fallback
- Relational DB: SQLite (local) / PostgreSQL (recommended for production)
- Vector/RAG integrations: Groq + Qdrant + HuggingFace (optional, graceful fallback)
- Frontend migration path: legacy Django templates + new `frontend-web` (Next.js scaffold)

## Layers

- `finanzas/`: core business models and web workflows (transactions/transfers/dashboard)
- `chatbot/`: conversation model, RAG pipeline, embedding/vector services
- `api/v1/`: API-facing serializers and controllers
- `config/settings/`: environment-specific settings (`dev`, `prod`, `test`)

## Security Hardening Applied

- Public DB diagnostic endpoint removed
- Health endpoints split into:
  - `/health/live/`
  - `/health/ready/`
- Cache headers secured:
  - authenticated responses: `private, no-store`
  - static versioned assets: long-lived immutable cache
- Production settings require `SECRET_KEY`
- Data integrity constraints:
  - `Transaccion.monto > 0`
  - `Transferencia.monto > 0`
  - `Transferencia.emisor != Transferencia.receptor`

## Transfer Consistency

- Transfer creation executes in `transaction.atomic()`
- Sender/receiver rows are locked with `select_for_update()` to reduce race conditions
- Balance validation runs inside the transaction
- Ledger entries are created for sender (expense) and receiver (income)

## Deployment Baseline

- `Dockerfile` for backend container
- `docker-compose.yml` for local stack (`web`, `db`, `redis`)
- CI baseline in `.github/workflows/ci.yml` for lint, type-check and tests

## Quality Baseline

- Formatting/lint/type config in `pyproject.toml`
- Pre-commit hooks in `.pre-commit-config.yaml`
- Initial backend regression tests in `finanzas/tests.py`
