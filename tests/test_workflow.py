import yaml
from pathlib import Path


def load_workflow():
    workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "django.yml"
    with open(workflow_path, "r") as f:
        return yaml.safe_load(f)


def test_workflow_exists():
    workflow = load_workflow()
    assert workflow is not None, "Workflow file is empty or invalid YAML"


def test_workflow_has_required_keys():
    workflow = load_workflow()
    required_keys = {"name", "on", "jobs"}
    assert required_keys.issubset(workflow.keys()), f"Workflow missing required keys: {required_keys - set(workflow.keys())}"


def test_workflow_name():
    workflow = load_workflow()
    assert workflow["name"], "Workflow name is empty"
    assert workflow["name"] == "Django CI", f"Expected 'Django CI', got '{workflow['name']}'"


def test_workflow_triggers():
    workflow = load_workflow()
    triggers = workflow["on"]
    assert "push" in triggers, "Workflow missing 'push' trigger"
    assert "pull_request" in triggers, "Workflow missing 'pull_request' trigger"
    assert triggers["push"]["branches"] == ["main", "develop", ], "Push branches should be main and develop"
    assert triggers["pull_request"]["branches"] == [ "main", "develop",], "PR branches should be main and develop"


def test_workflow_has_concurrency():
    workflow = load_workflow()
    assert "concurrency" in workflow, "Workflow missing concurrency settings"
    assert ("group" in workflow["concurrency"]), "Concurrency missing group configuration"
    assert (workflow["concurrency"]["cancel-in-progress"] is True), "Concurrency should cancel in-progress jobs"


def test_workflow_has_all_jobs():
    workflow = load_workflow()
    jobs = workflow["jobs"]
    required_jobs = {"test", "lint", "security", "build"}
    assert required_jobs.issubset(jobs.keys()), f"Workflow missing jobs: {required_jobs - set(jobs.keys())}"


def test_test_job():
    workflow = load_workflow()
    test_job = workflow["jobs"]["test"]
    assert test_job["runs-on"] == "ubuntu-latest", "Test job should run on ubuntu-latest"
    assert "strategy" in test_job, "Test job missing strategy"
    assert "matrix" in test_job["strategy"], "Test job strategy missing matrix"
    assert ("python-version" in test_job["strategy"]["matrix"]), "Test job matrix missing python-version"
    python_versions = test_job["strategy"]["matrix"]["python-version"]
    assert "3.10" in python_versions, "Test matrix should include Python 3.10"
    assert "3.11" in python_versions, "Test matrix should include Python 3.11"
    assert "3.12" in python_versions, "Test matrix should include Python 3.12"
    steps = test_job["steps"]
    step_names = [step.get("name") for step in steps if "name" in step]
    assert any("checkout" in name.lower() for name in step_names), "Missing checkout step"
    assert any("python" in name.lower() for name in step_names), "Missing Python setup step"
    assert any("dependencies" in name.lower() for name in step_names), "Missing dependencies install step"
    assert any("migration" in name.lower() for name in step_names), "Missing migrations step"
    assert any("test" in name.lower() for name in step_names), "Missing test step"


def test_lint_job():
    workflow = load_workflow()
    lint_job = workflow["jobs"]["lint"]
    assert lint_job["runs-on"] == "ubuntu-latest", "Lint job should run on ubuntu-latest"
    assert "needs" in lint_job, "Lint job should depend on test job"
    assert lint_job["needs"] == "test", "Lint job should depend on test"
    steps = lint_job["steps"]
    step_names = [step.get("name") for step in steps if "name" in step]
    assert any("black" in name.lower() for name in step_names), "Missing Black check"
    assert any("isort" in name.lower() for name in step_names), "Missing isort check"
    assert any("flake8" in name.lower() for name in step_names), "Missing flake8 check"


def test_security_job():
    workflow = load_workflow()
    security_job = workflow["jobs"]["security"]
    assert (security_job["runs-on"] == "ubuntu-latest"), "Security job should run on ubuntu-latest"
    assert "needs" in security_job, "Security job should have dependencies"
    steps = security_job["steps"]
    step_names = [step.get("name") for step in steps if "name" in step]
    assert any("bandit" in name.lower() for name in step_names), "Missing Bandit check"
    assert any(
        "safety" in name.lower() or "dependencies" in name.lower()
        for name in step_names
    ), "Missing dependency vulnerability check"


def test_build_job():
    workflow = load_workflow()
    build_job = workflow["jobs"]["build"]
    assert (build_job["runs-on"] == "ubuntu-latest"), "Build job should run on ubuntu-latest"
    assert "needs" in build_job, "Build job should depend on other jobs"
    assert "if" in build_job, "Build job should have condition"
    assert ("main" in build_job["if"]), "Build job should only run on main branch"
    steps = build_job["steps"]
    step_names = [step.get("name") for step in steps if "name" in step]
    assert any("static" in name.lower() for name in step_names), "Missing static files collection step"
    assert any("package" in name.lower() or "deploy" in name.lower() for name in step_names), "Missing deployment package step"
    assert any("artifact" in name.lower() for name in step_names), "Missing artifact upload step"


def test_test_job_has_secret_env_vars():
    workflow = load_workflow()
    test_job = workflow["jobs"]["test"]
    steps = test_job["steps"]
    env_steps = [step for step in steps if "env" in step]
    assert len(env_steps) > 0, "Test job should have steps with environment variables"
    all_env_vars = {}
    for step in env_steps:
        all_env_vars.update(step.get("env", {}))
    required_secrets = {"SECRET_KEY", "DEBUG", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET",}
    assert required_secrets.issubset(all_env_vars.keys()), f"Missing required environment variables: {required_secrets - set(all_env_vars.keys())}"


def test_workflow_caching():
    workflow = load_workflow()
    test_job = workflow["jobs"]["test"]
    steps = test_job["steps"]

    # Check for cache step
    cache_steps = [step for step in steps if step.get("uses", "").startswith("actions/cache")]
    assert len(cache_steps) > 0, "Test job should use pip caching"

    cache_step = cache_steps[0]
    assert cache_step["with"]["path"] == "~/.cache/pip", "Cache path should be ~/.cache/pip"


if __name__ == "__main__":
    import sys

    tests = [
        test_workflow_exists,
        test_workflow_has_required_keys,
        test_workflow_name,
        test_workflow_triggers,
        test_workflow_has_concurrency,
        test_workflow_has_all_jobs,
        test_test_job,
        test_lint_job,
        test_security_job,
        test_build_job,
        test_test_job_has_secret_env_vars,
        test_workflow_caching,
    ]

    failed = 0
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1

    if failed > 0:
        print(f"\n{failed} test(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed!")
