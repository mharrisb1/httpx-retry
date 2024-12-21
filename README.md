<p align="center">
  <img width="166" height="208" src="https://raw.githubusercontent.com/mharrisb1/httpx-retry/main/docs/img/httpx-retry.png" alt='RESPX'>
</p>
<p align="center">
  <strong>HTTPX Retry</strong> <em>- Middleware for implementing retry strategies with HTTPX</em>
</p>

---

## Installation

```sh
pip install httpx-retry
```

## Quick Start

```py
import httpx

from httpx_retry import RetryTransport
from httpx_retry.strategies import ExponentialBackoff

client = httpx.Client(
    transport=RetryTransport(
        strategy=ExponentialBackoff(
          min_delay=2,
          max_delay=30,
          multiplier=2,
          max_attempts=5,
          timeout=60,
          retry_on: [500, 502, 503, 504],
        )
    )
)
```

## Strategies

| Name                  | Description                                                                                     |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| `ExponentialBackoff`  | Time between retries increases exponentially with each attempt. Allows optional jitter.         |
| `LinearBackoff`       | Delay increases linearly with each retry.                                                       |
| `FixedInterval`       | Delay between retries is constant and does not change.                                          |
| `FibonacciBackoff`    | Delay follows the Fibonacci sequence (1s, 1s, 2s, 3s, 5s, etc.).                                |
| `RetryBudget`         | Limits retries based on a fixed budget to prevent excessive retries in a given time frame.      |
| `AdaptiveRetry`       | Dynamically adjusts retry behavior based on system conditions or server feedback.               |
| `CircuitBreakerRetry` | Stops retries temporarily when a failure threshold is reached to allow system recovery.         |
| `DecorrelatedJitter`  | Dynamically adjusts delays by adding randomness to prevent spikes while maintaining smoothness. |
| `TokenBucketRetry`    | Controls retry rates by allowing retries only when tokens are available in a bucket.            |
