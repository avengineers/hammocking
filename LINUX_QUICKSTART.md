# Linux Quickstart Guide

This guide helps you get started with **hammocking** on Linux.

## DevPod / Dev Container (Recommended)

The fastest way to get a fully configured development environment is via [DevPod](https://devpod.sh/) or any [devcontainer](https://containers.dev/)-compatible tool (VS Code Dev Containers, GitHub Codespaces):

```bash
# Using DevPod CLI
devpod up https://github.com/avengineers/hammocking

# Or open in VS Code with the Dev Containers extension
# 1. Clone the repo
# 2. Open in VS Code
# 3. "Reopen in Container" when prompted
```

This sets up Python 3.13, uv, clang, llvm, cmake, and ninja-build automatically.

## Manual Setup

### Prerequisites

### Required
- Python 3.10 or higher (3.13 recommended)
- Git

### Optional (for integration tests)
- clang/llvm
- ninja-build

### Installing Prerequisites on Ubuntu/Debian

```bash
# Install Python 3.13
sudo apt update
sudo apt install python3.13 python3.13-venv python3-pip

# Optional: Install build tools for integration tests
sudo apt install clang ninja-build llvm
```

## Installation

### Using the build script

```bash
# Clone the repository
git clone https://github.com/avengineers/hammocking
cd hammocking

# Install dependencies
./build.sh --install

# Run full build (includes lint, test, docs)
./build.sh
```

## Common Tasks

The common tasks are separated as functions within `./build.sh`.

## Setup Development Environment

```bash
# Complete setup with pre-commit hooks
./build.sh --setup

# Or manually
uv sync
uv run pre-commit install
```

## build.sh Targets Reference

Run `./build.sh --help` to see all available targets.

## Troubleshooting

### uv Not Found
If `uv` command is not found after installation:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Python Version Issues
Check your Python version:
```bash
python3 --version
```

### Integration Test Failures
If integration tests fail due to missing clang:
```bash
# Skip integration tests
uv run pytest -v -m "not integration"

# Or install clang
sudo apt install clang
```

### Lock File Issues
If you see lock file errors:
```bash
uv lock
uv sync
```

## Getting Help

- Documentation: Built docs at `build/docs/html/index.html` after running `./build.sh`
- Issues: https://github.com/avengineers/hammocking/issues
- Main command help: `uv run python -m hammocking --help`

## Next Steps

1. Read the full documentation: `./build.sh && firefox build/docs/html/index.html`
2. Explore the examples in `docs/usage/examples/`
3. Check out the test files in `tests/` to see how to use the API
