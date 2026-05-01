# homelab-gitops

GitOps repository for the homelab k3s cluster on JBK8S01 (192.168.0.207).
Managed by ArgoCD — changes merged to `main` are automatically applied to the cluster.

## Structure

```
apps/        ArgoCD Application manifests (one per app)
charts/      Helm umbrella charts with values overrides
```

## Apps

| App | Namespace | Chart | UI |
|-----|-----------|-------|----|
| argocd | argocd | argo/argo-cd 9.5.9 | http://192.168.0.207:30808 |

## Bootstrap (new cluster)

1. Install k3s: `curl -sfL https://get.k3s.io | sh -`
2. Install Helm: `curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`
3. Bootstrap ArgoCD manually: `helm repo add argo https://argoproj.github.io/argo-helm && helm install argocd argo/argo-cd -n argocd --create-namespace`
4. Apply self-management: `kubectl apply -f apps/argocd.yaml`
5. ArgoCD takes over — all future changes via Git
