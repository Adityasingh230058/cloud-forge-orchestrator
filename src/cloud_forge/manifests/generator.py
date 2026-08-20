"""
Production Kubernetes YAML Manifest and Bash Playbook Generator.
"""

import os
from typing import Dict, Any
from ..core.models import ClusterSpec


class ManifestGenerator:
    """
    Generates production-grade Kubernetes YAML manifests and bash bootstrapping scripts
    tailored to the supplied ClusterSpec.
    """

    @classmethod
    def generate_all(cls, spec: ClusterSpec, output_dir: str) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        manifests = {}

        # 1. MetalLB Manifests
        metallb_yaml = cls._generate_metallb_manifest(spec)
        metallb_path = os.path.join(output_dir, "01_metallb_l2_pool.yaml")
        with open(metallb_path, "w", encoding="utf-8") as f:
            f.write(metallb_yaml)
        manifests["01_metallb_l2_pool.yaml"] = metallb_yaml

        # 2. Ingress Controller Manifest
        ingress_yaml = cls._generate_ingress_manifest(spec)
        ingress_path = os.path.join(output_dir, "02_nginx_ingress_lb.yaml")
        with open(ingress_path, "w", encoding="utf-8") as f:
            f.write(ingress_yaml)
        manifests["02_nginx_ingress_lb.yaml"] = ingress_yaml

        # 3. Zero-Trust NetworkPolicies Manifest
        netpol_yaml = cls._generate_network_policy_manifest(spec)
        netpol_path = os.path.join(output_dir, "03_zero_trust_network_policies.yaml")
        with open(netpol_path, "w", encoding="utf-8") as f:
            f.write(netpol_yaml)
        manifests["03_zero_trust_network_policies.yaml"] = netpol_yaml

        # 4. Automated Bash Setup Playbook
        bash_script = cls._generate_bash_playbook(spec)
        bash_path = os.path.join(output_dir, "bootstrap_nodes.sh")
        with open(bash_path, "w", encoding="utf-8") as f:
            f.write(bash_script)
        manifests["bootstrap_nodes.sh"] = bash_script

        return manifests

    @staticmethod
    def _generate_metallb_manifest(spec: ClusterSpec) -> str:
        lb_range = spec.networking.load_balancer_ip_range
        return f"""# ==============================================================================
# MetalLB Layer 2 IP Address Pool & L2 Advertisement
# Cluster: {spec.cluster_name}
# ==============================================================================
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: edge-cloud-vip-pool
  namespace: metallb-system
spec:
  addresses:
    - {lb_range}
  autoAssign: true
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: edge-cloud-l2-advert
  namespace: metallb-system
spec:
  ipAddressPools:
    - edge-cloud-vip-pool
"""

    @staticmethod
    def _generate_ingress_manifest(spec: ClusterSpec) -> str:
        return f"""# ==============================================================================
# NGINX Ingress Controller Service (Type: LoadBalancer via MetalLB VIP)
# Cluster: {spec.cluster_name}
# ==============================================================================
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
  annotations:
    metallb.universe.tf/address-pool: edge-cloud-vip-pool
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
    - name: https
      port: 443
      targetPort: https
      protocol: TCP
  selector:
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/component: controller
"""

    @staticmethod
    def _generate_network_policy_manifest(spec: ClusterSpec) -> str:
        return f"""# ==============================================================================
# Zero-Trust Kubernetes Network Policies
# Cluster: {spec.cluster_name}
# ==============================================================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all-ingress-egress
  namespace: default
spec:
  podSelector: {{}}
  policyTypes:
    - Ingress
    - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend-tier
  namespace: default
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/tier: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/tier: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/tier: database
      ports:
        - protocol: TCP
          port: 5432
"""

    @staticmethod
    def _generate_bash_playbook(spec: ClusterSpec) -> str:
        master = spec.control_plane_nodes[0] if spec.control_plane_nodes else None
        master_ip = master.ip if master else "127.0.0.1"

        return f"""#!/usr/bin/env bash
# ==============================================================================
# Cloud Forge Orchestrator: Node Bootstrap & Setup Automation Playbook
# Target Cluster: {spec.cluster_name} ({spec.version})
# ==============================================================================
set -euo pipefail

echo "[*] Step 1: Disabling Linux Swap..."
swapoff -a
sed -i '/swap/d' /etc/fstab

echo "[*] Step 2: Loading Kernel Modules & Configuring Sysctl..."
modprobe overlay
modprobe br_netfilter

cat <<EOF | tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sysctl --system

echo "[*] Step 3: Installing & Configuring Containerd..."
apt-get update && apt-get install -y containerd
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
systemctl restart containerd
systemctl enable containerd

echo "[*] Step 4: Installing Kubeadm, Kubelet & Kubectl..."
apt-get update && apt-get install -y apt-transport-https curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/{spec.version}/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/{spec.version}/deb/ /" | tee /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

echo "[✓] Node setup successfully completed for cluster '{spec.cluster_name}'!"
"""
