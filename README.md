# Hammocking

<p align="center">
  <a href="https://github.com/avengineers/hammocking/actions/workflows/ci.yml?query=branch%3Adevelop">
    <img src="https://img.shields.io/github/actions/workflow/status/avengineers/hammocking/ci.yml?branch=develop&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://spl-core.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/spl-core.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
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
  <a href="https://pypi.org/project/spl-core/">
    <img src="https://img.shields.io/pypi/v/spl-core.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/spl-core.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/spl-core.svg?style=flat-square" alt="License">
</p>

Automatic mocking tool for C

## Installation and Building

### On Windows

#### Install Dependencies
```powershell
.\build.ps1 -install
```

#### Build
```powershell
.\build.ps1
```

### On Linux/macOS

#### Quick Start
```bash

# Using build script
./build.sh          # Normal build
./build.sh --clean  # Clean build
./build.sh --install # Install only
```

#### Prerequisites
- Python 3.10+ (Python 3.13 recommended)
- uv (will be auto-installed)
- For running integration tests: clang/llvm, cmake, ninja-build

#### What the Build Does
-   Pre-Commit checks and linting
-   Execution of all tests
-   Building documentation

### Using DevPod (Containerized Development)

You can use [DevPod](https://devpod.sh/) to spin up a fully configured development container.

#### Prerequisites
- [Podman](https://podman.io/) or [Docker](https://www.docker.com/) installed

#### Setup
```bash
# Install DevPod CLI
curl -L -o devpod "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64" \
    && sudo install -c -m 0755 devpod /usr/local/bin \
    && rm -f devpod

# Add and select the Docker provider (use Podman or Docker)
devpod provider add docker --option DOCKER_PATH=$(which podman)
devpod provider use docker

# Start the development container
devpod up .
```

The container comes pre-configured with Python 3.13, uv, clang/llvm, cmake, and ninja-build.
