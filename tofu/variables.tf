variable "proxmox_api_token" {
  description = "Proxmox API token in the format 'user@realm!tokenid=secret'"
  type        = string
  sensitive   = true
}
