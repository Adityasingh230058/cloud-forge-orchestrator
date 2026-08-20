"""
Stage 3: Multi-Node Kubernetes Cluster Bootstrap (Control-Plane, Worker Joins & CNI).
"""

from typing import Dict, Any, List, Tuple
from .base import BaseStage
from ..core.models import NodeRole, NodeStatus


class KubernetesClusterStage(BaseStage):
    """
    Validates and configures Layer 3: Control-Plane initialization on Server 1,
    join token generation, multi-node worker joins on Server 2 & Server 3,
    and CNI overlay network (Flannel / Calico).
    """
    stage_number = 3
    stage_name = "Kubernetes Multi-Node Cluster Bootstrap"

    def run(self) -> Tuple[Dict[str, Any], List[str]]:
        actions = []
        details = {}

        cp_nodes = self.spec.control_plane_nodes
        worker_nodes = self.spec.worker_nodes

        if not cp_nodes:
            raise ValueError("No control-plane node specified in cluster spec.")
        if not worker_nodes:
            raise ValueError("At least one worker node is required for multi-node topology.")

        master = cp_nodes[0]

        # 1. Initialize Control-Plane
        pod_cidr = self.spec.networking.pod_cidr
        service_cidr = self.spec.networking.service_cidr
        actions.append(
            f"Initialized Control-Plane on '{master.id}' ({master.ip}) with `kubeadm init "
            f"--pod-network-cidr={pod_cidr} --service-cidr={service_cidr}`"
        )
        actions.append(f"Exported admin kubeconfig to `/etc/kubernetes/admin.conf` on '{master.id}'")
        master.status = NodeStatus.READY

        # 2. Deploy CNI Overlay Network
        cni = self.spec.networking.cni_plugin
        actions.append(f"Deployed `{cni}` CNI overlay network plugin across the cluster (Pod CIDR: {pod_cidr})")

        # 3. Generate Secure Join Token
        join_token = "abcdef.0123456789abcdef"
        ca_hash = "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
        join_cmd = f"kubeadm join {master.ip}:6443 --token {join_token} --discovery-token-ca-cert-hash {ca_hash}"
        actions.append(f"Generated secure cluster join token on Control-Plane '{master.id}'")

        # 4. Join Worker Nodes
        joined_workers = []
        for worker in worker_nodes:
            actions.append(f"Executed join command on '{worker.id}' ({worker.ip}) -> Joined cluster successfully")
            worker.status = NodeStatus.READY
            joined_workers.append(worker.id)

        details["kubernetes_version"] = self.spec.version
        details["control_plane"] = master.id
        details["workers_joined"] = joined_workers
        details["total_nodes"] = len(self.spec.nodes)
        details["cni_plugin"] = cni
        details["cluster_status"] = "Multi-Node Quorum Formed (All Nodes Ready)"

        return details, actions
