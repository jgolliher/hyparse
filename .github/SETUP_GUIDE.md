# GitHub Actions Setup Guide

## 📋 What We've Created

Your repository now has automated CI/CD pipelines that will:
- ✅ Test your code on every push/PR
- ✅ Check code quality (linting, formatting)
- ✅ Build and publish packages to PyPI
- ✅ Work across Python 3.9-3.12 and Windows/macOS/Linux

## 🗂️ Files Created

```
.github/
├── workflows/
│   ├── ci.yml           # Main CI pipeline
│   ├── publish.yml      # PyPI publishing workflow
│   └── README.md        # Workflow documentation
└── SETUP_GUIDE.md       # This file

.gitattributes           # Ensures consistent line endings
```

## 🚀 Quick Start

### Step 1: Push to GitHub

```bash
git add .github/ .gitattributes
git commit -m "Add GitHub Actions CI/CD pipelines"
git push
```

### Step 2: View Your First Workflow Run

1. Go to your repository on GitHub
2. Click the **"Actions"** tab at the top
3. You should see the CI workflow running!
4. Click on it to watch the tests run in real-time

## 🔧 What Happens Automatically

### On Every Push/Pull Request:

**1. Testing** (runs in ~2-5 minutes)
- Tests run on Python 3.9, 3.10, 3.11, 3.12
- Tests run on Ubuntu, macOS, and Windows
- Code coverage is calculated
- Total: 12 test matrix combinations!

**2. Linting** (runs in ~1 minute)
- Black checks code formatting
- Flake8 catches code quality issues
- MyPy does type checking

**3. Build Check** (runs in ~1 minute)
- Ensures package can be built
- Validates package metadata

### Visual Flow:
```
Push to GitHub
    ↓
GitHub Actions triggers
    ↓
┌─────────────┬──────────────┬──────────────┐
│   Test      │    Lint      │    Build     │
│ (12 combos) │  (quality)   │   (check)    │
└─────────────┴──────────────┴──────────────┘
    ↓
All green? ✅ Ready to merge!
Any red? ❌ Check the logs
```

## 📊 Adding Status Badges (Optional)

Make your README look professional! Add these badges at the top:

```markdown
# hyparse

![CI](https://github.com/YOUR_USERNAME/hyparse/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/hyparse/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/hyparse)
```

Replace `YOUR_USERNAME` with your GitHub username.

## 📦 Publishing to PyPI (When Ready)

### Prerequisites:
1. Create account on [pypi.org](https://pypi.org)
2. Create account on [test.pypi.org](https://test.pypi.org)
3. Generate API tokens from both sites

### Setup PyPI Publishing:

1. **Add GitHub Secrets:**
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add these secrets:
     - Name: `PYPI_API_TOKEN`, Value: your PyPI token
     - Name: `TEST_PYPI_API_TOKEN`, Value: your TestPyPI token

2. **Enable Publishing:**
   - Edit `.github/workflows/publish.yml`
   - Uncomment the `password` lines (around line 45 and 68)

3. **Create a Release:**
   ```bash
   # Update version in hyparse/__init__.py first!
   git tag v0.2.0
   git push origin v0.2.0
   ```

   Then on GitHub:
   - Go to Releases → Draft a new release
   - Choose your tag (v0.2.0)
   - Write release notes
   - Click "Publish release"

4. **Watch it Deploy:**
   - Go to Actions tab
   - Watch your package get published to PyPI!
   - Anyone can now `pip install hyparse`!

## 🧪 Testing Locally Before Pushing

Run the same checks that GitHub Actions will run:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=hyparse

# Check formatting (add --diff to see what would change)
black --check hyparse/ tests/

# Auto-fix formatting
black hyparse/ tests/

# Run linting
flake8 hyparse/

# Type checking
mypy hyparse/ --ignore-missing-imports

# Build package
python -m build

# Check package
twine check dist/*
```

## 🔍 Understanding the CI Output

When you click on a workflow run, you'll see:

```
Jobs:
  ✅ test (ubuntu-latest, 3.9)
  ✅ test (ubuntu-latest, 3.10)
  ✅ test (ubuntu-latest, 3.11)
  ✅ test (ubuntu-latest, 3.12)
  ✅ test (macos-latest, 3.9)
  ... (12 total)
  ✅ lint
  ✅ build
```

Click any job to see detailed logs. If something fails:
1. Click the failed job
2. Expand the failing step (marked with ❌)
3. Read the error message
4. Fix locally and push again

## 🎯 Common Scenarios

### "My tests pass locally but fail on CI"
- Check if you're using OS-specific paths
- Verify all dependencies are in `requirements-dev.txt`
- Look at the specific Python version/OS that's failing

### "Black formatting check fails"
- Run `black hyparse/ tests/` locally to auto-fix
- Commit and push the changes

### "Flake8 reports errors"
- Most can be fixed with Black formatting
- Some may need manual fixes (check the error message)
- Update `.flake8` to ignore specific rules if needed

### "Want to skip CI on a commit?"
- Add `[skip ci]` to your commit message
- Example: `git commit -m "Update README [skip ci]"`

## 📈 Next Steps

1. **Push your changes** and watch the first CI run
2. **Add status badges** to your README
3. **Set up Codecov** for coverage tracking (optional)
4. **Configure PyPI** when ready to publish (optional)

## 💡 Tips

- CI runs are **free** for public repositories
- Each workflow run saves logs for 90 days
- You can re-run failed jobs without a new commit
- Use the "Actions" tab to monitor all workflow runs
- Failed CI doesn't prevent pushing code, only merging PRs (if you enable branch protection)

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Package Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Codecov Documentation](https://docs.codecov.com/docs)

---

Questions? The workflow files have detailed comments, and you can always check the Actions tab for live runs!
