import pytest

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_get_problem_by_id_returns_expected_shape(
    api: SdamGIA,
    known_subject: str,
    known_problem_id: str,
) -> None:
    result = await api.get_problem_by_id(known_subject, known_problem_id)

    assert isinstance(result, dict)
    assert {"id", "topic", "condition", "solution", "answer", "analogs", "url"}.issubset(result)
    assert result["id"] == known_problem_id
    assert isinstance(result["topic"], str) and result["topic"]
    assert isinstance(result["condition"], dict)
    assert isinstance(result["solution"], dict)
    assert isinstance(result["answer"], str)
    assert isinstance(result["analogs"], list)
    assert result["url"].startswith("https://math-ege.sdamgia.ru/problem?id=")
