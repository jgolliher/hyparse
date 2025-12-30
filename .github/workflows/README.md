# GitHub Actions Workflows

This directory contains automated workflows for the hyparse project.

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Every push to `main` branch
- Every pull request to `main` branch
- Manual trigger via GitHub UI

**What it does:**
- **Tests** across multiple Python versions (3.9, 3.10, 3.11, 3.12) and operating systems (Ubuntu, macOS, Windows)
- **Linting** with flake8 to catch code quality issues
- **Formatting** check with black to ensure consistent code style
- **Type checking** with mypy (optional, doesn't fail build)
- **Code coverage** reporting to Codecov
- **Build check** to ensure the package can be built successfully

**Viewing results:**
- Go to your repository → Actions tab
- Click on any workflow run to see detailed results
- Green checkmark = all tests passed
- Red X = something failed (click to see details)

### 2. PyPI Publishing (`publish.yml`)

**Triggers:**
- When you create a GitHub Release
- Manual trigger via GitHub UI

**What it does:**
- Builds the Python package (wheel and source distribution)
- Publishes to TestPyPI first (for testing)
- Publishes to PyPI (production) when ready

**Setup required:**
1. Create accounts on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. Generate API tokens from both sites
3. Add tokens as GitHub Secrets:
   - `PYPI_API_TOKEN` - for production PyPI
   - `TEST_PYPI_API_TOKEN` - for test PyPI
4. Uncomment the password lines in `publish.yml`

## Setting Up

### 1. Enable GitHub Actions
- Actions are enabled by default for public repos
- For private repos: Settings → Actions → Enable Actions

### 2. Add Codecov (Optional)
- Go to [codecov.io](https://codecov.io)
- Sign in with GitHub
- Enable coverage for your repository
- Add badge to README.md:
  ```markdown
  [![codecov](https://codecov.io/gh/YOUR_USERNAME/hyparse/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/hyparse)
  ```

### 3. Add Status Badges to README
Add these badges to show build status:

```markdown
![CI](https://github.com/YOUR_USERNAME/hyparse/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/hyparse/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/hyparse)
```

## Creating a Release

When you're ready to publish to PyPI:

1. Update version in `hyparse/__init__.py`
2. Commit and push changes
3. Create a Git tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. Create a GitHub Release:
   - Go to Releases → Draft a new release
   - Choose the tag you created
   - Write release notes describing changes
   - Click "Publish release"
5. The `publish.yml` workflow will automatically run and publish to PyPI

## Local Testing

Before pushing, you can run the same checks locally:

```bash
# Run tests
pytest tests/ -v --cov=hyparse

# Check formatting
black --check hyparse/ tests/

# Run linting
flake8 hyparse/

# Type check
mypy hyparse/ --ignore-missing-imports

# Build package
python -m build
```

## Troubleshooting

**Tests fail on Windows but pass locally (macOS/Linux)?**
- Check file path separators (use `pathlib.Path`)
- Check line endings (use `.gitattributes`)

**Linting errors?**
- Run `black hyparse/ tests/` to auto-format
- Check `.flake8` for configured rules

**Build fails?**
- Ensure `requirements.txt` and `requirements-dev.txt` are up to date
- Check that `pyproject.toml` or `setup.py` are correctly configured

**Can't publish to PyPI?**
- Verify API tokens are correctly set in GitHub Secrets
- Check that version number is unique (not already published)
- Ensure `publish.yml` has password lines uncommented
