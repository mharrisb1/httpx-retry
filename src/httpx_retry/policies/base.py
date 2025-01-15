from abc import ABC, abstractmethod
from typing import Optional

from httpx import Response


class BaseRetryPolicy(ABC):
    @abstractmethod
    def should_retry(
        self,
        attempt: int,
        response: Optional[Response] = None,
        exception: Optional[Exception] = None,
    ) -> bool:
        """
        Determine whether a retry should occur based on the current attempt,
        an HTTP response, or an exception.
        """
        ...

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay (seconds) before the next retry attempt,
        based on the current attempt number or other policy parameters.
        """
        ...

    @abstractmethod
    def get_timeout(self) -> Optional[float]:
        """
        Get timeout (seconds)
        """
        ...
