# JBDNS01 — Pi-hole DNS + DHCP + Tailscale / Debian 12 LXC (VMID 105)
resource "proxmox_virtual_environment_container" "jbdns01" {
  node_name   = "JBSRV01"
  vm_id       = 105
  description = "Pi-hole DNS + DHCP + Tailscale subnet router"

  unprivileged = true

  cpu {
    cores = 1
  }

  memory {
    dedicated = 512
    swap      = 512
  }

  disk {
    datastore_id = "local-lvm"
    size         = 8
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  # template_file_id is consumed at creation time only; ignore drift on import.
  operating_system {
    template_file_id = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"
    type             = "debian"
  }

  start_on_boot = true
  started       = true

  lifecycle {
    ignore_changes = [operating_system, initialization]
  }
}
