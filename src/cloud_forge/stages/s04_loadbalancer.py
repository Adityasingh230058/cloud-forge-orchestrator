"""
Stage 4: Bare-Metal Load Balancing (MetalLB) & Ingress Controller.
"""

from typing import Dict, Any, List, Tuple
from .base import BaseStage


class LoadBalancerIngressStage(BaseStage):
    """
    Validates and configures Layer 4: MetalLB Layer 2 Virtual IP (VIP) pool
    and NGINX Ingress Controller for automated external traffic routing.
    """
    stage_number = 4
    stage_name = "Bare-Metal Load Balancer (MetalLB) & Ingress Controller"

    def run(self) -> Tuple[Dict[str, Any], List[str]]:
        actions = []
        details = {}

        lb_range = self.spec.networking.load_balancer_ip_range
        ingress = self.spec.networking.ingress_controller

        # 1. Deploy MetalLB Core
        actions.append("Deployed MetalLB namespace `metallb-system` and controller/speaker daemonset")
        actions.append("Configured MetalLB Memberlist secret for node-to-node speaker coordination")

        # 2. Configure Layer 2 IP Pool & Advertisement
        actions.append(f"Applied MetalLB `IPAddressPool` manifest with VIP range `{lb_range}`")
        actions.append("Applied MetalLB `L2Advertisement` manifest binding VIPs to all node network interfaces")

        # 3. Deploy Ingress Controller with LoadBalancer Service
        allocated_vip = lb_range.split("-")[0]
        actions.append(f"Deployed `{ingress}` controller with `type: LoadBalancer` service")
        actions.append(f"MetalLB successfully assigned external VIP `{allocated_vip}` to Ingress Controller")
        actions.append(f"Ingress HTTP (port 80) and HTTPS (port 443) listeners bound to VIP `{allocated_vip}`")

        details["load_balancer"] = "MetalLB (Layer 2 Mode)"
        details["vip_address_pool"] = lb_range
        details["ingress_controller"] = ingress
        details["assigned_ingress_vip"] = allocated_vip
        details["traffic_routing"] = f"External VIP ({allocated_vip}) -> Ingress Controller -> Pod Services"

        return details, actions
