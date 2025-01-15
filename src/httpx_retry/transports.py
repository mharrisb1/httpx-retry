from typing import Any

from httpx import AsyncHTTPTransport, HTTPTransport, Request, Response

from .executor import AsyncRetryExecutor, RetryExecutor
from .policies.base import BaseRetryPolicy

__all__ = ["HTTPRetryTransport", "AsyncHTTPRetryTransport"]


class HTTPRetryTransport(HTTPTransport):
    def __init__(self, policy: BaseRetryPolicy, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.executor = RetryExecutor(policy)

    def handle_request(self, request: Request) -> Response:
        return self.executor.execute(
            lambda: super(HTTPRetryTransport, self).handle_request(request)
        )


class AsyncHTTPRetryTransport(AsyncHTTPTransport):
    def __init__(self, policy: BaseRetryPolicy, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.executor = AsyncRetryExecutor(policy)

    async def handle_async_request(self, request: Request) -> Response:
        return await self.executor.execute(
            lambda: super(AsyncHTTPRetryTransport, self).handle_async_request(request)
        )
