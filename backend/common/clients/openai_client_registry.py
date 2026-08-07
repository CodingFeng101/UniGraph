from __future__ import annotations

import asyncio
import hashlib
from collections import OrderedDict

import httpx
from openai import AsyncOpenAI

from backend.core.conf import settings


class OpenAIClientRegistry:
    """Process-local LRU registry for reusable OpenAI-compatible clients."""

    def __init__(self, max_clients: int | None = None) -> None:
        self.max_clients = max_clients or settings.LLM_HTTP_MAX_CLIENTS
        self._clients: OrderedDict[tuple[str, str], AsyncOpenAI] = OrderedDict()
        self._lock = asyncio.Lock()

    @staticmethod
    def _key(api_key: str, base_url: str) -> tuple[str, str]:
        normalized_url = (base_url or '').rstrip('/')
        key_hash = hashlib.sha256((api_key or '').encode('utf-8')).hexdigest()
        return normalized_url, key_hash

    @staticmethod
    def _create_client(api_key: str, base_url: str) -> AsyncOpenAI:
        http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=settings.LLM_HTTP_MAX_CONNECTIONS,
                max_keepalive_connections=settings.LLM_HTTP_MAX_KEEPALIVE_CONNECTIONS,
            ),
            timeout=httpx.Timeout(
                connect=settings.LLM_HTTP_CONNECT_TIMEOUT,
                read=settings.LLM_HTTP_READ_TIMEOUT,
                write=settings.LLM_HTTP_READ_TIMEOUT,
                pool=settings.LLM_HTTP_CONNECT_TIMEOUT,
            ),
        )
        return AsyncOpenAI(api_key=api_key, base_url=base_url, http_client=http_client)

    async def get(self, *, api_key: str, base_url: str) -> AsyncOpenAI:
        key = self._key(api_key, base_url)
        evicted: AsyncOpenAI | None = None
        async with self._lock:
            client = self._clients.pop(key, None)
            if client is None:
                client = self._create_client(api_key, base_url)
            self._clients[key] = client
            if len(self._clients) > self.max_clients:
                _, evicted = self._clients.popitem(last=False)
        if evicted is not None:
            await evicted.close()
        return client

    async def close_all(self) -> None:
        async with self._lock:
            clients = list(self._clients.values())
            self._clients.clear()
        await asyncio.gather(*(client.close() for client in clients), return_exceptions=True)

    @property
    def size(self) -> int:
        return len(self._clients)


openai_client_registry = OpenAIClientRegistry()
