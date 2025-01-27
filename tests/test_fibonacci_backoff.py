"""
Example of implementing Fibonacci backoff policy where the client
should increase the delay following the Fibonacci sequence for each try.
"""

import time
from typing import Callable

import httpx
import pytest
import respx

from httpx_retry import AsyncRetryTransport, RetryPolicy, RetryTransport


def fibonacci_delay(initial_delay: float) -> Callable[[int], float]:
    def fib(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    return lambda attempt: initial_delay * fib(attempt)


@respx.mock()
def test_fibonacci_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    fibonacci_retry = RetryPolicy().with_attempts(3).with_delay(fibonacci_delay(0.1))

    start = time.monotonic()
    with httpx.Client(transport=RetryTransport(policy=fibonacci_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.2

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_fibonacci_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    fibonacci_retry = RetryPolicy().with_attempts(3).with_delay(fibonacci_delay(0.1))

    start = time.monotonic()
    async with httpx.AsyncClient(
        transport=AsyncRetryTransport(policy=fibonacci_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.1

    assert route.call_count == 3
