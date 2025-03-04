from typing import Callable, Iterable, Optional, Protocol, TypeVar, Union

from httpx import Response

from .base import BaseRetryPolicy

__all__ = ["RetryPolicy"]

PolicyT = TypeVar("PolicyT", contravariant=True)


class AdapativePolicyFn(Protocol[PolicyT]):
    def __call__(
        self,
        policy: PolicyT,
        attempt: int,
        response: Optional[Response] = None,
        exception: Optional[Exception] = None,
    ) -> None: ...


class RetryPolicy(BaseRetryPolicy):
    def __init__(
        self,
        attempts: int = 1,
        initial_delay: float = 0.0,
        max_delay: Optional[float] = None,
        delay_func: Optional[Callable[[int], float]] = None,
        timeout: Optional[float] = None,
        multiplier: float = 1.0,
        retry_on: Optional[Union[list[int], Callable[[int], bool]]] = (lambda code: code >= 400),
        adaptive_func: Optional[AdapativePolicyFn["RetryPolicy"]] = None,
        adaptive_delay: Optional[float] = None,
    ) -> None:
        self._attempts = attempts
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._delay_func = delay_func
        self._timeout = timeout
        self._multiplier = multiplier
        self._retry_on = retry_on
        self._adaptive_func = adaptive_func
        self._adaptive_delay = adaptive_delay

    def with_attempts(self, attempts: int) -> "RetryPolicy":
        self._attempts = attempts
        return self

    def with_delay(self, delay: Union[float, Callable[[int], float]]) -> "RetryPolicy":
        if callable(delay):
            self._delay_func = delay
        else:
            self._initial_delay = delay

        return self

    def with_min_delay(self, seconds: float) -> "RetryPolicy":
        self._initial_delay = seconds
        return self

    def with_max_delay(self, seconds: float) -> "RetryPolicy":
        self._max_delay = seconds
        return self

    def with_delay_func(self, func: Callable[[int], float]) -> "RetryPolicy":
        self._delay_func = func
        return self

    def with_timeout(self, seconds: float) -> "RetryPolicy":
        self._timeout = seconds
        return self

    def with_multiplier(self, multiplier: float) -> "RetryPolicy":
        self._multiplier = multiplier
        return self

    def with_retry_on(
        self, codes: Union[list[int], Callable[[int], bool]]
    ) -> "RetryPolicy":
        self._retry_on = codes
        return self

    def with_adaptive_func(
        self, func: AdapativePolicyFn["RetryPolicy"]
    ) -> "RetryPolicy":
        self._adaptive_func = func
        return self

    def set_adaptive_delay(self, seconds: float) -> None:
        self._adaptive_delay = seconds

    def should_retry(
        self,
        attempt: int,
        response: Optional[Response] = None,
        exception: Optional[Exception] = None,
    ) -> bool:
        decision = False

        if attempt >= self._attempts:
            return decision

        if (
            exception
            or response
            and (
                callable(self._retry_on)
                and self._retry_on(response.status_code)
                or (
                    isinstance(self._retry_on, Iterable)
                    and response.status_code in self._retry_on
                )
            )
        ):
            decision = True

        if self._adaptive_func:
            self._adaptive_func(self, attempt, response, exception)

        return decision

    def get_delay(self, attempt: int) -> float:
        if self._delay_func:
            delay = self._delay_func(attempt)

        else:
            delay = self._initial_delay * (self._multiplier**attempt)
            if self._max_delay:
                delay = min(delay, self._max_delay)

        if self._adaptive_delay is not None:
            delay = self._adaptive_delay
            self._adaptive_delay = None

        return delay

    def get_timeout(self) -> Optional[float]:
        return self._timeout
