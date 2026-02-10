# Async-SdamGia-Api Public API Surface

## Package Entry Point

- Module: `sdamgia/__init__.py`
- Public export: `SdamGIA`

## Class: `SdamGIA`

### Constructor

`SdamGIA(timeout_seconds=20.0, retries=2, retry_base_delay_seconds=1.0, user_agent="sdamgia-api/async")`

Configures:
- shared async HTTP client
- retry strategy
- subject-to-base-url map
- optional tool settings (`tesseract_src`, `html2img_chrome_path`, `grabzit_auth`)

### Resource lifecycle

- `async with SdamGIA() as api:` preferred
- `await api.aclose()` to close underlying `httpx.AsyncClient`

## Supported Subject Codes

`math`, `mathb`, `phys`, `inf`, `rus`, `bio`, `en`, `chem`, `geo`, `soc`, `de`, `fr`, `lit`, `sp`, `hist`

Unknown subject currently raises `KeyError` from subject map lookup.

## Public Methods

### `await get_problem_by_id(subject, id, img=None, path_to_img=None, path_to_tmp_html="")`

Returns `dict[str, object] | None`.

Problem payload shape:
- `id: str`
- `topic: str`
- `condition: dict[str, object]` with `text`, `images`
- `solution: dict[str, object]` with `text`, `images`
- `answer: str`
- `analogs: list[str]`
- `url: str`

`img` backends: `pyppeteer`, `grabzit`, `html2img`.

### `await search(subject, request, page=1)`

Returns `list[str]` of problem IDs.

### `await get_test_by_id(subject, testid)`

Returns `list[str]` of problem IDs from test page.

### `await get_category_by_id(subject, categoryid, page=1)`

Returns `list[str]` of problem IDs from category listing.

### `await get_catalog(subject)`

Returns `list[dict[str, object]]`.

Catalog item shape:
- `topic_id: str`
- `topic_name: str`
- `categories: list[dict[str, str]]` with `category_id`, `category_name`

### `await get_random_problem(subject, topic_id, period_days=30, seed=None)`

Returns `dict[str, object] | None`.

- Returns the same payload shape as `get_problem_by_id`.
- `topic_id` is required.
- `period_days` must be `>= 1`, otherwise `ValueError` is raised.
- Unknown subject keeps existing `KeyError` behavior.
- Period matching is best-effort (freshness heuristic by category pages/problem IDs), not strict by publication date.
- If no candidates are found in requested period window, method retries once with fallback window equivalent to 365 days.

### `await generate_test(subject, problems=None)`

Returns generated `testid` as numeric `str`.

- Default generation uses `{"full": 1}`.
- Parses redirect `location` header and extracts `id` query param.
- Raises `ValueError` if redirect id is missing or non-numeric.

### `await generate_pdf(subject, testid, solution="", nums="", answers="", key="", crit="", instruction="", col="", pdf=True)`

Returns absolute PDF URL as `str`.

### `await search_by_img(subject, path)`

Returns unique `list[str]` of problem IDs based on OCR text.

- OCR source: `sdamgia.images.img_to_str(path, tesseract_src)`
- Splits OCR text into windows and issues concurrent search requests
- Skips failed search chunks on `httpx.HTTPError`

## Related Internal Boundaries

- `sdamgia/parsers.py`: problem/catalog payload extraction
- `sdamgia/rendering.py`: image backend adapters
- `sdamgia/images.py`: Tesseract OCR wrapper
- `tests/live/`: integration tests against live sdamgia endpoints
