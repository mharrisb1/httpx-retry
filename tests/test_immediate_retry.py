"""
Example of implementing immediate retry policy (spam policy) where the client
should retry immediately without a delay.
"""

import httpx
import pytest
import respx

from httpx_retry import AsyncRetryTransport, RetryPolicy, RetryTransport


@respx.mock()
def test_immediate_retry(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    immediate_retry = RetryPolicy().with_attempts(3).with_delay(0)

    with httpx.Client(transport=RetryTransport(policy=immediate_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_immediate_retry(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200),
    ]

    immediate_retry = RetryPolicy().with_attempts(3).with_delay(0)

    async with httpx.AsyncClient(
        transport=AsyncRetryTransport(policy=immediate_retry)
    ) as client:
        res = await client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 3
