"""
test_github_actions_pipeline_valid.py
======================================

The GitHub Actions release pipeline at .github/workflows/release-pipeline.yml
must be:
  1. Valid YAML
  2. Trigger on v* tag push
  3. Have a compile-binaries job with 4-platform matrix (macOS Intel, macOS ARM, Windows, Linux)
  4. Have a deploy-updater job that depends on compile-binaries
  5. Have a seal-release job that runs ogir_assessment + verify_chain
  6. Reference the required Tauri action and secrets

The workflow is the bridge between the local build (Tauri skeleton) and
the Cloudflare R2+Workers distribution.
"""
import os
from pathlib import Path
import yaml

PROJECT = Path(__file__).resolve().parent.parent
WORKFLOW = PROJECT / ".github" / "workflows" / "release-pipeline.yml"


def test_workflow_exists():
    """The workflow file exists at .github/workflows/release-pipeline.yml."""
    assert WORKFLOW.exists(), f"workflow not found at {WORKFLOW}"


def test_workflow_is_valid_yaml():
    """The workflow parses as YAML."""
    text = WORKFLOW.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    assert isinstance(obj, dict)


def test_workflow_triggers_on_tag_push():
    """The workflow triggers on push of v* tags."""
    text = WORKFLOW.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    on = obj.get(True, obj.get("on", {}))  # yaml 1.1 may parse 'on' as True
    push = on.get("push", {})
    tags = push.get("tags", [])
    assert "v*" in tags, f"expected v* in tags, got {tags}"


def test_workflow_has_compile_binaries_job():
    """The compile-binaries job exists with a 4-platform matrix."""
    text = WORKFLOW.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    jobs = obj.get("jobs", {})
    assert "compile-binaries" in jobs, "missing compile-binaries job"
    matrix = jobs["compile-binaries"]["strategy"]["matrix"]["include"]
    platforms = {entry["platform"] for entry in matrix}
    # macOS-latest appears twice (aarch64 + x86_64), but we want at least 3 distinct platforms
    assert "macos-latest" in platforms
    assert "windows-latest" in platforms
    assert "ubuntu-latest" in platforms
    # And we want all 4 targets
    targets = {entry["target"] for entry in matrix}
    assert "aarch64-apple-darwin" in targets
    assert "x86_64-apple-darwin" in targets
    assert "x86_64-pc-windows-msvc" in targets
    assert "x86_64-unknown-linux-gnu" in targets


def test_workflow_uses_tauri_action():
    """The workflow uses tauri-apps/tauri-action@v2 for compilation."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "tauri-apps/tauri-action@v2" in text, "missing tauri-action@v2"


def test_workflow_has_deploy_updater_job():
    """The deploy-updater job exists and depends on compile-binaries."""
    text = WORKFLOW.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    jobs = obj.get("jobs", {})
    assert "deploy-updater" in jobs, "missing deploy-updater job"
    assert "compile-binaries" in jobs["deploy-updater"]["needs"]


def test_workflow_has_seal_release_job():
    """The seal-release job exists and runs ogir_assessment + verify_chain."""
    text = WORKFLOW.read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    jobs = obj.get("jobs", {})
    assert "seal-release" in jobs, "missing seal-release job"
    assert "ogir_assessment" in text
    assert "verify_chain" in text
