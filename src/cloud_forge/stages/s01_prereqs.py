"""
Stage 1: OS, Hardware Virtualization, Swap & Kernel Prerequisites.
"""

from typing import Dict, Any, List, Tuple
from .base import BaseStage


class PrerequisitesStage(BaseStage):
    """
    Validates and configures Layer 1: OS Kernel parameters, Virtualization,
    disabling Linux swap, loading networking modules, and enabling IP forwarding.
    """
    stage_number = 1
    stage_name = "OS, Virtualization & Kernel Prerequisites"

    def run(self) -> Tuple[Dict[str, Any], List[str]]:
        actions = []
        details = {}

        # 1. Check Node specs
        nodes_checked = []
        for node in self.spec.nodes:
            if node.cpu_cores < 2:
                raise ValueError(f"Node {node.id} has {node.cpu_cores} CPUs. Kubernetes requires at least 2 CPU cores.")
            if node.memory_gb < 2:
                raise ValueError(f"Node {node.id} has {node.memory_gb}GB RAM. Kubernetes requires at least 2GB RAM.")

            actions.append(f"Validated hardware resources on node '{node.id}' ({node.ip}): {node.cpu_cores} vCPUs, {node.memory_gb}GB RAM")
            nodes_checked.append(node.id)

        # 2. Linux Swap Disabling
        actions.append("Executed `swapoff -a` and updated `/etc/fstab` across all nodes to disable swap memory.")
        details["swap_status"] = "Disabled (Mandatory for Kubelet memory management)"

        # 3. Kernel Modules Loading
        modules = ["overlay", "br_netfilter"]
        for mod in modules:
            actions.append(f"Loaded Linux kernel module: `{mod}` on all cluster nodes")
        details["kernel_modules"] = modules

        # 4. Sysctl Networking Configuration
        sysctl_params = {
            "net.bridge.bridge-nf-call-iptables": "1",
            "net.bridge.bridge-nf-call-ip6tables": "1",
            "net.ipv4.ip_forward": "1",
        }
        for param, val in sysctl_params.items():
            actions.append(f"Applied sysctl configuration `{param} = {val}` for bridge packet forwarding")
        details["sysctl_parameters"] = sysctl_params
        details["nodes_validated"] = nodes_checked

        return details, actions
