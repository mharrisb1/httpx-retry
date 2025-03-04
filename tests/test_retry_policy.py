import pytest

from httpx_retry import RetryPolicy


@pytest.mark.asyncio()
async def test_retry_policy_can_handle_no_retries():
    policy = RetryPolicy(attempts=0)
    assert not policy.should_retry(attempt=0)


@pytest.mark.asyncio()
async def test_retry_policy_make_1_retry_attempt_if_attempts_not_specified():
    policy = RetryPolicy()
    assert policy.should_retry(attempt=0, exception=Exception())
    assert not policy.should_retry(attempt=1, exception=Exception())
