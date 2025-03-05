"""
Example of implementing exponential backoff policy where the client
should increase the delay exponentially for each try.
"""

import time

import httpx
import pytest
import respx

from httpx_retry import AsyncRetryTransport, RetryPolicy, RetryTransport


@respx.mock()
def test_exponential_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    exponential_retry = (
        RetryPolicy()
        .with_max_retries(3)
        .with_min_delay(0.1)
        .with_multiplier(2)
        .with_retry_on(lambda code: code >= 500)
    )

    start = time.monotonic()
    with httpx.Client(transport=RetryTransport(policy=exponential_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.3

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_exponential_backoff(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    exponential_retry = (
        RetryPolicy().with_max_retries(3).with_min_delay(0.1).with_multiplier(2)
    )

    start = time.monotonic()
    async with httpx.AsyncClient(
        transport=AsyncRetryTransport(policy=exponential_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.3

    assert route.call_count == 3
