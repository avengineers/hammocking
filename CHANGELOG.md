# CHANGELOG


## v1.0.1 (2026-04-10)

### Bug Fixes

- Merge project ini over defaults
  ([`ada1c30`](https://github.com/avengineers/hammocking/commit/ada1c30cacee2d352c09a4a8ef4b38c18cc6d04d))

Project-level hammocking.ini via --config completely replaced the built-in defaults instead of
  overlaying. This caused critical settings like exclude_pattern to be lost, breaking builds with
  GCC/MinGW where runtime symbols like _pei386_runtime_relocator leaked through.

- Add HammockIni.merge() to overlay non-None values on top of defaults - HammockRunner always loads
  package defaults first, then project config - Extend default exclude_pattern with memcpy, memmove,
  memset, memcmp, bzero, strlen (compiler-generated intrinsics) - Rewrite docs/usage.md: complete
  CLI reference, config merge docs, output styles, real build examples - Add NmWrapper.mock_it()
  unit tests for symbol filtering logic

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v1.0.0 (2026-04-07)

### Documentation

- Consolidate README and LINUX_QUICKSTART into single README
  ([`b94e9a0`](https://github.com/avengineers/hammocking/commit/b94e9a04f9400c7b789509f117434eb5e0631fd1))

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

### Features

- Replace poetry and bootstrap with uv as package manager
  ([`d45bef3`](https://github.com/avengineers/hammocking/commit/d45bef3f3f196c754d651ea9699a3ec75f98e4f2))

Both build.ps1 and build.sh now follow the same call chain: OS wrapper -> uv -> pypeline, with
  pypeline.yaml as the single source of truth for pipeline steps.

- Replace poetry with uv for dependency management - Remove bootstrap in favor of direct uv/scoop
  installation - build.ps1: install scoop and uv, then `uv run pypeline run` - build.sh: install uv,
  then `uv run pypeline run` - pypeline.yaml: ScoopInstall, lint, test, docs - Add types-setuptools
  to dev dependencies

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v0.12.0 (2026-04-04)

### Features

- Update libclang to 1.18
  ([`640b4e1`](https://github.com/avengineers/hammocking/commit/640b4e169c2021567e71b9fa0b29d1dbd807a622))


## v0.11.0 (2026-03-27)

### Features

- Add ignore_symbols_outside_project option with INI/CLI support
  ([`1ee2679`](https://github.com/avengineers/hammocking/commit/1ee2679cbd3c29b288363bd62e9bbf34bbd67979))

- Add `ignore_symbols_outside_project` to HammockIni and ConfigReader - Set default to true in
  hammocking.ini (opt-out behavior) - Use None sentinel to allow INI value to override CLI default -
  Update CLI help text and usage documentation - Fix Function.__repr__: was using self.type instead
  of self.return_type - Fix HammockRunner: self.hammock not initialized to None (AttributeError) -
  Enable inline coverage report in pytest - Improve test coverage from 92% to 95%

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.10.0 (2026-03-24)

### Features

- Add devcontainer configuration for DevPod
  ([#80](https://github.com/avengineers/hammocking/pull/80),
  [`ba8c55d`](https://github.com/avengineers/hammocking/commit/ba8c55d8733e14822a8a4af97e10a29fe329c0ff))

Add .devcontainer/ with Dockerfile (Python 3.13, clang, llvm, cmake, ninja-build, Poetry) and
  devcontainer.json (VS Code extensions, GitHub CLI feature, postCreateCommand). Remove .gitpod.yml
  in favor of the devcontainer spec. Update LINUX_QUICKSTART.md with DevPod instructions.

Closes #80 Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.9.1 (2026-03-23)

### Bug Fixes

- **ci**: Gate publish steps on semantic-release output
  ([#79](https://github.com/avengineers/hammocking/pull/79),
  [`f43feca`](https://github.com/avengineers/hammocking/commit/f43fecabe338f73de8a4b3413f35e17a5e2498bf))

The PyPI and GitHub Releases publish steps ran unconditionally on develop, even when
  python-semantic-release found no releasable commits and produced no dist/ directory, causing
  FileNotFoundError.

Additionally, the released output is true even in --noop mode (dry runs on PRs), so a noop guard is
  also required.

- Use steps.release.outputs.released with noop guard - Update actions/checkout@v4 to @v6 (Node.js 20
  deprecation) - Pin release runner to ubuntu-24.04 to match test-on-linux - Remove disabled LLVM
  install step and unused publish_release var

Closes #79 Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


## v0.9.0 (2025-07-10)

### Features

- Add exclude-method
  ([`8c16402`](https://github.com/avengineers/hammocking/commit/8c16402c3e1bf93148ce696317262d3a7b42dc2c))


## v0.8.0 (2025-06-13)

### Features

- Do not mock strlen standard library function
  ([`197cffc`](https://github.com/avengineers/hammocking/commit/197cffc8dacabec83cd31194b3fb20423d9c9543))


## v0.7.0 (2025-05-21)

### Features

- Do not mock memcmp standard library function
  ([`026c210`](https://github.com/avengineers/hammocking/commit/026c210eab56e0725a9ae7760795eb5859e61541))


## v0.6.0 (2025-05-14)

### Features

- Ignore exp
  ([`f27782c`](https://github.com/avengineers/hammocking/commit/f27782c265f70995721a83ebe1c28ca2e61fbb4f))


## v0.5.1 (2025-04-09)

### Bug Fixes

- Pypi deployment with special token ([#57](https://github.com/avengineers/hammocking/pull/57),
  [`651b587`](https://github.com/avengineers/hammocking/commit/651b587d8e60b2c16aac4e678b450b67c2bf443a))


## v0.5.0 (2025-04-08)

### Features

- Ignore memcpy
  ([`e3996f6`](https://github.com/avengineers/hammocking/commit/e3996f6c8dde37b3ff59317156800c504ea6bf41))


## v0.4.1 (2025-04-08)

### Bug Fixes

- Unnecessary python dependency
  ([`9f18db9`](https://github.com/avengineers/hammocking/commit/9f18db9b4df70474ec49b4cb985dedba94f7a820))

### Features

- Handle nm errors and be more verbose
  ([`87a0704`](https://github.com/avengineers/hammocking/commit/87a07044699e0b3ebe4e92ec87423b0e9b96a7d7))
