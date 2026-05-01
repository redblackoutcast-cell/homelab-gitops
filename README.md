# homelab-gitops

GitOps repository for the homelab k3s cluster on JBK8S01 (192.168.0.207).
Managed by ArgoCD - changes merged to `main` are automatically applied to the cluster.

## Structure

```
apps/        ArgoCD Application manifests (one per app)
charts/      Helm umbrella charts with our values overrides
```

## Apps

| App | Namespace | Chart | Version | UI |
|-----|-----------|-------|---------|----|
| argocd | argocd | argo/argo-cd | 9.5.9 | http://192.168.0.207:30808 |
| kube-prometheus-stack | monitoring | prometheus-community/kube-prometheus-stack | 84.4.0 | Grafana: http://192.168.0.207:30300 · Prometheus: http://192.168.0.207:30900 |

## Adding a new app

1. Create `charts/<appname>/Chart.yaml` - umbrella chart declaring the upstream as a dependency
2. Create `charts/<appname>/values.yaml` - Helm values overrides
3. Create `apps/<appname>.yaml` - ArgoCD Application manifest pointing at `charts/<appname>`
4. Push to `main` → ArgoCD auto-syncs within ~3 minutes

## Known quirks

**Traefik holds ports 80/443 via ServiceLB**
k3s ships Traefik as the default ingress, and ServiceLB (klipper-lb) binds it to ports 80 and 443 on the node's IP. Any other service with `type: LoadBalancer` on those ports will stay `Pending`. Use `type: NodePort` with an explicit `nodePort` for everything else.

**Grafana initChownData fails on local-path PVs**
The Grafana chart's `initChownData` init container (`chown -R 472`) fails on directories already written by the Grafana process on an existing PV. All Grafana deployments in this repo disable it and use `fsGroup: 472` instead - the kernel sets group ownership at mount time. See `charts/kube-prometheus-stack/values.yaml`.

**Grafana admin password**
The k8s secret (`monitoring/kube-prometheus-stack-grafana`) can fall out of sync with the Grafana SQLite DB after rollouts. If login fails, reset via:
```bash
kubectl exec -n monitoring deployment/kube-prometheus-stack-grafana -c grafana -- /bin/sh -c "grafana cli admin reset-admin-password 'newpassword'"
```

## Bootstrap (new cluster from scratch)

Full step-by-step rebuild procedure is in the homelab docs repo:
`docs/jbk8s01.md` - covers Proxmox VM creation, cloud-init, k3s, Helm, ArgoCD bootstrap, and kube-prometheus-stack.

Short version:
1. Provision VM 106 on Proxmox from Ubuntu 24.04 cloud image (cloud-init sets static IP 192.168.0.207)
2. `curl -sfL https://get.k3s.io | sh -` on JBK8S01
3. Copy kubeconfig to JBVM02, install kubectl + Helm
4. `helm install argocd argo/argo-cd -n argocd --create-namespace --set server.service.type=NodePort --set server.service.nodePortHttp=30808 --set configs.params."server\.insecure"=true`
5. `kubectl apply -f apps/argocd.yaml` - ArgoCD takes over its own config
6. `kubectl apply -f apps/kube-prometheus-stack.yaml` - observability stack deploys
