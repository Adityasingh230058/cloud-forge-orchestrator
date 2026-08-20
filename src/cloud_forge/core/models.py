"""
Data models for cluster topologies, node specifications, stage results, and health audits.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import datetime


class NodeRole(str, Enum):
    CONTROL_PLANE = "control-plane"
    WORKER = "worker"


class NodeStatus(str, Enum):
    PROVISIONED = "Provisioned"
    RUNTIME_READY = "RuntimeReady"
    CLUSTER_JOINED = "ClusterJoined"
    READY = "Ready"
    HEALTHY = "Healthy"
    ERROR = "Error"


class StageStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class NodeConfig:
    id: str
    role: NodeRole
    ip: str
    user: str = "root"
    ssh_port: int = 22
    ssh_key_path: Optional[str] = None
    cpu_cores: int = 4
    memory_gb: int = 8
    disk_gb: int = 100
    status: NodeStatus = NodeStatus.PROVISIONED
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value if isinstance(self.role, NodeRole) else str(self.role),
            "ip": self.ip,
            "user": self.user,
            "ssh_port": self.ssh_port,
            "ssh_key_path": self.ssh_key_path,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "disk_gb": self.disk_gb,
            "status": self.status.value if isinstance(self.status, NodeStatus) else str(self.status),
            "labels": self.labels,
        }


@dataclass
class NetworkingConfig:
    pod_cidr: str = "10.244.0.0/16"
    service_cidr: str = "10.96.0.0/12"
    cni_plugin: str = "flannel"  # flannel, calico
    load_balancer_ip_range: str = "192.168.1.200-192.168.1.220"
    ingress_controller: str = "ingress-nginx"
    cluster_dns_ip: str = "10.96.0.10"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SecurityConfig:
    enforce_default_deny_network_policies: bool = True
    enable_host_firewall: bool = True
    restrict_kubelet_readonly_port: bool = True
    enforce_rbac_least_privilege: bool = True
    enable_mtls: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterSpec:
    cluster_name: str
    version: str = "v1.28.0"
    networking: NetworkingConfig = field(default_factory=NetworkingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    nodes: List[NodeConfig] = field(default_factory=list)

    @property
    def control_plane_nodes(self) -> List[NodeConfig]:
        return [n for n in self.nodes if n.role == NodeRole.CONTROL_PLANE]

    @property
    def worker_nodes(self) -> List[NodeConfig]:
        return [n for n in self.nodes if n.role == NodeRole.WORKER]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_name": self.cluster_name,
            "version": self.version,
            "networking": self.networking.to_dict(),
            "security": self.security.to_dict(),
            "nodes": [n.to_dict() for n in self.nodes],
        }


@dataclass
class StageResult:
    stage_number: int
    stage_name: str
    status: StageStatus
    duration_sec: float
    details: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_number": self.stage_number,
            "stage_name": self.stage_name,
            "status": self.status.value if isinstance(self.status, StageStatus) else str(self.status),
            "duration_sec": self.duration_sec,
            "details": self.details,
            "actions_taken": self.actions_taken,
            "errors": self.errors,
        }


@dataclass
class OrchestrationReport:
    cluster_name: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    total_nodes: int = 0
    control_planes: int = 0
    workers: int = 0
    stage_results: List[StageResult] = field(default_factory=list)
    overall_status: str = "SUCCESS"
    allocated_vip: Optional[str] = None
    ingress_endpoint: Optional[str] = None
    security_score: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_name": self.cluster_name,
            "timestamp": self.timestamp,
            "total_nodes": self.total_nodes,
            "control_planes": self.control_planes,
            "workers": self.workers,
            "stage_results": [s.to_dict() for s in self.stage_results],
            "overall_status": self.overall_status,
            "allocated_vip": self.allocated_vip,
            "ingress_endpoint": self.ingress_endpoint,
            "security_score": self.security_score,
        }
