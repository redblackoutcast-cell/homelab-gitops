# JBNAS01 — TrueNAS SCALE 25.04 (VMID 101)
resource "proxmox_virtual_environment_vm" "jbnas01" {
  node_name = "JBSRV01"
  vm_id     = 101
  name      = "JBNAS01"

  machine = "q35"
  bios    = "seabios"

  agent {
    enabled = false
  }

  cpu {
    cores = 4
    type  = "host"
  }

  memory {
    dedicated = 12288
  }

  # OS disk only; SATA passthrough disks (JBNAS_MEDIA HDDs, JBNAS_SSD SSDs)
  # are managed outside Tofu — ignore_changes prevents drift detection on them.
  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 32
  }

  network_device = [{
    bridge       = "vmbr0"
    model        = "virtio"
    enabled      = true  # deprecated but still required by provider schema
    disconnected = false
    firewall     = false
    mac_address  = null
    mtu          = null
    queues       = null
    rate_limit   = null
    trunks       = null
    vlan_id      = null
  }]

  on_boot = true
  started = true

  lifecycle {
    ignore_changes = [disk]
  }
}

# JBVM01 — Jump box / Debian 13 desktop (VMID 102)
resource "proxmox_virtual_environment_vm" "jbvm01" {
  node_name = "JBSRV01"
  vm_id     = 102
  name      = "JBVM01"

  machine = "q35"
  bios    = "seabios"

  agent {
    enabled = false
  }

  cpu {
    cores = 2
    type  = "host"
  }

  memory {
    dedicated = 4096
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 32
  }

  network_device = [{
    bridge       = "vmbr0"
    model        = "virtio"
    enabled      = true  # deprecated but still required by provider schema
    disconnected = false
    firewall     = false
    mac_address  = null
    mtu          = null
    queues       = null
    rate_limit   = null
    trunks       = null
    vlan_id      = null
  }]

  on_boot = true
  started = true
}

# JBVM02 — Claude Code / Ubuntu 24.04 (VMID 103)
resource "proxmox_virtual_environment_vm" "jbvm02" {
  node_name = "JBSRV01"
  vm_id     = 103
  name      = "JBVM02"

  machine = "q35"
  bios    = "seabios"

  agent {
    enabled = false
  }

  cpu {
    cores = 4
    type  = "host"
  }

  memory {
    dedicated = 8192
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 64
  }

  network_device = [{
    bridge       = "vmbr0"
    model        = "virtio"
    enabled      = true  # deprecated but still required by provider schema
    disconnected = false
    firewall     = false
    mac_address  = null
    mtu          = null
    queues       = null
    rate_limit   = null
    trunks       = null
    vlan_id      = null
  }]

  on_boot = true
  started = true
}

# JBVM03 — Minecraft server / Ubuntu 24.04 (VMID 104)
resource "proxmox_virtual_environment_vm" "jbvm03" {
  node_name = "JBSRV01"
  vm_id     = 104
  name      = "JBVM03"

  machine = "q35"
  bios    = "seabios"

  agent {
    enabled = false
  }

  cpu {
    cores = 4
    type  = "host"
  }

  memory {
    dedicated = 12288
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = 64
  }

  network_device = [{
    bridge       = "vmbr0"
    model        = "virtio"
    enabled      = true  # deprecated but still required by provider schema
    disconnected = false
    firewall     = false
    mac_address  = null
    mtu          = null
    queues       = null
    rate_limit   = null
    trunks       = null
    vlan_id      = null
  }]

  on_boot = true
  started = true
}
