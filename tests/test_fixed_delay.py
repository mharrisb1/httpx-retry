"""
Exmaple of implementing fixed delay policy where the client should retry after
a fixed interval.
"""

import httpx
import pytest
import respx

from httpx_retry import HTTPRetryTransport, RetryPolicy
from httpx_retry.transports import AsyncHTTPRetryTransport


@respx.mock()
def test_fixed_delay(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    immediate_retry = RetryPolicy().with_attempts(3).with_delay(0.5)

    with httpx.Client(transport=HTTPRetryTransport(policy=immediate_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_fixed_delay(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    immediate_retry = RetryPolicy().with_attempts(3).with_delay(0.5)

    async with httpx.AsyncClient(
        transport=AsyncHTTPRetryTransport(policy=immediate_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3
