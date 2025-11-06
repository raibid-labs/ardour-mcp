# Release Workflow Comparison

This document compares the three available release workflows for Ardour MCP, helping you choose the right approach for your situation.

## Quick Reference

| Workflow | Command | Push Required | Tests Run | Best For |
|----------|---------|---------------|-----------|----------|
| **Manual** | `just release-patch` | Manual | Manual | Careful releases |
| **Semi-Auto** | `just release-auto-patch` | Automatic | Automatic | Regular development |
| **Full Auto** | Push to main | N/A | Automatic | Team workflows |

## Workflow Comparison

### 1. Manual Release Workflow

**Commands:**
- `just release-patch` - Bug fixes (0.1.0 -> 0.1.1)
- `just release-minor` - New features (0.1.0 -> 0.2.0)
- `just release-major` - Breaking changes (0.1.0 -> 1.0.0)

**Process:**
```bash
# 1. Check status
just release-status

# 2. Run tests manually
just check

# 3. Create tag locally
just release-patch

# 4. Manually push tag
git push origin v0.1.1
```

**What It Does:**
1. Checks working directory is clean
2. Generates CHANGELOG.md (if git-cliff installed)
3. Commits changelog
4. Creates annotated git tag
5. Displays push instructions
6. **Waits for you to manually push**

**Pros:**
- Full control over every step
- Review everything before pushing
- Perfect for critical releases
- No surprises
- Can test locally before pushing
- Explicit confirmation required

**Cons:**
- More manual steps
- Easy to forget to push
- Slower process
- Must remember push command
- Can forget to run tests

**Best For:**
- Production releases
- First-time releases
- Breaking changes
- When you need review time
- Solo maintainer workflows
- Learning the release process

**Example Usage:**
```bash
# Fix a bug
git commit -m "fix(osc): resolve connection timeout"

# Check what would be released
just release-status

# Run tests
just check

# Create release tag
just release-patch
# Output: Tag v0.1.1 created locally

# Review everything
git show v0.1.1
git log v0.1.0..v0.1.1

# Push when ready
git push origin v0.1.1
```

---

### 2. Semi-Automated Release Workflow

**Commands:**
- `just release-auto-patch` - Automated patch release
- `just release-auto-minor` - Automated minor release
- `just release-auto-major` - Automated major release

**Process:**
```bash
# One command does everything
just release-auto-patch
```

**What It Does:**
1. Checks working directory is clean
2. **Runs all tests and checks automatically**
3. Updates CHANGELOG.md
4. Commits changelog
5. Creates git tag
6. **Automatically pushes to GitHub**
7. Shows release URL

**Pros:**
- Single command release
- Tests always run before release
- Fast and efficient
- Consistent process
- No forgotten steps
- Perfect for rapid iteration

**Cons:**
- Less time to review
- Auto-pushes immediately
- Can't test tag locally first
- Requires confirmation but moves fast
- All or nothing

**Best For:**
- Regular development releases
- Quick bug fixes
- When tests are comprehensive
- Trusted CI/CD environment
- Solo developer workflows
- Rapid iteration cycles

**Example Usage:**
```bash
# Fix bugs
git commit -m "fix(osc): resolve timeout"
git commit -m "fix(transport): correct position"

# Release in one command
just release-auto-patch

# Prompted:
# === Automated Patch Release: v0.1.1 ===
# This will:
#   1. Run all tests and checks
#   2. Update CHANGELOG.md
#   3. Commit changelog
#   4. Create git tag
#   5. Push tag to GitHub
# Continue? (yes/no): yes

# Then watch it go:
# Step 1/5: Running tests and checks...
# ✅ All tests passed
# Step 2/5: Updating changelog...
# ✅ CHANGELOG.md updated
# ...
# ✅ Release v0.1.1 complete!
```

---

### 3. Fully Automated Release Workflow (Release Please)

**Trigger:** Push commits to main branch

**Process:**
```bash
# Just commit with conventional commits
git commit -m "feat(mixer): add channel strip controls"
git push origin main
```

**What It Does:**
1. **Analyzes commits automatically** since last release
2. **Determines version bump** from commit types
3. **Opens a "Release PR"** with:
   - Updated CHANGELOG.md
   - Proposed version number
   - All changes listed
4. **When you merge the Release PR:**
   - Creates git tag
   - Creates GitHub release
   - Runs tests
   - Builds packages
   - Uploads artifacts

**Pros:**
- Zero manual release work
- Always knows what changed
- Great PR-based review
- Perfect for teams
- Never forget version bumps
- Conventional commits enforced
- Multiple developers can contribute

**Cons:**
- Requires PR workflow
- Extra step (merge Release PR)
- Less direct control
- Depends on commit messages
- Learning curve for team
- Can be overkill for solo projects

**Best For:**
- Team collaboration
- Open source projects
- When multiple contributors
- PR-based workflows
- Automated CI/CD pipelines
- Projects with many releases

**Example Usage:**
```bash
# Developer 1 adds feature
git commit -m "feat(tracks): implement track grouping"
git push origin main

# Developer 2 fixes bug
git commit -m "fix(osc): resolve memory leak"
git push origin main

# Release Please automatically:
# - Opens PR: "chore(main): release 0.2.0"
# - Shows all changes in PR description
# - Updates CHANGELOG.md in the PR

# Maintainer reviews Release PR
# - Checks changelog is correct
# - Verifies version bump is right
# - Merges PR

# On merge, automatically:
# - Creates tag v0.2.0
# - Creates GitHub release
# - Builds and uploads packages
```

---

## Feature Comparison Matrix

| Feature | Manual | Semi-Auto | Full Auto |
|---------|--------|-----------|-----------|
| **Automation Level** | Low | Medium | High |
| **Control Level** | High | Medium | Low |
| **Speed** | Slow | Fast | Fastest |
| **Test Enforcement** | Manual | Automatic | Automatic |
| **Push Control** | Manual | Automatic | Automatic |
| **Team Support** | Good | Good | Excellent |
| **PR Workflow** | No | No | Yes |
| **Changelog Generation** | Auto | Auto | Auto |
| **Version Decision** | Manual | Manual | Auto |
| **Rollback Ease** | Easy | Medium | Hard |
| **Learning Curve** | Easy | Easy | Medium |

---

## Choosing the Right Workflow

### Choose **Manual** if you:
- Are the sole maintainer
- Want full control
- Make infrequent releases
- Need time to review
- Are learning the release process
- Have critical production releases

### Choose **Semi-Auto** if you:
- Release frequently
- Trust your test suite
- Want speed without sacrificing safety
- Work solo or small team
- Don't use PR workflows
- Want simplicity

### Choose **Full Auto** if you:
- Have multiple contributors
- Use PR-based development
- Want zero manual release work
- Have established commit conventions
- Release very frequently
- Want maximum automation

---

## Hybrid Approach (Recommended)

You can use **different workflows for different situations**:

```bash
# Quick bug fix - use semi-auto
git commit -m "fix(osc): connection timeout"
just release-auto-patch

# Major feature - use release-please
git commit -m "feat: complete mixer implementation"
git push origin main
# Wait for Release PR, review, then merge

# Critical hotfix - use manual
git commit -m "fix: security vulnerability"
just release-patch
# Review everything carefully
git push origin v0.1.2
```

---

## Pre-release Workflows

All workflows support pre-releases for testing:

### Manual Pre-release
```bash
just pre-release minor alpha.1
git push origin v0.2.0-alpha.1
```

### Quick Pre-release Shortcuts
```bash
just pre-release-alpha  # Creates v0.2.0-alpha.1
just pre-release-beta   # Creates v0.2.0-beta.1
just pre-release-rc     # Creates v0.2.0-rc.1
```

Pre-releases are automatically marked as "pre-release" on GitHub.

---

## Migration Strategy

### Starting Out (Current)
Use **Manual** workflow to learn and establish patterns:
```bash
just release-patch
git push origin v0.1.1
```

### Growing Project
Add **Semi-Auto** for speed:
```bash
just release-auto-minor
```

### Team Development
Enable **Full Auto** for collaboration:
- Merge commits to main
- Review Release PRs
- Automatic releases

---

## Workflow Decision Tree

```
Need to release?
│
├─ Solo developer?
│  ├─ Quick fix? → Semi-Auto (release-auto-patch)
│  ├─ Major change? → Manual (release-patch + review)
│  └─ Regular feature? → Semi-Auto (release-auto-minor)
│
└─ Team project?
   ├─ PR workflow? → Full Auto (release-please)
   ├─ Direct commits? → Semi-Auto (release-auto-*)
   └─ Critical release? → Manual (release-* + manual push)
```

---

## Troubleshooting

### Manual Workflow Issues

**Problem:** Forgot to push tag
```bash
# Check for unpushed tags
git log --tags --oneline

# Push the tag
git push origin v0.1.1
```

**Problem:** Need to undo tag before pushing
```bash
# Delete local tag
git tag -d v0.1.1

# Recreate if needed
just release-patch
```

### Semi-Auto Workflow Issues

**Problem:** Push failed
```bash
# Pull first
git pull origin main --tags

# Try again
just release-auto-patch
```

**Problem:** Tests failed during release
```bash
# Fix the issues
git commit -m "fix: resolve test failures"

# Try release again
just release-auto-patch
```

### Full Auto Workflow Issues

**Problem:** Release PR not created
- Check commit messages follow conventional commits
- Ensure commits are on main branch
- Check GitHub Actions workflow ran

**Problem:** Wrong version in Release PR
- Close the PR
- Fix commit messages
- Push corrected commits
- New PR will be created

---

## Configuration Files

### Manual & Semi-Auto
- `justfile` - Contains all release commands
- `cliff.toml` - Changelog generation config
- `.github/workflows/release.yml` - Tag-based release

### Full Auto
- `release-please-config.json` - Release Please settings
- `.release-please-manifest.json` - Current version tracking
- `.github/workflows/semantic-release.yml` - Automated releases

---

## Best Practices

### For All Workflows

1. **Always use conventional commits:**
   ```bash
   feat: Add new feature
   fix: Fix a bug
   docs: Update documentation
   chore: Maintenance tasks
   ```

2. **Run tests before releasing:**
   ```bash
   just check  # Runs lint, typecheck, test
   ```

3. **Review CHANGELOG.md:**
   ```bash
   just changelog  # Generate and review
   ```

4. **Check release status:**
   ```bash
   just release-status  # See what would be released
   ```

### For Manual Workflow

- Always run `just check` before creating tag
- Review changes with `git log`
- Double-check version number
- Don't forget to push!

### For Semi-Auto Workflow

- Trust but verify tests
- Review the confirmation prompt
- Keep an eye on GitHub Actions

### For Full Auto Workflow

- Review Release PRs carefully
- Ensure commit messages are accurate
- Monitor automated releases
- Set up notifications

---

## Examples by Use Case

### Use Case 1: Solo Developer, Quick Bug Fix
**Recommended: Semi-Auto**
```bash
git commit -m "fix(osc): connection timeout"
just release-auto-patch
# Done! v0.1.1 released in 30 seconds
```

### Use Case 2: Team, New Feature
**Recommended: Full Auto**
```bash
git commit -m "feat(mixer): add EQ controls"
git push origin main
# Release PR created automatically
# Team reviews PR
# Merge PR -> Release!
```

### Use Case 3: Critical Security Fix
**Recommended: Manual**
```bash
git commit -m "fix: CVE-2024-XXXX security patch"
just check  # Thorough testing
just release-patch
git show v0.1.2  # Careful review
git push origin v0.1.2  # Explicit push
```

### Use Case 4: Pre-release Testing
**Any Workflow**
```bash
just pre-release-beta
git push origin v0.2.0-beta.1
# Test in production-like environment
# If good: just release-minor
```

---

## Summary

| When | Use | Command |
|------|-----|---------|
| Quick fix, solo | Semi-Auto | `just release-auto-patch` |
| Regular feature | Semi-Auto | `just release-auto-minor` |
| Team development | Full Auto | Push to main |
| Critical release | Manual | `just release-patch` + manual push |
| Learning releases | Manual | `just release-*` |
| Testing changes | Pre-release | `just pre-release-beta` |

**General Recommendation:**
- **Starting out?** Use Manual workflow
- **Established project?** Use Semi-Auto workflow
- **Team project?** Use Full Auto workflow
- **Critical releases?** Always use Manual workflow

All three workflows can coexist - choose based on the situation!

---

## References

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Release Please Documentation](https://github.com/googleapis/release-please)
- [Main Release Documentation](RELEASING.md)
