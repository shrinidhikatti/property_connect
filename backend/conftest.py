import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Reset DRF throttle counters between tests."""
    cache.clear()
    yield
    cache.clear()
