#!/usr/bin/env bash
set -euo pipefail

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

printf "==> CI preflight passed\n"
