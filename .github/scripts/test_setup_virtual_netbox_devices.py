#!/usr/bin/env python3
"""Contract tests for the setup-virtual-netbox-devices.sh wiring."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = ROOT / ".github/scripts/setup-virtual-netbox-devices.sh"
TEARDOWN_SCRIPT = ROOT / ".github/scripts/teardown.sh"


class SetupVirtualNetboxDevicesTests(unittest.TestCase):
    def test_cluster_wiring_matches_the_chart_and_the_teardown(self) -> None:
        """Pin the namespace, Secret, Route, CA and disk-path wiring."""
        setup = SETUP_SCRIPT.read_text()
        teardown = TEARDOWN_SCRIPT.read_text()

        # install-infra pins the osac-infra release — NetBox, its Route and
        # the superuser Secret — to the fixed osac-infra namespace.
        self.assertIn('NETBOX_NAMESPACE="${NETBOX_NAMESPACE:-osac-infra}"', setup)
        self.assertIn('NETBOX_SECRET="${NETBOX_SECRET:-osac-infra-netbox-superuser}"', setup)
        # The Route fallback resolves the chart's Route and verifies with
        # the router's own CA chain.
        self.assertIn('oc get route netbox -n "${NETBOX_NAMESPACE}"', setup)
        self.assertIn("openshift-ingress/router-certs-default", setup)
        # The VM disk dir must stay in lockstep with the teardown's derived
        # path (both default to /tmp).
        self.assertIn('VM_DISK_DIR="/tmp/virtual-bmh-disks-${CLONE_NAME}"', setup)
        self.assertIn('BMH_DISK_ROOT="${VM_DISK_DIR:-/tmp}"', teardown)
        self.assertIn('BMH_DISK_DIR="${BMH_DISK_ROOT%/}/virtual-bmh-disks-${CLONE_NAME}"', teardown)

    def test_transport_policy_stays_with_the_reconcile(self) -> None:
        """No insecure handling and no port-forward in the orchestrator."""
        setup = SETUP_SCRIPT.read_text()

        self.assertNotIn("--insecure", setup)
        self.assertNotIn("port-forward", setup)
        self.assertNotIn("NETBOX_ALLOW_HTTP", setup)


if __name__ == "__main__":
    unittest.main()
