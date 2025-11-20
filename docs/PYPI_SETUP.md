# PyPI Publishing Setup Guide

This guide explains how to configure PyPI trusted publishing for Ardour MCP using GitHub Actions.

## Overview

Ardour MCP uses **PyPI Trusted Publishing** (also called "OIDC publishing") which eliminates the need for API tokens. This is the recommended and most secure way to publish Python packages.

## Benefits of Trusted Publishing

- ✅ **No API tokens** to manage or rotate
- ✅ **More secure** - no long-lived credentials
- ✅ **Automated** - works seamlessly with GitHub Actions
- ✅ **Recommended by PyPI** for all new projects

## Prerequisites

1. **PyPI Account**: You need a PyPI account with permissions to manage the `ardour-mcp` package
2. **GitHub Repository**: Admin access to configure environments and workflows
3. **Package Name**: Reserve the package name on PyPI (first-time only)

## Step 1: Reserve Package Name on PyPI (First Time Only)

If this is the first release, you need to register the package name:

### Option A: Manual Upload (One-Time)

1. Build the package locally:
   ```bash
   uv build
   ```

2. Install twine:
   ```bash
   pip install twine
   ```

3. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

4. Enter your PyPI credentials when prompted

This creates the package on PyPI so you can configure trusted publishing.

### Option B: Use TestPyPI First

Test the publishing workflow without affecting production:

1. Create account on [TestPyPI](https://test.pypi.org/)

2. Configure trusted publishing on TestPyPI (see Step 2)

3. Use the `publish.yml` workflow with `test_pypi: true`

## Step 2: Configure PyPI Trusted Publishing

### On PyPI

1. **Log in to PyPI**: https://pypi.org/

2. **Go to Your Projects**: https://pypi.org/manage/projects/

3. **Select `ardour-mcp`** project

4. **Navigate to Publishing**:
   - Click "Publishing" in the left sidebar
   - Or go directly to: `https://pypi.org/manage/project/ardour-mcp/settings/publishing/`

5. **Add a new publisher**:
   - Publisher: **GitHub**
   - Owner: `raibid-labs`
   - Repository: `ardour-mcp`
   - Workflow name: `release.yml` (or `publish.yml`)
   - Environment name: `pypi`

6. **Save** the configuration

### On GitHub

1. **Go to Repository Settings**: https://github.com/raibid-labs/ardour-mcp/settings

2. **Navigate to Environments**:
   - Settings → Environments
   - Or: https://github.com/raibid-labs/ardour-mcp/settings/environments

3. **Create `pypi` environment**:
   - Click "New environment"
   - Name: `pypi`
   - Click "Configure environment"

4. **Configure Environment Protection Rules** (recommended):
   - ✅ **Required reviewers**: Add yourself or team members
   - ✅ **Wait timer**: 0 minutes (or add delay if you want review time)
   - ✅ **Deployment branches**: Only allow `main` branch or tags matching `v*`

5. **Save protection rules**

## Step 3: Verify Workflow Configuration

The release workflow (`.github/workflows/release.yml`) should include:

```yaml
publish-to-pypi:
  name: Publish to PyPI
  needs: release
  runs-on: ubuntu-latest
  if: "!contains(github.ref, '-')"  # Skip pre-releases
  environment:
    name: pypi  # Must match environment name in GitHub and PyPI
    url: https://pypi.org/p/ardour-mcp
  permissions:
    id-token: write  # IMPORTANT: Required for trusted publishing

  steps:
    - name: Download build artifacts
      uses: actions/download-artifact@v4
      with:
        name: python-package-distributions
        path: dist/

    - name: Publish distribution to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
```

Key points:
- ✅ `environment: name: pypi` matches PyPI and GitHub configuration
- ✅ `permissions: id-token: write` is set
- ✅ Uses `pypa/gh-action-pypi-publish@release/v1` (no credentials needed!)

## Step 4: Test the Setup

### Test with TestPyPI

1. **Configure TestPyPI trusted publishing** (same steps as PyPI)
   - URL: https://test.pypi.org/manage/project/ardour-mcp/settings/publishing/

2. **Run the publish workflow manually**:
   - Go to Actions → Publish to PyPI
   - Click "Run workflow"
   - Check "Publish to TestPyPI"
   - Click "Run workflow"

3. **Verify the package**:
   - Check https://test.pypi.org/project/ardour-mcp/
   - Try installing: `pip install -i https://test.pypi.org/simple/ ardour-mcp`

### Test with Production PyPI

1. **Create a test release tag**:
   ```bash
   git tag -a v0.3.1-rc1 -m "Release candidate 0.3.1-rc1"
   git push origin v0.3.1-rc1
   ```

2. **Monitor GitHub Actions**:
   - Go to https://github.com/raibid-labs/ardour-mcp/actions
   - Watch the "Release" workflow
   - The PyPI publish job should run after release creation

3. **Verify on PyPI**:
   - Check https://pypi.org/project/ardour-mcp/
   - Verify the new version appears
   - Test installation: `pip install ardour-mcp==0.3.1rc1`

4. **If successful**, create the real release:
   ```bash
   git tag -a v0.3.1 -m "Release v0.3.1"
   git push origin v0.3.1
   ```

## Troubleshooting

### Error: "Publisher verification failed"

**Problem**: PyPI can't verify the GitHub Action is authorized.

**Solutions**:
1. Double-check environment name matches exactly (`pypi`)
2. Verify workflow name in PyPI config matches actual file name
3. Ensure repository owner and name are correct
4. Check that `id-token: write` permission is set

### Error: "Missing id-token permission"

**Problem**: Workflow doesn't have permission to get OIDC token.

**Solution**: Add to the job:
```yaml
permissions:
  id-token: write
```

### Error: "Environment protection rule"

**Problem**: Environment requires approval but no reviewers configured.

**Solutions**:
1. Add yourself as required reviewer in environment settings
2. Approve the deployment in GitHub Actions UI
3. Adjust protection rules if needed

### Build artifacts not found

**Problem**: PyPI publish job can't find distribution files.

**Solutions**:
1. Ensure build step creates `dist/` directory
2. Verify `actions/upload-artifact@v4` runs in release job
3. Check artifact name matches: `python-package-distributions`
4. Ensure `actions/download-artifact@v4` runs before publish

### Wrong version published

**Problem**: Published version doesn't match tag.

**Solutions**:
1. Check `pyproject.toml` uses `hatch-vcs` for versioning
2. Ensure `fetch-depth: 0` in checkout step (for full git history)
3. Verify tag is properly annotated: `git tag -a v0.3.1`

## Manual Publishing (Emergency Only)

If automated publishing fails, you can publish manually:

1. **Build locally**:
   ```bash
   git checkout v0.3.1
   uv build
   ```

2. **Install twine**:
   ```bash
   pip install twine
   ```

3. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

4. **Enter PyPI credentials** when prompted

⚠️ **Note**: This requires PyPI API token. Trusted publishing is preferred.

## Security Best Practices

1. **Use environment protection rules** to require approval for releases
2. **Limit who can approve** deployments to `pypi` environment
3. **Monitor PyPI releases** for unauthorized uploads
4. **Enable 2FA** on your PyPI account
5. **Review workflow changes** that touch publishing carefully

## Resources

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA Publish Action](https://github.com/pypa/gh-action-pypi-publish)
- [Python Packaging Guide](https://packaging.python.org/)

## Questions?

If you encounter issues not covered here:

1. Check [GitHub Actions logs](https://github.com/raibid-labs/ardour-mcp/actions)
2. Review [PyPI project settings](https://pypi.org/manage/project/ardour-mcp/)
3. Open an issue or discussion on GitHub
