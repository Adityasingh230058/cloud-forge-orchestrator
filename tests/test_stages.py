"""
Unit tests for each of the 5 orchestration stages.
"""

import pytest
from cloud_forge.core.models import ClusterSpec, NodeConfig, NodeRole, NodeStatus, StageStatus
from cloud_forge.stages.s01_prereqs import PrerequisitesStage
from cloud_forge.stages.s02_runtime import ContainerRuntimeStage
from cloud_forge.stages.s03_cluster import KubernetesClusterStage
from cloud_forge.stages.s04_loadbalancer import LoadBalancerIngressStage
from cloud_forge.stages.s05_security import SecurityHardeningStage
from cloud_forge.simulation.mock_engine import ClusterSimulator


@pytest.fixture
def default_spec():
    return ClusterSimulator.get_default_3node_spec()


def test_stage_01_prerequisites(default_spec):
    stage = PrerequisitesStage(default_spec)
    result = stage.execute()

    assert result.stage_number == 1
    assert result.status == StageStatus.SUCCESS
    assert "overlay" in result.details["kernel_modules"]
    assert "br_netfilter" in result.details["kernel_modules"]
    assert len(result.actions_taken) > 0


def test_stage_01_insufficient_cpu():
    spec = ClusterSimulator.get_default_3node_spec()
    spec.nodes[0].cpu_cores = 1  # Invalid CPU for K8s
    stage = PrerequisitesStage(spec)
    result = stage.execute()

    assert result.status == StageStatus.FAILED
    assert "at least 2 CPU cores" in result.errors[0]


def test_stage_02_container_runtime(default_spec):
    stage = ContainerRuntimeStage(default_spec)
    result = stage.execute()

    assert result.stage_number == 2
    assert result.status == StageStatus.SUCCESS
    assert result.details["runtime"] == "containerd"
    assert result.details["cgroup_driver"] == "systemd"
    for node in default_spec.nodes:
        assert node.status == NodeStatus.RUNTIME_READY


def test_stage_03_kubernetes_cluster(default_spec):
    stage = KubernetesClusterStage(default_spec)
    result = stage.execute()

    assert result.stage_number == 3
    assert result.status == StageStatus.SUCCESS
    assert result.details["control_plane"] == "srv-master-01"
    assert len(result.details["workers_joined"]) == 2
    assert default_spec.nodes[0].status == NodeStatus.READY


def test_stage_04_loadbalancer(default_spec):
    stage = LoadBalancerIngressStage(default_spec)
    result = stage.execute()

    assert result.stage_number == 4
    assert result.status == StageStatus.SUCCESS
    assert "MetalLB" in result.details["load_balancer"]
    assert result.details["assigned_ingress_vip"] == "192.168.1.200"


def test_stage_05_security(default_spec):
    stage = SecurityHardeningStage(default_spec)
    result = stage.execute()

    assert result.stage_number == 5
    assert result.status == StageStatus.SUCCESS
    assert "Default-Deny" in result.details["network_policies"]
    assert "100%" in result.details["security_compliance_score"]
