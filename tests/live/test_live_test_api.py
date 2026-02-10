import pytest

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_get_test_by_id_returns_problem_ids(
    api: SdamGIA,
    known_subject: str,
    known_test_id: str,
) -> None:
    result = await api.get_test_by_id(known_subject, known_test_id)

    assert isinstance(result, list)
    assert result
    assert all(isinstance(problem_id, str) and problem_id.isdigit() for problem_id in result)
