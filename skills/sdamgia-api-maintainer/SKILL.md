---
name: sdamgia-api-maintainer
description: Maintain and evolve the sdamgia-api Python library. Use when working on scraping/parsing logic for sdamgia.ru, updating package structure, adding tests/CI, refactoring the SdamGIA class, or introducing breaking API changes in this repository.
---

# SdamGIA API Maintainer

## Overview

Use this skill to develop and modernize `sdamgia-api` as a maintainable Python package.
Focus on deliberate refactoring, clear OOP design, deterministic tests, and repository-specific coding rules.

## Core Workflow

### 1. Build Context Before Editing
Read these files first:
- `sdamgia/__init__.py`
- `sdamgia/images.py`
- `pyproject.toml`
- `README.md`
- `AGENTS.md`

Then inspect current git state to avoid clobbering in-progress user changes.

### 2. Apply Repository Design Rules
Use OOP style for new logic:
- Prefer cohesive classes and explicit responsibilities.
- Avoid utility dumps and speculative abstractions.
- Group behavior by domain (`problem parsing`, `catalog parsing`, `test generation`).

Breaking changes are allowed in this repository. Do not preserve old contracts unless explicitly requested.

### 3. Follow Docstring Contract
For public classes, methods, and functions, write Google-style docstrings with strict sections:
- Summary line.
- `Args:`
- `Returns:`

Do not include `Examples`, `Notes`, `Raises`, or auxiliary narrative blocks.

### 4. Keep Code Human-Like
When editing or creating code:
- Use domain names that match the repository vocabulary.
- Avoid repetitive generic scaffolding and template-heavy phrasing.
- Keep comments sparse and purposeful; do not narrate obvious assignments.
- Match local coding style instead of forcing uniform boilerplate.

### 5. Validate in Layers
Run fast checks first:
- `python3 -m compileall -q sdamgia`
- unit tests for touched modules

Run broader checks after local fixes:
- package install/build checks
- full test suite

Document behavior changes in README and changelog-style notes when changing public behavior.

## References

- API map: `references/api-surface.md`
- Coding rules: `references/coding-rules.md`

Load only the reference that is relevant to the current task.
