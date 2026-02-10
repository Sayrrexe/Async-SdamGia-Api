import pytest

import sdamgia.images as images_module
from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_search_by_img_returns_problem_ids_with_mocked_ocr(
    api: SdamGIA,
    known_subject: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        images_module,
        "img_to_str",
        lambda *_args, **_kwargs: "На экзамен вынесено 60 вопросов Андрей не выучил 3 из них",
    )
    result = await api.search_by_img(known_subject, "unused-path.png")

    assert isinstance(result, list)
    assert result
    assert all(isinstance(problem_id, str) and problem_id.isdigit() for problem_id in result)
