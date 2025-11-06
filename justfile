# Ardour MCP Development & Testing Justfile
# Provides recipes for building, testing, and integrating with Ardour

# Default recipe - show available commands
default:
    @just --list

# Ardour paths
ardour_repo := "/home/beengud/raibid-labs/ardour"
ardour_build := ardour_repo + "/build"
ardour_install := "/tmp/ardour-install"
ardour_binary := ardour_install + "/usr/local/bin/ardour9"

# Install Python dependencies
install:
    uv sync --all-extras

# Run all unit tests
test:
    uv run pytest -v

# Run tests with coverage report
test-coverage:
    uv run pytest -v --cov=src/ardour_mcp --cov-report=term --cov-report=html

# Run specific test file
test-file FILE:
    uv run pytest tests/{{FILE}} -v

# Lint code with ruff
lint:
    uv run ruff check src/ tests/

# Format code with ruff
format:
    uv run ruff format src/ tests/

# Type check with mypy
typecheck:
    uv run mypy src/ardour_mcp

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Build and install Ardour (if not already built)
build-ardour:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ ! -f "{{ardour_binary}}" ]; then
        echo "Building and installing Ardour..."
        cd {{ardour_repo}}

        # Configure if not already configured
        if [ ! -f "build/build.ninja" ]; then
            python3 waf configure --optimize --no-phone-home
        fi

        # Build
        python3 waf build -j$(nproc)

        # Install to temp location
        python3 waf install --destdir={{ardour_install}}

        echo "✅ Ardour built and installed successfully"
    else
        echo "✅ Ardour already installed at {{ardour_binary}}"
    fi

# Check if Ardour is running
check-ardour:
    #!/usr/bin/env bash
    if pgrep -f "ardour-9" > /dev/null; then
        echo "✅ Ardour is running"
        exit 0
    else
        echo "❌ Ardour is not running"
        echo "Start Ardour with: just start-ardour"
        exit 1
    fi

# Start Ardour with OSC enabled
start-ardour:
    #!/usr/bin/env bash
    set -euo pipefail

    if pgrep -f "ardour-9" > /dev/null; then
        echo "⚠️  Ardour is already running"
        exit 0
    fi

    if [ ! -f "{{ardour_binary}}" ]; then
        echo "❌ Ardour not built. Building now..."
        just build-ardour
    fi

    echo "🎵 Starting Ardour with OSC enabled..."
    echo "Configure OSC in Ardour:"
    echo "  Edit → Preferences → Control Surfaces"
    echo "  Enable 'Open Sound Control (OSC)'"
    echo "  Set OSC Server Port: 3819"
    echo "  Enable all feedback options"

    # Start Ardour (wrapper script handles library paths)
    {{ardour_binary}} &

    echo "Waiting for Ardour to start..."
    sleep 5

    if pgrep -f "ardour-9" > /dev/null; then
        echo "✅ Ardour started successfully"
    else
        echo "❌ Failed to start Ardour"
        exit 1
    fi

# Stop Ardour
stop-ardour:
    #!/usr/bin/env bash
    if pgrep -f "ardour-9" > /dev/null; then
        echo "Stopping Ardour..."
        pkill -f "ardour-9"
        sleep 2
        echo "✅ Ardour stopped"
    else
        echo "ℹ️  Ardour is not running"
    fi

# Test OSC connection to Ardour
test-osc:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Testing OSC connection to Ardour..."

    # Check if Ardour is running
    if ! pgrep -f "ardour-9" > /dev/null; then
        echo "❌ Ardour is not running. Start it with: just start-ardour"
        exit 1
    fi

    # Test OSC connection with Python
    uv run python3 scripts/test_osc.py

# Run MCP server (for manual testing)
run-server:
    #!/usr/bin/env bash
    echo "Starting Ardour MCP Server..."
    echo "Connect from Claude Desktop or test with MCP Inspector"
    uv run ardour-mcp

# Integration test - full workflow
integration-test: check-ardour
    @uv run python3 scripts/integration_test.py

# Quick integration test - just connection
quick-test: check-ardour test-osc
    @echo "✅ Quick test passed - Ardour MCP is ready!"

# Full test suite - unit tests + integration
test-all: test integration-test
    @echo "✅ All tests passed!"

# Development workflow - start Ardour and run tests
dev: start-ardour
    @sleep 3
    @just integration-test

# Clean up test artifacts
clean:
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf .ruff_cache
    rm -rf src/**/__pycache__
    rm -rf tests/**/__pycache__
    find . -name "*.pyc" -delete

# Show Ardour OSC configuration instructions
show-osc-config:
    @echo "=== Ardour OSC Configuration ==="
    @echo ""
    @echo "1. Open Ardour"
    @echo "2. Go to: Edit → Preferences → Control Surfaces"
    @echo "3. Enable: 'Open Sound Control (OSC)'"
    @echo "4. Click the 'Show Protocol Settings' button"
    @echo "5. Configure:"
    @echo "   - OSC Server Port: 3819"
    @echo "   - Reply Port: 3820"
    @echo "   - Enable all feedback options:"
    @echo "     ✓ Send track/bus information"
    @echo "     ✓ Send master/monitor information"
    @echo "     ✓ Send transport information"
    @echo "     ✓ Send playhead position"
    @echo "6. Click OK to save"
    @echo ""
    @echo "Then run: just test-osc"

# Complete setup - install deps and show instructions
setup: install
    @echo ""
    @echo "=== Ardour MCP Setup Complete ==="
    @echo ""
    @echo "⚠️  Manual Step Required:"
    @echo "  You need to start Ardour manually due to library dependencies."
    @echo ""
    @echo "Option 1 - Use system Ardour (recommended):"
    @echo "  Install Ardour from your package manager, then run it."
    @echo ""
    @echo "Option 2 - Run from build:"
    @echo "  cd {{ardour_repo}}"
    @echo "  ./build/gtk2_ardour/ardour-9.0.pre0.1983"
    @echo ""
    @just show-osc-config
    @echo ""
    @echo "After Ardour is running with OSC configured:"
    @echo "  just quick-test      # Test OSC connection"
    @echo "  just integration-test # Run full integration tests"

# Restart everything
restart: stop-ardour
    @sleep 2
    @just start-ardour
    @sleep 3
    @just quick-test
