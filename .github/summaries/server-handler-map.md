# Copilot Summary: Server Handler Map

Use this summary before loading `app/server/` handler files when the task only needs route ownership or API surface orientation.

## Source of Truth

- `app/server/_base.py` (routing dispatch)
- `app/server/<handler>.py` (per-feature logic)

## Entry Point

- `server.py` → `app/server/` (thin entry point; do not add logic here)
- `app/server/_base.py` owns the `HTTPServer` instance, `do_GET`, `do_POST`, `do_DELETE`, routing dispatch, and shared helpers.

## Route → Handler File Map

| Route(s) | Method(s) | Handler file |
|----------|-----------|--------------|
| `/api/config` | GET, POST | `config_handlers.py` |
| `/api/test-connection` | POST | `connection_handlers.py` |
| `/api/cert-status` | GET | `cert_handlers.py` |
| `/api/fetch-cert` | POST | `cert_handlers.py` |
| `/api/schemas` | GET, POST, DELETE | `schema_handlers.py` |
| `/api/filters`, `/api/filters/<slug>` | GET, POST, DELETE | `filter_handlers.py` |
| `/api/generate` | GET (SSE stream) | `generate_handlers.py` |
| `/api/reports` | GET, DELETE | `generate_handlers.py` |
| `/api/data-preview` | GET | `data_handlers.py` |
| `/api/dau/config` | GET | `dau_handlers.py` |
| `/api/dau/records` | GET, POST, DELETE | `dau_handlers.py` |
| `/api/dau/roster` | GET, POST, DELETE | `dau_handlers.py` |
| `/api/dau/import` | POST | `dau_handlers.py` |
| `/api/version` | GET | `_base.py` (inline) |
| All static assets / `ui/index.html` | GET | `_base.py` (inline) |

## Handler Mixin Pattern

Each `*_handlers.py` is a mixin class. `_base.py` composes them all into the final handler. Logic belongs in the owning handler file, never in `_base.py` routing dispatch.

## Shared Conventions

- Read request body with `self._read_body()`.
- Write JSON responses with `self._send_json(data)`.
- All handlers proxy Jira API through the server to avoid CORS.

## Escalate to Source When

- you need exact request/response shapes for a specific route
- you are adding a new route (must update `_base.py` dispatch and create or extend a handler file)
- you need to understand authentication or SSL passthrough logic
