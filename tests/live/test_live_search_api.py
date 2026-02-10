import pytest

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_search_returns_non_empty_problem_ids(api: SdamGIA, known_subject: str) -> None:
    result = await api.search(known_subject, "Найдите количество")

    assert isinstance(result, list)
    assert result
    assert all(isinstance(problem_id, str) and problem_id.isdigit() for problem_id in result)


@pytest.mark.asyncio
async def test_invalid_subject_raises_key_error(api: SdamGIA) -> None:
    with pytest.raises(KeyError):
        await api.search("invalid-subject", "test")
