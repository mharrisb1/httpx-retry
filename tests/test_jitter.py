"""
Example of implementing exponential backoff with jitter policy where the client
should increase the delay exponentially with added randomness (jitter) for each try.
"""

import random
from typing import Callable

import httpx
import pytest
import respx

from httpx_retry import AsyncHTTPRetryTransport, HTTPRetryTransport, RetryPolicy


def exponential_jitter_delay(
    min_delay: float, multiplier: float
) -> Callable[[int], float]:
    return lambda attempt: random.uniform(0, min_delay * (multiplier**attempt))


@respx.mock()
def test_exponential_backoff_with_jitter(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    jitter_retry = (
        RetryPolicy().with_attempts(3).with_delay_func(exponential_jitter_delay(100, 2))
    )

    with httpx.Client(transport=HTTPRetryTransport(policy=jitter_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_exponential_backoff_with_jitter(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    jitter_retry = (
        RetryPolicy().with_attempts(3).with_delay_func(exponential_jitter_delay(100, 2))
    )

    async with httpx.AsyncClient(
        transport=AsyncHTTPRetryTransport(policy=jitter_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3
