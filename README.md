<p align="center">
  <img width="166" height="208" src="https://raw.githubusercontent.com/mharrisb1/httpx-retry/main/docs/img/httpx-retry.png" alt='RESPX'>
</p>
<p align="center">
  <strong>HTTPX Retry</strong> <em>- Middleware for implementing retry policies with HTTPX</em>
</p>

---

## Usage

Retries are defined at the transport layer.

```python
import httpx

from httpx_retry import RetryTransport, RetryPolicy

exponential_retry = (
    RetryPolicy()
    .with_max_retries(3)
    .with_min_delay(0.1)
    .with_multiplier(2)
    .with_retry_on(lambda status_code: status_code >= 500)
)

client = httpx.Client(transport=RetryTransport(policy=exponential_retry))
res = client.get("https://example.com")
```

## Examples

There are examples of implementing common retry policies in [`/tests`](./tests)

- [Adaptive Retry](./tests/test_adaptive_retry.py)
- [Circuit Breaker](./tests/test_circuit_breaker.py)
- [Exponential Backoff](./tests/test_exponential_backoff.py)
- [Fibonacci Backoff](./tests/test_fibonacci_backoff.py)
- [Fixed Delay](./tests/test_fixed_delay.py)
- [Immediate Retry](./tests/test_immediate_retry.py)
- [Jitter](./tests/test_jitter.py)
- [Linear Backoff](./tests/test_linear_backoff.py)

## Installation

[![PyPI version](https://badge.fury.io/py/httpx-retry.svg)](https://badge.fury.io/py/httpx-retry)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/httpx-retry.svg)](https://pypi.org/project/httpx-retry/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/httpx-retry)](https://pypi.org/project/httpx-retry/)

Available in [PyPI](https://pypi.org/project/httpx-retry)

```sh
pip install httpx-retry
```

## License

[![PyPI - License](https://img.shields.io/pypi/l/httpx-retry)](https://opensource.org/blog/license/mit)

See [LICENSE](https://github.com/mharrisb1/httpx-retry/blob/main/LICENSE) for more info.

## Contributing

[![Open Issues](https://img.shields.io/github/issues/mharrisb1/httpx-retry)](https://github.com/mharrisb1/httpx-retry/issues)
[![Stargazers](https://img.shields.io/github/stars/mharrisb1/httpx-retry?style)](https://pypistats.org/packages/httpx-retry)

See [CONTRIBUTING.md](https://github.com/mharrisb1/httpx-retry/blob/main/CONTRIBUTING.md) for info on PRs, issues, and feature requests.

## Changelog

See [CHANGELOG.md](https://github.com/mharrisb1/httpx-retry/blob/main/CHANGELOG.md) for summarized notes on changes or view [releases](https://github.com/mharrisb1/httpx-retry/releases) for more details information on changes.
