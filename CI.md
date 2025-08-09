# Pre-commit and CI Setup Instructions

## 1. Install Pre-commit Locally

```bash
# Install pre-commit
uv add --dev pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files initially
pre-commit run --all-files
```

## 2. File Structure

Create these files in your repository:

```
your-repo/
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt (or pyproject.toml)
└── your-python-files...
```

## 3. What Each Tool Does

### Pre-commit Hooks:
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml/toml/json**: Validates file formats
- **black**: Code formatting (88 char line length)
- **isort**: Import sorting (compatible with black)
- **flake8**: Python linting
- **mypy**: Type checking
- **bandit**: Security vulnerability scanning
- **hadolint**: Dockerfile linting

### CI Pipeline:
- **lint-and-format**: Runs all pre-commit hooks
- **test**: Runs pytest with coverage reporting
- **security**: Additional security scans

## 4. Customization Options

### Adjust Python versions:
Edit the `matrix.python-version` arrays in `ci.yml`

### Skip specific hooks:
```bash
SKIP=mypy,bandit git commit -m "commit message"
```

### Modify formatting rules:
Edit args in `.pre-commit-config.yaml`:
- Black line length: `args: [--line-length=100]`
- Flake8 rules: `args: [--max-line-length=100, --extend-ignore=E203,W503]`

### Add project-specific dependencies:
Update the CI workflow to install your requirements:
```yaml
- name: Install dependencies
  run: |
    uv pip install -r requirements.txt --system
    uv pip install -r requirements-dev.txt --system  # if you have dev deps
```

## 5. Optional: pyproject.toml Configuration

If you prefer to configure tools in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

## 6. First Run

After setup:
1. Commit the config files
2. Make a test commit to see pre-commit in action
3. Check GitHub Actions tab after pushing

The pre-commit hooks will run locally before each commit, and the CI will run on GitHub when you push or create pull requests.
