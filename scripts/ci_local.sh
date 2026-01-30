#!/usr/bin/env bash
set -euo pipefail

printf "==> CI preflight (local)\n"

run_ci_steps() {
  if [[ "${ENABLE_GRPC:-}" == "true" ]]; then
    printf "==> Generating gRPC stubs\n"
    bash scripts/generate_grpc.sh
  fi

  printf "==> Ruff lint\n"
  ruff check src tests

  printf "==> Ruff format check\n"
  ruff format --check src tests

  printf "==> Mypy\n"
  mypy src

  printf "==> Pytest\n"
  pytest
}

if command -v python3.12 >/dev/null 2>&1; then
  run_ci_steps
  printf "==> CI preflight passed\n"
  exit 0
fi

printf "==> python3.12 not found; running CI steps in Docker\n"

docker_env_args=""
if [[ -n "${ENABLE_GRPC:-}" ]]; then
  docker_env_args+=" -e ENABLE_GRPC=${ENABLE_GRPC}"
fi
if [[ -n "${DATABASE_URL:-}" ]]; then
  docker_env_args+=" -e DATABASE_URL=${DATABASE_URL}"
fi

docker run --rm \
  ${docker_env_args} \
  -v "$(pwd)":/app \
  -w /app \
  python:3.12-slim \
  bash -lc "pip install --no-cache-dir uv && uv pip install --system '.[dev]' && bash scripts/ci_local_inner.sh"
