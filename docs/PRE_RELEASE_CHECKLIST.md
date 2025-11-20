# Pre-Release Checklist

Use this checklist before creating a new release of Ardour MCP to ensure everything is ready.

## Version Planning

- [ ] Determine version number (MAJOR.MINOR.PATCH following [SemVer](https://semver.org/))
  - [ ] MAJOR: Breaking changes
  - [ ] MINOR: New features (backward compatible)
  - [ ] PATCH: Bug fixes (backward compatible)
- [ ] Update version in relevant documents if needed
- [ ] Check milestone completion in GitHub

## Code Quality

- [ ] All tests pass locally (`uv run pytest`)
- [ ] Test coverage is acceptable (`uv run pytest --cov`)
- [ ] No linting errors (`uv run ruff check src/ tests/`)
- [ ] Code is properly formatted (`uv run ruff format --check src/ tests/`)
- [ ] Type checking passes (`uv run mypy src/`)
- [ ] All GitHub Actions CI checks pass on main branch

## Documentation

- [ ] README.md is up to date
  - [ ] Feature list reflects current capabilities
  - [ ] Installation instructions are current
  - [ ] Examples work as documented
  - [ ] Version numbers are correct
- [ ] CHANGELOG.md includes all changes for this release
  - [ ] Breaking changes clearly marked
  - [ ] New features listed
  - [ ] Bug fixes documented
  - [ ] Contributors credited
- [ ] All guide documents in `docs/guides/` are current
- [ ] Architecture documentation reflects any changes
- [ ] API documentation is complete for new features

## Testing

- [ ] Manual testing completed
  - [ ] Test on Ubuntu/Debian
  - [ ] Test on macOS (if available)
  - [ ] Test on Windows (if available)
- [ ] Test with different Ardour versions
  - [ ] Ardour 8.x
  - [ ] Ardour 9.x
- [ ] Test with different Python versions
  - [ ] Python 3.10
  - [ ] Python 3.11
  - [ ] Python 3.12
- [ ] Test with different MCP clients
  - [ ] Claude Desktop
  - [ ] Claude Code
- [ ] Integration tests pass
- [ ] Example workflows from docs work correctly

## Dependencies

- [ ] All dependencies are up to date and compatible
- [ ] `uv.lock` is synchronized (`uv sync`)
- [ ] No known security vulnerabilities in dependencies
- [ ] Optional dependencies work correctly (`uv sync --all-extras`)

## GitHub Repository

- [ ] All open issues for this milestone are resolved or moved
- [ ] Pull requests for this release are merged
- [ ] Branch is up to date with main
- [ ] No pending breaking changes that should be included

## Release Preparation

- [ ] Update CHANGELOG.md with final release date
- [ ] Review and update version references in:
  - [ ] README.md
  - [ ] pyproject.toml
  - [ ] Documentation
- [ ] Ensure git-cliff configuration (`cliff.toml`) is correct
- [ ] Create release notes draft

## GitHub Configuration

- [ ] PyPI trusted publishing is configured in GitHub repository settings
  - Environment: `pypi`
  - Environment protection rules configured
- [ ] GitHub Actions have necessary permissions
- [ ] Release workflow file is up to date (`.github/workflows/release.yml`)
- [ ] Publish workflow file is ready (`.github/workflows/publish.yml`)

## PyPI Configuration

- [ ] PyPI trusted publishing configured for this repository
  - Publisher: GitHub Actions
  - Workflow: `release.yml` or `publish.yml`
  - Environment: `pypi`
- [ ] Package metadata in `pyproject.toml` is complete
  - [ ] Name
  - [ ] Description
  - [ ] Keywords
  - [ ] Classifiers
  - [ ] URLs
  - [ ] License

## Communication

- [ ] Release announcement draft prepared
- [ ] Community notified of upcoming release (if major)
- [ ] Breaking changes communicated clearly
- [ ] Migration guide prepared (if breaking changes)

## Legal & Compliance

- [ ] LICENSE file is current and correct
- [ ] All code contributions have proper attribution
- [ ] No proprietary or restricted code included
- [ ] Security vulnerabilities addressed
- [ ] SECURITY.md is up to date

## Post-Release Planning

- [ ] Next milestone planned
- [ ] Issues triaged and labeled for next release
- [ ] Roadmap updated if needed

## Release Process

Once all checks are complete:

### Using Just Commands (Recommended)

1. **Check status**:
   ```bash
   just release-status
   ```

2. **Create release**:
   ```bash
   # For patch release (0.3.0 -> 0.3.1)
   just release-auto-patch

   # For minor release (0.3.0 -> 0.4.0)
   just release-auto-minor

   # For major release (0.3.0 -> 1.0.0)
   just release-auto-major
   ```

### Manual Process

1. **Create and push tag**:
   ```bash
   git tag -a v0.3.1 -m "Release v0.3.1"
   git push origin v0.3.1
   ```

2. **Monitor GitHub Actions**:
   - Watch the Release workflow complete
   - Verify GitHub Release is created with correct changelog
   - Check that artifacts are uploaded
   - Confirm PyPI publish job succeeds

3. **Verify Release**:
   - [ ] GitHub Release is published
   - [ ] PyPI package is available
   - [ ] Installation works: `pip install ardour-mcp==<version>`
   - [ ] Documentation renders correctly on GitHub

4. **Post-Release**:
   - [ ] Announce release in GitHub Discussions
   - [ ] Update any external references
   - [ ] Close the milestone
   - [ ] Create next milestone

## Rollback Plan

If something goes wrong:

1. **GitHub Release**: Can be edited or deleted
2. **PyPI Release**: Cannot be deleted (only yanked)
   - If package is broken, yank it: `pip yank ardour-mcp==<version>`
   - Release fixed version immediately
3. **Git Tag**: Can be deleted if release failed
   ```bash
   git tag -d v0.3.1
   git push origin :refs/tags/v0.3.1
   ```

## Common Issues

### PyPI Publishing Fails

- Check trusted publishing configuration in PyPI
- Verify GitHub environment name matches workflow
- Ensure workflow has `id-token: write` permission

### Tests Fail in CI but Pass Locally

- Check Python version consistency
- Verify all dependencies in `pyproject.toml`
- Check for environment-specific issues

### Build Artifacts Missing

- Verify `uv build` completes successfully
- Check GitHub Actions artifact upload step
- Ensure artifact name matches between jobs

## References

- [Releasing Guide](RELEASING.md)
- [Release Workflows](RELEASE-WORKFLOWS.md)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
