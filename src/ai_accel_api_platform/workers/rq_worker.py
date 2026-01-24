from __future__ import annotations

from redis import Redis
from rq import Worker

from ai_accel_api_platform.settings import get_settings


def main() -> None:
    settings = get_settings()
    redis_conn = Redis.from_url(settings.redis_url)
    worker = Worker(["default"], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
