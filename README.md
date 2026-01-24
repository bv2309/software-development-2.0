# AI Accel API Platform

An AI-accelerated Python backend that auto-selects CUDA/MPS/CPU, uses pgvector for ANN search, and serves a FastAPI REST API (with optional gRPC).

## Quickstart

```bash
uv sync
cp .env.example .env
make up
make worker
PYTHONPATH=src uv run uvicorn ai_accel_api_platform.main:app --reload --host 0.0.0.0 --port 8000
```

Default credentials are set via `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` in `.env`.

## Local Services

- API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs
- Prometheus metrics: http://localhost:8000/metrics

## Key Endpoints

- `GET /v1/health`
- `POST /v1/items`
- `GET /v1/items/{id}`
- `POST /v1/embeddings`
- `POST /v1/search`
- `POST /v1/auth/token`

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
2. Install gRPC tools: `uv pip install \"grpcio grpcio-tools\"`.
3. Generate stubs: `bash scripts/generate_grpc.sh`.
4. Start the API; the gRPC server runs in the background.

## Configuration

See `.env.example` for all supported environment variables.

## Testing

```bash
make test
```

Integration tests require a running Postgres with pgvector and `DATABASE_URL` set.

## Docs

- `docs/architecture.md`
- `migrations/README.md`
