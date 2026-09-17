import pytest
import subprocess
import json
import os

def test_cli_success(tmp_path):
    """Tests normal CLI execution with valid JSON input."""
    log_file = tmp_path / "sample.json"
    log_file.write_text(json.dumps({"generated_for": "test", "events": []}))

    result = subprocess.run(["sysdiag", "--file", str(log_file)], capture_output=True, text=True)
    assert result.returncode == 0
    assert "CLI DIAGNOSTICS REPORT" in result.stdout

def test_cli_json_flag(tmp_path):
    """Tests CLI execution with --json flag."""
    log_file = tmp_path / "sample.json"
    log_file.write_text(json.dumps({"generated_for": "test", "events": []}))

    result = subprocess.run(["sysdiag", "--file", str(log_file), "--json"], capture_output=True, text=True)
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert "system_info" in parsed

def test_missing_file():
    """Tests exit code 2 when log file is missing."""
    result = subprocess.run(["sysdiag", "--file", "non_existent_file.json"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "Error: File 'non_existent_file.json' not found." in result.stderr

def test_malformed_json(tmp_path):
    """Tests exit code 2 when JSON file is invalid."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ malformed json content ")

    result = subprocess.run(["sysdiag", "--file", str(bad_file)], capture_output=True, text=True)
    assert result.returncode == 2
    assert "contains malformed JSON" in result.stderr