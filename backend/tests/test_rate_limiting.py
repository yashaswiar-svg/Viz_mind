import pytest
from app.core.middleware.rate_limiter import RateLimiter


def test_rate_limiter_exceeded():
    limiter = RateLimiter(requests_limit=5, window_seconds=60)
    ip = "192.168.1.100"

    # Make 5 requests (should pass)
    for _ in range(5):
        assert limiter.is_rate_limited(ip) is False

    # 6th request should fail
    assert limiter.is_rate_limited(ip) is True


def test_rate_limiter_different_ips():
    limiter = RateLimiter(requests_limit=2, window_seconds=60)
    ip1 = "192.168.1.1"
    ip2 = "192.168.1.2"

    assert limiter.is_rate_limited(ip1) is False
    assert limiter.is_rate_limited(ip1) is False
    assert limiter.is_rate_limited(ip1) is True

    # ip2 is unaffected
    assert limiter.is_rate_limited(ip2) is False
