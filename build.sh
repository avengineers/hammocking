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

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        log_warn "uv not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add uv to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        if ! command -v uv &> /dev/null; then
            log_error "Failed to install uv"
            log_info "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
            exit 1
        fi
        log_success "uv installed successfully"
    else
        log_info "uv found: $(uv --version)"
    fi
}

# Clean build artifacts
clean_build() {
    log_info "Cleaning build artifacts..."

    if [ -d ".venv" ]; then
        log_info "Removing virtual environment..."
        rm -rf .venv
    fi

    if [ -d "build" ]; then
        rm -rf build
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

    check_uv

    # Install dependencies with uv
    uv sync

    log_success "Dependencies installed"
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

    # Run pypeline (CI-agnostic pipeline runner)
    log_info "Running pypeline..."
    uv run pypeline run

    log_success "===================================="
    log_success "Build completed successfully!"
    log_success "===================================="
}

# Run main function
main
