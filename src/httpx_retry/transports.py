from typing import Optional

from httpx import (
    AsyncBaseTransport,
    AsyncHTTPTransport,
    BaseTransport,
    HTTPTransport,
    Request,
    Response,
)

from .executor import AsyncRetryExecutor, RetryExecutor
from .policies.base import BaseRetryPolicy

__all__ = ["RetryTransport", "AsyncRetryTransport"]


class RetryTransport(BaseTransport):
    def __init__(
        self,
        transport: Optional[BaseTransport] = None,
        policy: Optional[BaseRetryPolicy] = None,
    ) -> None:
        self.transport = transport or HTTPTransport()
        self.executor = RetryExecutor(policy)

    def handle_request(self, request: Request) -> Response:
        return self.executor.execute(lambda: self.transport.handle_request(request))


class AsyncRetryTransport(AsyncBaseTransport):
    def __init__(
        self,
        transport: Optional[AsyncBaseTransport] = None,
        policy: Optional[BaseRetryPolicy] = None,
    ) -> None:
        self.transport = transport or AsyncHTTPTransport()
        self.executor = AsyncRetryExecutor(policy)

    async def handle_async_request(self, request: Request) -> Response:
        return await self.executor.execute(
            lambda: self.transport.handle_async_request(request)
        )
