.PHONY: fmt lint typecheck test ci up down worker build-cpp

CMAKE_ARGS ?=

fmt:
	ruff format src tests

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	PYTHONPATH=src pytest

ci:
	bash scripts/ci_local.sh

up:
	bash scripts/ci_local.sh
	docker compose up -d --build

down:
	docker compose down

worker:
	PYTHONPATH=src uv run python -m ai_accel_api_platform.workers.rq_worker

build-cpp:
	cmake -S src/ai_accel_api_platform/cpp -B build/cpp -DCMAKE_BUILD_TYPE=Release $(CMAKE_ARGS)
	cmake --build build/cpp --config Release
