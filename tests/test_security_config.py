import os
import subprocess
import sys
import pytest

def test_dashboard_fails_without_secret_key():
    """Test that the dashboard app fails to start if DASHBOARD_SECRET_KEY is missing."""
    env = os.environ.copy()
    if "DASHBOARD_SECRET_KEY" in env:
        del env["DASHBOARD_SECRET_KEY"]

    # We need to make sure we don't load from .env file during test
    # But dashboard/app.py calls load_dotenv()
    # So we might need to mock the .env file or rely on the fact that if we
    # run it in a way that it can't find .env or .env doesn't have the key.

    # Let's create a temporary directory without .env and run from there
    # or just rely on the fact that we can control the environment.

    python_code = "from dashboard.app import app"

    process = subprocess.Popen(
        [sys.executable, "-c", python_code],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()

    assert process.returncode != 0
    assert "RuntimeError: DASHBOARD_SECRET_KEY environment variable is not set" in stderr

def test_dashboard_starts_with_secret_key():
    """Test that the dashboard app starts (imports) if DASHBOARD_SECRET_KEY is set."""
    env = os.environ.copy()
    env["DASHBOARD_SECRET_KEY"] = "test-secret-key"

    python_code = "from dashboard.app import app; print('Success')"

    process = subprocess.Popen(
        [sys.executable, "-c", python_code],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()

    assert process.returncode == 0
    assert "Success" in stdout
