"""
Unit tests for CloudForgeOrchestrator state machine.
"""

from cloud_forge.core.orchestrator import CloudForgeOrchestrator
from cloud_forge.core.models import StageStatus
from cloud_forge.simulation.mock_engine import ClusterSimulator


def test_orchestrator_full_pipeline():
    spec = ClusterSimulator.get_default_3node_spec()
    orchestrator = CloudForgeOrchestrator(spec)

    report = orchestrator.run_deployment()

    assert report.overall_status == "SUCCESS"
    assert report.total_nodes == 3
    assert report.control_planes == 1
    assert report.workers == 2
    assert len(report.stage_results) == 5

    for stage_res in report.stage_results:
        assert stage_res.status == StageStatus.SUCCESS

    assert report.allocated_vip == "192.168.1.200"
    assert "http://" in report.ingress_endpoint


def test_orchestrator_failure_handling():
    spec = ClusterSimulator.get_default_3node_spec()
    spec.nodes = []  # No nodes configured -> should fail in stage 3
    orchestrator = CloudForgeOrchestrator(spec)

    report = orchestrator.run_deployment()
    assert report.overall_status == "FAILED"
