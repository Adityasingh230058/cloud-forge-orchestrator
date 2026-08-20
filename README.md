<div align="center">

# ⚙️ Cloud Forge Orchestrator
### Automated Multi-Server Private Cloud & Kubernetes Cluster Orchestrator with MetalLB & Security Hardening

[![CI Build](https://img.shields.io/badge/CI-GitHub%20Actions-blue.svg)](.github/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11%20|%203.12-brightgreen.svg)](https://www.python.org/)
[![Kubernetes Version](https://img.shields.io/badge/Kubernetes-v1.28%2B-326ce5.svg)](https://kubernetes.io/)
[![Load Balancer](https://img.shields.io/badge/Load%20Balancer-MetalLB%20L2-orange.svg)](https://metallb.universe.tf/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

**`cloud-forge-orchestrator`** is an automated, production-grade private cloud orchestration engine. It transforms raw, multi-server infrastructure (such as 3 bare-metal rack servers or virtual machines) into a fully orchestrated, hardened, multi-node Kubernetes cloud platform equipped with native **Layer 2 Bare-Metal Load Balancing (MetalLB)**, **NGINX Ingress Routing**, and **Zero-Trust NetworkPolicies**.

</div>

---

## 🌟 The Challenge & Solution

In enterprise on-premise data centers, edge computing, and private cloud deployments, setting up a production-ready Kubernetes cluster from scratch across physical servers often lacks a standardized, automated pathway. Administrators struggle to cleanly bridge:
1. **OS & Virtualization Prerequisites** (VT-x, swap memory deactivation, bridge netfilters).
2. **Container Runtime Configuration** (`containerd` with systemd cgroups v2).
3. **Multi-Node Cluster Bootstrapping** (Control-Plane initialization and worker node joining).
4. **Bare-Metal Load Balancing** (Solving the `External-IP: <pending>` problem without cloud provider LB APIs).
5. **Multi-Layer Security Hardening** (Host firewalls, pod micro-segmentation, and secure kubelets).

**`cloud-forge-orchestrator`** solves this by providing a declarative, 5-stage orchestration pipeline that automates the entire lifecycle end-to-end.

---

## 🏛️ 5-Layer Architectural Blueprint

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LAYER 5: SECURITY & HARDENING                          │
│  - Host Firewall (UFW/IPTables)       - Kubernetes NetworkPolicies          │
│  - Namespace Isolation (Default-Deny) - Secure Kubelet & RBAC Controls      │
├─────────────────────────────────────────────────────────────────────────────┤
│                 LAYER 4: LOAD BALANCING & INGRESS TRAFFIC                   │
│  - MetalLB (Bare-Metal Layer 2 IPAddressPool & Virtual IP Speaker)         │
│  - NGINX Ingress Controller (SSL Termination & HTTP/HTTPS Host Routing)    │
├─────────────────────────────────────────────────────────────────────────────┤
│                 LAYER 3: KUBERNETES MULTI-NODE CLUSTER                      │
│  - Server 1: Control-Plane (Master) -> API Server, Etcd, Controller        │
│  - Server 2: Worker Node 01         -> Application Pods & Ingress Pods      │
│  - Server 3: Worker Node 02         -> Data Services & Stateful Pods        │
│  - CNI Plugin: Flannel / Calico VXLAN Overlay Network                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                 LAYER 2: CONTAINER RUNTIME ENGINE                           │
│  - containerd v1.7+ with systemd cgroup driver & cgroups v2                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                 LAYER 1: HYPERVISOR & HARDWARE PREREQUISITES                │
│  - CPU Virtualization flags (VT-x / AMD-V) & Swap Deactivation              │
│  - Linux Kernel Modules (overlay, br_netfilter) & sysctl IP Forwarding      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 3-Server Topology Specification

A typical enterprise deployment maps across 3 servers (1 Master + 2 Workers):

```yaml
# samples/3node_cluster_spec.yaml
cluster_name: "enterprise-edge-k8s"
version: "v1.28.0"

networking:
  pod_cidr: "10.244.0.0/16"
  service_cidr: "10.96.0.0/12"
  cni_plugin: "flannel"
  load_balancer_ip_range: "192.168.1.200-192.168.1.220"
  ingress_controller: "ingress-nginx"

security:
  enforce_default_deny_network_policies: true
  enable_host_firewall: true
  restrict_kubelet_readonly_port: true

nodes:
  - id: "srv-master-01"
    role: "control-plane"
    ip: "192.168.1.101"
    cpu_cores: 4
    memory_gb: 8

  - id: "srv-worker-01"
    role: "worker"
    ip: "192.168.1.102"
    cpu_cores: 8
    memory_gb: 16

  - id: "srv-worker-02"
    role: "worker"
    ip: "192.168.1.103"
    cpu_cores: 8
    memory_gb: 16
```

---

## ⚡ Quickstart

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Adityasingh230058/cloud-forge-orchestrator.git
cd cloud-forge-orchestrator

# Install package in editable mode
pip install -e .
```

---

## 💻 CLI Usage & Commands

### 1. Run Multi-Server Simulation (Zero Hardware Needed)
Simulate the full 5-stage orchestration pipeline locally with rich terminal dashboards and manifest exports:

```bash
cloud-forge simulate --manifests ./generated_manifests
```

### 2. Deploy from Custom Topology Spec
Deploy and configure a live 3-node cluster from a declarative YAML file:

```bash
cloud-forge deploy --spec samples/3node_cluster_spec.yaml --manifests ./deploy_manifests
```

### 3. Generate Production Manifests & Bootstrap Scripts
Output production-ready YAML manifests and bash bootstrapping scripts for each node:

```bash
cloud-forge generate-manifests --output ./k8s_production_manifests
```

### 4. Cluster Health Diagnostics
Inspect API server latency, etcd cluster quorum, CNI routing, and MetalLB VIP pool status:

```bash
cloud-forge health
```

### 5. Security & CIS Compliance Audit
Audit host firewalls, Kubelet port restrictions, and Zero-Trust NetworkPolicies:

```bash
cloud-forge security-audit
```

---

## 🧪 Testing

Run the full automated test suite covering all 5 architectural layers, manifest generation, and CLI commands:

```bash
pytest --cov=cloud_forge --cov-report=term-missing tests/
```

---

## 📂 Repository Structure

```
cloud-forge-orchestrator/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Multi-Python CI test workflow
├── src/
│   └── cloud_forge/
│       ├── __init__.py
│       ├── cli.py                     # Typer + Rich interactive CLI
│       ├── core/
│       │   ├── models.py              # Data models: ClusterSpec, NodeConfig, StageResult
│       │   └── orchestrator.py        # 5-Stage Orchestration State Machine
│       ├── stages/
│       │   ├── base.py                # BaseStage interface
│       │   ├── s01_prereqs.py         # Layer 1: OS, swap, kernel & sysctl
│       │   ├── s02_runtime.py         # Layer 2: containerd & cgroup v2
│       │   ├── s03_cluster.py         # Layer 3: K8s multi-node bootstrap & CNI
│       │   ├── s04_loadbalancer.py    # Layer 4: MetalLB L2 VIP & Ingress
│       │   └── s05_security.py        # Layer 5: Firewall & Zero-Trust NetPol
│       ├── simulation/
│       │   └── mock_engine.py         # Multi-server local sandbox engine
│       ├── manifests/
│       │   └── generator.py           # Production Kubernetes YAML & Bash generator
│       └── reports/
│           └── console.py             # Terminal topology visualizer & dashboards
├── samples/
│   └── 3node_cluster_spec.yaml        # Standard 3-server topology specification
├── tests/
│   ├── test_stages.py                 # Layer 1 to Layer 5 stage tests
│   ├── test_manifests.py              # Manifest validation tests
│   ├── test_orchestrator.py           # State machine pipeline tests
│   └── test_cli.py                    # Typer CLI execution tests
├── pyproject.toml                     # Packaging configuration
├── requirements.txt                   # Dependencies
├── LICENSE                            # MIT License
└── README.md                          # Technical Documentation
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
