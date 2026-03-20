#!/usr/bin/env bash

#
# Build script for hammocking project on Linux/macOS
# This is the equivalent of build.ps1 for Unix-like systems
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
readonly BLUE='\033[0;34m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
CLEAN=false
INSTALL_ONLY=false

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build and test the hammocking project

OPTIONS:
    -c, --clean         Clean build (remove all build artifacts)
    -i, --install       Only install dependencies, don't build
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Normal build
    $0 --clean          # Clean build
    $0 --install        # Install dependencies only
EOF
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -i|--install)
            INSTALL_ONLY=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$SCRIPT_DIR"
log_info "Running in: $(pwd)"

# Check if poetry is installed
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        log_warn "Poetry not found. Installing..."
        curl -sSL https://install.python-poetry.org | python3 -

        # Add poetry to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        if ! command -v poetry &> /dev/null; then
            log_error "Failed to install poetry"
            log_info "Please install poetry manually: https://python-poetry.org/docs/#installation"
            exit 1
        fi
        log_success "Poetry installed successfully"
    else
        log_info "Poetry found: $(poetry --version)"
    fi
}

# Clean build artifacts
clean_build() {
    log_info "Cleaning build artifacts..."

    if [ -d ".venv" ]; then
        log_info "Removing virtual environment..."
        rm -rf .venv
    fi

    if [ -d ".bootstrap" ]; then
        log_info "Removing bootstrap directory..."
        rm -rf .bootstrap
    fi

    if [ -d "build" ]; then
        rm -rf build
    fi

    if [ -d "out" ]; then
        rm -rf out
    fi

    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

    log_success "Cleanup completed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    check_poetry

    # Install dependencies with poetry
    poetry install

    log_success "Dependencies installed"
}

# Run pre-commit checks
run_precommit() {
    log_info "Running pre-commit checks..."
    poetry run pre-commit run --all-files || {
        log_warn "Some pre-commit checks failed"
        return 1
    }
    log_success "Pre-commit checks passed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    poetry run pytest --verbose --capture=tee-sys
    log_success "Tests passed"
}

# Build documentation
build_docs() {
    log_info "Building documentation..."
    mkdir -p out/docs/html
    poetry run sphinx-build docs out/docs/html
    log_success "Documentation built: out/docs/html/index.html"
}

# Main build function
main() {
    log_info "Starting build process..."
    echo ""

    # Clean if requested
    if [ "$CLEAN" = true ]; then
        clean_build
        echo ""
    fi

    # Install dependencies
    install_dependencies
    echo ""

    # If install only, exit here
    if [ "$INSTALL_ONLY" = true ]; then
        log_success "Installation completed"
        exit 0
    fi

    # Run build pipeline
    local failed=0

    # Pre-commit checks
    if ! run_precommit; then
        failed=$((failed + 1))
        log_error "Pre-commit checks failed"
    fi
    echo ""

    # Tests
    if ! run_tests; then
        failed=$((failed + 1))
        log_error "Tests failed"
    fi
    echo ""

    # Documentation
    if ! build_docs; then
        failed=$((failed + 1))
        log_error "Documentation build failed"
    fi
    echo ""

    # Final status
    if [ $failed -eq 0 ]; then
        log_success "===================================="
        log_success "Build completed successfully! 🎉"
        log_success "===================================="
        exit 0
    else
        log_error "===================================="
        log_error "Build completed with $failed error(s)"
        log_error "===================================="
        exit 1
    fi
}

# Run main function
main
