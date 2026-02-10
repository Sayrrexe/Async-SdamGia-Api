# Coding Rules for `sdamgia-api`

## Design Direction
- Use object-oriented design for new production logic.
- Keep classes focused on one domain responsibility.
- Allow breaking changes when they simplify architecture or improve maintainability.

## Anti-AI Writing Rule
Make code look human-authored and repository-native:
- Reuse local naming vocabulary and intent.
- Avoid generic abstractions added "just in case."
- Avoid repetitive template comments and mechanical phrasing.
- Do not add explanatory comments for obvious lines.

## Python Style
- Use explicit type hints for public APIs.
- Keep control flow direct and readable.
- Prefer specific exceptions over blanket `except Exception`.
- Do not hide behavior in large utility modules.

## Docstrings (Google Style, Restricted)
For public classes, methods, and functions, use only:
- summary
- `Args:`
- `Returns:`

Do not add:
- `Examples`
- `Notes`
- `Raises`
- long prose blocks
