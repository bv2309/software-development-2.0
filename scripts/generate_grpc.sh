#!/usr/bin/env bash
set -euo pipefail

python -m grpc_tools.protoc \
  -I proto \
  --python_out=src/ai_accel_api_platform/grpc \
  --grpc_python_out=src/ai_accel_api_platform/grpc \
  proto/search.proto
