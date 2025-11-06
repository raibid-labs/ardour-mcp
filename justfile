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

# ============================================================================
# Version Management & Release Commands
# ============================================================================

# Display current version from git tags
version:
    #!/usr/bin/env bash
    set -euo pipefail

    # Get the latest tag
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")

    # Get commit count since tag
    COMMIT_COUNT=$(git rev-list ${LATEST_TAG}..HEAD --count 2>/dev/null || echo "0")

    # Get current commit hash
    COMMIT_HASH=$(git rev-parse --short HEAD)

    if [ "$COMMIT_COUNT" -eq 0 ]; then
        echo "Current version: ${LATEST_TAG}"
    else
        echo "Current version: ${LATEST_TAG}+${COMMIT_COUNT}.${COMMIT_HASH} (unreleased)"
    fi

    echo ""
    echo "Git tags:"
    git tag -l | sort -V || echo "  (no tags yet)"

# Show what would be released (dry-run)
release-status:
    #!/usr/bin/env bash
    set -euo pipefail

    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    COMMIT_COUNT=$(git rev-list ${LATEST_TAG}..HEAD --count 2>/dev/null || echo "0")

    echo "=== Release Status ==="
    echo ""
    echo "Current version: ${LATEST_TAG}"
    echo "Commits since last release: ${COMMIT_COUNT}"
    echo ""

    if [ "$COMMIT_COUNT" -eq 0 ]; then
        echo "No new commits to release."
        exit 0
    fi

    echo "Commits since ${LATEST_TAG}:"
    echo ""
    git log ${LATEST_TAG}..HEAD --oneline --pretty=format:'  %h %s'
    echo ""
    echo ""

    # Calculate next versions
    NEXT_PATCH=$(just _next-patch-version)
    NEXT_MINOR=$(just _next-minor-version)
    NEXT_MAJOR=$(just _next-major-version)

    echo "Suggested version bumps:"
    echo "  Patch release (bug fixes):      ${NEXT_PATCH}"
    echo "  Minor release (new features):   ${NEXT_MINOR}"
    echo "  Major release (breaking):       ${NEXT_MAJOR}"
    echo ""

    # Analyze commits for suggestions
    if git log ${LATEST_TAG}..HEAD --oneline | grep -q "^[a-f0-9]\+ feat"; then
        echo "Recommended: MINOR release (contains new features)"
    elif git log ${LATEST_TAG}..HEAD --oneline | grep -q "^[a-f0-9]\+ fix"; then
        echo "Recommended: PATCH release (contains bug fixes)"
    else
        echo "Recommended: PATCH release (contains changes)"
    fi

    # Check for breaking changes
    if git log ${LATEST_TAG}..HEAD --grep="BREAKING CHANGE" --oneline | grep -q .; then
        echo ""
        echo "⚠️  WARNING: Breaking changes detected! Consider MAJOR release."
    fi

# Install git-cliff for changelog generation (optional - uses cargo)
install-git-cliff:
    #!/usr/bin/env bash
    if ! command -v git-cliff &> /dev/null; then
        echo "git-cliff not found. Installing via cargo..."
        if command -v cargo &> /dev/null; then
            cargo install git-cliff
            echo "✅ git-cliff installed successfully"
        else
            echo "❌ cargo not found. Please install Rust toolchain:"
            echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
            echo ""
            echo "Alternatively, update CHANGELOG.md manually."
            exit 1
        fi
    else
        echo "✅ git-cliff is already installed"
    fi

# Generate/update CHANGELOG.md (requires git-cliff)
changelog:
    #!/usr/bin/env bash
    if command -v git-cliff &> /dev/null; then
        echo "Generating CHANGELOG.md..."
        git-cliff -o CHANGELOG.md
        echo "✅ CHANGELOG.md updated"
    else
        echo "⚠️  git-cliff not found. Skipping changelog generation."
        echo "Install git-cliff with: just install-git-cliff"
        echo "Or update CHANGELOG.md manually."
    fi

# Check if git working directory is clean
_check-clean:
    #!/usr/bin/env bash
    if [ -n "$(git status --porcelain)" ]; then
        echo "❌ Error: Git working directory is not clean"
        echo ""
        echo "Please commit or stash your changes before creating a release:"
        git status --short
        exit 1
    fi

# Calculate next patch version (e.g., 0.1.0 -> 0.1.1)
_next-patch-version:
    #!/usr/bin/env bash
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    VERSION=${LATEST_TAG#v}
    IFS='.' read -r major minor patch <<< "$VERSION"
    patch=$((patch + 1))
    echo "v$major.$minor.$patch"

# Calculate next minor version (e.g., 0.1.0 -> 0.2.0)
_next-minor-version:
    #!/usr/bin/env bash
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    VERSION=${LATEST_TAG#v}
    IFS='.' read -r major minor patch <<< "$VERSION"
    minor=$((minor + 1))
    echo "v$major.$minor.0"

# Calculate next major version (e.g., 0.1.0 -> 1.0.0)
_next-major-version:
    #!/usr/bin/env bash
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    VERSION=${LATEST_TAG#v}
    IFS='.' read -r major minor patch <<< "$VERSION"
    major=$((major + 1))
    echo "v$major.0.0"

# ============================================================================
# Manual Release Commands (create tag locally, manual push)
# ============================================================================

# Create patch release tag locally (0.1.0 -> 0.1.1)
release-patch: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-patch-version)

    echo "Creating patch release: $NEXT_VERSION"
    echo ""

    # Try to update changelog if git-cliff is available
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION" || echo "No changelog changes to commit"
    else
        echo "⚠️  git-cliff not found. Please update CHANGELOG.md manually."
        echo "Press Enter to continue or Ctrl+C to abort..."
        read
    fi

    # Create annotated tag
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "✅ Tag $NEXT_VERSION created locally"
    echo ""
    echo "To push the release to GitHub (triggers release workflow):"
    echo "  git push origin main --tags"
    echo ""
    echo "Or to push just this tag:"
    echo "  git push origin $NEXT_VERSION"

# Create minor release tag locally (0.1.0 -> 0.2.0)
release-minor: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-minor-version)

    echo "Creating minor release: $NEXT_VERSION"
    echo ""

    # Try to update changelog if git-cliff is available
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION" || echo "No changelog changes to commit"
    else
        echo "⚠️  git-cliff not found. Please update CHANGELOG.md manually."
        echo "Press Enter to continue or Ctrl+C to abort..."
        read
    fi

    # Create annotated tag
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "✅ Tag $NEXT_VERSION created locally"
    echo ""
    echo "To push the release to GitHub (triggers release workflow):"
    echo "  git push origin main --tags"
    echo ""
    echo "Or to push just this tag:"
    echo "  git push origin $NEXT_VERSION"

# Create major release tag locally (0.1.0 -> 1.0.0)
release-major: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-major-version)

    echo "⚠️  Creating MAJOR release: $NEXT_VERSION"
    echo "This indicates breaking changes!"
    echo ""
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi

    # Try to update changelog if git-cliff is available
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION" || echo "No changelog changes to commit"
    else
        echo "⚠️  git-cliff not found. Please update CHANGELOG.md manually."
        echo "Press Enter to continue or Ctrl+C to abort..."
        read
    fi

    # Create annotated tag
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "✅ Tag $NEXT_VERSION created locally"
    echo ""
    echo "To push the release to GitHub (triggers release workflow):"
    echo "  git push origin main --tags"
    echo ""
    echo "Or to push just this tag:"
    echo "  git push origin $NEXT_VERSION"

# ============================================================================
# Automated Release Commands (test + tag + push in one step)
# ============================================================================

# Fully automated patch release (test + tag + push)
release-auto-patch: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-patch-version)

    echo "=== Automated Patch Release: $NEXT_VERSION ==="
    echo ""
    echo "This will:"
    echo "  1. Run all tests and checks"
    echo "  2. Update CHANGELOG.md"
    echo "  3. Commit changelog"
    echo "  4. Create git tag"
    echo "  5. Push tag to GitHub"
    echo ""
    read -p "Continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi

    echo ""
    echo "Step 1/5: Running tests and checks..."
    just check

    echo ""
    echo "Step 2/5: Updating changelog..."
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
    else
        echo "⚠️  git-cliff not found. Skipping changelog."
    fi

    echo ""
    echo "Step 3/5: Committing changelog..."
    if [ -n "$(git status --porcelain CHANGELOG.md 2>/dev/null)" ]; then
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION"
    else
        echo "No changelog changes to commit"
    fi

    echo ""
    echo "Step 4/5: Creating tag..."
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "Step 5/5: Pushing to GitHub..."
    git push origin main
    git push origin "$NEXT_VERSION"

    echo ""
    echo "✅ Release $NEXT_VERSION complete!"
    echo ""
    echo "GitHub Actions will now:"
    echo "  - Build packages"
    echo "  - Create GitHub release"
    echo "  - Upload artifacts"
    echo ""
    echo "View release at: https://github.com/raibid-labs/ardour-mcp/releases/tag/$NEXT_VERSION"

# Fully automated minor release (test + tag + push)
release-auto-minor: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-minor-version)

    echo "=== Automated Minor Release: $NEXT_VERSION ==="
    echo ""
    echo "This will:"
    echo "  1. Run all tests and checks"
    echo "  2. Update CHANGELOG.md"
    echo "  3. Commit changelog"
    echo "  4. Create git tag"
    echo "  5. Push tag to GitHub"
    echo ""
    read -p "Continue? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi

    echo ""
    echo "Step 1/5: Running tests and checks..."
    just check

    echo ""
    echo "Step 2/5: Updating changelog..."
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
    else
        echo "⚠️  git-cliff not found. Skipping changelog."
    fi

    echo ""
    echo "Step 3/5: Committing changelog..."
    if [ -n "$(git status --porcelain CHANGELOG.md 2>/dev/null)" ]; then
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION"
    else
        echo "No changelog changes to commit"
    fi

    echo ""
    echo "Step 4/5: Creating tag..."
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "Step 5/5: Pushing to GitHub..."
    git push origin main
    git push origin "$NEXT_VERSION"

    echo ""
    echo "✅ Release $NEXT_VERSION complete!"
    echo ""
    echo "GitHub Actions will now:"
    echo "  - Build packages"
    echo "  - Create GitHub release"
    echo "  - Upload artifacts"
    echo ""
    echo "View release at: https://github.com/raibid-labs/ardour-mcp/releases/tag/$NEXT_VERSION"

# Fully automated major release (test + tag + push)
release-auto-major: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    NEXT_VERSION=$(just _next-major-version)

    echo "=== Automated Major Release: $NEXT_VERSION ==="
    echo "⚠️  This indicates BREAKING CHANGES!"
    echo ""
    echo "This will:"
    echo "  1. Run all tests and checks"
    echo "  2. Update CHANGELOG.md"
    echo "  3. Commit changelog"
    echo "  4. Create git tag"
    echo "  5. Push tag to GitHub"
    echo ""
    read -p "Are you absolutely sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi

    echo ""
    echo "Step 1/5: Running tests and checks..."
    just check

    echo ""
    echo "Step 2/5: Updating changelog..."
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
    else
        echo "⚠️  git-cliff not found. Skipping changelog."
    fi

    echo ""
    echo "Step 3/5: Committing changelog..."
    if [ -n "$(git status --porcelain CHANGELOG.md 2>/dev/null)" ]; then
        git add CHANGELOG.md
        git commit -m "chore(release): prepare for $NEXT_VERSION"
    else
        echo "No changelog changes to commit"
    fi

    echo ""
    echo "Step 4/5: Creating tag..."
    git tag -a "$NEXT_VERSION" -m "Release $NEXT_VERSION"

    echo ""
    echo "Step 5/5: Pushing to GitHub..."
    git push origin main
    git push origin "$NEXT_VERSION"

    echo ""
    echo "✅ Release $NEXT_VERSION complete!"
    echo ""
    echo "GitHub Actions will now:"
    echo "  - Build packages"
    echo "  - Create GitHub release"
    echo "  - Upload artifacts"
    echo ""
    echo "View release at: https://github.com/raibid-labs/ardour-mcp/releases/tag/$NEXT_VERSION"

# ============================================================================
# Pre-release Commands
# ============================================================================

# Create a pre-release (alpha, beta, rc)
pre-release TYPE SUFFIX: check _check-clean
    #!/usr/bin/env bash
    set -euo pipefail

    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    VERSION=${LATEST_TAG#v}

    # Determine next version based on TYPE
    case "{{TYPE}}" in
        patch)
            IFS='.' read -r major minor patch <<< "$VERSION"
            patch=$((patch + 1))
            NEXT_VERSION="v$major.$minor.$patch-{{SUFFIX}}"
            ;;
        minor)
            IFS='.' read -r major minor patch <<< "$VERSION"
            minor=$((minor + 1))
            NEXT_VERSION="v$major.$minor.0-{{SUFFIX}}"
            ;;
        major)
            IFS='.' read -r major minor patch <<< "$VERSION"
            major=$((major + 1))
            NEXT_VERSION="v$major.0.0-{{SUFFIX}}"
            ;;
        *)
            echo "❌ Invalid TYPE. Use: patch, minor, or major"
            exit 1
            ;;
    esac

    echo "Creating pre-release: $NEXT_VERSION"
    echo ""

    # Update changelog if git-cliff is available
    if command -v git-cliff &> /dev/null; then
        git-cliff -o CHANGELOG.md
        if [ -n "$(git status --porcelain CHANGELOG.md 2>/dev/null)" ]; then
            git add CHANGELOG.md
            git commit -m "chore(release): prepare for $NEXT_VERSION"
        fi
    fi

    # Create annotated tag
    git tag -a "$NEXT_VERSION" -m "Pre-release $NEXT_VERSION"

    echo ""
    echo "✅ Pre-release tag $NEXT_VERSION created locally"
    echo ""
    echo "To push (triggers release workflow, will be marked as pre-release):"
    echo "  git push origin $NEXT_VERSION"

# Quick pre-release shortcuts
pre-release-alpha: (pre-release "minor" "alpha.1")
pre-release-beta: (pre-release "minor" "beta.1")
pre-release-rc: (pre-release "minor" "rc.1")
