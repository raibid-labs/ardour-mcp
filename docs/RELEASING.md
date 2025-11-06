# Release Process

This document describes the complete release workflow for Ardour MCP.

## Quick Start

Ardour MCP offers **three release workflows** to suit different needs. For a detailed comparison, see [RELEASE-WORKFLOWS.md](RELEASE-WORKFLOWS.md).

### Choose Your Workflow

```bash
# 1. Manual Release (full control, manual push)
just release-patch
git push origin v0.1.1

# 2. Semi-Automated Release (one command, auto push)
just release-auto-patch

# 3. Fully Automated (commit to main, auto PR)
git commit -m "feat: new feature"
git push origin main
```

## Overview

Ardour MCP uses:
- **Semantic Versioning (SemVer)** for version numbers
- **Conventional Commits** for changelog generation
- **Git tags** as the source of truth for versions
- **GitHub Actions** for automated releases
- **git-cliff** for changelog generation
- **Hatchling with VCS** for dynamic Python package versioning
- **Release Please** (optional) for fully automated releases

## Branching Strategy

### Current: Tags Off Main

Ardour MCP follows a **trunk-based development** model:

```
main branch (trunk)
    |
    v
  commit (fix: bug)
    |
    v
  commit (feat: feature)
    |
    v
  tag v0.2.0 ← Release here
    |
    v
  continue development
```

**Key Points:**
- All development happens on `main` branch
- Tags mark release points
- No separate release branches needed (yet)
- Simple, linear history

**When to use release branches:**
- After version 1.0.0
- When maintaining multiple major versions
- Example: `v1.x-maint`, `v2.x-maint` branches
- Not needed for pre-1.0 development

**Benefits of this approach:**
- Simple workflow
- Easy to understand
- Fast releases
- Perfect for rapid development
- No branch management overhead

## Version Numbering

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (x.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.x.0): New features, backward-compatible
- **PATCH** (0.0.x): Bug fixes, backward-compatible

Examples:
- `v0.1.0` -> `v0.1.1`: Patch release (bug fixes)
- `v0.1.0` -> `v0.2.0`: Minor release (new features)
- `v0.1.0` -> `v1.0.0`: Major release (breaking changes)

### Pre-release Versions

For pre-releases, append a suffix:
- `v0.1.0-alpha.1`: Alpha release
- `v0.1.0-beta.1`: Beta release
- `v0.1.0-rc.1`: Release candidate

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature (triggers MINOR version bump)
- `fix`: Bug fix (triggers PATCH version bump)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Breaking Changes

For breaking changes, add `!` after type or `BREAKING CHANGE:` in footer:

```
feat!: remove deprecated OSC methods

BREAKING CHANGE: Removed legacy OSC methods. Use new API instead.
```

This triggers a MAJOR version bump.

## Release Workflows

### Workflow 1: Manual Release (Recommended for Learning)

**Best for:** Careful releases, learning process, critical changes

```bash
# Check what would be released
just release-status

# Run tests
just check

# Create tag locally (choose one)
just release-patch   # 0.1.0 -> 0.1.1
just release-minor   # 0.1.0 -> 0.2.0
just release-major   # 0.1.0 -> 1.0.0

# Manually push when ready
git push origin v0.1.1
```

**What happens:**
1. Checks working directory is clean
2. Runs tests (via `check` dependency)
3. Generates CHANGELOG.md
4. Commits changelog
5. Creates git tag
6. **Waits for manual push** (safety measure)

**Pros:** Full control, time to review, explicit confirmation
**Cons:** More steps, slower, must remember to push

### Workflow 2: Semi-Automated Release (Recommended for Regular Use)

**Best for:** Quick releases, regular development, trusted environment

```bash
# One command does everything
just release-auto-patch   # Automated patch
just release-auto-minor   # Automated minor
just release-auto-major   # Automated major
```

**What happens:**
1. Checks working directory is clean
2. **Automatically runs all tests**
3. Updates CHANGELOG.md
4. Commits changelog
5. Creates git tag
6. **Automatically pushes to GitHub**
7. Shows release URL

**Pros:** Fast, consistent, tests always run, single command
**Cons:** Less time to review, auto-pushes immediately

### Workflow 3: Fully Automated Release (Recommended for Teams)

**Best for:** Team collaboration, PR workflows, maximum automation

```bash
# Just commit with conventional commits
git commit -m "feat(mixer): add channel strip"
git push origin main
```

**What happens:**
1. Release Please analyzes commits
2. Determines version bump automatically
3. Opens a "Release PR" with:
   - Updated CHANGELOG.md
   - Proposed version
   - All changes
4. When Release PR merged:
   - Creates tag
   - Creates GitHub release
   - Builds packages
   - Uploads artifacts

**Pros:** Zero manual work, perfect for teams, PR-based review
**Cons:** Extra PR step, requires workflow discipline

**See [RELEASE-WORKFLOWS.md](RELEASE-WORKFLOWS.md) for detailed comparison.**

## Quick Reference

### Check Current Version

```bash
just version
```

Shows:
- Current version from latest git tag
- Number of commits since last release
- Current commit hash

### Check Release Status (Dry-run)

```bash
just release-status
```

Shows:
- Current version
- Commits since last release
- Suggested version bumps
- Breaking change warnings

### Pre-releases

```bash
# Quick shortcuts
just pre-release-alpha    # Creates v0.2.0-alpha.1
just pre-release-beta     # Creates v0.2.0-beta.1
just pre-release-rc       # Creates v0.2.0-rc.1

# Custom pre-release
just pre-release minor alpha.2
just pre-release patch beta.3
```

Pre-releases are automatically marked on GitHub.

## Detailed Workflows

### Manual Release Workflow

**Step 1: Prepare**

```bash
# Ensure all changes are committed
git status

# Run full test suite
just check

# Check what would be released
just release-status
```

**Step 2: Generate Changelog (Optional)**

```bash
# Manual changelog generation
just changelog

# Review changes
cat CHANGELOG.md
```

**Step 3: Create Release Tag**

```bash
# For bug fixes only
just release-patch

# For new features (backward-compatible)
just release-minor

# For breaking changes (requires confirmation)
just release-major
```

**Step 4: Review Before Pushing**

```bash
# View the tag
git show v0.1.1

# View recent commits
git log --oneline -10

# Check what will be pushed
git push origin main --dry-run --tags
```

**Step 5: Push Release**

```bash
# Push the specific tag (triggers GitHub Actions)
git push origin v0.1.1

# Or push everything
git push origin main --tags
```

**Step 6: Monitor**

1. Go to: https://github.com/raibid-labs/ardour-mcp/actions
2. Watch the "Release" workflow
3. Verify release at: https://github.com/raibid-labs/ardour-mcp/releases

### Semi-Automated Release Workflow

**One Command Release:**

```bash
just release-auto-patch
```

**Interactive Confirmation:**
```
=== Automated Patch Release: v0.1.1 ===

This will:
  1. Run all tests and checks
  2. Update CHANGELOG.md
  3. Commit changelog
  4. Create git tag
  5. Push tag to GitHub

Continue? (yes/no):
```

**Progress Output:**
```
Step 1/5: Running tests and checks...
✅ All tests passed

Step 2/5: Updating changelog...
✅ CHANGELOG.md updated

Step 3/5: Committing changelog...
✅ Changelog committed

Step 4/5: Creating tag...
✅ Tag v0.1.1 created

Step 5/5: Pushing to GitHub...
✅ Pushed to GitHub

✅ Release v0.1.1 complete!

View release at: https://github.com/raibid-labs/ardour-mcp/releases/tag/v0.1.1
```

### Fully Automated Release Workflow (Release Please)

**Step 1: Make Changes**

```bash
# Commit with conventional commits
git commit -m "feat(tracks): add track grouping"
git commit -m "fix(osc): resolve timeout issue"
git push origin main
```

**Step 2: Review Release PR**

Release Please automatically creates a PR titled: `chore(main): release 0.2.0`

The PR includes:
- Updated CHANGELOG.md
- Version bump in manifest
- All commits since last release

**Step 3: Merge Release PR**

When you merge the Release PR:
- Tag `v0.2.0` is created automatically
- GitHub release is created
- Packages are built and uploaded
- Artifacts are attached to release

**No manual steps required!**

## GitHub Actions Workflows

### Workflow 1: Manual Tag-Based Release

**File:** `.github/workflows/release.yml`

**Trigger:** Push of version tags (v*.*.*)

**Steps:**
1. Checkout code with full history
2. Setup Python 3.10 and uv
3. Install git-cliff
4. Extract version from tag
5. Generate release notes
6. Create GitHub Release
7. Build packages
8. Upload artifacts

**Used by:** Manual and Semi-Auto workflows

### Workflow 2: Semantic Release (Release Please)

**File:** `.github/workflows/semantic-release.yml`

**Trigger:** Push to main branch

**Steps:**
1. Analyze commits since last release
2. Determine version bump
3. Create/update Release PR
4. On merge: create tag and release
5. Run tests
6. Build packages
7. Upload artifacts

**Used by:** Full Auto workflow

**Both workflows can coexist!**

## Changelog Management

### Automatic Generation

The changelog is generated from commit messages using `git-cliff`.

**Configuration:** `cliff.toml`

**Manual generation:**
```bash
just changelog
```

### Manual Editing

After generation, you can manually edit `CHANGELOG.md` to:
- Add context or explanations
- Group related changes
- Highlight important updates
- Add migration guides

Always regenerate before each release to capture all changes.

## Version Access in Code

The version is automatically available in Python:

```python
from ardour_mcp import __version__

print(__version__)  # e.g., "0.1.0"
```

The version is derived from git tags using `hatchling-vcs`.

### Development Versions

Between releases, the version includes development info:

- With tag: `0.1.0`
- After 5 commits: `0.1.0.post5.dev0+abc1234`

## Configuration Files

### For All Workflows
- `justfile` - Release commands
- `cliff.toml` - Changelog config
- `.github/workflows/release.yml` - Tag-based releases

### For Full Auto Workflow
- `release-please-config.json` - Release Please settings
- `.release-please-manifest.json` - Current version
- `.github/workflows/semantic-release.yml` - Automated releases

## Best Practices

### Before Any Release

- [ ] All tests passing (`just check`)
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Migration guide provided (if needed)
- [ ] Dependencies up to date
- [ ] Security vulnerabilities addressed

### Commit Messages

- [ ] Use conventional commit format
- [ ] Clear, descriptive messages
- [ ] Reference issues when applicable
- [ ] Mark breaking changes explicitly

### Release Frequency

- **Patch**: As needed for bug fixes (weekly/bi-weekly)
- **Minor**: Every 2-4 weeks for new features
- **Major**: When significant breaking changes accumulate

### Communication

After release:
- Update project README if needed
- Announce in discussions/issues
- Update documentation sites
- Notify users of breaking changes

## Troubleshooting

### Version not detected

If `just version` shows `v0.0.0`:

```bash
# Check for tags
git tag -l

# If no tags exist, create initial tag
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

### Release workflow fails

Common issues:

1. **No commits since last tag**: This is OK, release notes will be empty
2. **Duplicate tag**: Delete and recreate:
   ```bash
   git tag -d v0.1.0
   git push origin :refs/tags/v0.1.0
   just release-patch
   ```
3. **Tests fail**: Fix issues and try again

### Changelog incomplete

If commits are missing from changelog:

1. Check commit message format (must follow conventional commits)
2. Regenerate: `just changelog`
3. Check git-cliff config: `cliff.toml`

### Forgot to push tag (Manual workflow)

```bash
# Find unpushed tags
git log --tags --oneline

# Push the tag
git push origin v0.1.1
```

### Need to rollback release

```bash
# Delete local tag
git tag -d v0.1.1

# Delete remote tag (if pushed)
git push origin :refs/tags/v0.1.1

# Delete GitHub release (manual via web UI)
# Then recreate if needed
```

## Examples

### Example 1: Patch Release (Semi-Auto)

```bash
# Fix bugs
git commit -m "fix(osc): resolve connection timeout"
git commit -m "fix(transport): correct playhead calculation"

# Quick release
just release-auto-patch

# Automatically:
# - Runs tests
# - Updates changelog
# - Creates tag v0.1.1
# - Pushes to GitHub
# - Creates release
```

### Example 2: Minor Release (Manual)

```bash
# Add features
git commit -m "feat(mixer): add channel strip controls"
git commit -m "feat(tracks): implement track grouping"

# Check what would be released
just release-status

# Run tests
just check

# Create tag
just release-minor

# Review before pushing
git show v0.2.0

# Push when ready
git push origin v0.2.0
```

### Example 3: Team Release (Full Auto)

```bash
# Developer commits
git commit -m "feat(effects): add reverb control"
git push origin main

# Release Please automatically:
# - Opens Release PR
# - Shows proposed v0.2.0
# - Lists all changes

# Maintainer reviews Release PR
# Merges PR

# Automatically:
# - Creates tag v0.2.0
# - Creates GitHub release
# - Builds packages
```

### Example 4: Pre-release

```bash
# Test upcoming features
just pre-release-beta

# Push pre-release
git push origin v0.2.0-beta.1

# Users test beta version

# If good, create official release
just release-minor
git push origin v0.2.0
```

## Migration Path

### Phase 1: Learning (Current)
Use **Manual** workflow:
- `just release-patch`
- Manual push
- Full control

### Phase 2: Regular Development
Add **Semi-Auto** workflow:
- `just release-auto-patch`
- Faster releases
- Tests enforced

### Phase 3: Team Collaboration
Enable **Full Auto** workflow:
- Push to main
- Release PRs
- Zero manual work

**All three can coexist - use what fits your situation!**

## Future Enhancements

### PyPI Publishing (Planned)

The release workflows include commented-out PyPI publishing.

To enable:

1. Create PyPI account and API token
2. Add token to GitHub Secrets: `PYPI_API_TOKEN`
3. Uncomment PyPI publish step in workflows
4. Test with TestPyPI first

### Automated Testing in Release PRs

Future enhancement: Add more comprehensive testing to Release PRs.

## References

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [git-cliff Documentation](https://git-cliff.org/)
- [Hatchling VCS](https://github.com/ofek/hatch-vcs)
- [Release Please](https://github.com/googleapis/release-please)
- [Workflow Comparison](RELEASE-WORKFLOWS.md)

## Support

For questions or issues with the release process:
- Open an issue: https://github.com/raibid-labs/ardour-mcp/issues
- Discussion: https://github.com/raibid-labs/ardour-mcp/discussions
