"""
Multi-Server Local Simulation Sandbox Engine.
"""

from typing import Dict, Any
from ..core.models import ClusterSpec, NodeConfig, NodeRole, NodeStatus, NetworkingConfig, SecurityConfig
from ..core.orchestrator import CloudForgeOrchestrator, OrchestrationReport


class ClusterSimulator:
    """
    Simulates a 3-server bare-metal/VM environment to validate cluster orchestration
    logic, stage transitions, and manifest generation locally.
    """

    @classmethod
    def get_default_3node_spec(cls) -> ClusterSpec:
        """Returns standard 3-server enterprise cluster spec (1 Master + 2 Workers)."""
        return ClusterSpec(
            cluster_name="enterprise-edge-k8s",
            version="v1.28.0",
            networking=NetworkingConfig(
                pod_cidr="10.244.0.0/16",
                service_cidr="10.96.0.0/12",
                cni_plugin="flannel",
                load_balancer_ip_range="192.168.1.200-192.168.1.220",
                ingress_controller="ingress-nginx",
            ),
            security=SecurityConfig(
                enforce_default_deny_network_policies=True,
                enable_host_firewall=True,
                restrict_kubelet_readonly_port=True,
                enforce_rbac_least_privilege=True,
            ),
            nodes=[
                NodeConfig(
                    id="srv-master-01",
                    role=NodeRole.CONTROL_PLANE,
                    ip="192.168.1.101",
                    cpu_cores=4,
                    memory_gb=8,
                    disk_gb=120,
                    status=NodeStatus.PROVISIONED,
                    labels={"node.kubernetes.io/role": "control-plane", "topology.kubernetes.io/zone": "rack-1"},
                ),
                NodeConfig(
                    id="srv-worker-01",
                    role=NodeRole.WORKER,
                    ip="192.168.1.102",
                    cpu_cores=8,
                    memory_gb=16,
                    disk_gb=250,
                    status=NodeStatus.PROVISIONED,
                    labels={"node.kubernetes.io/role": "worker", "tier": "app-workloads"},
                ),
                NodeConfig(
                    id="srv-worker-02",
                    role=NodeRole.WORKER,
                    ip="192.168.1.103",
                    cpu_cores=8,
                    memory_gb=16,
                    disk_gb=250,
                    status=NodeStatus.PROVISIONED,
                    labels={"node.kubernetes.io/role": "worker", "tier": "data-workloads"},
                ),
            ],
        )

    @classmethod
    def run_simulation(cls, spec: ClusterSpec = None) -> OrchestrationReport:
        if spec is None:
            spec = cls.get_default_3node_spec()

        orchestrator = CloudForgeOrchestrator(spec)
        return orchestrator.run_deployment()
