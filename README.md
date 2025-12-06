# Cluster With prod and staging nodes
## Quick Set-up

### 1. Prerequisites Check
```bash
# Verify all tools are installed
kind version
kubectl version --client
helm version
docker --version
```

### 2. Setup Cluster
```bash
make setup-cluster
# OR
./scripts/setup-cluster.sh
```

### 3. Configure Hosts
```bash
sudo sh -c 'echo "127.0.0.1 staging.local.app" >> /etc/hosts'
sudo sh -c 'echo "127.0.0.1 prod.local.app" >> /etc/hosts'
```

### 4. Get Ingress Port
```bash
kubectl get svc -n ingress-nginx
# Note the port (e.g., 8080:xxxxx)
```

### 5. Deploy
```bash
make deploy-staging
make deploy-prod
# OR
./scripts/deploy-staging.sh
./scripts/deploy-prod.sh
```

### 6. Access
```bash
# Replace PORT with the ingress port from step 4
curl http://staging.local.app:PORT/health
curl http://prod.local.app:PORT/health
```

## 📋 Common Commands

```bash
# Build and reload image
make build

# View status
make status

# View logs
make logs-staging
make logs-prod

# Clean everything
make clean

# Jenkins
make start-jenkins
make stop-jenkins
```

## 🔍 Troubleshooting

**Pods not starting?**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

**Image not found?**
```bash
make build
```

**Ingress not working?**
```bash
kubectl get ingress --all-namespaces
kubectl describe ingress <name> -n <namespace>
```

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

