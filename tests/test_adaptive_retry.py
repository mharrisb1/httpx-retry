"""
Example of implementing adaptive retry policy that parses the `Retry-After` response header.
"""

import contextlib
import time
from typing import Optional

import httpx
import pytest
import respx

from httpx_retry import AsyncHTTPRetryTransport, HTTPRetryTransport, RetryPolicy


def adaptive_adjustment(
    policy: RetryPolicy,
    attempt: int,
    response: Optional[httpx.Response] = None,
    exception: Optional[Exception] = None,
) -> None:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            with contextlib.suppress(Exception):
                # NOTE: `Retry-After` should be in seconds so we need to adjust
                #       https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After
                policy.set_adaptive_delay(float(retry_after) * 1e3)


@respx.mock()
def test_adaptive_retry_with_retry_after(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500, headers={"Retry-After": "1"}),
        httpx.Response(200),
    ]

    adaptive_policy = (
        RetryPolicy()
        .with_attempts(2)
        .with_delay(50)
        .with_multiplier(2)
        .with_retry_on([500])
        .with_adaptive_func(adaptive_adjustment)
    )

    start = time.monotonic()
    with httpx.Client(transport=HTTPRetryTransport(policy=adaptive_policy)) as client:
        response = client.get("https://example.com")
        assert response.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.1

    assert route.call_count == 2


@pytest.mark.asyncio()
@respx.mock()
async def test_async_adaptive_retry_with_retry_after(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500, headers={"Retry-After": "1"}),
        httpx.Response(200),
    ]

    adaptive_policy = (
        RetryPolicy()
        .with_attempts(2)
        .with_delay(50)
        .with_multiplier(2)
        .with_retry_on([500])
        .with_adaptive_func(adaptive_adjustment)
    )

    start = time.monotonic()
    async with httpx.AsyncClient(
        transport=AsyncHTTPRetryTransport(policy=adaptive_policy)
    ) as client:
        response = await client.get("https://example.com")
        assert response.status_code == 200
    end = time.monotonic()

    elapsed = end - start
    assert elapsed >= 0.005

    assert route.call_count == 2
