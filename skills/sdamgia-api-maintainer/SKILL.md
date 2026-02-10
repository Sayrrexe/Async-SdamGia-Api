---
name: sdamgia-api-maintainer
description: Maintain and evolve the Async-SdamGia-Api Python library for sdamgia.ru. Use when Codex needs to change SdamGIA client behavior, HTML parsing/rendering/OCR logic, public API contracts, package/test configuration, or repository docs for this library.
---

# SdamGIA API Maintainer

Maintain this repository with a domain-first, OOP style and explicit behavior changes.

## Workflow

1. Read baseline context.
- Read `AGENTS.md`, `README.md`, `pyproject.toml`.
- Read touched modules under `sdamgia/` and related tests under `tests/`.
- Check git status before editing to avoid clobbering user work.

2. Load only required references.
- Load `references/coding-rules.md` for coding, docstring, and testing constraints.
- Load `references/api-surface.md` for public contracts and payload shapes.
- Load only the reference relevant to the active task.

3. Keep module ownership clear.
- Change transport/retry/request behavior in `sdamgia/client.py`.
- Change HTML extraction and payload shaping in `sdamgia/parsers.py`.
- Change image-render backends in `sdamgia/rendering.py`.
- Change OCR integration in `sdamgia/images.py`.
- Re-export public API from `sdamgia/__init__.py` only.

4. Implement with repository rules.
- Use explicit domain names from the codebase.
- Keep logic straightforward; avoid speculative helper layers.
- Keep public APIs fully type hinted.
- Use Google-style docstrings with `Summary`, `Args:`, `Returns:` only.
- Handle failures explicitly; avoid silent broad exception swallowing.

5. Validate in layers.
- Run `python3 -m compileall -q sdamgia` first.
- Run targeted tests for touched behavior.
- Run `pytest -q` for deterministic coverage.
- Run `pytest -m live -q` only when integration behavior changed.

6. Sync external contracts.
- Update `README.md` when user-facing behavior changes.
- Update `references/api-surface.md` when signatures/payloads change.
- Call out breaking changes explicitly in the final handoff.
