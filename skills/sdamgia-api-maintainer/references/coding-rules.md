# Coding Rules for Async-SdamGia-Api

## Architecture

- Keep production changes OOP and domain-focused.
- Group behavior by domain boundary: client transport, HTML parsing, rendering, OCR.
- Prefer explicit logic over generic wrappers and speculative abstractions.
- Allow breaking changes only when structure/clarity improves and tests/docs are updated.

## Public API and Naming

- Keep `SdamGIA` as the main public entry point in `sdamgia/__init__.py`.
- Match repository vocabulary (`subject`, `problem`, `catalog`, `test`, `pdf`, `ocr`).
- Add type hints to all public classes, methods, and functions.

## Docstrings

- Use Google-style docstrings for all public classes, methods, and functions.
- Keep only this structure:
  - short summary
  - `Args:`
  - `Returns:`
- Do not use `Examples`, `Notes`, `Raises`, `Attributes`, or long tutorial prose.

## Error Handling

- Handle failures explicitly with concrete exception behavior.
- Avoid silent broad `except Exception` blocks unless narrowly justified.
- Preserve existing error semantics unless changing them intentionally with tests/docs updates.

## Async and I/O Patterns

- Keep HTTP interactions async via `httpx.AsyncClient`.
- Move blocking integrations (`pytesseract`, `html2image`, GrabzIT SDK) to `asyncio.to_thread`.
- Keep resource lifecycle explicit (`async with SdamGIA()` or `await api.aclose()`).

## Testing Policy

- Add or update tests for any behavior change.
- Keep default tests deterministic and isolated from external services.
- Keep live integration tests under `tests/live/` and mark with `pytest.mark.live`.
- Mock OCR extraction in tests instead of requiring a local Tesseract installation.

## Validation Commands

- `python3 -m compileall -q sdamgia`
- `pytest -q`
- `pytest -m live -q` (only for integration-sensitive changes)
