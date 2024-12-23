from httpx import BaseTransport, AsyncBaseTransport

from .strategies.base import RetryStrategy, AsyncRetryStrategy


class RetryTransport(BaseTransport):
    def __init__(self, strategy: RetryStrategy) -> None:
        super().__init__()
        self.strategy = strategy


class AsyncRetryTransport(AsyncBaseTransport):
    def __init__(self, strategy: AsyncRetryStrategy) -> None:
        super().__init__()
        self.strategy = strategy
