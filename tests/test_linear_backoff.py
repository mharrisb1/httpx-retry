"""
Example of implementing linear backoff policy where the client should increase
the delay by a fixed interval for each try.
"""

import time
from typing import Callable

import httpx
import pytest
import respx

from httpx_retry import AsyncRetryTransport, RetryPolicy, RetryTransport


def linear_delay(initial_delay: float, increment: float) -> Callable[[int], float]:
    return lambda attempt: initial_delay + attempt * increment


@respx.mock()
def test_linear_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    linear_retry = RetryPolicy().with_attempts(3).with_delay(linear_delay(0.1, 0.1))

    start = time.monotonic()
    with httpx.Client(transport=RetryTransport(policy=linear_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.03

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_linear_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    linear_retry = RetryPolicy().with_attempts(3).with_delay(linear_delay(0.1, 0.1))

    start = time.monotonic()
    async with httpx.AsyncClient(
        transport=AsyncRetryTransport(policy=linear_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.03

    assert route.call_count == 3
