# Project
A Django-based web-based voting system application.

## Recommended: create and activate a virtual environment

VScode Terminal(PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Database

```bash
python manage.py migrate
python manage.py makemigrations
```

## Running the app locally

Start the development server:

```bash
python manage.py runserver
```

Then open http://127.0.0.1:8000 in your browser.

## Tests

Run the test suite with:

```bash
python manage.py test
```

## Linting & Formatting

To check formatting and linting locally (optional):

```bash
pip install black isort flake8
black --check .
isort --check-only .
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
```

## Continuous Integration (GitHub Actions)

This repository previously ran automatic CI on `push` and `pull_request` events. To prevent GitHub Actions from running (for example, due to billing or account limits), the main workflow triggers were disabled and the workflow is configured to support manual runs using `workflow_dispatch` only.

If you wish to re-enable automatic CI runs, open `.github/workflows/django.yml` and re-enable the `push` and `pull_request` triggers. Example:

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  # or use workflow_dispatch to allow manual triggering only
```

## Notable changes made

- `PyYAML==6.0.1` was added to `requirements.txt` to support tests that parse the workflow YAML.
- The GitHub Actions workflow `django.yml` had its automatic triggers disabled to avoid CI runs that could incur billing; it supports `workflow_dispatch` for manual runs.
- `tests/test_workflow.py` assertions were corrected to handle both string and list forms for job `needs`, fixed branch list formatting checks, and repaired a syntax error in the build job test.

## Project structure

- `engine/` — Django project settings and WSGI/ASGI entrypoints
- `nominee/`, `voting/`, `userauth/` — Django apps
- `templates/` — HTML templates
- `tests/` — repository-level tests (includes CI/workflow checks)

## Contributing

- Run tests and linters locally before submitting PRs.
- Keep changes focused and include tests for new behavior.
