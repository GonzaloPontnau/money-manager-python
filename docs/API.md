# API Reference - Money Manager

## Overview

- Base URL (versioned API): `/api/v1/`
- API schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Authentication: JWT Bearer tokens (`Authorization: Bearer <access_token>`)

## Auth

- `POST /api/v1/auth/login`
  - Body: `{ "username": "...", "password": "..." }`
  - Returns: `access`, `refresh`
- `POST /api/v1/auth/refresh`
  - Body: `{ "refresh": "..." }`
  - Returns: new `access` (+ rotated `refresh` if enabled)
- `POST /api/v1/auth/logout`
  - Stateless logout endpoint (204)

## Dashboard

- `GET /api/v1/dashboard/summary`
  - Returns:
    - `ingresos_totales`
    - `gastos_totales`
    - `balance`
    - `gastos_por_categoria[]`
    - `tiene_datos_demo`

## Transactions

- `GET /api/v1/transactions`
- `POST /api/v1/transactions`
- `GET /api/v1/transactions/{id}`
- `PATCH /api/v1/transactions/{id}`
- `DELETE /api/v1/transactions/{id}`

Notes:
- All transaction resources are user-scoped.
- Category must belong to the authenticated user.
- Category type must match transaction type.

## Transfers

- `GET /api/v1/transfers`
- `POST /api/v1/transfers`
  - Body:
    - `receptor_username` (string)
    - `monto` (decimal > 0)
    - `concepto` (string, optional)
- `GET /api/v1/transfers/{uuid}`
- `POST /api/v1/transfers/{uuid}/cancel`

Notes:
- Self-transfer is blocked at form, view, and DB-constraint levels.
- Transfer execution uses DB transaction and row locking for sender/receiver.

## Chat

- `GET /api/v1/chat/sessions`
- `POST /api/v1/chat/sessions`
  - Creates a new `session_id`
- `POST /api/v1/chat/messages`
  - Body: `{ "session_id": "...", "message": "..." }`
- `GET /api/v1/chat/sessions/{session_id}/messages`

## Health

- `GET /health/live/`
- `GET /health/ready/`

Readiness intentionally avoids leaking DB engine details or exception text.

## Legacy Web Endpoints

Legacy HTML routes remain active during migration:
- `/`
- `/login/`
- `/register/`
- `/logout/`
- `/transacciones/*`
- `/transferencias/*`
- `/chatbot/api/chat/*`
