"""
Unit tests for Kubernetes YAML and bash manifest generation.
"""

import os
import yaml
from cloud_forge.manifests.generator import ManifestGenerator
from cloud_forge.simulation.mock_engine import ClusterSimulator


def test_manifest_generation(tmp_path):
    spec = ClusterSimulator.get_default_3node_spec()
    out_dir = os.path.join(tmp_path, "manifests")

    manifests = ManifestGenerator.generate_all(spec, out_dir)

    assert len(manifests) == 4
    assert "01_metallb_l2_pool.yaml" in manifests
    assert "02_nginx_ingress_lb.yaml" in manifests
    assert "03_zero_trust_network_policies.yaml" in manifests
    assert "bootstrap_nodes.sh" in manifests

    # Validate YAML content
    metallb_content = manifests["01_metallb_l2_pool.yaml"]
    assert "IPAddressPool" in metallb_content
    assert spec.networking.load_balancer_ip_range in metallb_content

    netpol_content = manifests["03_zero_trust_network_policies.yaml"]
    assert "default-deny-all-ingress-egress" in netpol_content

    bash_content = manifests["bootstrap_nodes.sh"]
    assert "swapoff -a" in bash_content
    assert "containerd" in bash_content
