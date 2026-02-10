import pytest
import pytest_asyncio

from sdamgia import SdamGIA

@pytest_asyncio.fixture(scope="session")
async def api() -> SdamGIA:
    client = SdamGIA(
        timeout_seconds=20.0,
        retries=2,
        retry_base_delay_seconds=1.0,
        user_agent="sdamgia-api-live-tests/1.0",
    )
    yield client
    await client.aclose()


@pytest.fixture(scope="session")
def known_subject() -> str:
    return "math"


@pytest.fixture(scope="session")
def known_problem_id() -> str:
    return "1001"


@pytest.fixture(scope="session")
def known_test_id() -> str:
    return "1770"


@pytest.fixture(scope="session")
def known_category_id() -> str:
    return "1"
