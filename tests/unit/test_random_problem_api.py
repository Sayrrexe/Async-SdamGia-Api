import pytest

from sdamgia import SdamGIA


@pytest.mark.asyncio
async def test_get_random_problem_returns_full_problem_payload(
    api: SdamGIA,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_catalog(subject: str) -> list[dict[str, object]]:
        assert subject == "math"
        return [
            {
                "topic_id": "1",
                "topic_name": "Task 1",
                "categories": [{"category_id": "cat-1", "category_name": "Category"}],
            }
        ]

    async def fake_get_category_by_id(subject: str, categoryid: str, page: int = 1) -> list[str]:
        assert subject == "math"
        assert categoryid == "cat-1"
        if page == 1:
            return ["1001", "1002"]
        return []

    async def fake_get_problem_by_id(
        subject: str,
        id: str,
        img: str | None = None,
        path_to_img: str | None = None,
        path_to_tmp_html: str = "",
    ) -> dict[str, object]:
        assert subject == "math"
        assert img is None
        assert path_to_img is None
        assert path_to_tmp_html == ""
        return {
            "id": id,
            "topic": "1",
            "condition": {"text": "Condition", "images": []},
            "solution": {"text": "Solution", "images": []},
            "answer": "42",
            "analogs": [],
            "url": f"https://math-ege.sdamgia.ru/problem?id={id}",
        }

    monkeypatch.setattr(api, "get_catalog", fake_get_catalog)
    monkeypatch.setattr(api, "get_category_by_id", fake_get_category_by_id)
    monkeypatch.setattr(api, "get_problem_by_id", fake_get_problem_by_id)

    result = await api.get_random_problem("math", topic_id="1", period_days=30, seed=7)

    assert isinstance(result, dict)
    assert {"id", "topic", "condition", "solution", "answer", "analogs", "url"}.issubset(result)


@pytest.mark.asyncio
async def test_get_random_problem_seed_makes_selection_deterministic(
    api: SdamGIA,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_catalog(_subject: str) -> list[dict[str, object]]:
        return [
            {
                "topic_id": "1",
                "topic_name": "Task 1",
                "categories": [{"category_id": "cat-1", "category_name": "Category"}],
            }
        ]

    async def fake_get_category_by_id(_subject: str, _categoryid: str, page: int = 1) -> list[str]:
        if page == 1:
            return ["1001", "1002", "1003", "1004"]
        return []

    async def fake_get_problem_by_id(
        _subject: str,
        id: str,
        img: str | None = None,
        path_to_img: str | None = None,
        path_to_tmp_html: str = "",
    ) -> dict[str, object]:
        return {
            "id": id,
            "topic": "1",
            "condition": {"text": "Condition", "images": []},
            "solution": {"text": "Solution", "images": []},
            "answer": "42",
            "analogs": [],
            "url": f"https://math-ege.sdamgia.ru/problem?id={id}",
        }

    monkeypatch.setattr(api, "get_catalog", fake_get_catalog)
    monkeypatch.setattr(api, "get_category_by_id", fake_get_category_by_id)
    monkeypatch.setattr(api, "get_problem_by_id", fake_get_problem_by_id)

    first = await api.get_random_problem("math", topic_id="1", period_days=30, seed=123)
    second = await api.get_random_problem("math", topic_id="1", period_days=30, seed=123)

    assert isinstance(first, dict)
    assert isinstance(second, dict)
    assert first["id"] == second["id"]


@pytest.mark.asyncio
@pytest.mark.parametrize("period_days", [0, -1])
async def test_get_random_problem_invalid_period_days_raises_value_error(
    api: SdamGIA,
    period_days: int,
) -> None:
    with pytest.raises(ValueError, match="period_days must be >= 1"):
        await api.get_random_problem("math", topic_id="1", period_days=period_days)


@pytest.mark.asyncio
async def test_get_random_problem_missing_topic_returns_none(
    api: SdamGIA,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_catalog(_subject: str) -> list[dict[str, object]]:
        return [
            {
                "topic_id": "2",
                "topic_name": "Task 2",
                "categories": [{"category_id": "cat-2", "category_name": "Category"}],
            }
        ]

    monkeypatch.setattr(api, "get_catalog", fake_get_catalog)

    result = await api.get_random_problem("math", topic_id="1", period_days=30, seed=1)

    assert result is None


@pytest.mark.asyncio
async def test_get_random_problem_fallback_to_year_when_initial_pool_empty(
    api: SdamGIA,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested_pages: list[int] = []

    async def fake_get_catalog(_subject: str) -> list[dict[str, object]]:
        return [
            {
                "topic_id": "1",
                "topic_name": "Task 1",
                "categories": [{"category_id": "cat-1", "category_name": "Category"}],
            }
        ]

    async def fake_get_category_by_id(_subject: str, _categoryid: str, page: int = 1) -> list[str]:
        requested_pages.append(page)
        if page == 10:
            return ["9910"]
        return []

    async def fake_get_problem_by_id(
        _subject: str,
        id: str,
        img: str | None = None,
        path_to_img: str | None = None,
        path_to_tmp_html: str = "",
    ) -> dict[str, object]:
        return {
            "id": id,
            "topic": "1",
            "condition": {"text": "Condition", "images": []},
            "solution": {"text": "Solution", "images": []},
            "answer": "42",
            "analogs": [],
            "url": f"https://math-ege.sdamgia.ru/problem?id={id}",
        }

    monkeypatch.setattr(api, "get_catalog", fake_get_catalog)
    monkeypatch.setattr(api, "get_category_by_id", fake_get_category_by_id)
    monkeypatch.setattr(api, "get_problem_by_id", fake_get_problem_by_id)

    result = await api.get_random_problem("math", topic_id="1", period_days=30, seed=3)

    assert isinstance(result, dict)
    assert result["id"] == "9910"
    assert 10 in requested_pages


@pytest.mark.asyncio
async def test_get_random_problem_invalid_subject_keeps_key_error(api: SdamGIA) -> None:
    with pytest.raises(KeyError):
        await api.get_random_problem("invalid-subject", topic_id="1", period_days=30)
