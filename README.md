# Hammocking

<p align="center">
  <a href="https://github.com/avengineers/hammocking/actions/workflows/ci.yml?query=branch%3Adevelop">
    <img src="https://img.shields.io/github/actions/workflow/status/avengineers/hammocking/ci.yml?branch=develop&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://hammocking.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/hammocking.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/avengineers/hammocking">
    <img src="https://img.shields.io/codecov/c/github/avengineers/hammocking.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://docs.astral.sh/uv/">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/hammocking/">
    <img src="https://img.shields.io/pypi/v/hammocking.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/hammocking.svg?style=flat-square&logo=python&logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/hammocking.svg?style=flat-square" alt="License">
</p>

Automatic mocking tool for C.

## Installation

Install from PyPI:

```bash
pip install hammocking
```

Or with uv:

```bash
uv add hammocking
```

Hammocking depends on Jinja2 and libclang. They are installed automatically.

## Development

### DevPod / Dev Container (recommended)

The fastest way to get a working development environment is [DevPod](https://devpod.sh/) or any [devcontainer](https://containers.dev/)-compatible tool (VS Code Dev Containers, GitHub Codespaces).

```bash
# Using DevPod CLI
devpod up https://github.com/avengineers/hammocking

# Or in VS Code: clone the repo, open it, and select "Reopen in Container"
```

The container comes with Python 3.13, uv, clang, llvm, cmake, and ninja-build.

### Linux / macOS

#### Prerequisites

- Python 3.10 or higher (3.13 recommended)
- Git

Optional, for integration tests:

- clang / llvm
- cmake
- ninja-build

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.13 python3.13-venv python3-pip git

# Optional: tools for integration tests
sudo apt install clang llvm cmake ninja-build
```

#### Build

```bash
./build.sh              # full build (lint, test, docs)
./build.sh --clean      # clean build
./build.sh --install    # install dependencies only
```

### Windows

#### Build

```powershell
.\build.ps1             # full build (lint, test, docs)
.\build.ps1 -clean      # clean build
.\build.ps1 -install    # install dependencies only
```

### Setting up the development environment manually

```bash
uv sync
uv run pre-commit install
```

### Running tests

```bash
uv run pytest               # all tests
uv run pytest -m unit        # unit tests only
uv run pytest -m integration # integration tests only
```

If integration tests fail because clang is not installed, skip them:

```bash
uv run pytest -m "not integration"
```

### What the build does

- Pre-commit checks and linting
- Running all tests
- Building documentation

## Troubleshooting

### uv not found

Make sure `~/.local/bin` is on your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Lock file errors

```bash
uv lock
uv sync
```

## Links

- Documentation: https://hammocking.readthedocs.io
- PyPI: https://pypi.org/project/hammocking/
- Issues: https://github.com/avengineers/hammocking/issues
