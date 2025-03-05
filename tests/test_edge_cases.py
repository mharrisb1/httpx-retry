import httpx
import respx

from httpx_retry import RetryPolicy, RetryTransport


@respx.mock()
def test_set_attempts_to_zero(respx_mock: respx.MockRouter):
    route = respx_mock.get("https://example.com")
    route.side_effect = [httpx.Response(200)]

    # ensure there is an initial try before any determination on retries
    zero_retry = RetryPolicy().with_max_retries(0)

    with httpx.Client(transport=RetryTransport(policy=zero_retry)) as client:
        res = client.get("https://example.com")
        assert res.status_code == 200

    assert route.call_count == 1
