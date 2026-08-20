"""
Unit tests for Typer CLI commands.
"""

import os
from typer.testing import CliRunner
from cloud_forge.cli import app

runner = CliRunner()


def test_cli_simulate(tmp_path):
    manifests_dir = os.path.join(tmp_path, "out_manifests")
    result = runner.invoke(app, ["simulate", "--manifests", manifests_dir])

    assert result.exit_code == 0
    assert "CLOUD FORGE ORCHESTRATOR" in result.stdout
    assert "5-Layer Orchestration Pipeline Status" in result.stdout
    assert os.path.exists(manifests_dir)


def test_cli_generate_manifests(tmp_path):
    out_dir = os.path.join(tmp_path, "gen_yaml")
    result = runner.invoke(app, ["generate-manifests", "--output", out_dir])

    assert result.exit_code == 0
    assert "Successfully generated" in result.stdout
    assert os.path.exists(os.path.join(out_dir, "01_metallb_l2_pool.yaml"))
    assert os.path.exists(os.path.join(out_dir, "02_nginx_ingress_lb.yaml"))
    assert os.path.exists(out_dir)


def test_cli_health():
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "Cluster Component Health Matrix" in result.stdout
    assert "kube-apiserver" in result.stdout


def test_cli_security_audit():
    result = runner.invoke(app, ["security-audit"])
    assert result.exit_code == 0
    assert "Security Hardening & CIS Compliance Audit" in result.stdout
    assert "UFW API Port" in result.stdout
