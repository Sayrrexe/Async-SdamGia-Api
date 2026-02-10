import pytest

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest.mark.asyncio
async def test_get_catalog_returns_topics_with_categories(api: SdamGIA, known_subject: str) -> None:
    catalog = await api.get_catalog(known_subject)

    assert isinstance(catalog, list)
    assert catalog

    topic = catalog[0]
    assert {"topic_id", "topic_name", "categories"}.issubset(topic)
    assert isinstance(topic["topic_id"], str) and topic["topic_id"]
    assert isinstance(topic["topic_name"], str) and topic["topic_name"]
    assert isinstance(topic["categories"], list)

    if topic["categories"]:
        category = topic["categories"][0]
        assert {"category_id", "category_name"}.issubset(category)
        assert isinstance(category["category_id"], str) and category["category_id"]
        assert isinstance(category["category_name"], str) and category["category_name"]
