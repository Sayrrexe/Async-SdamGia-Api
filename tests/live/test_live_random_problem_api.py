import pytest

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_get_random_problem_returns_problem_or_none(
    api: SdamGIA,
    known_subject: str,
) -> None:
    result = await api.get_random_problem(known_subject, topic_id="1", period_days=30, seed=1)

    assert result is None or isinstance(result, dict)
    if isinstance(result, dict):
        assert {"id", "topic", "condition", "solution", "answer", "analogs", "url"}.issubset(result)
