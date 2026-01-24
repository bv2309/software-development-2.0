from __future__ import annotations

import asyncio
import threading

import structlog

from ai_accel_api_platform.settings import get_settings

logger = structlog.get_logger(__name__)


def _load_grpc_modules():
    try:
        import grpc  # type: ignore
        from ai_accel_api_platform.grpc import search_pb2, search_pb2_grpc
    except Exception as exc:
        logger.warning("grpc_disabled", reason="grpc_not_installed_or_stubs_missing", error=str(exc))
        return None
    return grpc, search_pb2, search_pb2_grpc


def start_grpc_server() -> None:
    modules = _load_grpc_modules()
    if modules is None:
        return

    grpc, search_pb2, search_pb2_grpc = modules
    settings = get_settings()

    class SearchService(search_pb2_grpc.SearchServiceServicer):
        async def Search(self, request, context):
            return search_pb2.SearchResponse(results=[])

        async def Upsert(self, request, context):
            return search_pb2.UpsertResponse(id=request.id)

    async def serve() -> None:
        server = grpc.aio.server()
        search_pb2_grpc.add_SearchServiceServicer_to_server(SearchService(), server)
        server.add_insecure_port(f"[::]:{settings.grpc_port}")
        await server.start()
        logger.info("grpc_server_started", port=settings.grpc_port)
        await server.wait_for_termination()

    thread = threading.Thread(target=lambda: asyncio.run(serve()), daemon=True)
    thread.start()
