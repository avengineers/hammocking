# AGENTS.md

## Project Overview

Hammocking is an automatic mocking tool for C code. It parses C/C++ source files using libclang, extracts undefined symbols from object files via `nm`, and generates mock implementations using Jinja2 templates. Output styles: Google Mock (C++) and plain C stubs.

## Architecture

```
src/hammocking/
├── hammocking.py      # Core logic (all key classes)
├── __main__.py        # CLI entry point
├── hammocking.ini     # Default config (OS-specific sections)
└── templates/
    ├── gmock/         # Google Mock C++ templates (.j2)
    └── plain_c/       # Plain C stub templates (.j2)
```

**Key classes** (all in `hammocking.py`):
- `HammockConfig` / `HammockIni` — Configuration dataclasses with `mashumaro` serialization
- `Hammock` — Main parser: walks libclang AST to find symbols, delegates to `MockupWriter`
- `MockupWriter` — Renders Jinja2 templates into mock `.c`/`.cc`/`.h` files
- `NmWrapper` — Extracts undefined symbols from partially-linked object files via `nm`
- `HammockRunner` — Orchestrates config loading, parsing, and output
- `Function` / `Variable` / `RenderableType` — AST node wrappers for code generation

**Entry point:** `main()` in `hammocking.py` parses CLI args and runs `HammockRunner`.

## Tech Stack

- **Language:** Python >=3.10, <3.14 (3.13 recommended)
- **Package Manager:** uv
- **Key dependencies:** libclang (C parsing), Jinja2 (templating), py-app-dev (subprocess), mashumaro (serialization)
- **Testing:** pytest + pytest-cov
- **Linting:** ruff, mypy (strict), pre-commit hooks
- **Documentation:** Sphinx + ReadTheDocs (Markdown via myst-parser)
- **CI/CD:** GitHub Actions → semantic-release → PyPI

## Build & Test

```bash
# Install dependencies
./build.sh --install

# Full build (pre-commit + tests + docs)
./build.sh

# Run tests only
uv run pytest

# Run specific test markers
uv run pytest -m unit
uv run pytest -m integration
```

On Windows: `.\build.ps1`

## Code Conventions

- **Style:** ruff with line-length 220, target Python 3.10
- **Type checking:** mypy strict (`disallow_untyped_defs`, `disallow_any_generics`)
- **Formatting:** 4-space indentation, UTF-8, LF line endings (`.editorconfig`)
- **Imports:** isort via ruff (first-party: `hammocking`, `tests`)
- **Types:** Use Python 3.10+ union syntax (`str | None`, not `Optional[str]`)
- **Config objects:** Dataclasses with `DataClassDictMixin` from mashumaro
- **Paths:** Always use `pathlib.Path`, never string paths
- **Logging:** Standard `logging` module, no print statements
- **Naming:** PascalCase classes, snake_case functions/methods
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) — enforced by commitlint and commitizen

## Testing Guidelines

- Tests live in `tests/` with fixtures in `tests/data/`
- Unit tests: Test classes/functions directly using libclang's in-memory parsing (`clang_parse()` helper)
- Integration tests: Full CMake build cycles in `tests/data/mini_c_test/`
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`
- Integration tests require clang/llvm, cmake, ninja-build installed
- Test output goes to `out/test-report.xml` (JUnit format)

## CI Pipeline

1. **Lint** — pre-commit hooks + commitlint (conventional commits)
2. **Test on Windows** — `build.ps1` on windows-latest
3. **Test on Linux** — `build.sh` on ubuntu-24.04 with Python 3.13
4. **Release** — python-semantic-release to PyPI (develop branch only)

## Common Patterns

- The tool accepts symbols either directly (`--symbols`) or by extracting them from a partially-linked object (`--plink`)
- Templates use Jinja2 with `Function` and `Variable` objects exposed to the template context
- Configuration merges CLI args → INI file → defaults, with OS-specific INI sections (`[hammocking.darwin]`, `[hammocking.linux]`, `[hammocking.win32]`)
- libclang AST traversal skips function bodies and dives into `extern "C"` blocks

## Important Notes

- The main branch is `develop` (not `main`)
- Pre-Alpha status (v0.9.0) — API may change
- Cross-platform: Windows, Linux, macOS (with OS-specific clang/nm paths)
- `exclude_paths` filters prevent mocking system headers
- When adding new mock output styles, create a new template directory under `templates/` with `.j2` files
