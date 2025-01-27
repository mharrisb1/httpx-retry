import asyncio
import time
from typing import Any, Awaitable, Callable, Optional

from httpx import Response

from .policies import RetryPolicy
from .policies.base import BaseRetryPolicy


class RetryExecutor:
    def __init__(self, policy: Optional[BaseRetryPolicy] = None) -> None:
        self.policy = policy or RetryPolicy()

    def execute(
        self, func: Callable[..., Response], *args: Any, **kwargs: Any
    ) -> Response:
        attempt = 1
        start_time = time.monotonic()
        last_exception: Optional[Exception] = None

        while True:
            response = None
            exception = None

            try:
                response = func(*args, **kwargs)
            except Exception as e:
                exception = e
                last_exception = exception

            should_retry = self.policy.should_retry(attempt, response, exception)

            if not should_retry:
                if exception:
                    raise exception

                if response:
                    return response

            delay = self.policy.get_delay(attempt)
            time.sleep(delay)

            attempt += 1

            timeout = self.policy.get_timeout()
            if timeout is not None:
                elapsed = time.monotonic() - start_time
                if elapsed > timeout:
                    break

        if last_exception:
            raise last_exception
        raise Exception("Retry attempts exhausted without a successful response.")


class AsyncRetryExecutor:
    def __init__(self, policy: Optional[BaseRetryPolicy] = None) -> None:
        self.policy = policy or RetryPolicy()

    async def execute(
        self,
        func: Callable[..., Awaitable[Optional[Response]]],
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        attempt = 0
        start_time = time.monotonic()
        last_exception: Optional[Exception] = None

        while True:
            response = None
            exception = None

            try:
                response = await func(*args, **kwargs)
            except Exception as e:
                exception = e
                last_exception = exception

            should_retry = self.policy.should_retry(attempt, response, exception)

            if not should_retry:
                if exception:
                    raise exception

                if response:
                    return response

            delay = self.policy.get_delay(attempt)
            await asyncio.sleep(delay)

            attempt += 1

            timeout = self.policy.get_timeout()
            if timeout is not None:
                elapsed = time.monotonic() - start_time
                if elapsed > timeout:
                    break

        if last_exception:
            raise last_exception
        raise Exception("Retry attempts exhausted without a successful response.")
