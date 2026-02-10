import re

import pytest
import pytest_asyncio

from sdamgia import SdamGIA

pytestmark = [pytest.mark.live]


@pytest_asyncio.fixture(scope="module")
async def generated_test_id(api: SdamGIA, known_subject: str) -> str:
    test_id = await api.generate_test(known_subject, {"full": 1})
    assert isinstance(test_id, str) and test_id.isdigit()
    return test_id


def test_generate_test_returns_valid_numeric_id(generated_test_id: str) -> None:
    assert generated_test_id.isdigit()
    assert len(generated_test_id) >= 6


@pytest.mark.asyncio
async def test_generate_pdf_returns_pdf_url(
    api: SdamGIA,
    known_subject: str,
    generated_test_id: str,
) -> None:
    pdf_url = await api.generate_pdf(known_subject, generated_test_id, pdf="h")

    assert isinstance(pdf_url, str)
    assert pdf_url.startswith("https://math-ege.sdamgia.ru/pdf/")
    assert re.match(r"^https://math-ege\.sdamgia\.ru/pdf/[a-f0-9]+\.pdf$", pdf_url)
