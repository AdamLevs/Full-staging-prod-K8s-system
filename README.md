# Local Cloud Project - Kubernetes + Helm + Jenkins

A minimal but realistic local cloud project that simulates a typical AWS/EKS setup, running entirely on your local machine using Docker, Kubernetes (kind), Helm, and Jenkins.

##  Project Overview

This project demonstrates a complete local cloud infrastructure with:

- **Kubernetes cluster** (kind) with 3 nodes:
  - 1 control-plane node
  - 1 worker node for staging (labeled `env=staging`)
  - 1 worker node for production (labeled `env=prod`)

- **Demo Application**: A FastAPI REST API that:
  - Connects to PostgreSQL database
  - Uses Redis for caching
  - Exposes endpoints: `/health`, `/items`, `/stats`

- **Infrastructure Components**:
  - PostgreSQL database (deployed per namespace)
  - Redis cache (deployed per namespace)
  - Nginx Ingress Controller
  - Jenkins CI/CD pipeline

- **Kubernetes Namespaces**:
  - `ingress` - for ingress controller
  - `staging` - for staging environment
  - `prod` - for production environment
  - `monitoring` - reserved for future monitoring tools

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10+)
- **kind** (Kubernetes in Docker) - [Installation Guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- **kubectl** - [Installation Guide](https://kubernetes.io/docs/tasks/tools/)
- **helm** (version 3.0+) - [Installation Guide](https://helm.sh/docs/intro/install/)
- **Python 3.11+** (for local development/testing)

### Quick Install (macOS)

```bash
# Install kind
brew install kind

# Install kubectl
brew install kubectl

# Install helm
brew install helm
```

## Quick Start

### 1. Setup Kubernetes Cluster

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Create and configure the cluster
./scripts/setup-cluster.sh
```

This script will:
- Create a kind cluster with 3 nodes (1 control-plane, 2 workers)
- Label worker nodes with `env=staging` and `env=prod`
- Create namespaces (ingress, staging, prod, monitoring)
- Install nginx ingress controller

### 2. Configure Hosts File

Add the following entries to `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

Add these lines:
```
127.0.0.1 staging.local.app
127.0.0.1 prod.local.app
```

### 3. Get Ingress Port

```bash
kubectl get svc -n ingress-nginx
```

Note the port mapping for `ingress-nginx-controller` (usually `80:xxxxx` or `8080:xxxxx`).

### 4. Deploy to Staging

```bash
./scripts/deploy-staging.sh
```

This will:
- Build the Docker image for the application
- Load the image into the kind cluster
- Deploy PostgreSQL, Redis, and the application to the staging namespace
- Configure node selectors to run on the staging node

### 5. Deploy to Production

```bash
./scripts/deploy-prod.sh
```

This will deploy the same components to the production namespace, running on the prod node.

### 6. Access the Application

Once deployed, access your applications:

- **Staging**: `http://staging.local.app:<INGRESS_PORT>`
- **Production**: `http://prod.local.app:<INGRESS_PORT>`

Replace `<INGRESS_PORT>` with the port you noted in step 3.

### 7. Test the API

```bash
# Health check
curl http://staging.local.app:<INGRESS_PORT>/health

# Create an item
curl -X POST http://staging.local.app:<INGRESS_PORT>/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item"}'

# Get all items
curl http://staging.local.app:<INGRESS_PORT>/items

# Get API stats
curl http://staging.local.app:<INGRESS_PORT>/stats
```

##  Project Structure

```
.
├── app/                    # Application source code
│   ├── main.py            # FastAPI application
│   ├── test_main.py       # Unit tests
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Application container image
│
├── helm/                  # Helm charts
│   ├── demo-app/         # Application Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-staging.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/
│   ├── postgresql/        # PostgreSQL Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-staging.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/
│   └── redis/             # Redis Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-staging.yaml
│       ├── values-prod.yaml
│       └── templates/
│
├── k8s/                   # Kubernetes manifests
│   └── namespaces.yaml   # Namespace definitions
│
├── jenkins/               # Jenkins configuration
│   ├── Jenkinsfile       # CI/CD pipeline definition
│   └── docker-compose.yml # Jenkins container setup
│
├── scripts/              # Setup and deployment scripts
│   ├── setup-cluster.sh  # Cluster initialization
│   ├── deploy-staging.sh # Staging deployment
│   ├── deploy-prod.sh    # Production deployment
│   └── setup-jenkins.sh  # Jenkins setup
│
├── kind-config.yaml      # kind cluster configuration
└── README.md             # This file
```

##  Manual Deployment

If you prefer to deploy manually:

### Deploy PostgreSQL

```bash
# Staging
helm upgrade --install postgresql-staging ./helm/postgresql \
  --namespace staging \
  --create-namespace \
  --values ./helm/postgresql/values-staging.yaml \
  --set postgresql.database=appdb \
  --set postgresql.username=appuser \
  --set postgresql.password=apppass

# Production
helm upgrade --install postgresql-prod ./helm/postgresql \
  --namespace prod \
  --create-namespace \
  --values ./helm/postgresql/values-prod.yaml \
  --set postgresql.database=appdb \
  --set postgresql.username=appuser \
  --set postgresql.password=apppass
```

### Deploy Redis

```bash
# Staging
helm upgrade --install redis-staging ./helm/redis \
  --namespace staging \
  --create-namespace \
  --values ./helm/redis/values-staging.yaml

# Production
helm upgrade --install redis-prod ./helm/redis \
  --namespace prod \
  --create-namespace \
  --values ./helm/redis/values-prod.yaml
```

### Build and Load Application Image

```bash
# Build image
docker build -t demo-app:latest ./app

# Load into kind cluster
kind load docker-image demo-app:latest --name local-cluster
```

### Deploy Application

```bash
# Staging
helm upgrade --install demo-app-staging ./helm/demo-app \
  --namespace staging \
  --create-namespace \
  --values ./helm/demo-app/values-staging.yaml \
  --set image.repository=demo-app \
  --set image.tag=latest \
  --set image.pullPolicy=IfNotPresent

# Production
helm upgrade --install demo-app-prod ./helm/demo-app \
  --namespace prod \
  --create-namespace \
  --values ./helm/demo-app/values-prod.yaml \
  --set image.repository=demo-app \
  --set image.tag=latest \
  --set image.pullPolicy=IfNotPresent
```

## CI/CD with Jenkins

### Setup Jenkins

1. **Start Jenkins**:

```bash
./scripts/setup-jenkins.sh
```

2. **Access Jenkins**:
   - Open `http://localhost:8080` in your browser
   - Get initial admin password:
     ```bash
     docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
     ```

3. **Configure Jenkins**:
   - Install suggested plugins
   - Create admin user
   - Ensure Docker, kubectl, helm, and kind are available in Jenkins container

4. **Copy kubectl config to Jenkins**:

```bash
# Create .kube directory in Jenkins
docker exec jenkins mkdir -p /var/jenkins_home/.kube

# Copy kubeconfig
docker cp ~/.kube/config jenkins:/var/jenkins_home/.kube/config

# Set permissions
docker exec jenkins chown jenkins:jenkins /var/jenkins_home/.kube/config
```

5. **Create Pipeline Job**:
   - Go to Jenkins dashboard
   - Click "New Item"
   - Enter name: "demo-app-pipeline"
   - Select "Pipeline"
   - Click OK
   - In Pipeline section:
     - Definition: "Pipeline script from SCM"
     - SCM: Git
     - Repository URL: `file:///workspace` (or your git repository URL)
     - Script Path: `jenkins/Jenkinsfile`
   - Click Save

6. **Run Pipeline**:
   - Click "Build Now" on the pipeline job
   - The pipeline will:
     - Checkout code
     - Build Docker image
     - Run tests
     - Load image to kind cluster
     - Deploy to staging
     - Optionally deploy to production (requires manual approval)

### Jenkins Pipeline Stages

The Jenkins pipeline includes:

1. **Checkout**: Gets code from repository
2. **Build**: Builds Docker image
3. **Test**: Runs unit tests
4. **Load Image to Kind**: Loads image into Kubernetes cluster
5. **Deploy to Staging**: Deploys application to staging namespace
6. **Smoke Test**: Verifies staging deployment
7. **Deploy to Production**: Manual approval required for production deployment

## Architecture

### Cluster Layout

```
┌─────────────────────────────────────────┐
│         kind Cluster                    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Control Plane Node             │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Worker Node (env=staging)      │  │
│  │   - PostgreSQL                   │  │
│  │   - Redis                        │  │
│  │   - Demo App (staging)           │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Worker Node (env=prod)         │  │
│  │   - PostgreSQL                   │  │
│  │   - Redis                        │  │
│  │   - Demo App (prod)              │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Application Flow

```
Browser → Ingress Controller → Demo App → PostgreSQL
                              ↓
                            Redis
```

## Verification

### Check Cluster Status

```bash
# List nodes
kubectl get nodes --show-labels

# List pods in all namespaces
kubectl get pods --all-namespaces

# Check staging deployment
kubectl get all -n staging

# Check production deployment
kubectl get all -n prod
```

### Verify Node Selectors

```bash
# Check staging pods are on staging node
kubectl get pods -n staging -o wide

# Check prod pods are on prod node
kubectl get pods -n prod -o wide
```

### View Logs

```bash
# Application logs (staging)
kubectl logs -n staging -l app.kubernetes.io/name=demo-app

# Application logs (prod)
kubectl logs -n prod -l app.kubernetes.io/name=demo-app

# PostgreSQL logs
kubectl logs -n staging -l app.kubernetes.io/name=postgresql

# Redis logs
kubectl logs -n staging -l app.kubernetes.io/name=redis
```

## Cleanup

### Delete Deployments

```bash
# Delete staging
helm uninstall demo-app-staging -n staging
helm uninstall postgresql-staging -n staging
helm uninstall redis-staging -n staging

# Delete production
helm uninstall demo-app-prod -n prod
helm uninstall postgresql-prod -n prod
helm uninstall redis-prod -n prod
```

### Delete Cluster

```bash
kind delete cluster --name local-cluster
```

### Stop Jenkins

```bash
cd jenkins
docker-compose down
```

## Security Notes

**Important**: This is a local development setup. The following are **NOT** production-ready:

- Database passwords are in plain text in values files
- No TLS/SSL encryption
- No network policies
- No RBAC restrictions
- Secrets are stored in Helm values (should use external secret management)

For production use, implement:
- External secret management (e.g., AWS Secrets Manager, HashiCorp Vault)
- TLS certificates
- Network policies
- RBAC with least privilege
- Image scanning
- Resource quotas

## Moving to AWS/EKS

This project is designed to be easily portable to AWS/EKS. Key changes needed:

1. **Replace kind with EKS cluster**
2. **Use ECR for container registry** instead of loading images directly
3. **Use RDS for PostgreSQL** (optional, can still use in-cluster)
4. **Use ElastiCache for Redis** (optional, can still use in-cluster)
5. **Use ALB/NLB** instead of nginx ingress (or use AWS Load Balancer Controller)
6. **Use EKS node groups** with proper labels
7. **Configure IAM roles** for service accounts
8. **Use AWS Secrets Manager** for secrets
9. **Use Route53** for DNS instead of /etc/hosts

## Configuration Differences: Staging vs Production

| Feature | Staging | Production |
|---------|---------|------------|
| Replicas | 1 | 2 |
| CPU Request | 100m | 200m |
| CPU Limit | 500m | 1000m |
| Memory Request | 128Mi | 256Mi |
| Memory Limit | 512Mi | 1Gi |
| PostgreSQL Storage | 10Gi | 20Gi |
| Node Selector | `env=staging` | `env=prod` |

## Troubleshooting

### Images not found

```bash
# Rebuild and reload image
docker build -t demo-app:latest ./app
kind load docker-image demo-app:latest --name local-cluster
```

### Pods stuck in Pending

```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name> -n <namespace>
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl get ingress --all-namespaces
kubectl describe ingress <ingress-name> -n <namespace>
```

### Database connection issues

```bash
# Check PostgreSQL service
kubectl get svc -n <namespace>

# Test connection from app pod
kubectl exec -it <app-pod> -n <namespace> -- psql -h postgresql-service -U appuser -d appdb
```

## Additional Resources

- [kind Documentation](https://kind.sigs.k8s.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)

## Contributing

This is a demonstration project. Feel free to extend it with:
- Frontend application
- Monitoring stack (Prometheus/Grafana)
- Logging stack (ELK/Loki)
- Service mesh (Istio/Linkerd)
- GitOps (ArgoCD/Flux)

## License

This project is provided as-is for educational and demonstration purposes.

---

**Happy Cloud Native Development!**
