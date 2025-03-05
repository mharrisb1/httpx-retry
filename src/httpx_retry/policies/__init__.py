from typing import Callable, Iterable, Optional, Protocol, TypeVar, Union

from httpx import Response

from .base import BaseRetryPolicy

__all__ = ["RetryPolicy"]

PolicyT = TypeVar("PolicyT", contravariant=True)


class AdapativePolicyFn(Protocol[PolicyT]):
    """Protocol for an adaptive policy function.

    This function is used to adjust the retry policy after each attempt based on
    the outcome (response or exception).

    Parameters:
        policy: The current instance of the retry policy.
        attempt: The current attempt number.
        response: The HTTP response received, if any.
        exception: The exception encountered, if any.
    """

    def __call__(
        self,
        policy: PolicyT,
        attempt: int,
        response: Optional[Response] = None,
        exception: Optional[Exception] = None,
    ) -> None: ...


class RetryPolicy(BaseRetryPolicy):
    """Retry policy for network requests.

    This policy provides a configurable mechanism for retrying network calls.
    It supports customizable delays, timeouts, and adaptive adjustments based on
    responses or exceptions.

    Note:
        The `max_retries` parameter represents the number of retry attempts, not the
        total number of attempts. An initial call will always be made, even if `max_retries`
        is set to 0.
    """

    def __init__(
        self,
        max_retries: Optional[int] = None,
        initial_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        delay_func: Optional[Callable[[int], float]] = None,
        timeout: Optional[float] = None,
        multiplier: Optional[float] = None,
        retry_on: Optional[Union[list[int], Callable[[int], bool]]] = None,
        adaptive_func: Optional[AdapativePolicyFn["RetryPolicy"]] = None,
        adaptive_delay: Optional[float] = None,
    ) -> None:
        """
        Note:
            It is recommended to use the builder methods instead of the constructor directly

        Parameters:
            max_retries: The number of retry attempts. Note that an initial call is always made,
                         even if max_retries is set to 0.
            initial_delay: The initial delay (in seconds) before the first retry.
            max_delay: The maximum allowed delay (in seconds) between retries.
            delay_func: A function to calculate the delay based on the attempt number.
            timeout: The timeout (in seconds) for each network call attempt.
            multiplier: The factor by which the delay increases with each attempt.
            retry_on: A list of HTTP status codes or a callable that determines whether a given
                      status code should trigger a retry.
            adaptive_func: A function that adapts the policy based on the response or exception.
            adaptive_delay: An adaptive delay override (in seconds) that can be dynamically set.
        """
        self._max_retries = max_retries or 1
        self._initial_delay = initial_delay or 0.0
        self._max_delay = max_delay
        self._delay_func = delay_func
        self._timeout = timeout
        self._multiplier = multiplier or 1.0
        self._retry_on = retry_on or (lambda code: code >= 500)
        self._adaptive_func = adaptive_func
        self._adaptive_delay = adaptive_delay

    def with_max_retries(self, max_retries: int) -> "RetryPolicy":
        """Set the number of maximum retry attempts.

        Note:
            This value represents the number of retries after the initial call.

        Parameters:
            max_retries: The number of retry attempts.

        Returns:
            The updated retry policy instance.
        """
        self._max_retries = max_retries
        return self

    def with_delay(self, delay: Union[float, Callable[[int], float]]) -> "RetryPolicy":
        """Configure the delay before retry attempts.

        Parameters:
            delay: Either a constant delay (in seconds) or a callable that returns
                   a delay based on the attempt number.

        Returns:
            The updated retry policy instance.
        """
        if callable(delay):
            self._delay_func = delay
        else:
            self._initial_delay = delay

        return self

    def with_min_delay(self, seconds: float) -> "RetryPolicy":
        """Set the minimum delay before a retry attempt.

        Parameters:
            seconds: The minimum delay in seconds.

        Returns:
            The updated retry policy instance.
        """
        self._initial_delay = seconds
        return self

    def with_max_delay(self, seconds: float) -> "RetryPolicy":
        """Set the maximum allowed delay between retries.

        Parameters:
            seconds: The maximum delay in seconds.

        Returns:
            The updated retry policy instance.
        """
        self._max_delay = seconds
        return self

    def with_delay_func(self, func: Callable[[int], float]) -> "RetryPolicy":
        """Set a custom function to calculate the delay based on the attempt number.

        Parameters:
            func: A function that takes the attempt number and returns the delay in seconds.

        Returns:
            The updated retry policy instance.
        """
        self._delay_func = func
        return self

    def with_timeout(self, seconds: float) -> "RetryPolicy":
        """Set the timeout for each network call attempt.

        Parameters:
            seconds: The timeout in seconds.

        Returns:
            The updated retry policy instance.
        """
        self._timeout = seconds
        return self

    def with_multiplier(self, multiplier: float) -> "RetryPolicy":
        """Set the multiplier to increase the delay after each attempt.

        Parameters:
            multiplier: The multiplier factor.

        Returns:
            The updated retry policy instance.
        """
        self._multiplier = multiplier
        return self

    def with_retry_on(
        self, codes: Union[list[int], Callable[[int], bool]]
    ) -> "RetryPolicy":
        """Configure the conditions for retrying based on HTTP status codes.

        Parameters:
            codes: A list of status codes or a callable that returns True for codes
                   that should trigger a retry.

        Returns:
            The updated retry policy instance.
        """
        self._retry_on = codes
        return self

    def with_adaptive_func(
        self, func: AdapativePolicyFn["RetryPolicy"]
    ) -> "RetryPolicy":
        """Set an adaptive function to adjust the retry policy dynamically.

        The adaptive function is called on every retry attempt and can modify the policy
        based on the response or exception.

        Parameters:
            func: A callable to adapt the policy.

        Returns:
            The updated retry policy instance.
        """
        self._adaptive_func = func
        return self

    def set_adaptive_delay(self, seconds: float) -> None:
        """Set an adaptive delay that overrides the standard delay for the next attempt.

        Parameters:
            seconds: The adaptive delay in seconds.
        """
        self._adaptive_delay = seconds

    def should_retry(
        self,
        attempt: int,
        response: Optional[Response] = None,
        exception: Optional[Exception] = None,
    ) -> bool:
        """Determine whether a retry should be attempted.

        A retry is allowed if the current attempt is less than the allowed max retries
        and if either an exception occurred or the response status code meets the retry criteria.

        If an adaptive function is set, it will be called to adjust the policy dynamically.

        Parameters:
            attempt: The current attempt number.
            response: The HTTP response received, if any.
            exception: The exception encountered, if any.

        Returns:
            True if a retry should be performed, False otherwise.
        """
        decision = False

        if attempt >= self._max_retries:
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
        """Calculate the delay before the next retry attempt.

        The delay is determined either by a custom delay function or by using the
        initial delay increased by a multiplier for each attempt. The delay is capped
        by the maximum delay if specified. An adaptive delay, if set, overrides the calculated delay.

        Parameters:
            attempt: The current attempt number.

        Returns:
            The delay in seconds before the next retry attempt.
        """
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
        """Retrieve the timeout setting for network calls.

        Returns:
            The timeout in seconds, or None if not set.
        """
        return self._timeout
