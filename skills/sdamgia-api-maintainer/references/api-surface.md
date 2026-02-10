# `sdamgia-api` Current Public API Surface

## Module
- `sdamgia/__init__.py`
- Main class: `SdamGIA`

## Public Methods

### `SdamGIA.__init__()`
Initializes base domain, subject URLs, and optional tool settings:
- `tesseract_src`
- `html2img_chrome_path`
- `grabzit_auth`

### `get_problem_by_id(subject, id, img=None, path_to_img=None, path_to_tmp_html='')`
Fetches and parses problem details:
- `condition`
- `solution`
- `answer`
- `analogs`
- `url`

Can optionally generate an image via:
- `pyppeteer`
- `grabzit`
- `html2img`

### `search(subject, request, page=1)`
Searches problems by text query and returns problem IDs.

### `get_test_by_id(subject, testid)`
Returns IDs of problems included in a test.

### `get_category_by_id(subject, categoryid, page=1)`
Returns IDs of problems from a category page.

### `get_catalog(subject)`
Returns topic/category catalog structure for a subject.

### `generate_test(subject, problems=None)`
Generates a test and extracts generated `testid` from redirect headers.

### `generate_pdf(subject, testid, solution='', nums='', answers='', key='', crit='', instruction='', col='', pdf=True)`
Generates and returns a PDF URL for a test.

### `search_by_img(subject, path)`
Uses OCR (`sdamgia/images.py`) and threaded search requests to return matching problem IDs.

## Secondary Module
- `sdamgia/images.py`

### `img_to_str(src, path_to_tesseract)`
Converts image text via `pytesseract` using `rus+eng`.

## Known Operational Notes
- The package relies on live HTML structure from `sdamgia.ru` pages.
- Parsing behavior is tightly coupled to CSS classes (`prob_maindiv`, `pbody`, `prob_nums`, etc.).
- Unknown subjects currently raise `KeyError`.
- Image/OCR branches depend on external binaries or services.
