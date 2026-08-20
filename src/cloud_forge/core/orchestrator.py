"""
Cloud Forge Orchestrator: 5-Stage Private Cloud Provisioning State Machine.
"""

from typing import List, Optional
from .models import ClusterSpec, OrchestrationReport, StageStatus
from ..stages.s01_prereqs import PrerequisitesStage
from ..stages.s02_runtime import ContainerRuntimeStage
from ..stages.s03_cluster import KubernetesClusterStage
from ..stages.s04_loadbalancer import LoadBalancerIngressStage
from ..stages.s05_security import SecurityHardeningStage


class CloudForgeOrchestrator:
    """
    Coordinates the end-to-end 5-layer private cloud provisioning lifecycle:
      Layer 1: OS, Kernel & Virtualization Prerequisites
      Layer 2: Container Runtime Engine (containerd)
      Layer 3: Kubernetes Multi-Node Cluster Bootstrap (Control-Plane + Workers)
      Layer 4: Bare-Metal Load Balancer (MetalLB) & Ingress Controller
      Layer 5: Multi-Layer Security Hardening & Zero-Trust NetworkPolicies
    """

    def __init__(self, spec: ClusterSpec):
        self.spec = spec
        self.stages = [
            PrerequisitesStage(self.spec),
            ContainerRuntimeStage(self.spec),
            KubernetesClusterStage(self.spec),
            LoadBalancerIngressStage(self.spec),
            SecurityHardeningStage(self.spec),
        ]

    def run_deployment(self) -> OrchestrationReport:
        """
        Executes all 5 stages in strict sequential dependency order.
        Halts pipeline if any stage fails.
        """
        report = OrchestrationReport(
            cluster_name=self.spec.cluster_name,
            total_nodes=len(self.spec.nodes),
            control_planes=len(self.spec.control_plane_nodes),
            workers=len(self.spec.worker_nodes),
            overall_status="SUCCESS",
        )

        for stage in self.stages:
            stage_result = stage.execute()
            report.stage_results.append(stage_result)

            # Capture key allocated properties
            if stage.stage_number == 4 and stage_result.status == StageStatus.SUCCESS:
                report.allocated_vip = stage_result.details.get("assigned_ingress_vip")
                report.ingress_endpoint = f"http://{report.allocated_vip}"

            if stage_result.status == StageStatus.FAILED:
                report.overall_status = "FAILED"
                break

        return report
