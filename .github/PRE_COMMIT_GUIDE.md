# Pre-commit Hooks Guide

Pre-commit hooks automatically run code quality checks before each commit, catching issues early and ensuring consistent code quality.

## 📦 Installation

```bash
# Install pre-commit (included in requirements-dev.txt)
pip install pre-commit

# Install the git hooks into your local repository
pre-commit install
```

You only need to run `pre-commit install` once per repository clone.

## ✨ What Gets Checked

Every time you run `git commit`, these checks run automatically:

### 1. **Black** - Code Formatting
- Automatically formats Python code to PEP 8 style
- Fixes line length, spacing, quotes, etc.
- **Auto-fixes and re-stages files**

### 2. **Flake8** - Code Linting
- Catches code quality issues (unused imports, undefined variables, etc.)
- Compatible with Black's formatting
- **Blocks commit if issues found**

### 3. **Built-in Checks**
- Prevents committing large files (>1MB)
- Removes trailing whitespace
- Ensures files end with newline
- Validates YAML/TOML syntax
- Prevents direct commits to main/master branch

### 4. **MyPy** - Type Checking (Optional)
- Currently set to manual mode (doesn't block commits)
- Run with: `pre-commit run mypy --all-files`

## 🎯 Common Workflows

### Making a Commit (Normal)

```bash
git add .
git commit -m "Add new feature"
```

**What happens:**
1. Pre-commit runs all hooks
2. If Black finds formatting issues, it auto-fixes them
3. You'll see: "Files were modified by this hook"
4. **Re-run the commit command** to commit the formatted files
5. If Flake8 finds issues, the commit is blocked
6. Fix the issues and try again

### Example Output (Success)

```
black....................................................................Passed
flake8...................................................................Passed
Check for added large files.............................................Passed
Check for case conflicts.................................................Passed
Fix End of Files.........................................................Passed
Trim Trailing Whitespace.................................................Passed
Check Yaml...............................................................Passed
Check Toml...............................................................Passed
Don't commit to branch...................................................Passed
[main 1a2b3c4] Add new feature
 3 files changed, 45 insertions(+), 12 deletions(-)
```

### Example Output (Black Fixed Files)

```
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted hyparse/parser/hy3_file.py

All done! ✨ 🍰 ✨
1 file reformatted.
```

**What to do:** Just run `git commit` again!

```bash
# Files were auto-formatted, just commit again
git commit -m "Add new feature"
```

### Example Output (Linting Error)

```
flake8...................................................................Failed
- hook id: flake8
- exit code: 1

hyparse/parser/hy3_file.py:42:1: F401 'sys' imported but unused
hyparse/parser/hy3_file.py:125:80: E501 line too long (92 > 88 characters)
```

**What to do:** Fix the issues manually:

```bash
# Remove unused import, let Black handle line length
# Edit the file, then:
git add hyparse/parser/hy3_file.py
git commit -m "Add new feature"
```

## 🚀 Running Manually

You don't need to commit to run the hooks:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run all hooks on staged files only
pre-commit run

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Run mypy (disabled by default)
pre-commit run mypy --all-files
```

## 🔧 Configuration

The configuration is in [`.pre-commit-config.yaml`](../.pre-commit-config.yaml).

### Temporarily Disable a Hook

Edit `.pre-commit-config.yaml` and add `stages: [manual]` to the hook:

```yaml
- repo: https://github.com/pycqa/flake8
  rev: 7.1.1
  hooks:
    - id: flake8
      stages: [manual]  # Now only runs when explicitly called
```

### Bypass Hooks for One Commit

**Not recommended**, but useful for emergencies:

```bash
git commit --no-verify -m "Emergency fix"
```

## 🔄 Updating Hooks

Hook versions are specified in `.pre-commit-config.yaml`. To update:

```bash
# Update to latest versions
pre-commit autoupdate

# Install updated hooks
pre-commit install --install-hooks
```

## 💡 Tips

1. **Run before you commit**: Use `pre-commit run --all-files` to check everything before staging
2. **Don't fight Black**: If Black reformats your code, just accept it and move on
3. **Fix lint errors promptly**: They're usually quick fixes and improve code quality
4. **Use `--no-verify` sparingly**: It defeats the purpose of pre-commit hooks

## 🐛 Troubleshooting

### "command not found: pre-commit"
```bash
pip install pre-commit
```

### "No .pre-commit-config.yaml found"
Make sure you're in the repository root directory.

### "Hook failed to install"
```bash
pre-commit clean
pre-commit install --install-hooks
```

### "I want to remove pre-commit hooks"
```bash
pre-commit uninstall
```

You can reinstall anytime with `pre-commit install`.

## 📚 Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)

---

**Remember:** Pre-commit hooks are your friend! They catch issues before CI does, saving you from failed builds and making code reviews faster.
