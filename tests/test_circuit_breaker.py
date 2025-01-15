"""
Example of implementing a circuit breaker policy where the client
stops retrying after a certain number of failures.
"""

import contextlib
import time
from typing import Optional

import httpx
import pytest
import respx

from httpx_retry import AsyncHTTPRetryTransport, HTTPRetryTransport
from httpx_retry.policies.base import BaseRetryPolicy


class CircuitBreakerPolicy(BaseRetryPolicy):
    def __init__(self) -> None:
        self._failure_threshold = 3
        self._recovery_timeout = 60.0
        self._success_threshold = 1
        self._state = "closed"
        self._failure_count = 0
        self._opened_timestamp: Optional[float] = None

    def with_failure_threshold(self, threshold: int) -> "CircuitBreakerPolicy":
        self._failure_threshold = threshold
        return self

    def with_recovery_timeout(self, timeout: float) -> "CircuitBreakerPolicy":
        self._recovery_timeout = timeout
        return self

    def with_success_threshold(self, threshold: int) -> "CircuitBreakerPolicy":
        self._success_threshold = threshold
        return self

    def should_retry(
        self,
        attempt: int,
        response: Optional[httpx.Response] = None,
        exception: Optional[Exception] = None,
    ) -> bool:
        now = time.monotonic()
        if self._state == "open":
            if (
                self._opened_timestamp
                and (now - self._opened_timestamp) >= self._recovery_timeout
            ):
                self._state = "half-open"
            else:
                return False

        if exception or (response and response.status_code >= 500):
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                self._state = "open"
                self._opened_timestamp = now
                return False
            return True
        else:
            self._failure_count = 0
        return False

    def get_delay(self, attempt: int) -> float:
        return 0.0

    def get_timeout(self) -> Optional[float]:
        return None


@respx.mock()
def test_circuit_breaker(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(500),
    ]

    circuit_breaker = (
        CircuitBreakerPolicy().with_failure_threshold(3).with_recovery_timeout(60)
    )

    with httpx.Client(transport=HTTPRetryTransport(policy=circuit_breaker)) as client:  # noqa: SIM117
        with contextlib.suppress(Exception):
            client.get("https://example.com")

    assert route.call_count == 3


@pytest.mark.asyncio()
@respx.mock()
async def test_async_circuit_breaker(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(500),
    ]

    circuit_breaker = (
        CircuitBreakerPolicy().with_failure_threshold(3).with_recovery_timeout(60)
    )

    async with httpx.AsyncClient(
        transport=AsyncHTTPRetryTransport(policy=circuit_breaker)
    ) as client:
        with contextlib.suppress(Exception):
            await client.get("https://example.com")

    assert route.call_count == 3
