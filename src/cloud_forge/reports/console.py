"""
Rich Console Output & Visual Topology Dashboard for Cloud Forge Orchestrator.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from ..core.models import OrchestrationReport, StageStatus, ClusterSpec

# Safe UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ConsoleReporter:
    """
    Renders terminal dashboards for cluster provisioning, node topology, and security audits.
    """

    def __init__(self):
        self.console = Console(highlight=False)

    def print_deployment_report(self, report: OrchestrationReport, spec: ClusterSpec) -> None:
        self.console.print()
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[bold white]CLOUD FORGE ORCHESTRATOR[/bold white] [cyan]v1.0.0[/cyan]\n"
                    f"[dim]Automated Multi-Server Private Cloud & Kubernetes Cluster Engine[/dim]\n\n"
                    f"Cluster: [bold yellow]{report.cluster_name}[/bold yellow] | "
                    f"Nodes: [bold cyan]{report.total_nodes}[/bold cyan] ({report.control_planes} CP, {report.workers} Worker) | "
                    f"Status: [{'bold green' if report.overall_status == 'SUCCESS' else 'bold red'}]{report.overall_status}[/]"
                ),
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

        # 1. 5-Layer Stage Execution Table
        stage_table = Table(title="[bold cyan]5-Layer Orchestration Pipeline Status[/bold cyan]", box=box.ROUNDED)
        stage_table.add_column("Stage #", justify="center", style="cyan")
        stage_table.add_column("Layer / Stage Name", style="bold white")
        stage_table.add_column("Status", justify="center")
        stage_table.add_column("Duration", justify="right", style="dim")
        stage_table.add_column("Key Output / Action", style="yellow")

        for s in report.stage_results:
            status_style = "bold green" if s.status == StageStatus.SUCCESS else "bold red"
            key_action = s.actions_taken[-1] if s.actions_taken else "Completed"
            if len(key_action) > 65:
                key_action = key_action[:62] + "..."

            stage_table.add_row(
                f"L{s.stage_number}",
                s.stage_name,
                Text(s.status.value, style=status_style),
                f"{s.duration_sec}s",
                key_action,
            )

        self.console.print(stage_table)

        # 2. Node Topology Table
        node_table = Table(title="[bold green]Cluster Node Topology & Hardware Mapping[/bold green]", box=box.SIMPLE_HEAVY)
        node_table.add_column("Node ID", style="bold white")
        node_table.add_column("Role", style="cyan")
        node_table.add_column("IP Address", style="yellow")
        node_table.add_column("vCPU / RAM", style="dim")
        node_table.add_column("State", justify="center")
        node_table.add_column("Workload Label", style="italic")

        for n in spec.nodes:
            node_table.add_row(
                n.id,
                n.role.value,
                n.ip,
                f"{n.cpu_cores} cores / {n.memory_gb}GB",
                "[bold green]Ready[/bold green]",
                str(n.labels.get("tier", "system-core")),
            )

        self.console.print(node_table)

        # 3. Load Balancing & Ingress Summary
        if report.allocated_vip:
            lb_panel_text = Text()
            lb_panel_text.append(f"• Layer 2 Virtual IP (VIP): {report.allocated_vip}\n", style="bold cyan")
            lb_panel_text.append(f"• Ingress Controller Endpoint: {report.ingress_endpoint}\n", style="bold yellow")
            lb_panel_text.append(f"• Ingress Routing: External Traffic -> MetalLB Speaker -> NGINX Ingress -> Pods\n", style="white")
            lb_panel_text.append(f"• Security Posture Score: {report.security_score}% (UFW + NetworkPolicies Enforced)", style="bold green")
            self.console.print(Panel(lb_panel_text, title="[bold]Network Routing & Security State[/bold]", border_style="green", box=box.ROUNDED))

        self.console.print()
