# Architecture

## Modules

- `api`: FastAPI routes, dependencies, and middleware.
- `core`: settings, device selection, security, and shared schemas.
- `db`: async SQLAlchemy engine, models, repositories, and pgvector helpers.
- `ai`: embeddings, retrieval helpers, and optional reranking.
- `workers`: Redis + RQ tasks and worker entrypoint.
- `telemetry`: Prometheus metrics and optional OpenTelemetry hooks.
- `cpp`: optional pybind11 extension for hot paths.

## Data Flow

1. `POST /v1/items` accepts content and optional metadata.
2. The embeddings layer generates vectors on the best device.
3. pgvector stores embeddings and powers ANN search.
4. `POST /v1/search` retrieves the top-k nearest neighbors and optional hybrid filters.

## Extension Points

- C++: build the pybind11 module with `make build-cpp` to speed up hot paths.
- CUDA: add Torch C++ extensions in `src/ai_accel_api_platform/ai/retrieval.py` when needed.
- gRPC: enable with `ENABLE_GRPC=true` and implement server wiring.

## CUDA Extensions (Future)

Torch custom C++/CUDA extensions can be added alongside `ai/retrieval.py`. A typical flow is to create a new extension module, register it with `torch.utils.cpp_extension`, and route hot paths through it while keeping the Python fallback available.
