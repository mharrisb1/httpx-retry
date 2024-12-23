from abc import ABC, abstractmethod
from typing import Coroutine

from httpx import Request, Response


class RetryStrategy(ABC):
    @abstractmethod
    def exhaust(self, req: Request) -> Response: ...


class AsyncRetryStrategy(ABC):
    @abstractmethod
    def exhaust(self, req: Request) -> Coroutine[None, None, Response]: ...
