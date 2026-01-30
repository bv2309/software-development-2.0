# AI Accel API Platform

An AI-accelerated Python backend that auto-selects CUDA/MPS/CPU, uses pgvector for ANN search, and serves a FastAPI REST API (with optional gRPC). It includes Redis-backed tasks, Prometheus metrics, and optional OpenTelemetry tracing.

## Features

- FastAPI REST API with JWT auth
- Postgres + pgvector vector search
- Redis + RQ background jobs
- CPU/GPU auto-selection (CUDA/MPS/CPU)
- Optional gRPC server
- Prometheus metrics + optional OpenTelemetry
- Optional C++ (pybind11) acceleration
- pgAdmin for database browsing

## Requirements

- Python 3.12 (for local dev)
- Docker + Docker Compose (recommended)

## Quickstart (Docker)

```bash
cp .env.example .env
make up
```

Apply migrations (first run):

```bash
docker compose exec api alembic upgrade head
```

## Local (non-Docker) run

```bash
uv sync
cp .env.example .env
PYTHONPATH=src uv run uvicorn ai_accel_api_platform.main:app --reload --host 0.0.0.0 --port 8000
```

## Local Services

- API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs
- Prometheus metrics: http://localhost:8000/metrics
- pgAdmin: http://localhost:5050

## Key Endpoints

- `GET /v1/health`
- `POST /v1/items`
- `GET /v1/items/{id}`
- `POST /v1/embeddings`
- `POST /v1/search`
- `GET /v1/user`
- `POST /v1/auth/token`

## Authentication

Default admin credentials are configured in `.env`:

- `DEFAULT_ADMIN_USERNAME` (default: `admin@localdomain.com`)
- `DEFAULT_ADMIN_PASSWORD` (default: `admin`)
- `DEFAULT_ADMIN_FIRST_NAME` (default: `Branimir`)
- `DEFAULT_ADMIN_LAST_NAME` (default: `Viljevac`)

Obtain a token via:

```bash
curl -X POST http://localhost:8000/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@localdomain.com&password=admin"
```

## Data Model Notes

- `users` table includes `first_name`, `last_name`, and `user_type`.
- `user_type`: `0` = admin, `1` = regular user.
- The `/v1/user` endpoint returns `full_name` derived from `first_name` + `last_name`.

## pgAdmin

Login using the same admin credentials:

- URL: http://localhost:5050
- Email: `admin@localdomain.com`
- Password: `admin`

Connect to Postgres using:

- Host: `postgres`
- Port: `5432`
- Database: `app`
- Username: `user`
- Password: `pass`

## Configuration

See `.env.example` for all supported environment variables.

## Command Cheat Sheet

### Run / build (Docker)

Build + run all services (now gated by CI preflight):
```bash
make up
```

Build + run without the Makefile wrapper:
```bash
docker compose up -d --build
```

Start only (no rebuild):
```bash
docker compose up -d
```

Stop services (keep volumes):
```bash
docker compose down
```

Stop + remove volumes (wipe DB/pgAdmin data):
```bash
docker compose down -v
```

### Restart

Restart everything:
```bash
docker compose restart
```

Restart a single service:
```bash
docker compose restart api
docker compose restart worker
docker compose restart postgres
docker compose restart pgadmin
```

### Logs

Tail all logs:
```bash
docker compose logs -f
```

Tail one service:
```bash
docker compose logs -f api
```

### Database

Apply migrations:
```bash
docker compose exec api alembic upgrade head
```

Open psql:
```bash
docker compose exec postgres psql -U user -d app
```

### CI preflight (local)

Run the same steps as CI:
```bash
make ci
```

or:
```bash
bash scripts/ci_local.sh
```

### Tests / lint / format / typecheck

Tests:
```bash
make test
# or
pytest
```

Lint:
```bash
make lint
# or
ruff check src tests
```

Format:
```bash
make fmt
# or
ruff format src tests
```

Typecheck:
```bash
make typecheck
# or
mypy src
```

## Device Selection

`core.device.get_best_device()` picks CUDA, then MPS, then CPU. Device details are included in `/v1/health`.

## Embeddings + pgvector

Embeddings are generated with SentenceTransformers and stored in Postgres using pgvector. Vector search uses the `<=>` operator.
Ensure `EMBEDDING_DIM` matches the model dimension and the pgvector column (default: 384).

## C++ Acceleration

A small pybind11 extension provides a fast batch cosine similarity implementation. Build it with:

```bash
make build-cpp
```

If the extension is not built, the Python fallback is used.
Requires a C++ toolchain plus `cmake` and `pybind11` (`uv pip install .[cpp]`).
Pass extra build flags with `CMAKE_ARGS`, for example: `make build-cpp CMAKE_ARGS="-DCMAKE_CXX_FLAGS=-O3"`.

## gRPC (optional)

1. Set `ENABLE_GRPC=true` and `GRPC_PORT` in `.env`.
2. Install gRPC tools: `uv pip install "grpcio grpcio-tools"`.
3. Generate stubs: `bash scripts/generate_grpc.sh`.
4. Start the API; the gRPC server runs in the background.

## Testing

```bash
make test
```

Integration tests require a running Postgres with pgvector and `DATABASE_URL` set.

## Docs

- `docs/architecture.md`
- `migrations/README.md`
