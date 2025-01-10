<p align="center">
  <img width="166" height="208" src="https://raw.githubusercontent.com/mharrisb1/httpx-retry/main/docs/img/httpx-retry.png" alt='RESPX'>
</p>
<p align="center">
  <strong>HTTPX Retry</strong> <em>- Middleware for implementing retry strategies with HTTPX</em>
</p>

---

> [!WARNING]
> Under development

## Usage

Retries are defined at the transport layer so that they can apply to all requests from the client.

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

| Name                 | Description                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------ |
| `ExponentialBackoff` | Time between retries increases exponentially with each attempt. Allows optional jitter.    |
| `LinearBackoff`      | Delay increases linearly with each retry.                                                  |
| `FixedInterval`      | Delay between retries is constant and does not change.                                     |
| `FibonacciBackoff`   | Delay follows the Fibonacci sequence (1s, 1s, 2s, 3s, 5s, etc.).                           |
| `RetryBudget`        | Limits retries based on a fixed budget to prevent excessive retries in a given time frame. |
| `AdaptiveRetry`      | Dynamically adjusts retry behavior based on system conditions or server feedback.          |

> [!NOTE]  
> Please help by contributing more strategies

## Installation

[![PyPI version](https://badge.fury.io/py/httpx-retry.svg)](https://badge.fury.io/py/httpx-retry)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/httpx-retry.svg)](https://pypi.org/project/httpx-retry/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/httpx-retry)](https://pypi.org/project/httpx-retry/)

Available in [PyPI](https://pypi.org/project/httpx-retry)

```sh
pip install httpx-retry
```

## Documentation

<!-- TODO -->

## License

[![PyPI - License](https://img.shields.io/pypi/l/httpx-retry)](https://opensource.org/blog/license/mit)

See [LICENSE](https://github.com/mharrisb1/httpx-retry/blob/main/LICENSE) for more info.

## Contributing

[![Open Issues](https://img.shields.io/github/issues/mharrisb1/httpx-retry)](https://github.com/mharrisb1/httpx-retry/issues)
[![Stargazers](https://img.shields.io/github/stars/mharrisb1/httpx-retry?style)](https://pypistats.org/packages/httpx-retry)

See [CONTRIBUTING.md](https://github.com/mharrisb1/httpx-retry/blob/main/CONTRIBUTING.md) for info on PRs, issues, and feature requests.

## Changelog

See [CHANGELOG.md](https://github.com/mharrisb1/httpx-retry/blob/main/CHANGELOG.md) for summarized notes on changes or view [releases](https://github.com/mharrisb1/httpx-retry/releases) for more details information on changes.
